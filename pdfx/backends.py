# -*- coding: utf-8 -*-
"""
PDF Backend: pdfMiner
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import re
from io import BytesIO, StringIO
from collections import namedtuple

# Character Detection Helper
import chardet

# Find URLs in text via regex
from .libs import urlmarker

# Setting `psparser.STRICT` is the first thing to do because it is
# referenced in the other pdfparser modules
from pdfminer import psparser
psparser.STRICT = False
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter


IS_PY2 = sys.version_info < (3, 0)
if not IS_PY2:
    # Python 3
    unicode = str


def make_compat_str(in_str):
    """ Tries to guess encoding and return a standard unicode string """
    assert isinstance(in_str, (bytes, str, unicode))
    if not in_str:
        return in_str
    enc = chardet.detect(in_str)
    out_str = in_str.decode(enc['encoding'])
    if enc['encoding'] == "UTF-16BE":
        # Remove byte order marks (BOM)
        if out_str.startswith('\ufeff'):
            out_str = out_str[1:]
    return out_str


class Reference(object):
    """ Generic Reference """
    ref = ""
    reftype = "url"

    def __init__(self, uri):
        self.ref = uri
        if uri.lower().endswith(".pdf"):
            self.reftype = "pdf"

    def __hash__(self):
        return hash(self.ref)

    def __eq__(self, other):
        assert isinstance(other, Reference)
        return self.ref == other.ref

    def __str__(self):
        return "<%s:%s>" % (self.reftype, self.ref)

class ReaderBackend(object):
    """
    Base class of all Readers (eg. for PDF files, text, etc.)

    The job of a Reader is to extract Text and Links.
    """
    text = ""
    metadata = {}
    references = set()

    def get_metadata(self):
        return self.metadata

    def get_text(self):
        return self.text

    def get_references(self, reftype=None, sort=False):
        refs = self.references
        if reftype:
            refs = set([ref for ref in refs if ref.reftype == "pdf"])
        return sorted(refs) if sort else refs


class PDFMinerBackend(ReaderBackend):
    def __init__(self, pdf_stream, password='', pagenos=[], maxpages=0):
        self.pdf_stream = pdf_stream

        # Extract Metadata
        parser = PDFParser(pdf_stream)
        doc = PDFDocument(parser, password=password, caching=True)
        if doc.info:
            for k in doc.info[0]:
                v = doc.info[0][k]
                # print(repr(v), type(v))
                if isinstance(v, (bytes, str, unicode)):
                    self.metadata[k] = make_compat_str(v)
                elif isinstance(v, (psparser.PSLiteral, psparser.PSKeyword)):
                    self.metadata[k] = v.name

        # Extract Content
        text_io = BytesIO()
        rsrcmgr = PDFResourceManager(caching=True)
        converter = TextConverter(rsrcmgr, text_io, codec="utf-8",
                laparams=LAParams(), imagewriter=None)
        interpreter = PDFPageInterpreter(rsrcmgr, converter)

        self.metadata["Pages"] = 0
        for page in PDFPage.get_pages(self.pdf_stream, pagenos=pagenos,
                                      maxpages=maxpages, password=password,
                                      caching=True, check_extractable=True):
            # Read page contents
            interpreter.process_page(page)
            self.metadata["Pages"] += 1

            # Collect URL annotations
            if page.annots:
                for annot in page.annots:
                    a = annot.resolve()
                    if "A" in a and "URI" in a["A"]:
                        ref = Reference(a["A"]["URI"].decode("utf-8"))
                        self.references.add(ref)

        # Get text from stream
        self.text = text_io.getvalue().decode("utf-8")
        text_io.close()
        converter.close()
        # print(self.text)

        # Extract URL references from text
        for url in urlmarker.get_urls(self.text):
            self.references.add(Reference(url))

        # TODO: Search for ArXiv References

class TextBackend(ReaderBackend):
    def __init__(self, stream):
        self.text = stream.read()
        for url in urlmarker.get_urls(self.text):
            self.references.add(Reference.from_url(url))
