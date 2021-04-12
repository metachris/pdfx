"""
Inspired by http://stackoverflow.com/a/7257510
"""

from threading import Thread
import sys

IS_PY2 = sys.version_info < (3, 0)

if IS_PY2:
    # Python 2
    from Queue import Queue
else:
    # Python 3
    from queue import Queue


class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                print(e)
            finally:
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """

    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()


if __name__ == "__main__":
    from random import randrange
    from time import sleep

    delays = [randrange(5, 10) for i in range(100)]

    def wait_delay(d):
        print("sleeping for (%d)sec" % d)
        sleep(d)

    pool = ThreadPool(5)

    for i, d in enumerate(delays):
        pool.add_task(wait_delay, d)

    pool.wait_completion()
