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


_head = """<!DOCTYPE HTML>
<html lang="en">
<head>
<META name="viewport" content="width=500, initial-scale=1">
<title>CodePlug'ORama</title>
<link rel=StyleSheet href="style.css" type="text/css">
</head>
<body>
<table>
<tr><th>Group</th><th>Channel</th><th>Txfreq</th><th>Rxfreq</th>
<th>Offset</th><th>Name</th><th>Comment</th><th>Txtone</th>
<th>Rxtone</th><th>Mode</th><th>Wide</th><th>Power</th><th>Skip</th></tr>"""

_foot = """</table></body></html>"""

class HtmlText(Channel):
    """Write this data out as an HTML table."""

    # There is no input section


    # OUTPUT SECTION

    @classmethod
    def getOutputType(cls):
        """Return the content type of the output and a reasonable file extension."""
        return ("text/html; charset=utf-8", None)

    @classmethod
    def getWriter(cls, ofile):
        """Return an output file writer suitable for this format.
        In most cases, it's a csv writer."""
        return ofile

    @staticmethod
    def header(ofile, recFilter):
        print(_head, file=ofile)

    @staticmethod
    def footer(ofile, recFilter):
        print(_foot, file=ofile)

    @staticmethod
    def write(rec, ofile, count: int, recFilter):
        Group = rec.Group or ""
        Txfreq = rec.Txfreq or ""
        Rxfreq = rec.Rxfreq or ""
        Offset = rec.Offset or ""
        Name = rec.Name or ""
        Comment = rec.Comment or ""
        Txtone = rec.Txtone or ""
        Rxtone = rec.Rxtone or ""
        Mode = rec.Mode or ""
        Wide = rec.Wide or ""
        Power = rec.Power or ""
        Skip = rec.Skip or ""
        if recFilter.get('longName'): Name = rec.getLongName()
        print(f"<tr><td>{Group}</td><td>{count}</td><td>{Txfreq}</td><td>{Rxfreq}</td><td>{Offset}</td><td>{Name}</td><td>{Comment}</td><td>{Txtone}</td><td>{Rxtone}</td><td>{Mode}</td><td>{Wide}</td><td>{Power}</td><td>{Skip}</td></td>", file=ofile)
