#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3
from threading import Thread
from queue import Queue

import conf


class DB(Thread):
    def __init__(self, dbn=conf.dbn):
        Thread.__init__(self)
        self.dbn = dbn
        self.reqs = Queue()
        self.daemon = True
        self.start()

    def run(self):
        self.con = sqlite3.connect(self.dbn, check_same_thread=False)
        self.cur = self.con.cursor()

        while True:
            req, arg, res = self.reqs.get()
            if req == '--close--':
                break
            if req == '--commit--':
                self.con.commit()

            try:
                self.cur.execute(req, arg)
            except:
                self.con.rollback()

            if self.cur.description:
                for row in self.cur:
                    res.put(row)
            else:
                res.put(self.cur.rowcount)
            res.put('--no more--')

        self.con.close()

    def execute(self, req, arg=tuple()):
        res = Queue()
        self.reqs.put((req, arg, res))

    def query(self, req, arg=tuple()):
        res = Queue()
        self.reqs.put((req, arg, res))

        def iterwrapper():
            while True:
                row = res.get()
                if row == '--no more--':
                    break
                yield row

        return iterbetter(iterwrapper())

    def close(self):
        self.execute('--close--')

    def commit(self):
        self.execute('--commit--')


# Copy from https://github.com/webpy/webpy/blob/master/web/utils.py
class IterBetter:
    """
    Returns an object that can be used as an iterator
    but can also be used via __getitem__ (although it
    cannot go backwards -- that is, you cannot request
    `iterbetter[0]` after requesting `iterbetter[1]`).
        >>> import itertools
        >>> c = iterbetter(itertools.count())
        >>> c[1]
        1
        >>> c[5]
        5
        >>> c[3]
        Traceback (most recent call last):
            ...
        IndexError: already passed 3
    It is also possible to get the first value of the iterator or None.
        >>> c = iterbetter(iter([3, 4, 5]))
        >>> print(c.first())
        3
        >>> c = iterbetter(iter([]))
        >>> print(c.first())
        None
    For boolean test, IterBetter peeps at first value in the itertor without effecting the iteration.
        >>> c = iterbetter(iter(range(5)))
        >>> bool(c)
        True
        >>> list(c)
        [0, 1, 2, 3, 4]
        >>> c = iterbetter(iter([]))
        >>> bool(c)
        False
        >>> list(c)
        []
    """
    def __init__(self, iterator):
        self.i, self.c = iterator, 0

    def first(self, default=None):
        """Returns the first element of the iterator or None when there are no
        elements.
        If the optional argument default is specified, that is returned instead
        of None when there are no elements.
        """
        try:
            return next(iter(self))
        except StopIteration:
            return default

    def list(self):
        return list(self)

    def __iter__(self):
        if hasattr(self, "_head"):
            yield self._head

        while 1:
            yield next(self.i)
            self.c += 1

    def __getitem__(self, i):
        # todo: slices
        if i < self.c:
            raise IndexError("already passed " + str(i))
        try:
            while i > self.c:
                next(self.i)
                self.c += 1
            # now self.c == i
            self.c += 1
            return next(self.i)
        except StopIteration:
            raise IndexError(str(i))

    def __nonzero__(self):
        if hasattr(self, "__len__"):
            return self.__len__() != 0
        elif hasattr(self, "_head"):
            return True
        else:
            try:
                self._head = next(self.i)
            except StopIteration:
                return False
            else:
                return True

    __bool__ = __nonzero__


iterbetter = IterBetter
