Extract metadata and all links from a local or remote PDF, and optionally download all referenced PDFs.

**Features**

* Extract metadata and PDF URLs from a given PDF
* **Download all PDFs referenced in the original PDF**
* Works with local and online pdfs
* Use as command-line tool or Python package
* Compatible with Python 2 and 3

Getting Started
---------------

Grab a copy of the code and run it::

    $ pip install pdfx
    ...
    $ pdfx <pdf-file-or-url>

Run ``pdfx -h`` to see the help output::

    $ pdfx -h
    usage: pdfx [-h] [-d OUTPUT_DIRECTORY] [-j] [-v] [--debug] [--version] pdf

    Get infos and links from a PDF, and optionallydownload all referenced PDFs.
    See http://www.metachris.com/pdfx for more information.

    positional arguments:
      pdf                   Filename or URL of a PDF file

    optional arguments:
      -h, --help            show this help message and exit
      -d OUTPUT_DIRECTORY, --download-pdfs OUTPUT_DIRECTORY
                            Download all referenced PDFs into specified directory
      -j, --json            Output infos as json (instead of plain text)
      -v, --verbose         Print all urls (instead of only PDF urls)
      --debug               Output debug infos
      --version             show program's version number and exit


Examples
--------

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

    17 PDF URLs:
    - http://cr.yp.to/factorization/smoothparts-20040510.pdf
    - http://www.spiegel.de/media/media-35671.pdf
    - http://www.spiegel.de/media/media-35529.pdf
    - http://cryptome.org/2013/08/spy-budget-fy13.pdf
    - http://www.spiegel.de/media/media-35514.pdf
    - http://www.spiegel.de/media/media-35509.pdf
    - http://www.spiegel.de/media/media-35515.pdf
    - http://www.spiegel.de/media/media-35533.pdf
    - http://www.spiegel.de/media/media-35519.pdf
    - http://www.spiegel.de/media/media-35522.pdf
    - http://www.spiegel.de/media/media-35513.pdf
    - http://www.spiegel.de/media/media-35528.pdf
    - http://www.spiegel.de/media/media-35526.pdf
    - http://www.spiegel.de/media/media-35517.pdf
    - http://www.spiegel.de/media/media-35527.pdf
    - http://www.spiegel.de/media/media-35520.pdf
    - http://www.spiegel.de/media/media-35551.pdf


Download all referenced pdfs with **``-d``** (for ``download-pdfs``) to the specified directory (eg. ``./``)::

    $ pdfx https://weakdh.org/imperfect-forward-secrecy.pdf -d ./
    Document infos:
    - CreationDate = D:20150821110623-04'00'
    - Creator = LaTeX with hyperref package
    - ModDate = D:20150821110805-04'00'
    - PTEX.Fullbanner = This is pdfTeX, Version 3.1415926-2.5-1.40.14 (TeX Live 2013/Debian) kpathsea version 6.1.1
    - Pages = 13
    - Producer = pdfTeX-1.40.14
    - Title = Imperfect Forward Secrecy: How Diffie-Hellman Fails in Practice
    - Trapped = False

    17 PDF URLs:
    - http://cr.yp.to/factorization/smoothparts-20040510.pdf
    - http://www.spiegel.de/media/media-35671.pdf
    - http://www.spiegel.de/media/media-35529.pdf
    - http://cryptome.org/2013/08/spy-budget-fy13.pdf
    - http://www.spiegel.de/media/media-35514.pdf
    - http://www.spiegel.de/media/media-35509.pdf
    - http://www.spiegel.de/media/media-35515.pdf
    - http://www.spiegel.de/media/media-35533.pdf
    - http://www.spiegel.de/media/media-35519.pdf
    - http://www.spiegel.de/media/media-35522.pdf
    - http://www.spiegel.de/media/media-35513.pdf
    - http://www.spiegel.de/media/media-35528.pdf
    - http://www.spiegel.de/media/media-35526.pdf
    - http://www.spiegel.de/media/media-35517.pdf
    - http://www.spiegel.de/media/media-35527.pdf
    - http://www.spiegel.de/media/media-35520.pdf
    - http://www.spiegel.de/media/media-35551.pdf

    Downloading 17 pdfs to './'...
    All done!

Usage as Python library::

    >>> import pdfx
    >>> pdf = pdfx.PDFx("filename-or-url.pdf")
    >>> print(pdf.get_metadata())
    >>> pdf.analyze_text()
    >>> print(pdf.get_urls())
    >>> pdf.download_pdfs("target-directory")

Feedback, ideas and pull requests are welcome!


Various
-------

Author: Chris Hager <chris@linuxuser.at>

Homepage: http://www.metachris.com/pdfx

License: GPLv3
