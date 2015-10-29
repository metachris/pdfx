from __future__ import absolute_import, division, print_function

import os
from pdfx import cli
# import pytest

curdir = os.path.dirname(os.path.realpath(__file__))


def test_cli():
    parser = cli.create_parser()
    parsed = parser.parse_args(['-j', 'pdfs/valid.pdf'])
    assert parsed.json
    assert parsed.pdf == "pdfs/valid.pdf"
