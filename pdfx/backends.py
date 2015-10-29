# -*- coding: utf-8 -*-
"""
PDF Backend: pdfMiner
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
import re
from io import BytesIO
from .libs import urlmarker

from .libs import PyPDF2

from .libs.pdfminer.pdfdocument import PDFDocument
from .libs.pdfminer.pdfparser import PDFParser
from .libs.pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from .libs.pdfminer.pdfdevice import PDFDevice, TagExtractor
from .libs.pdfminer.pdfpage import PDFPage
from .libs.pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from .libs.pdfminer.cmapdb import CMapDB
from .libs.pdfminer.layout import LAParams
from .libs.pdfminer.image import ImageWriter

if sys.version_info < (3, 0):
    # Python 2
    parse_str = unicode
else:
    # Python 3
    parse_str = str


class ReaderBackend(object):
    """
    Base class of all Readers (eg. for PDF files, text, etc.)

    The job of a Reader is to extract Text and Links.
    """
    metadata = {}
    text = ""

    urls_text = set()  # URLs found in text
    urls_annotations = set()  # URLs found in annotation
    urls = set()  # All URLs combined

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

    def get_urls_annotations(self):
        return self.urls_annotations

    def get_urls_text(self):
        return self.urls_text

    def get_urls(self, pdf_only=False, sort=False):
        urls = self.urls
        if pdf_only:
            urls = set([url for url in self.urls if url.lower().endswith(".pdf")])
        return sorted(urls) if sort else urls



class PyPDF2Backend(ReaderBackend):
    pdf_stream = None
    pdf = None
    pdf_metadata = {}
    num_pages = 0

    def __init__(self, pdf_stream):
        self.pdf_stream = pdf_stream
        self.pdf = PyPDF2.PdfFileReader(self.pdf_stream)
        self.num_pages = self.pdf.getNumPages()

        self.pdf_metadata["Pages"] = self.num_pages
        doc_info = self.pdf.getDocumentInfo()
        if doc_info:
            for k, v in doc_info.items():
                if isinstance(v, PyPDF2.generic.IndirectObject):
                    self.pdf_metadata[k.strip("/")] = parse_str(v.getObject())
                else:
                    self.pdf_metadata[k.strip("/")] = parse_str(v)

    def get_number_of_pages(self):
        return self.num_pages

    def get_metadata(self):
        return self.pdf_metadata

    def get_annotations(self):
        return []

    def get_text(self):
        text = ""
        for page in self.pdf.pages:
            text = text + page.extractText()
        return text

    def get_url_annotations(self):
        return []


class PDFMinerBackend(ReaderBackend):
    rsrcmgr = None
    converter = None
    interpreter = None
    text_io = None

    def __init__(self, pdf_stream, debug=0):
        self.pdf_stream = pdf_stream

        PDFDocument.debug = debug
        PDFParser.debug = debug
        CMapDB.debug = debug
        PDFPageInterpreter.debug = debug

        self.text_io = BytesIO()

        self.rsrcmgr = PDFResourceManager(caching=True)
        self.converter = TextConverter(self.rsrcmgr, self.text_io, codec="utf-8",
                laparams=LAParams(), imagewriter=None)
        self.interpreter = PDFPageInterpreter(self.rsrcmgr, self.converter)

        for page in PDFPage.get_pages(self.pdf_stream, pagenos=set(),
                                      maxpages=0, password='',
                                      caching=True, check_extractable=True):

            # Collect URL annotations
            for annot in page.annots:
                a = annot.resolve()
                if "A" in a and "URI" in a["A"]:
                    self.urls_annotations.add(a["A"]["URI"])

            # Read page contents
            self.interpreter.process_page(page)

        # Get text from stream
        self.text = self.text_io.getvalue()
        self.text_io.close()
        self.converter.close()

        # Extract URLs from text
        self.urls_text = set(re.findall(urlmarker.URL_REGEX, self.text))
        self.urls = self.urls_annotations | self.urls_text
        # print(self.urls)

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
