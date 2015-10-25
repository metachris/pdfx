# -*- coding: utf-8 -*-
"""
Extract all links from a local or remote PDF, and optionally download all
referenced PDFs.

Features

* Get general information about a PDF (metadata, number of pages, ...)
* See all PDF urls in the original PDF (using the `-v` flag)
* See all urls in the original PDF (using the `-vv` flag)
* **Download all PDFs referenced in the original PDF** (using the `-d` flag)

Usage

PDFx can be used to extract infos from PDF in two ways:

* Command line tool `pdfx`
* Python library `import pdfx`

https://github.com/metachris/pdfx

Copyright (c) 2015, Chris Hager <chris@linuxuser.at>
License: GPLv3
"""
from __future__ import absolute_import, division, print_function

__title__ = 'pdfx'
__version__ = '1.0.0'
__author__ = 'Chris Hager'
__license__ = 'GPLv3'
__copyright__ = 'Copyright 2015 Chris Hager'

from .pdfx import PDFx
