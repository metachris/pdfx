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

import chardet

from .libs import urlmarker

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
    """ Tries to guess encoding and return unicode """
    assert isinstance(in_str, (bytes, str, unicode))
    enc = chardet.detect(in_str)
    out_str = in_str.decode(enc['encoding'])
    if enc['encoding'] == "UTF-16BE":
        # Remove byte order marks (BOM)
        if out_str.startswith('\ufeff'):
            out_str = out_str[1:]
    return out_str


class Reference(namedtuple("Reference", ["ref", "type"])):
    """ Generic Reference """
    @staticmethod
    def from_url(s):
        reftype = "url"
        if s.lower().endswith(".pdf"):
            reftype = "pdf"
        return Reference(s, reftype)


class ReaderBackend(object):
    """
    Base class of all Readers (eg. for PDF files, text, etc.)

    The job of a Reader is to extract Text and Links.
    """
    text = ""
    metadata = {}
    references = set()

    def __init__(self, stream):
        """
        This is the only method required to implement. Should at least
        extract `self.text` and `self.urls` from the stream.
        """
        pass

    def get_metadata(self):
        return self.metadata

    def get_text(self):
        return self.text

    def get_references(self, reftype=None, sort=False):
        refs = self.references
        if reftype:
            refs = set([ref for ref in refs if ref.type == "pdf"])
        return sorted(refs) if sort else refs


class PDFMinerBackend(ReaderBackend):
    def __init__(self, pdf_stream, password='', pagenos=[], maxpages=0):
        self.pdf_stream = pdf_stream

        # Extract Metadata
        parser = PDFParser(pdf_stream)
        doc = PDFDocument(parser, password=password, caching=True)
        if doc.info:
            for k in doc.info[0]:
                self.metadata[k] = make_compat_str(doc.info[0][k])

        # Extract Content
        text_io = BytesIO()
        rsrcmgr = PDFResourceManager(caching=True)
        converter = TextConverter(rsrcmgr, text_io, codec="utf-8",
                laparams=LAParams(), imagewriter=None)
        interpreter = PDFPageInterpreter(rsrcmgr, converter)
        for page in PDFPage.get_pages(self.pdf_stream, pagenos=pagenos,
                                      maxpages=maxpages, password=password,
                                      caching=True, check_extractable=True):
            # Collect URL annotations
            for annot in page.annots:
                a = annot.resolve()
                if "A" in a and "URI" in a["A"]:
                    ref = Reference.from_url(a["A"]["URI"].decode("utf-8"))
                    self.references.add(ref)

            # Read page contents
            interpreter.process_page(page)

        # Get text from stream
        self.text = text_io.getvalue().decode("utf-8")
        text_io.close()
        converter.close()
        # print(self.text)

        # Extract URL references from text
        for url in urlmarker.get_urls(self.text):
            self.references.add(Reference.from_url(url))

        # print(self.references)

        # Get Metadata
        # self.num_pages = self.pdf.getNumPages()
        # self.pdf_metadata["Pages"] = self.num_pages
        # doc_info = self.pdf.getDocumentInfo()
        # if doc_info:
        #     for k, v in doc_info.items():
        #         if isinstance(v, PyPDF2.generic.IndirectObject):
        #             self.pdf_metadata[k.strip("/")] = parse_str(v.getObject())
        #         else:
        #             self.pdf_metadata[k.strip("/")] = parse_str(v)

class TextBackend(ReaderBackend):
    def __init__(self, stream):
        self.text = stream.read()
        self.urls_text = urlmarker.get_urls(self.text)
        self.urls = self.urls_annotations | self.urls_text
