#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extract all links from a local or remote PDF, and optionally download all referenced PDFs.

Features

* Get general information about a PDF (metadata, number of pages, ...)
* See all PDF urls in the original PDF (using the `-v` flag)
* See all urls in the original PDF (using the `-vv` flag)
* **Download all PDFs referenced in the original PDF** (using the `-d` and `-o` flags)

https://github.com/metachris/pdf-link-extractor

Copyright (c) 2015, Chris Hager <chris@linuxuser.at>
License: GPLv3
"""
from __future__ import print_function
import os
import sys
import re
import json
import shutil
import argparse

from threading import Thread
from time import sleep
from urllib2 import Request, urlopen, HTTPError
from StringIO import StringIO
from pprint import pprint

from libs import PyPDF2, urlmarker

def error(*objs):
    print("ERROR:", *objs, file=sys.stderr)

def exit_with_error(code, *objs):
    print("ERROR %s:" % code, *objs, file=sys.stderr)
    exit(code)

# Error Status Codes
ERROR_COMMAND_LINE_OPTIONS = 1
ERROR_DOWNLOAD = 2
ERROR_FILE_NOT_FOUND = 3
ERROR_PDF_INVALID = 4
ERROR_COULD_NOT_EXTRACT_PDF = 5


class ThreadedDownloader(object):
    """
    Class which can download many files simultaneously to a specific
    output directory. Usage:

    >>> urls = ["http://test.com/a.pdf", "http://test.com/b.pdf"]
    >>> tdl = ThreadedDownloader(urls, "download_dir")
    >>> tdl.start_downloads()     # Downloads are started as threads in the background
    >>> tdl.wait_for_downloads()  # Waits until all download threads are finished (blocking)
    """
    urls = []
    output_directory = None
    threads = []

    def __init__(self, urls, output_directory):
        assert type(urls) in [list, tuple], "ThreadedDownloader urls need to be a list"
        assert len(urls), "ThreadedDownloader needs urls"
        assert output_directory, "ThreadedDownloader needs an output_directory"
        self.urls = urls
        self.output_directory = output_directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            print("Created directory '%s'" % output_directory)

    def _download_threaded(self, url):
        try:
            fn = url.split("/")[-1]
            fn_download = os.path.join(self.output_directory, fn)
            with open(fn_download, "wb") as f:
                f.write(urlopen(Request(url)).read())
        except Exception, e:
            print("Error downloading '%s' (%s)" % (url, str(e)))
            return
        print("Downloaded '%s' to '%s'..." % (url, fn_download))

    def start_downloads(self):
        for url in self.urls:
            thread = Thread(target=self._download_threaded, args=(url,))
            thread.start()
            self.threads.append(thread)

    def wait_for_downloads(self):
        for thread in self.threads:
            thread.join()


class PdfInfo(object):
    """
    Main class which extracts infos from PDF
    """
    # Available after init
    pdf_uri = None
    pdf_fn = None
    pdf_is_url = False
    pdf_handle = None
    output_directory = None
    verbosity = 0

    # Available after `get_infos`
    pdf_summary = None
    pdf_summary_json = None

    def __init__(self, pdf_uri, output_directory=None, verbosity=0):
        """
        - pdf_uri can bei either a filename or an url
        """
        self.pdf_uri = pdf_uri
        self.output_directory = output_directory
        self.verbosity = verbosity

        if output_directory and not os.path.exists(output_directory):
            os.makedirs(output_directory)
            print("Created output directory '%s'" % output_directory)

        url = re.findall(urlmarker.URL_REGEX, pdf_uri)
        self.pdf_is_url = len(url)
        if self.pdf_is_url:
            print("Reading url '%s'..." % pdf_uri)
            try:
                remoteFile = urlopen(Request(pdf_uri)).read()
            except Exception, e:
                exit_with_error(ERROR_DOWNLOAD, "Error downloading '%s' (%s)" % (pdf_uri, str(e)))
            self.pdf_handle = StringIO(remoteFile)

            if output_directory:
                self.pdf_fn = pdf_uri.split("/")[-1]
                fn_download = os.path.join(output_directory, self.pdf_fn)
                with open(fn_download, "wb") as f:
                    f.write(remoteFile)
                print("Saved pdf as '%s'" % fn_download)

        else:
            if not os.path.isfile(pdf_uri):
                exit_with_error(ERROR_FILE_NOT_FOUND, "Invalid filename and not an url: '%s'" % pdf_uri)
            self.pdf_handle = open(pdf_uri, "rb")

            if output_directory:
                self.pdf_fn = os.path.basename(pdf_uri)
                fn_download = os.path.join(output_directory, self.pdf_fn)
                shutil.copyfile(pdf_uri, fn_download)
                print("Saved pdf as '%s'" % fn_download)

        # Start getting infos from PDF
        try:
            pdf = PyPDF2.PdfFileReader(self.pdf_handle)
        except Exception, e:
            exit_with_error(ERROR_PDF_INVALID, "Invalid PDF (%s)" % str(e))

        print("Document infos:")
        infos = {}
        infos["Pages"] = pdf.getNumPages()

        for k,v in pdf.getDocumentInfo().iteritems():
            if isinstance(v, PyPDF2.generic.IndirectObject):
                infos[k] = str(v.getObject())
            else:
                infos[k] = str(v)

        for k,v in sorted(infos.iteritems()):
            if v:
                print("-", k.strip("/"), "=", str(v).strip("/"))

        print()
        print("Analyzing text...")
        text = ""
        for page in pdf.pages:
            text = text + page.extractText()
            # print text

        if len(text.strip()) < 10:
            exit_with_error(ERROR_COULD_NOT_EXTRACT_PDF, "Error: Failed extracting text from PDF file.")

        self.urls = re.findall(urlmarker.URL_REGEX, text)
        self.urls_pdf = [url for url in self.urls if url.endswith(".pdf")]

        print("- URLs: %s" % len(self.urls))
        print("- URLs to PDFs: %s" % len(self.urls_pdf))

        if verbosity > 1:
            print("- URLs:")
            for url in self.urls:
                print("  - %s" % url)

        elif verbosity > 0:
            print("- PDF URLs:")
            for url in self.urls_pdf:
                print("  - %s" % url)

        out = {
            "source": "url" if self.pdf_is_url else "file",
            "location": self.pdf_uri,
            "document_infos": infos,
            "urls": self.urls,
        }

        self.pdf_summary = out
        self.pdf_summary_json = json.dumps(out)

        if output_directory:
            fn_json = "%s.infos.json" % fn_download
            with open(fn_json, "w") as f:
                f.write(self.pdf_summary_json)
            print("\nJSON summary saved as '%s'\n" % fn_json)

    def download_references(self):
        assert self.pdf_summary, "Need to grab pdf infos before downloading!"
        assert self.output_directory, "Need an output directory"

        if self.urls_pdf:
            dir_target = os.path.join(self.output_directory, "%s-referenced-pdfs" % self.pdf_fn)
            print("Downloading %s referenced pdfs..." % len(self.urls_pdf))
            tdl = ThreadedDownloader(self.urls_pdf, dir_target)
            tdl.start_downloads()
            tdl.wait_for_downloads()


def main():
    parser = argparse.ArgumentParser(description='Get infos and links from PDFs.')
    parser.add_argument("pdf", help="Filename or URL of a PDF")
    parser.add_argument("-d", "--download-pdfs",action='store_true', help="Download all referenced PDFs")
    parser.add_argument("-o", "--output-directory", help="If specified, PDF and infos will be saved there. Required to download referenced pdfs.")
    parser.add_argument('-v', '--verbose', action='count', default=0, help="'-v' will print pdf urls, '-vv' will print all urls")
    # parser.add_argument("-j", "--json",action='store_true', help="Output infos as json")
    args = parser.parse_args()

    if args.download_pdfs and not args.output_directory:
        print("Error: To download referenced pdfs, please specifiy a output directory!")
        exit(ERROR_COMMAND_LINE_OPTIONS)

    pdfInfo = PdfInfo(args.pdf, args.output_directory, verbosity=args.verbose)
    if args.download_pdfs:
        pdfInfo.download_references()

    # if args.json:
    #     print()
    #     print("JSON Summary:")
    #     print(pdfInfo.pdf_summary_json)

if __name__ == "__main__":
    main();
