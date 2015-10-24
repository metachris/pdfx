#
# This file is used to be able to import ../pdfx as pdfx
#
import sys
import os

# append module root directory to sys.path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
