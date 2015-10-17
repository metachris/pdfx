Extract all links from a local or remote PDF, and optionally download all referenced PDFs.

Features

* Get general information about a PDF (metadata, number of pages, ...)
* See all PDF urls in the original PDF (using the `-v` flag)
* See all urls in the original PDF (using the `-vv` flag)
* **Download all PDFs referenced in the original PDF** (using the `-d` and `-o` flags)


Getting Started
---------------

Grab a copy of the code and run it:

    git clone https://github.com/metachris/pdfx.git
    cd pdfx
    ./pdfx.py <pdf_filename_or_url>

Run `./pdfx.py -h` to see the help output:

    $ ./pdfx.py -h
    usage: pdfx.py [-h] [-d OUTPUT_DIRECTORY] [-v] pdf

    Get infos and links from a PDF, and optionally download all referenced PDFs.

    positional arguments:
      pdf                   Filename or URL of a PDF

    optional arguments:
      -h, --help            show this help message and exit
      -d OUTPUT_DIRECTORY, --download-pdfs OUTPUT_DIRECTORY
                            Download all referenced PDFs into specified directory
      -v, --verbose         Print all urls (instead of only PDF urls)

Examples
--------

Lets take a look at this paper: [https://weakdh.org/imperfect-forward-secrecy.pdf](https://weakdh.org/imperfect-forward-secrecy.pdf)

    $ ./pdfx.py https://weakdh.org/imperfect-forward-secrecy.pdf
    Reading url 'https://weakdh.org/imperfect-forward-secrecy.pdf'...
    Document infos:
    - CreationDate = D:20150821110623-04'00'
    - Creator = LaTeX with hyperref package
    - ModDate = D:20150821110805-04'00'
    - PTEX.Fullbanner = This is pdfTeX, Version 3.1415926-2.5-1.40.14 (TeX Live 2013/Debian) kpathsea version 6.1.1
    - Pages = 13
    - Producer = pdfTeX-1.40.14
    - Title = Imperfect Forward Secrecy: How Diffie-Hellman Fails in Practice
    - Trapped = False

    Analyzing text...
    - Words (approx.): 1796
    - URLs: 49
    - URLs to PDFs: 17
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

Download all referenced pdfs with **`-d`** (for download-pdfs) to the current directory (`./`):

    $ ./pdfx.py https://weakdh.org/imperfect-forward-secrecy.pdf -d ./
    Reading url 'https://weakdh.org/imperfect-forward-secrecy.pdf'...
    Saved pdf as './imperfect-forward-secrecy.pdf'
    Document infos:
    - CreationDate = D:20150821110623-04'00'
    - Creator = LaTeX with hyperref package
    - ModDate = D:20150821110805-04'00'
    - PTEX.Fullbanner = This is pdfTeX, Version 3.1415926-2.5-1.40.14 (TeX Live 2013/Debian) kpathsea version 6.1.1
    - Pages = 13
    - Producer = pdfTeX-1.40.14
    - Title = Imperfect Forward Secrecy: How Diffie-Hellman Fails in Practice
    - Trapped = False

    Analyzing text...
    - Words (approx.): 1796
    - URLs: 49
    - URLs to PDFs: 17
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

    JSON summary saved as './imperfect-forward-secrecy.pdf.infos.json'

    Downloading 17 referenced pdfs...
    Created directory './imperfect-forward-secrecy.pdf-referenced-pdfs'
    Downloaded 'http://cr.yp.to/factorization/smoothparts-20040510.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/smoothparts-20040510.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35514.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35514.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35517.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35517.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35522.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35522.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35519.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35519.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35509.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35509.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35528.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35528.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35513.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35513.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35520.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35520.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35533.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35533.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35551.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35551.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35527.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35527.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35526.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35526.pdf'...
    Downloaded 'http://cryptome.org/2013/08/spy-budget-fy13.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/spy-budget-fy13.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35515.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35515.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35529.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35529.pdf'...
    Downloaded 'http://www.spiegel.de/media/media-35671.pdf' to './imperfect-forward-secrecy.pdf-referenced-pdfs/media-35671.pdf'...

Feedback, ideas and pull requests are welcome!


Various
-------

Author: Chris Hager <chris@metachris.org>

License: GPLv3

TODO

* Quiet mode -> use as library
* Output in JSON only
* Reduce PyPDF2 lib to only used parts
