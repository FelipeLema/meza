#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4:ts=4:expandtab

"""
dbf.io
~~~~~~

Provides methods for reading dbf files

Examples:
    literal blocks::

        from tabutils.io import read_csv

        csv_records = read_csv('path/to/file.csv')
        csv_header = csv_records.next().keys()
        csv_records.next()

Attributes:
    ENCODING (str): Default file encoding.
"""

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from os import path as p
from collections import OrderedDict
from datetime import date

from dbfread import DBF
from dbfread.dbf import expand_year
from dbfread.exceptions import DBFNotFound
from dbfread.field_parser import FieldParser
from dbfread.ifiles import ifind


class DBF2(DBF):
    """DBF table."""
    def __init__(self, filepath, **kwargs):
        """Reads a dBase, Visual FoxPro, or FoxBase+ file

        Args:
            filepath (str): The dbf file path or file like object.
            **kwargs: Keyword arguments that are passed to the DBF reader.

        Kwargs:
            load (bool): Load all records into memory (default: false).
            encoding (bool): Character encoding (default: None, parsed from
                the `language_driver`).

            sanitize (bool): Convert field names to lower case
                (default: False).
            ignorecase (bool): Treat file name as case insensitive
                (default: true).
            ignore_missing_memofile (bool): Suppress `MissingMemoFile`
                exceptions (default: False).
        """
        try:
            return super(DBF2, self).__init__(filepath, **kwargs)
        except AttributeError:
            filename = filepath.name

        defaults = {
            'ignorecase': True,
            'parserclass': FieldParser,
            'recfactory': OrderedDict
        }

        [kwargs.setdefault(k, v) for k, v in defaults.items()]
        [self.__setattr__(k, v) for k, v in kwargs.items()]
        self.name = p.splitext(p.basename(filename))[0].lower()
        self.filename = ifind(filename) if self.ignorecase else filename

        if not self.filename:
            raise DBFNotFound('could not find file {!r}'.format(filename))

        self.fields = []
        self.field_names = []
        self._read_headers(filepath, self.ignore_missing_memofile)
        self._check_headers()

        try:
            year = expand_year(self.header.year)
        except ValueError:
            self.date = None
        else:
            self.date = date(year, self.header.month, self.header.day)

        self.memofilename = self._get_memofilename()

        if self.load:
            self.load()

    def __getattr__(self, name):
        return None
