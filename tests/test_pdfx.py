from __future__ import absolute_import, division, print_function

import os
import pdfx
import pytest

curdir = os.path.dirname(os.path.realpath(__file__))


def test_all():
    with pytest.raises(pdfx.exceptions.FileNotFoundError):
        pdfx.PDFx("asd")

    with pytest.raises(pdfx.exceptions.DownloadError):
        pdfx.PDFx("http://invalid.com/404.pdf")

    with pytest.raises(pdfx.exceptions.PDFInvalidError):
        pdfx.PDFx(os.path.join(curdir, "pdfs/invalid.pdf"))

    pdf = pdfx.PDFx(os.path.join(curdir, "pdfs/valid.pdf"))
    urls = pdf.get_references(reftype="pdf")
    assert len(urls) == 18
    # pdf.download_pdfs("/tmp/")
