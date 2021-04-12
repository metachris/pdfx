# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


HEADER = "\033[95m"
OKBLUE = "\033[94m"
OKGREEN = "\033[92m"
WARNING = "\033[93m"
FAIL = "\033[91m"

# Text Style
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
REVERSE = "\033[7m"

# Nothing (Standard)
ENDC = "\033[0m"


def colorprint(color, s):
    print("%s%s%s" % (color, s, ENDC))
