# -*- coding: utf-8 -*-


class FileNotFoundError(Exception):
    """
    Raised if PDF URI could not be opened
    """


class DownloadError(Exception):
    """
    Raised if PDF URI could not be opened
    """


class PDFInvalidError(Exception):
    """
    Raised if PDF content could not be decoded
    """


class PDFExtractionError(Exception):
    """
    Raised if PDF content be decoded but content could not be read
    """
