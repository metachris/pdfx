====
PDFx
====

.. image:: https://badge.fury.io/py/pdfx.svg
   :target: https://pypi.python.org/pypi/pdfx

.. image:: https://travis-ci.org/metachris/pdfx.svg?branch=master
   :target: https://travis-ci.org/metachris/pdfx

.. image:: https://img.shields.io/badge/license-Apache-blue.svg
   :target: https://github.com/metachris/pdfx/blob/master/LICENSE

Introduction
============

Extract references (pdf, url, doi) and metadata from a PDF. Optionally download all referenced PDFs and check for broken links.

**Features**

* Extract references and metadata from a given PDF
* Detects pdf, url, arxiv and doi references
* **Fast, parallel download of all referenced PDFs**
* **Check for broken links** (using the ``-c`` flag)
* Output as text or JSON (using the ``-j`` flag)
* Extract the PDF text (using the ``--text`` flag)
* Use as command-line tool or Python package
* Compatible with Python 2 and 3
* Works with local and online pdfs


Getting Started
===============

Grab a copy of the code with ``easy_install`` or ``pip``, and run it::

    $ sudo easy_install -U pdfx
    ...
    $ pdfx <pdf-file-or-url>

Run ``pdfx -h`` to see the help output::

    $ pdfx -h
    usage: pdfx [-h] [-d OUTPUT_DIRECTORY] [-c] [-j] [-v] [-t] [-o OUTPUT_FILE]
                [--version]
                pdf

    Extract metadata and references from a PDF, and optionally download all
    referenced PDFs. Visit https://www.metachris.com/pdfx for more information.

    positional arguments:
      pdf                   Filename or URL of a PDF file

    optional arguments:
      -h, --help            show this help message and exit
      -d OUTPUT_DIRECTORY, --download-pdfs OUTPUT_DIRECTORY
                            Download all referenced PDFs into specified directory
      -c, --check-links     Check for broken links
      -j, --json            Output infos as JSON (instead of plain text)
      -v, --verbose         Print all references (instead of only PDFs)
      -t, --text            Only extract text (no metadata or references)
      -o OUTPUT_FILE, --output-file OUTPUT_FILE
                            Output to specified file instead of console
      --version             show program's version number and exit


Examples
========

Lets take a look at this paper: https://weakdh.org/imperfect-forward-secrecy.pdf::

    $ pdfx https://weakdh.org/imperfect-forward-secrecy.pdf
    Document infos:
    - CreationDate = D:20150821110623-04'00'
    - Creator = LaTeX with hyperref package
    - ModDate = D:20150821110805-04'00'
    - PTEX.Fullbanner = This is pdfTeX, Version 3.1415926-2.5-1.40.14 (TeX Live 2013/Debian) kpathsea version 6.1.1
    - Pages = 13
    - Producer = pdfTeX-1.40.14
    - Title = Imperfect Forward Secrecy: How Diffie-Hellman Fails in Practice
    - Trapped = False
    - dc = {'title': {'x-default': 'Imperfect Forward Secrecy: How Diffie-Hellman Fails in Practice'}, 'creator': [None], 'description': {'x-default': None}, 'format': 'application/pdf'}
    - pdf = {'Keywords': None, 'Producer': 'pdfTeX-1.40.14', 'Trapped': 'False'}
    - pdfx = {'PTEX.Fullbanner': 'This is pdfTeX, Version 3.1415926-2.5-1.40.14 (TeX Live 2013/Debian) kpathsea version 6.1.1'}
    - xap = {'CreateDate': '2015-08-21T11:06:23-04:00', 'ModifyDate': '2015-08-21T11:08:05-04:00', 'CreatorTool': 'LaTeX with hyperref package', 'MetadataDate': '2015-08-21T11:08:05-04:00'}
    - xapmm = {'InstanceID': 'uuid:4e570f88-cd0f-4488-85ad-03f4435a4048', 'DocumentID': 'uuid:98988d37-b43d-4c1a-965b-988dfb2944b6'}

    References: 36
    - URL: 18
    - PDF: 18

    PDF References:
    - http://www.spiegel.de/media/media-35533.pdf
    - http://www.spiegel.de/media/media-35513.pdf
    - http://www.spiegel.de/media/media-35509.pdf
    - http://www.spiegel.de/media/media-35529.pdf
    - http://www.spiegel.de/media/media-35527.pdf
    - http://cr.yp.to/factorization/smoothparts-20040510.pdf
    - http://www.spiegel.de/media/media-35517.pdf
    - http://www.spiegel.de/media/media-35526.pdf
    - http://www.spiegel.de/media/media-35519.pdf
    - http://www.spiegel.de/media/media-35522.pdf
    - http://cryptome.org/2013/08/spy-budget-fy13.pdf
    - http://www.spiegel.de/media/media-35515.pdf
    - http://www.spiegel.de/media/media-35514.pdf
    - http://www.hyperelliptic.org/tanja/SHARCS/talks06/thorsten.pdf
    - http://www.spiegel.de/media/media-35528.pdf
    - http://www.spiegel.de/media/media-35671.pdf
    - http://www.spiegel.de/media/media-35520.pdf
    - http://www.spiegel.de/media/media-35551.pdf

You can use the ``-v`` flag to output all references instead of just the PDFs.

**Download all referenced pdfs** with ``-d`` (for ``download-pdfs``) to the specified directory (eg. to ``/tmp/``)::

    $ pdfx https://weakdh.org/imperfect-forward-secrecy.pdf -d /tmp/
    ...

To **extract text**, you can use the ``-t`` flag::

    # Extract text to console
    $ pdfx https://weakdh.org/imperfect-forward-secrecy.pdf -t

    # Extract text to file
    $ pdfx https://weakdh.org/imperfect-forward-secrecy.pdf -t -o pdf-text.txt

To **check for broken links** use the ``-c`` flag::

    $ pdfx https://weakdh.org/imperfect-forward-secrecy.pdf -c

Example video of checking for broken links: http://recordit.co/PsigiMaooH


Usage as Python library
=======================

::

    >>> import pdfx
    >>> pdf = pdfx.PDFx("filename-or-url.pdf")
    >>> metadata = pdf.get_metadata()
    >>> references_list = pdf.get_references()
    >>> references_dict = pdf.get_references_as_dict()
    >>> pdf.download_pdfs("target-directory")


Various
=======

* Author: Chris Hager <chris@linuxuser.at>
* Homepage: https://www.metachris.com/pdfx
* License: Apache

Feedback, ideas and pull requests are welcome!
