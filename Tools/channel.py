#!/usr/bin/env python3
# -*- coding: utf8 -*-

# This is the base class for holding radio programming
# info.
#
# Channel class holds the following 13 values:
#
#  Group
#    Not commonly used. Some radios, e.g. TK-780, divide the
#    channels into groups. Normally leave this unset.
#
#  Chan
#    The channel number. Caller is responsible for making sure
#    this works for the radio in question. ACS 217 files have channel
#    numbers like "V01" or "U22" so obviously the software is going to
#    have to provide its own numbering when writing out the CSV files.
#
#  Rxfreq
#    Receive frequency, Hz. Specify as a string; it will be
#    converted if necessary
#
#  Txfreq
#    Transmit frequency, Hz. Specify as a string; it will be
#    converted if necessary
#
#  Offset
#    difference between txfreq and rxfreq: txfreq-rxfreq
#
#    It's not necessary to set all of txfreq, rxfreq, and offset.
#    For simplex, just set one of txfreq or rxfreq (or set them both
#    to the same value). For duplex, set two and the third will be
#    derived if needed.
#
#  Name
#
#  Comment
#
#  Txtone
#    numeric CTCSS tone or Dnnn.
#
#  Rxtone
#    numeric CTCSS tone or Dnnn.
#
#  Mode: AM, FM, etc.
#
#  Wide: 'W', 'N'
#
#  Power:
#    Prefer a number representing watts. "high", "med", "low"
#    if necessary. Subclasses that write out CSV files are
#    responsible for converting if necessary.
#
#  Skip:
#    'Y', 'N' or '' for don't care.
#
# Many fields may be None. It is the responsibility of the output writers
# to convert that to the appropriate (typically empty) string.
# TODO: change this?

import csv
import decimal
import re
import sys

# Schema:
#   0 group, usually blank
#   1 chan
#   2 rxfreq
#   3 txfreq
#   4 offset
#   5 name
#   6 comment
#   7 txtone
#   8 rxtone
#   9 mode
#  10 wide
#  11 power
#  12 skip

callsign_re = re.compile(r'''[A-Z]+\d[A-Z]+(-\d+)?''')  # callsign with optional -nn
callsign_l_re = re.compile(r'''[A-Z]+\d[A-Z]+-\d+''')   # callsign with non-optional -nn

def csvget(value):
    """Return numeric value in a form suitable for a csv file"""
    if value is None: return ''
    value = str(value)
    if '"' in value: value = value.replace('"', '\\"')
    if ',' in value: value = '"' + value + '"'
    return value


class Channel(object):
    """Channel data base class. Can parse a generic format."""

    # INPUT SECTION

    # Subclasses can either override the probe() method, or override
    # the `columns` dict below and let this class's probe() method
    # figure it out. The latter method is more robust, but a little
    # more work for the parser.

    # Subclasses can override this dict. The value is the default
    # if the column isn't found. None means it's mandatory. At least
    # some of the columns must be mandatory to prevent the probe()
    # function from just blindly accepting everything.
    columns = {'group':'', 'chan':None, 'rxfreq':None, 'txfreq':'', 'offset':'',
        'name':None, 'comment':'', 'txtone':'', 'rxtone':'', 'mode':'',
        'wide':'W', 'power':'5.0W', 'skip':''}

    # This dict is filled in by the probe function. Keys are the same as above.
    # Values are either int indices into the input line, or string default values.
    colIdx = {}

    @classmethod
    def probe(cls, line: list):
        """Examine line to see if the input is in generic format.
        If so, return a class that can read it. Usually this
        class."""
        columns = Channel.columns
        colIdx = Channel.colIdx

        # Step 1: see what we've got
        for idx,header in enumerate(line):
            if header in columns:
                colIdx[header] = idx

        # Step 2: see what we're missing
        for key,value in columns.items():
            if key not in colIdx:
                dflt = columns[key]
                if dflt is not None:
                    colIdx[key] = dflt
                else:
                    return None

        return cls


    def __init__(self, recFilter: dict, *args):
        """Create one channel object. Caller is responsible for ensuring that
        rxfreq and txfreq are both valid. If offset is not provided, it will
        be computed from txfreq and rxfreq. All other fields must be provided."""
        if len(args) == 1:
            line = args[0]
            group, chan, rxfreq, txfreq, offset, \
                name, comment, txtone, rxtone, mode, wide, power, skip = \
                    self.fetchValues(line, "group", "chan", "rxfreq", "txfreq", "offset",
                        "name", "comment", "txtone", "rxtone", "mode", "wide", "power", "skip")
        else:
            group, chan, rxfreq, txfreq, offset, \
                name, comment, txtone, rxtone, mode, wide, power, skip = args

        if not txfreq:
            if offset:
                try:
                    rf = decimal.Decimal(rxfreq)
                    off = decimal.Decimal(offset)
                    txfreq = str(rf + off)
                except:
                    pass    # no helping it
            else:
                txfreq = rxfreq
        if not rxfreq:
            if offset:
                try:
                    tf = decimal.Decimal(txfreq)
                    off = decimal.Decimal(offset)
                    rxfreq = str(tf - off)
                except:
                    pass    # no helping it
            else:
                rxfreq = txfreq
        if not offset:
            try:
                tf = decimal.Decimal(txfreq)
                rf = decimal.Decimal(rxfreq)
                offset = str(tf - rf)
            except:
                pass    # no helping it

        if not mode: mode = 'FM' if float(rxfreq) >= 100.0 else 'AM'

        self.Group = group
        self.Chan = chan
        self.Rxfreq = rxfreq
        self.Txfreq = txfreq
        self.Offset = offset
        self.Name = name
        self.Comment = comment
        self.Txtone = txtone
        self.Rxtone = rxtone
        self.Mode = mode
        self.Wide = wide
        self.Power = power
        self.Skip = skip or recFilter.get('skip','')

    def __repr__(self):
        return f'''Channel({repr(self.Group)}, {repr(self.Chan)}, {repr(self.Rxfreq)}, {repr(self.Txfreq)}, {repr(self.Offset)}, {repr(self.Name)}, {repr(self.Comment)}, {repr(self.Txtone)}, {repr(self.Rxtone)}, {repr(self.Mode)}, {repr(self.Wide)}, {repr(self.Power)}, {repr(self.Skip)})'''

    def getLongName(this):
        """Return a reasonable long-form name for this item; incorporate the
        name and comment."""
        # If the name field is not a call sign and a call sign can be
        # found in the comment, append that call sign to the name. If
        # call sign with a dash, e.g. KK7ABC-10 is found, prefer that
        # to a simple call sign.
        #print(f"name:{this.Name}, comment:{this.Comment}")
        mo_l = callsign_l_re.search(this.Comment)
        mo = callsign_re.search(this.Comment)
        if not this.Name:
            # No name at all, look for a callsign in the comment, else the first
            # word of the comment, else nothing.
            if mo_l:
                return mo_l.group()
            if mo:
                return mo.group()
            if this.Comment:
                return this.Comment.split()[0]
            return this.Name
        elif callsign_l_re.search(this.Name):     # Can't really improve on this
            return this.Name
        elif callsign_re.search(this.Name):
            # Callsign but no dash; look for one with a dash in the comment
            if mo_l:
                return this.Name + ' ' + mo_l.group()
            else:
                return this.Name
        else:
            # No callsign in the name, look for one in the comment
            if mo_l:
                return this.Name + ' ' + mo_l.group()
            if mo:
                return this.Name + ' ' + mo.group()
            else:
                return this.Name


    @classmethod
    def fetchValue(cls, line, key):
        """Given an input line, a key, and the colummn index dict
        previously computed in probe(), return the referenced value."""
        idx = cls.colIdx[key]
        return line[idx] if isinstance(idx, int) else idx

    @classmethod
    def fetchValues(cls, line: list, *keys) -> list:
        """Given an input line, a list of keys, and the colummn index dict
        previously computed in probe(), return the referenced values."""
        rval = []
        for key in keys:
            idx = cls.colIdx[key]
            rval.append(line[idx] if isinstance(idx, int) else idx)
        return rval

    @classmethod
    def parse(cls, line, recFilter):
        """Given a list, most likely provided by the csv module, return
        an ics217 object or None if the list can't be parsed."""

        chan, rxfreq, txfreq = cls.fetchValues(line, 'chan', 'txfreq', 'rxfreq')

        regex = recFilter.get('regex')
        if regex and not regex.match(chan):
            return None
        # At least one of rxfreq, txfreq must be provided
        if not rxfreq and not txfreq:
            return None
        try:
            rxfreq = float(rxfreq)
        except:
            try:
                txfreq = float(txfreq)
            except:
                return None
        try:
            rval = cls(recFilter, line)
            return rval if rval.testFilter(recFilter) else None
        except Exception as e:
            print("Failed to parse: ", line, file=sys.stderr)
            print(e, file=sys.stderr)
            return None

    bandList = {'L':(1.8,54.0), 'V':(144.0,148.0), 'T':(219.0,225.0),
        'U':(420.0,450.0), 'G':(462.55,467.725)}
    modeList = {'A':"AM", 'F':"FM", 'L':"LSB", 'U':"USB", 'C':"CW",
        'S':'DSTAR', 'D':"DMR", 'V':"DV",}

    def testFilter(self, recFilter):
        """Confirm that this record passes the filter."""
        bands = recFilter.get('bands')
        if bands and not self._checkBand(bands):   # VULTGH
            return False
        modes = recFilter.get('modes')
        if modes and not self._checkMode(modes):
            return False
        return True

    def _checkBand(self, bands):
        if 'H' in bands: bands += 'G'   # H and G are the same band
        rxfreq = float(self.Rxfreq)
        for c in bands:
            if c in Channel.bandList:
                freqs = Channel.bandList[c]
                if rxfreq >= freqs[0] and rxfreq <= freqs[1]:
                    return True
        return False

    def _checkMode(self, modes):
        mode = self.Mode.upper()
        for c in modes:
            if c in Channel.modeList and Channel.modeList[c] == mode:
                return True
            elif c == 'd' and mode not in Channel.modeList.values():
                return True
        return False

    # OUTPUT SECTION

    @classmethod
    def getOutputType(cls):
        """Return the content type of the output and a reasonable file extension."""
        return ("text/csv; charset=utf-8", "csv")

    @classmethod
    def getWriter(cls, ofile):
        """Return an output file writer suitable for this format.
        In most cases, it's a csv writer."""
        return csv.writer(ofile)

    @staticmethod
    def header(csvout, recFilter):
        """Write out the header"""
        csvout.writerow(["group","chan","rxfreq","txfreq","offset","name","comment","txtone","rxtone","mode","wide","power","skip"])

    @staticmethod
    def footer(csvout, recFilter):
        """Write out the final piece of output"""
        pass

    @staticmethod
    def write(rec, csvout, count: int, recFilter):
        """Write out one record. This may throw an exception if any of
        the fields are not valid."""
        outrow = [rec.Group, count, rec.Rxfreq, rec.Txfreq, rec.Offset, rec.Name, rec.Comment, rec.Txtone, rec.Rxtone, rec.Mode, rec.Wide, rec.Power, rec.Skip]
        csvout.writerow(outrow)



# ---- program


if __name__ == '__main__':
    print('test')

# chan = Channel(None, "3", "146.9", "146.3", "-0.6",
#         "PSRG", "This is a comment", "103.5", None, 'W', '5W')
# print(chan)
# print(f"  {chan.Txfreq}  {chan.Rxfreq}  {chan.Offset}")
# print(chan.ToValues())
# l = chan.ToValues()
# chan2 = Channel.FromValues(l)
# print(chan2)

# 
# chan = Channel(None, "3", "146.9", "146.3", None,
#         "PSRG", "This is a comment", "103.5", None, 'W', '5W')
# print(chan)
# print(f"  {chan.Txfreq}  {chan.Rxfreq}  {chan.Offset}")
# 
# chan = Channel(None, "3", "146.9", None, "-0.6",
#         "PSRG", "This is a comment", "103.5", None, 'W', '5W')
# print(chan)
# print(f"  {chan.Txfreq}  {chan.Rxfreq}  {chan.Offset}")
# 
# chan = Channel(2, "3", "146.9", "146.3", "-0.6",
#         "PSRG", "This is a comment", "103.5", None, 'W', '5W')
# print(chan)
# print(f"  {chan.Txfreq}  {chan.Rxfreq}  {chan.Offset}")
# 
# chan = Channel(2, "3", "146.9", "146.3", "-0.6",
#         "PSRG", None, "103.5", None, 'W', '5W')
# print(chan)
# print(f"  {chan.Txfreq}  {chan.Rxfreq}  {chan.Offset}")
# 

# print(csvget("foo"))
# print(csvget("foo bar"))
# print(csvget("foo, bar"))
# print(csvget(None))
# print(csvget(''))
# print(csvget("that's all"))
# print(csvget('that"s all'))
