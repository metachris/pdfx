# -*- coding: utf-8 -*-
"""
PDF Backend: pdfMiner
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import logging
from io import BytesIO
from re import compile

# Character Detection Helper
import chardet

# Find URLs in text via regex
from . import extractor
from .libs.xmp import xmp_to_dict

# Setting `psparser.STRICT` is the first thing to do because it is
# referenced in the other pdfparser modules
from pdfminer import settings as pdfminer_settings

pdfminer_settings.STRICT = False
from pdfminer import psparser  # noqa: E402
from pdfminer.pdfdocument import PDFDocument  # noqa: E402
from pdfminer.pdfparser import PDFParser  # noqa: E402
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter  # noqa: E402
from pdfminer.pdfpage import PDFPage  # noqa: E402
from pdfminer.pdftypes import resolve1, PDFObjRef  # noqa: E402
from pdfminer.converter import TextConverter  # noqa: E402
from pdfminer.layout import LAParams  # noqa: E402


logger = logging.getLogger(__name__)


IS_PY2 = sys.version_info < (3, 0)
if not IS_PY2:
    # Python 3
    unicode = str


def make_compat_str(in_str):
    """
    Tries to guess encoding of [str/bytes] and
    return a standard unicode string
    """
    assert isinstance(in_str, (bytes, str, unicode))
    if not in_str:
        return unicode()

    # Chardet in Py2 works on str + bytes objects
    if IS_PY2 and isinstance(in_str, unicode):
        return in_str

    # Chardet in Py3 works on bytes objects
    if not IS_PY2 and not isinstance(in_str, bytes):
        return in_str

    # Detect the encoding now
    enc = chardet.detect(in_str)

    # Decode the object into a unicode object
    out_str = in_str.decode(enc["encoding"])

    # Cleanup
    if enc["encoding"] == "UTF-16BE":
        # Remove byte order marks (BOM)
        if out_str.startswith("\ufeff"):
            out_str = out_str[1:]
    return out_str


class Reference(object):
    """ Generic Reference """

    ref = ""
    reftype = "url"
    page = 0

    def __init__(self, uri, page=0):
        self.ref = uri
        self.reftype = "url"
        self.page = page

        self.pdf_regex = compile(r"\.pdf(:?\?.*)?$")

        # Detect reftype by filetype
        if self.pdf_regex.search(uri.lower()):
            self.reftype = "pdf"
            return

        # Detect reftype by extractor
        arxiv = extractor.extract_arxiv(uri)
        if arxiv:
            self.ref = arxiv.pop()
            self.reftype = "arxiv"
            return

        doi = extractor.extract_doi(uri)
        if doi:
            self.ref = doi.pop()
            self.reftype = "doi"
            return

    def __hash__(self):
        return hash(self.ref)

    def __eq__(self, other):
        assert isinstance(other, Reference)
        return self.ref == other.ref

    def __str__(self):
        return "<%s: %s>" % (self.reftype, self.ref)


class ReaderBackend(object):
    """
    Base class of all Readers (eg. for PDF files, text, etc.)

    The job of a Reader is to extract Text and Links.
    """

    text = ""
    metadata = {}
    references = set()

    def __init__(self):
        self.text = ""
        self.metadata = {}
        self.references = set()

    def get_metadata(self):
        return self.metadata

    def metadata_key_cleanup(self, d, k):
        """ Recursively clean metadata dictionaries """
        if isinstance(d[k], (str, unicode)):
            d[k] = d[k].strip()
            if not d[k]:
                del d[k]
        elif isinstance(d[k], (list, tuple)):
            new_list = []
            for item in d[k]:
                if isinstance(item, (str, unicode)):
                    if item.strip():
                        new_list.append(item.strip())
                elif item:
                    new_list.append(item)
            d[k] = new_list
            if len(d[k]) == 0:
                del d[k]
        elif isinstance(d[k], dict):
            for k2 in list(d[k].keys()):
                self.metadata_key_cleanup(d[k], k2)

    def metadata_cleanup(self):
        """ Clean metadata (delete all metadata fields without values) """
        for k in list(self.metadata.keys()):
            self.metadata_key_cleanup(self.metadata, k)

    def get_text(self):
        return self.text

    def get_references(self, reftype=None, sort=False):
        refs = self.references
        if reftype:
            refs = set([ref for ref in refs if ref.reftype == "pdf"])
        return sorted(refs) if sort else refs

    def get_references_as_dict(self, reftype=None, sort=False):
        ret = {}
        refs = self.references
        if reftype:
            refs = set([ref for ref in refs if ref.reftype == "pdf"])
        for r in sorted(refs) if sort else refs:
            if r.reftype in ret:
                ret[r.reftype].append(r.ref)
            else:
                ret[r.reftype] = [r.ref]
        return ret


class PDFMinerBackend(ReaderBackend):
    def __init__(self, pdf_stream, password="", pagenos=[], maxpages=0):  # noqa: C901
        ReaderBackend.__init__(self)
        self.pdf_stream = pdf_stream

        # Extract Metadata
        parser = PDFParser(pdf_stream)
        doc = PDFDocument(parser, password=password, caching=True)
        if doc.info:
            for k in doc.info[0]:
                v = doc.info[0][k]
                # print(repr(v), type(v))
                if isinstance(v, (bytes, str, unicode)):
                    self.metadata[k] = make_compat_str(v)
                elif isinstance(v, (psparser.PSLiteral, psparser.PSKeyword)):
                    self.metadata[k] = make_compat_str(v.name)

        # Secret Metadata
        if "Metadata" in doc.catalog:
            metadata = resolve1(doc.catalog["Metadata"]).get_data()
            # print(metadata)  # The raw XMP metadata
            # print(xmp_to_dict(metadata))
            self.metadata.update(xmp_to_dict(metadata))
            # print("---")

        # Extract Content
        text_io = BytesIO()
        rsrcmgr = PDFResourceManager(caching=True)
        converter = TextConverter(
            rsrcmgr, text_io, codec="utf-8", laparams=LAParams(), imagewriter=None
        )
        interpreter = PDFPageInterpreter(rsrcmgr, converter)

        self.metadata["Pages"] = 0
        self.curpage = 0
        for page in PDFPage.get_pages(
            self.pdf_stream,
            pagenos=pagenos,
            maxpages=maxpages,
            password=password,
            caching=True,
            check_extractable=False,
        ):
            # Read page contents
            interpreter.process_page(page)
            self.metadata["Pages"] += 1
            self.curpage += 1

            # Collect URL annotations
            # try:
            if page.annots:
                refs = self.resolve_PDFObjRef(page.annots)
                if refs:
                    if isinstance(refs, list):
                        for ref in refs:
                            if ref:
                                self.references.add(ref)
                    elif isinstance(refs, Reference):
                        self.references.add(refs)

            # except Exception as e:
            # logger.warning(str(e))

        # Remove empty metadata entries
        self.metadata_cleanup()

        # Get text from stream
        self.text = text_io.getvalue().decode("utf-8")
        text_io.close()
        converter.close()
        # print(self.text)

        # Extract URL references from text
        for url in extractor.extract_urls(self.text):
            self.references.add(Reference(url, self.curpage))

        for ref in extractor.extract_arxiv(self.text):
            self.references.add(Reference(ref, self.curpage))

        for ref in extractor.extract_doi(self.text):
            self.references.add(Reference(ref, self.curpage))

    def resolve_PDFObjRef(self, obj_ref):
        """
        Resolves PDFObjRef objects. Returns either None, a Reference object or
        a list of Reference objects.
        """
        if isinstance(obj_ref, list):
            return [self.resolve_PDFObjRef(item) for item in obj_ref]

        # print(">", obj_ref, type(obj_ref))
        if not isinstance(obj_ref, PDFObjRef):
            # print("type not of PDFObjRef")
            return None

        obj_resolved = obj_ref.resolve()
        # print("obj_resolved:", obj_resolved, type(obj_resolved))
        if isinstance(obj_resolved, bytes):
            obj_resolved = obj_resolved.decode("utf-8")

        if isinstance(obj_resolved, (str, unicode)):
            if IS_PY2:
                ref = obj_resolved.decode("utf-8")
            else:
                ref = obj_resolved
            return Reference(ref, self.curpage)

        if isinstance(obj_resolved, list):
            return [self.resolve_PDFObjRef(o) for o in obj_resolved]

        if "URI" in obj_resolved:
            if isinstance(obj_resolved["URI"], PDFObjRef):
                return self.resolve_PDFObjRef(obj_resolved["URI"])

        if "A" in obj_resolved:
            if isinstance(obj_resolved["A"], PDFObjRef):
                return self.resolve_PDFObjRef(obj_resolved["A"])

            if "URI" in obj_resolved["A"]:
                # print("->", a["A"]["URI"])
                return Reference(obj_resolved["A"]["URI"].decode("utf-8"), self.curpage)


class TextBackend(ReaderBackend):
    def __init__(self, stream):
        ReaderBackend.__init__(self)
        self.text = stream.read()

        # Extract URL references from text
        for url in extractor.extract_urls(self.text):
            self.references.add(Reference(url))

        for ref in extractor.extract_arxiv(self.text):
            self.references.add(Reference(ref))

        for ref in extractor.extract_doi(self.text):
            self.references.add(Reference(ref))
