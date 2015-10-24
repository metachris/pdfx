# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
import sys
import logging
from threading import Thread

if sys.version_info < (3, 0):
    # Python 2
    from urllib2 import Request, urlopen
else:
    # Python 3
    from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


class ThreadedDownloader(object):
    """
    Class which can download many files simultaneously to a specific
    output directory. Usage:

    >>> urls = ["http://test.com/a.pdf", "http://test.com/b.pdf"]
    >>> tdl = ThreadedDownloader(urls, "download_dir")
    >>> tdl.start_downloads()     # Downloads are started as threads
                                    in the background
    >>> tdl.wait_for_downloads()  # Waits until all download threads
                                    are finished (blocking)
    """
    urls = []
    output_directory = None
    threads = []

    def __init__(self, urls, output_directory):
        assert type(urls) in [list, tuple, set
                              ], "ThreadedDownloader urls need to be a list"
        assert len(urls), "ThreadedDownloader needs urls"
        assert output_directory, "ThreadedDownloader needs an output_directory"
        self.urls = urls
        self.output_directory = output_directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            logger.debug("Created directory '%s'" % output_directory)

    def _download_threaded(self, url):
        try:
            fn = url.split("/")[-1]
            fn_download = os.path.join(self.output_directory, fn)
            with open(fn_download, "wb") as f:
                f.write(urlopen(Request(url)).read())
        except Exception as e:
            logger.warn("Error downloading '%s' (%s)" % (url, str(e)))
            return
        logger.debug("Downloaded '%s' to '%s'..." % (url, fn_download))

    def start_downloads(self):
        for url in self.urls:
            thread = Thread(target=self._download_threaded, args=(url, ))
            thread.start()
            self.threads.append(thread)

    def wait_for_downloads(self):
        for thread in self.threads:
            thread.join()
