# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import sys
import ssl

from collections import defaultdict
from .threadpool import ThreadPool
from .colorprint import colorprint, OKGREEN, FAIL

IS_PY2 = sys.version_info < (3, 0)
if IS_PY2:
    # Python 2
    from urllib2 import Request, urlopen, HTTPError, URLError
else:
    # Python 3
    from urllib.request import Request, urlopen, HTTPError, URLError
    unicode = str


MAX_THREADS_DEFAULT = 5

# Used to allow downloading files even if https certificate doesn't match
if hasattr(ssl, "_create_unverified_context"):
    ssl_unverified_context = ssl._create_unverified_context()
else:
    # Not existing in Python 2.6
    ssl_unverified_context = None


def sanitize_url(url):
    """ Make sure this url works with urllib2 (ascii, http, etc) """
    if url and not url.startswith("http"):
        url = u"http://%s" % url
    url = url.encode('ascii', 'ignore').decode("utf-8")
    return url


def get_status_code(url):
    """ Perform HEAD request and return status code """
    try:
        request = Request(sanitize_url(url))
        request.add_header("User-Agent", "Mozilla/5.0 (compatible; MSIE 9.0; "
                           "Windows NT 6.1; Trident/5.0)")
        request.get_method = lambda: 'HEAD'
        response = urlopen(request, context=ssl_unverified_context)
        # print response.info()
        return response.getcode()
    except URLError as e:
        return e.reason
    except HTTPError as e:
        return e.code
    except Exception as e:
        print(e, url)
        return None


def check_refs(refs, verbose=True, max_threads=MAX_THREADS_DEFAULT,
               signal_item_started=None, signal_item_finished=None):
    """ Check if urls exist """
    codes = defaultdict(list)

    def check_url(ref):
        if signal_item_started:
            signal_item_started(ref)
        url = ref.ref

        # Download and collect status
        status_code = str(get_status_code(url))
        codes[status_code].append(ref)

        # After downloading, process result
        if signal_item_finished:
            signal_item_finished(ref, status_code)
        if verbose:
            if status_code == "200":
                colorprint(OKGREEN, "%s - %s" % (status_code, url))
            else:
                colorprint(FAIL, "%s - %s" % (status_code, url))

    # Start a threadpool and add the check-url tasks
    try:
        pool = ThreadPool(max_threads)
        pool.map(check_url, refs)
        pool.wait_completion()

    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        pass

    # Print summary
    if verbose:
        print("\nSummary of link checker:")
        if "200" in codes:
            colorprint(OKGREEN, "%s working" % len(codes["200"]))
        for c in sorted(codes):
            if c != "200":
                colorprint(FAIL, "%s broken (reason: %s)" % (len(codes[c]), c))
                for ref in codes[c]:
                    o = u"  - %s" % ref.ref
                    if hasattr(ref, "page") and ref.page > 0:
                        o += " (page %s)" % ref.page
                    print(o)

    return codes


def download_refs(refs, output_directory, verbose=True,
                  max_threads=MAX_THREADS_DEFAULT,
                  signal_item_started=None, signal_item_finished=None):
    """ Download refs to a target directory """
    assert type(refs) in [list, tuple, set], "Urls must be some kind of list"
    assert len(refs), "Need urls"
    assert output_directory, "Need an output_directory"

    def vprint(s):
        if verbose:
            print(s)

    def download_ref(ref):
        # Signal start of download
        if signal_item_started:
            signal_item_started(ref)

        status = ""
        url = ref.ref
        # fn = url.split("/")[-1]
        fn = os.path.basename(url)
        fn_download = os.path.join(output_directory, fn)
        try:
            request = Request(sanitize_url(url))
            request.add_header("User-Agent", "Mozilla/5.0 (compatible; "
                               "MSIE 9.0; Windows NT 6.1; Trident/5.0)")
            response = urlopen(request, context=ssl_unverified_context)
            status = response.getcode()
            with open(fn_download, "wb") as f:
                if status == 200:
                    f.write(urlopen(request).read())
                    colorprint(OKGREEN, "Downloaded '%s' to '%s'" %
                                        (url, fn_download))
                else:
                    colorprint(FAIL, "Error downloading '%s' (%s)" %
                                     (url, status))
        except URLError as e:
            colorprint(FAIL, "Error downloading '%s' (%s %s)" %
                             (url, e.code, e.reason))
            status = e.reason
        except HTTPError as e:
            colorprint(FAIL, "Error downloading '%s' (%s)" % (url, e.code))
            status = "HTTPError %s" % e.code
        except Exception as e:
            colorprint(FAIL, "Error downloading '%s' (%s)" % (url, str(e)))
            status = str(e)
        finally:
            if signal_item_finished:
                signal_item_finished(ref, str(status))

    # Create directory
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        vprint("Created directory '%s'" % output_directory)

    try:
        pool = ThreadPool(max_threads)
        pool.map(download_ref, refs)
        pool.wait_completion()

    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        pass
