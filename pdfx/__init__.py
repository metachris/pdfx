# -*- coding: utf-8 -*-
"""
Extract metadata and links from a local or remote PDF, and
optionally download all referenced PDFs.

Features

* Extract metadata and PDF URLs from a given PDF
* Download all PDFs referenced in the original PDF
* Works with local and online pdfs
* Use as command-line tool or Python package
* Compatible with Python 2 and 3

Usage

PDFx can be used to extract infos from PDF in two ways:

* Command line tool `pdfx`
* Python library `import pdfx`

>>> import pdfx
>>> pdf = pdfx.PDFx("filename-or-url.pdf")
>>> print(pdf.get_metadata())
>>> pdf.analyze_text()
>>> print(pdf.get_urls())
>>> pdf.download_pdfs("target-directory")

https://www.metachris.com/pdfx

Copyright (c) 2015, Chris Hager <chris@linuxuser.at>
License: GPLv3
"""
from __future__ import absolute_import, division, print_function

__title__ = 'pdfx'
__version__ = '1.0.3'
__author__ = 'Chris Hager'
__license__ = 'GPLv3'
__copyright__ = 'Copyright 2015 Chris Hager'

import os
import re
import sys
import json
import shutil
import logging

if sys.version_info < (3, 0):
    # Python 2
    from cStringIO import StringIO as BytesIO
    from urllib2 import Request, urlopen
    parse_str = unicode
else:
    # Python 3
    from io import BytesIO
    from urllib.request import Request, urlopen
    parse_str = str

from .libs import PyPDF2, urlmarker
from .threadeddownload import ThreadedDownloader
from .exceptions import (
    FileNotFoundError, DownloadError, PDFInvalidError, PDFExtractionError)

logger = logging.getLogger(__name__)


class PDFx(object):
    """
    Main class which extracts infos from PDF

    General flow:
    * init -> get_metadata()
    * analyze_text() -> get_urls()

    In detail:
    >>> import pdfx
    >>> pdf = pdfx.PDFx("filename-or-url.pdf")
    >>> print(pdf.get_metadata())
    >>> pdf.analyze_text()
    >>> print(pdf.get_urls())
    >>> pdf.download_pdfs("target-directory")
    """
    # Available after init
    pdf_uri = None  # Original URI
    pdf_is_url = False  # False if file
    pdf_fn = None  # Filename
    pdf_stream = None  # ByteIO Stream
    pdf = None  # PdfFileReader Instance
    pdf_metadata = {}  # PDF Metadata
    summary = {}

    # Available after analyze_text()
    urls = []  # All urls
    urls_pdf = []  # PDF urls

    def __init__(self, pdf_uri):
        """
        Open PDF handle and parse PDF metadata
        - `pdf_uri` can bei either a filename or an url
        """
        logger.debug("Init with uri: %s" % pdf_uri)

        self.pdf_uri = pdf_uri
        self.urls = []
        self.urls_pdf = []

        # Find out whether pdf is an URL or local file
        url = re.findall(urlmarker.URL_REGEX, pdf_uri)
        self.pdf_is_url = len(url)

        # Grab content of referenced PDF
        if self.pdf_is_url:
            logger.debug("Reading url '%s'..." % pdf_uri)
            self.pdf_fn = pdf_uri.split("/")[-1]
            try:
                content = urlopen(Request(pdf_uri)).read()
                self.pdf_stream = BytesIO(content)
            except Exception as e:
                raise DownloadError("Error downloading '%s' (%s)" %
                                    (pdf_uri, str(e)))

        else:
            if not os.path.isfile(pdf_uri):
                raise FileNotFoundError(
                    "Invalid filename and not an url: '%s'" % pdf_uri)
            self.pdf_fn = os.path.basename(pdf_uri)
            self.pdf_stream = open(pdf_uri, "rb")

        # Create PdfFileReader instance
        try:
            self.pdf = PyPDF2.PdfFileReader(self.pdf_stream)
        except Exception as e:
            raise PDFInvalidError("Invalid PDF (%s)" % str(e))

        # Extract metadata
        self.pdf_metadata = {}
        self.pdf_metadata["Pages"] = self.pdf.getNumPages()

        doc_info = self.pdf.getDocumentInfo()
        if doc_info:
            for k, v in doc_info.items():
                if isinstance(v, PyPDF2.generic.IndirectObject):
                    self.pdf_metadata[k.strip("/")] = parse_str(v.getObject())
                else:
                    self.pdf_metadata[k.strip("/")] = parse_str(v)

        # Save metadata to user-supplied directory
        self.summary = {
            "source": "url" if self.pdf_is_url else "file",
            "location": self.pdf_uri,
            "metadata": self.pdf_metadata,
        }

    def get_metadata(self):
        return self.pdf_metadata

    def analyze_text(self):
        logger.debug("Analyzing text...")

        text = ""
        for page in self.pdf.pages:
            text = text + page.extractText()

        # Process PDF
        if len(text.strip()) < 10:
            raise PDFExtractionError(
                "Error: Failed extracting text from PDF file.")

        # Search for URLs
        self.urls = re.findall(urlmarker.URL_REGEX, text)
        self.urls_pdf = [url for url in self.urls
                         if url.lower().endswith(".pdf")]
        self.summary["urls"] = self.urls

    def get_urls(self, pdf_only=False, sort=False):
        urls = self.urls_pdf if pdf_only else self.urls
        return sorted(urls) if sort else urls

    def download_pdfs(self, target_dir):
        logger.debug("Download pdfs to %s" % target_dir)
        assert target_dir, "Need a download directory"
        assert not os.path.isfile(target_dir), "Download directory is a file"

        # Create output directory
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir)
            logger.debug("Created output directory '%s'" % target_dir)

        # Save original PDF to user-supplied directory
        fn = os.path.join(target_dir, self.pdf_fn)
        with open(fn, "wb") as f:
            self.pdf_stream.seek(0)
            shutil.copyfileobj(self.pdf_stream, f)
        logger.debug("- Saved original pdf as '%s'" % fn)

        fn_json = "%s.infos.json" % fn
        with open(fn_json, "w") as f:
            f.write(json.dumps(self.summary, indent=2))
        logger.debug("- Saved metadata to '%s'" % fn_json)

        # Download references
        if self.urls_pdf:
            dir_referenced_pdfs = os.path.join(
                target_dir, "%s-referenced-pdfs" % self.pdf_fn)
            logger.debug("Downloading %s referenced pdfs..." %
                         len(self.urls_pdf))

            # Download urls as a set to avoid duplicates
            tdl = ThreadedDownloader(set(self.urls_pdf), dir_referenced_pdfs)
            tdl.start_downloads()
            tdl.wait_for_downloads()
