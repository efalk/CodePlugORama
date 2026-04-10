#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Parse lines from the Repeater Roundabout spreadsheet.
#
# Typical usage:
#
#    from rr import rr
#
#    reader = csv.reader(sys.stdin)
#
#    for l in reader:
#        rec = rr.parse(l)
#        if not rec:
#           continue            # this is fine; not all records contain data

# Schema:
#   0 RR#, starts with 1
#   1 Callsign, e.g. WW7PSR
#   2 Output (rxfreq) (MHz), e.g. 146.96
#   3 Offset (MHz), e.g. -0.6
#   4 Tone (Hz), e.g. 103.5
#   5 RepeaterBook ID, often blank
#   6 Location, e.g. "Capitol Hill, Seattle, WA"
#   7 Mode, FM, NBFM, etc.
#   8 Group, e.g. Snohomish County Auxiliary Communications Service
#   9 Website, e.g. https://wa7dem.info
#  10 RepeaterBook State ID, typically blank
#  11 Latitude, e.g. 47.75619
#  12 Longitude, e.g. -122.34575



import sys

import channel
from channel import csvget

class rr(channel.Channel):
    """Represents one Repeater Roundabout record. See above for list of fields."""

    # INPUT SECTION (there is no output section)

    @classmethod
    def probe(cls, line: list):
        """Examine line to see if the input is in Repeater Roundabout format. Return
        None if not. Anything else is true."""
        match = len(line) >= 13 and \
            line[1] == "Callsign" and \
            line[2] == "Output (MHz)" and \
            line[3] == "Offset (MHz)" and \
            line[4] == "Tone (Hz)" and \
            line[7] == "Mode"
        return cls if match else None

    def __init__(this, recFilter: dict, line):
        """Create an rr object from a list of csv values. Caller
        must have already vetted the input. The parse() function
        below can handle that."""
        mode = line[7]
        wide = 'W'
        if mode.startswith('NB'):
            mode = mode[2:]
            wide = 'N'
        super().__init__(recFilter, None, line[0], line[2], None, line[3],
            line[1], line[5], line[4], None, mode, wide, 'High', '')
        this.Loc = line[6]
        this.Grp = line[8]
        this.Website = line[9]
        this.State = line[10]
        this.Lat = line[11]
        this.Lon = line[12]
        this.Comment = this.getComment()

    def __repr__(this):
        mode = this.Mode if this.Wide == 'W' else 'NB'+this.Mode
        return f"""rr(None, ({this.Chan!r}, {this.Rxfreq!r}, {this.Offset!r}, {this.Txtone!r},, {this.Loc!r}, {mode!r}, {this.Grp!r}, {this.Website!r}, {this.State!r}, {this.Lat!r}, {this.Lon!r}))"""

    def __str__(this):
        mode = this.Mode if this.Wide == 'W' else 'NB'+this.Mode
        return f"""rr({this.Chan}, {this.Rxfreq}, {this.Offset}, {this.Txtone},, {this.Loc}, {mode}, {this.Grp}, {this.Website}, {this.State}, {this.Lat}, {this.Lon})"""

    def getComment(this):
        """Return a reasonable comment for this item"""
        try:
            c = []
            if this.Grp: c.append(this.Grp)
            if this.Loc: c.append(this.Loc)
            if this.Website: c.append(this.Website)
            if this.Lat: c.append(','.join((this.Lat,this.Lon)))
            return '; '.join(c)
        except Exception as e:
            print(this, e, file=sys.stderr)
            raise

    @classmethod
    def parse(cls, line, recFilter):
        """Given a list, most likely provided by the csv module, return
        an rr object or None if the list can't be parsed."""
        if len(line) < 13: return None
        # line[0] is channel number; if missing or not a number, reject
        if not line[0].isdigit(): return None
        regex = recFilter.get('regex')
        if regex and not regex.match(line[1]):
            return None
        try:
            return cls(recFilter, line)
        except Exception as e:
            print("Failed to parse: ", line, file=sys.stderr)
            print(e, file=sys.stderr)
            return None

def strNeg(s):
    return s[1:] if s[0] == '-' else '-'+s
