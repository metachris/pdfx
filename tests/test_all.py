from __future__ import absolute_import, division, print_function

import os
import env
import pdfx
import pytest

curdir = os.path.dirname(os.path.realpath(__file__))

def test_all():
    with pytest.raises(pdfx.exceptions.FileNotFoundError):
        pdfx.open_pdf("asd")

    with pytest.raises(pdfx.exceptions.DownloadError):
        pdfx.open_pdf("http://invalid.com/404.pdf")

    with pytest.raises(pdfx.exceptions.PDFInvalidError):
        pdf = pdfx.open_pdf(os.path.join(curdir, "pdfs/invalid.pdf"))

    # with pytest.raises(pdfx.exceptions.PDFExtractionError):
    #     pdf = pdfx.open_pdf(os.path.join(curdir, "pdfs/invalid.pdf"))
    #     pdf.analyze_text()

    assert True == True
