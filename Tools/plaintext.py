#!/usr/bin/env python3
# -*- coding: utf8 -*-


import csv

from channel import Channel

class Plaintext(Channel):

    # There is no input section


    # OUTPUT SECTION

    @classmethod
    def getOutputType(cls):
        """Return the content type of the output and a reasonable file extension."""
        return ("text/plain; charset=utf-8", None)

    @classmethod
    def getWriter(cls, ofile):
        """Return an output file writer suitable for this format.
        In most cases, it's a csv writer."""
        return csv.writer(ofile, dialect=csv.excel_tab)
