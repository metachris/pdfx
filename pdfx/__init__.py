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
>>> metadata = pdf.get_metadata()
>>> references_list = pdf.get_references()
>>> references_dict = pdf.get_references_as_dict()
>>> pdf.download_pdfs("target-directory")

https://www.metachris.com/pdfx

Copyright (c) 2015, Chris Hager <chris@linuxuser.at>
License: GPLv3
"""
from __future__ import absolute_import, division, print_function, unicode_literals

__title__ = "pdfx"
__version__ = "1.4.1"
__author__ = "Chris Hager"
__license__ = "Apache 2.0"
__copyright__ = "Copyright 2015 Chris Hager"

import os
import sys
import json
import shutil
import logging


from .extractor import extract_urls
from .backends import PDFMinerBackend, TextBackend
from .downloader import download_urls
from .exceptions import FileNotFoundError, DownloadError, PDFInvalidError
from pdfminer.pdfparser import PDFSyntaxError


IS_PY2 = sys.version_info < (3, 0)

if IS_PY2:
    # Python 2
    from cStringIO import StringIO as BytesIO
    from urllib2 import Request, urlopen
else:
    # Python 3
    from io import BytesIO
    from urllib.request import Request, urlopen

    unicode = str

logger = logging.getLogger(__name__)


class PDFx(object):
    """
    Main class which extracts infos from PDF

    General flow:
    * init -> get_metadata()

    In detail:
    >>> import pdfx
    >>> pdf = pdfx.PDFx("filename-or-url.pdf")
    >>> print(pdf.get_metadata())
    >>> print(pdf.get_tet())
    >>> print(pdf.get_references())
    >>> pdf.download_pdfs("target-directory")
    """

    # Available after init
    uri = None  # Original URI
    fn = None  # Filename part of URI
    is_url = False  # False if file
    is_pdf = True

    stream = None  # ByteIO Stream
    reader = None  # ReaderBackend
    summary = {}

    def __init__(self, uri):
        """
        Open PDF handle and parse PDF metadata
        - `uri` can bei either a filename or an url
        """
        logger.debug("Init with uri: %s" % uri)

        self.uri = uri

        # Find out whether pdf is an URL or local file
        url = extract_urls(uri)
        self.is_url = len(url)

        # Grab content of reference
        if self.is_url:
            logger.debug("Reading url '%s'..." % uri)
            self.fn = uri.split("/")[-1]
            try:
                content = urlopen(Request(uri)).read()
                self.stream = BytesIO(content)
            except Exception as e:
                raise DownloadError("Error downloading '%s' (%s)" % (uri, unicode(e)))

        else:
            if not os.path.isfile(uri):
                raise FileNotFoundError("Invalid filename and not an url: '%s'" % uri)
            self.fn = os.path.basename(uri)
            self.stream = open(uri, "rb")

        # Create ReaderBackend instance
        try:
            self.reader = PDFMinerBackend(self.stream)
        except PDFSyntaxError as e:
            raise PDFInvalidError("Invalid PDF (%s)" % unicode(e))

            # Could try to create a TextReader
            logger.info(unicode(e))
            logger.info("Trying to create a TextReader backend...")
            self.stream.seek(0)
            self.reader = TextBackend(self.stream)
            self.is_pdf = False
        except Exception as e:
            raise
            raise PDFInvalidError("Invalid PDF (%s)" % unicode(e))

        # Save metadata to user-supplied directory
        self.summary = {
            "source": {
                "type": "url" if self.is_url else "file",
                "location": self.uri,
                "filename": self.fn,
            },
            "metadata": self.reader.get_metadata(),
        }

        # Search for URLs
        self.summary["references"] = self.reader.get_references_as_dict()
        # print(self.summary)

    def get_text(self):
        return self.reader.get_text()

    def get_metadata(self):
        return self.reader.get_metadata()

    def get_references(self, reftype=None, sort=False):
        """ reftype can be `None` for all, `pdf`, etc. """
        return self.reader.get_references(reftype=reftype, sort=sort)

    def get_references_as_dict(self, reftype=None, sort=False):
        """ reftype can be `None` for all, `pdf`, etc. """
        return self.reader.get_references_as_dict(reftype=reftype, sort=sort)

    def get_references_count(self, reftype=None):
        """ reftype can be `None` for all, `pdf`, etc. """
        r = self.reader.get_references(reftype=reftype)
        return len(r)

    def download_pdfs(self, target_dir):
        logger.debug("Download pdfs to %s" % target_dir)
        assert target_dir, "Need a download directory"
        assert not os.path.isfile(target_dir), "Download directory is a file"

        # Create output directory
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir)
            logger.debug("Created output directory '%s'" % target_dir)

        # Save original PDF to user-supplied directory
        fn = os.path.join(target_dir, self.fn)
        with open(fn, "wb") as f:
            self.stream.seek(0)
            shutil.copyfileobj(self.stream, f)
        logger.debug("- Saved original pdf as '%s'" % fn)

        fn_json = "%s.infos.json" % fn
        with open(fn_json, "w") as f:
            f.write(json.dumps(self.summary, indent=2))
        logger.debug("- Saved metadata to '%s'" % fn_json)

        # Download references
        urls = [ref.ref for ref in self.get_references("pdf")]
        if not urls:
            return

        dir_referenced_pdfs = os.path.join(target_dir, "%s-referenced-pdfs" % self.fn)
        logger.debug("Downloading %s referenced pdfs..." % len(urls))

        # Download urls as a set to avoid duplicates
        download_urls(urls, dir_referenced_pdfs)
