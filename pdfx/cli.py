#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extract all links from a local or remote PDF, and optionally download all referenced PDFs.
"""
from __future__ import absolute_import, division, print_function

import sys
import logging
import argparse
import json

import pdfx
from pdfx.exceptions import *


def exit_with_error(code, *objs):
    print("ERROR %s:" % code, *objs, file=sys.stderr)
    exit(code)

# Error Status Codes
ERROR_FILE_NOT_FOUND = 1
ERROR_DOWNLOAD = 2
ERROR_PDF_INVALID = 4
ERROR_COULD_NOT_EXTRACT_PDF = 5


def main():
    parser = argparse.ArgumentParser(
        description=
        'Get infos and links from a PDF, and optionally download all referenced PDFs.\nSee http://www.metachris.com/pdfx for more information.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="")
    parser.add_argument("pdf", help="Filename or URL of a PDF file")
    parser.add_argument(
        "-d",
        "--download-pdfs",
        metavar="OUTPUT_DIRECTORY",
        help="Download all referenced PDFs into specified directory")
    parser.add_argument("-j",
                        "--json",
                        action='store_true',
                        help="Output infos as json (instead of plain text)")
    parser.add_argument("-v",
                        "--verbose",
                        action="count",
                        default=0,
                        help="Print all urls (instead of only PDF urls)")
    parser.add_argument("--debug",
                        action='store_true',
                        help="Output debug infos")

    parser.add_argument("--version",
                        action="version",
                        version="%(prog)s (version {version})".format(
                            version=pdfx.__version__))

    args = parser.parse_args()

    # if args.download_pdfs and not args.output_directory:
    #     print("Error: To download referenced pdfs, please specifiy a output directory!")
    #     exit(ERROR_COMMAND_LINE_OPTIONS)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(levelname)s - %(module)s - %(message)s')

    try:
        pdf = pdfx.open_pdf(args.pdf)
    except FileNotFoundError as e:
        exit_with_error(ERROR_FILE_NOT_FOUND, str(e))
    except DownloadError as e:
        exit_with_error(ERROR_DOWNLOAD, str(e))
    except PDFInvalidError as e:
        exit_with_error(ERROR_PDF_INVALID, str(e))

    # Print Metadata
    if not args.json:
        print("Document infos:")
        for k, v in sorted(pdf.get_metadata().items()):
            if v:
                print("- %s = %s" % (k, str(v).strip("/")))

    # Analyze PDF Text
    try:
        pdf.analyze_text()
    except PDFExtractionError as e:
        exit_with_error(ERROR_COULD_NOT_EXTRACT_PDF, str(e))

    if not args.json:
        urls = pdf.get_urls(pdf_only=args.verbose == 0)
        print("%s URLs:" % len(urls))
        for url in urls:
            print("  - %s" % url)

    try:
        if not args.json:
            print("Downloading %s pdfs..." % len(pdf.urls_pdf))
        if args.download_pdfs:
            pdf.download_pdfs(args.download_pdfs)
    except Exception as e:
        exit_with_error(ERROR_DOWNLOAD, str(e))

    if args.json:
        print(json.dumps(pdf.summary, indent=2))


if __name__ == "__main__":
    main()
