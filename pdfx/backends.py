# -*- coding: utf-8 -*-
"""
PDF Backend: pdfMiner
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import logging
from io import BytesIO

# Character Detection Helper
import chardet

# Find URLs in text via regex
from . import extractor
from .libs.xmp import xmp_to_dict

# Setting `psparser.STRICT` is the first thing to do because it is
# referenced in the other pdfparser modules
from pdfminer import settings as pdfminer_settings
pdfminer_settings.STRICT = False
from pdfminer import psparser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdftypes import resolve1
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams


logger = logging.getLogger(__name__)


IS_PY2 = sys.version_info < (3, 0)
if not IS_PY2:
    # Python 3
    unicode = str


def make_compat_str(in_str):
    """
    Tries to guess encoding of [str/bytes] and
    return a standard unicode string
    """
    assert isinstance(in_str, (bytes, str, unicode))
    if not in_str:
        return unicode()

    # Chardet in Py2 works on str + bytes objects
    if IS_PY2 and isinstance(in_str, unicode):
        return in_str

    # Chardet in Py3 works on bytes objects
    if not IS_PY2 and not isinstance(in_str, bytes):
        return in_str

    # Detect the encoding now
    enc = chardet.detect(in_str)

    # Decode the object into a unicode object
    out_str = in_str.decode(enc['encoding'])

    # Cleanup
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
        self.reftype = "url"

        # Detect reftype by filetype
        if uri.lower().endswith(".pdf"):
            self.reftype = "pdf"
            return

        # Detect reftype by extractor
        arxiv = extractor.extract_arxiv(uri)
        if arxiv:
            self.ref = arxiv.pop()
            self.reftype = "arxiv"
            return

        doi = extractor.extract_doi(uri)
        if doi:
            self.ref = doi.pop()
            self.reftype = "doi"
            return

    def __hash__(self):
        return hash(self.ref)

    def __eq__(self, other):
        assert isinstance(other, Reference)
        return self.ref == other.ref

    def __str__(self):
        return "<%s: %s>" % (self.reftype, self.ref)


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

    def metadata_cleanup(self):
        """ Delete all metadata fields without values """
        for k in list(self.metadata.keys()):
            if self.metadata[k] == "":
                del self.metadata[k]

    def get_text(self):
        return self.text

    def get_references(self, reftype=None, sort=False):
        refs = self.references
        if reftype:
            refs = set([ref for ref in refs if ref.reftype == "pdf"])
        return sorted(refs) if sort else refs

    def get_references_as_dict(self, reftype=None, sort=False):
        ret = {}
        refs = self.references
        if reftype:
            refs = set([ref for ref in refs if ref.reftype == "pdf"])
        for r in sorted(refs) if sort else refs:
            if r.reftype in ret:
                ret[r.reftype].append(r.ref)
            else:
                ret[r.reftype] = [r.ref]
        return ret


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
                    self.metadata[k] = make_compat_str(v.name)

        # Secret Metadata
        if 'Metadata' in doc.catalog:
            metadata = resolve1(doc.catalog['Metadata']).get_data()
            # print(metadata)  # The raw XMP metadata
            # print(xmp_to_dict(metadata))
            self.metadata.update(xmp_to_dict(metadata))
            # print("---")

        # Extract Content
        text_io = BytesIO()
        rsrcmgr = PDFResourceManager(caching=True)
        converter = TextConverter(rsrcmgr, text_io, codec="utf-8",
                                  laparams=LAParams(), imagewriter=None)
        interpreter = PDFPageInterpreter(rsrcmgr, converter)

        self.metadata["Pages"] = 0
        for page in PDFPage.get_pages(self.pdf_stream, pagenos=pagenos,
                                      maxpages=maxpages, password=password,
                                      caching=True, check_extractable=False):
            # Read page contents
            interpreter.process_page(page)
            self.metadata["Pages"] += 1

            # Collect URL annotations
            try:
                if page.annots and isinstance(page.annots, list):
                    for annot in page.annots:
                        a = annot.resolve()
                        if "A" in a and "URI" in a["A"]:
                            ref = Reference(a["A"]["URI"].decode("utf-8"))
                            self.references.add(ref)
            except Exception as e:
                logger.warning(str(e))

        # Remove empty metadata entries
        self.metadata_cleanup()

        # Get text from stream
        self.text = text_io.getvalue().decode("utf-8")
        text_io.close()
        converter.close()
        # print(self.text)

        # Extract URL references from text
        for url in extractor.extract_urls(self.text):
            self.references.add(Reference(url))

        for ref in extractor.extract_arxiv(self.text):
            self.references.add(Reference(ref))

        for ref in extractor.extract_doi(self.text):
            self.references.add(Reference(ref))


class TextBackend(ReaderBackend):
    def __init__(self, stream):
        self.text = stream.read()

        # Extract URL references from text
        for url in extractor.extract_urls(self.text):
            self.references.add(Reference(url))

        for ref in extractor.extract_arxiv(self.text):
            self.references.add(Reference(ref))

        for ref in extractor.extract_doi(self.text):
            self.references.add(Reference(ref))
