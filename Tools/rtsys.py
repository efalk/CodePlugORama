#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Convert CSV file from ACS 217 spreadsheet to format RT Systems uses for FT-60

import csv
import sys

import channel

# RT Systems schema
#  0 <ch>                  1-1000                  column header is blank, column ignored
#  1 Receive Frequency     146.96000
#  2 Transmit Frequency    146.36000
#  3 Offset Frequency      600 kHz | 5.00000 MHz | (blank)
#  4 Offset Direction      Minus | Plus | Simplex
#  5 Operating Mode        FM | AM; RtSystems also accepts "Auto".
#  6 Name                  e.g. PSRG
#  7 Show Name             Y
#  8 Tone Mode             None, Tone, DCS (others ignored for now)
#  9 CTCSS                 103.5
# 10 DCS                   023
# 11 Skip                  Scan
# 12 Step                  e.g. "5 kHz"
# 13 Clock Shift           N
# 14 Tx Power              High | Low
# 15 Tx Narrow             Y | N
# 16 Pager Enable          N
# 17 Comment               any string

class RtSys(channel.Channel):
    """This is the "generic" RT Systems code. It generates output that
    both Yaesu FT-60 and QRZ-1 are happy with. Other radios might
    want something different; we may make subclasses for those
    radios at some later date."""
    # Output schema is based on the Yaesu FT-60, with optional bank select
    # TODO: RxTone, RxDCS. For now, always set to CSQ.

    # INPUT SECTION

    # List of columns we're interested in, and reasonable defaults if not
    # found. "None" indicates that the column is mandatory.
    columns = {"":"", "n":"", "Receive Frequency":None, "Transmit Frequency":None,
        "Operating Mode":"Auto", "Name":"", "Tone Mode":None,
        "CTCSS":"", "DCS":"", "Skip":"Scan", "Tx Power":"High",
        "Tx Narrow":"N", "Comment":"",
        "Bank 1":"N", "Bank 2":"N", "Bank 3":"N", "Bank 4":"N", "Bank 5":"N",
        "Bank 6":"N", "Bank 7":"N", "Bank 8":"N", "Bank 9":"N", "Bank 10":"N"}

    hasBanks = False

    @classmethod
    def probe(cls, line: list):
        cls.hasBanks = "Bank 1" in line
        return super().probe(line)

    def __init__(this, recFilter: dict, line):
        """Create an RtSys object from a list of csv values. Caller
        must have already vetted the input. The parse() function
        below can handle that."""

        chan, chann, rxfreq, txfreq, mode, name, toneMode, ctcss, dcs, \
            skip, power, narrow, comment = this.fetchValues(line,
            "", "n", "Receive Frequency", "Transmit Frequency",
            "Operating Mode", "Name", "Tone Mode", "CTCSS",
            "DCS", "Skip", "Tx Power", "Tx Narrow", "Comment")

        # Some csv files have no label in the channel column, some have 'n'
        # so we look for both.
        chan = chan or chann

        if RtSys.hasBanks:
            banks = this.fetchValues(line,
                "Bank 1", "Bank 2", "Bank 3", "Bank 4", "Bank 5",
                "Bank 6", "Bank 7", "Bank 8", "Bank 9", "Bank 10")
        else:
            banks = None

        txtone = rxtone = ''
        if toneMode == 'None':
            pass
        elif toneMode == 'Tone':
            txtone = ctcss
        elif toneMode == 'T Sql':
            txtone = rxtone = ctcss
        elif toneMode == 'Rev CTCSS':   # Not supported
            pass
        elif toneMode == 'DCS':
            txtone = 'D' + dcs
        elif toneMode == 'D Code':      # Not sure what this is
            pass
        elif toneMode == 'T DCS':
            txtone = ctcss; rxtone = 'D' + dcs
        elif toneMode == 'D Tone':
            txtone = 'D' + DCS; rxtone = ctcss

        skip = 'N' if skip == 'Scan' else 'Y'

        super().__init__(recFilter, None, chan, txfreq, rxfreq, None, name, comment,
            txtone, rxtone, mode, 'N' if narrow == 'Y' else 'W', power, skip)

        this.banks = banks

    @classmethod
    def parse(cls, line, recFilter):
        """Given a list, most likely provided by the csv module, return
        an RtSys object or None if the list can't be parsed."""

        rxfreq = cls.fetchValue(line, "Receive Frequency")
        if not rxfreq:
            return None
        try:
            rxfreq = float(rxfreq)
            rval = cls(recFilter, line)
            return rval if rval.testFilter(recFilter) else None
        except Exception as e:
            print("Failed to parse: ", line, file=sys.stderr)
            print(e, file=sys.stderr)
            return None



    # OUTPUT SECTION

    @staticmethod
    def header(csvout: csv.writer, recFilter):
        """Write out the header line for the CSV file."""
        banks = recFilter.get('banks')
        if banks:
            Banks = [f"Bank {i}," for i in range(1,11)]
        else:
            Banks = []
        csvout.writerow(["","Receive Frequency","Transmit Frequency","Offset Frequency","Offset Direction","Operating Mode","Name","Show Name","Tone Mode","CTCSS","DCS","Skip","Step","Clock Shift","Tx Power","Tx Narrow","Pager Enable"] + Banks + ["Comment"])

    @staticmethod
    def write(rec: channel.Channel, csvout: csv.writer, count: int, recFilter):
        """Write out one record. This may throw an exception if any of
        the ics-217 fields are not valid."""
        # There are some derived values here, so we compute them now.
        Chan = rec.Chan       # memory #, 0-based
        Name = rec.Name       # memory label
        Rxfreq = rec.Rxfreq       # RX freq
        Wide = rec.Wide
        Txfreq = rec.Txfreq       # RX freq
        Txtone = rec.Txtone
        Rxtone = rec.Rxtone
        Comment = rec.Comment
        Skip = '' if rec.Skip == 'N' else 'Scan'

        if recFilter.get('longName'): Name = rec.getLongName()
        derived = RtSys.Derived(rec, recFilter)
        Txtone = derived.Txtone
        Rxtone = derived.Rxtone
        Offset_s = derived.Offset
        OpMode = derived.OpMode
        ToneMode = derived.ToneMode
        banks = derived.banks

        CTCSS = derived.CTCSS
        DCS = derived.DCS

        #  0 <ch>                  1-1000                  column header is blank, column ignored
        #  1 Receive Frequency     146.96000
        #  2 Transmit Frequency    146.36000
        #  3 Offset Frequency      600 kHz | 5.00000 MHz | (blank)
        #  4 Offset Direction      Minus | Plus | Simplex
        #  5 Operating Mode        FM | AM; RtSystems also accepts "Auto".
        #  6 Name                  e.g. PSRG
        #  7 Show Name             Y
        #  8 Tone Mode             None, Tone, DCS (others ignored for now)
        #  9 CTCSS                 103.5
        # 10 DCS                   023
        # 11 Skip                  Scan
        # 12 Step                  e.g. "5 kHz"
        # 13 Clock Shift           N
        # 14 Tx Power              High | Low
        # 15 Tx Narrow             Y | N
        # 16 Pager Enable          N
        # 17 Comment               any string

        Wide = 'Y' if Wide=="N" else 'N'
        csvout.writerow([count, Rxfreq, Txfreq, Offset_s, OpMode, 'Auto', Name, 'Y' if Name else 'N', ToneMode, CTCSS, DCS, Skip, 'Auto', 'N', 'High', Wide, 'N'] + banks + [Comment])


    class Derived:
        """Represents the derived values used by RT Systems"""
        def __init__(self, rec: channel.Channel, recFilter):
            """Contains the following derived values:
                Txtone
                Rxtone
                Offset: e.g. "n.nnnn MHz" or "nnn kHz" or ''
                OpMode: "Simple", "Plus", "Minus"
                ToneMode: e.g. "None", "T Sql", "DCS", "D Tone", etc.
                CTCSS: e.g. "103.5"
                DCS: e.g. "D23"
            self.CTCSS = CTCSS
            self.DCS = DCS
            """
            # There are some derived values here, so we compute them now.
            Rxfreq = rec.Rxfreq
            Txfreq = rec.Txfreq
            Txtone = rec.Txtone
            Rxtone = rec.Rxtone

            # Derived values
            Offset = float(rec.Offset)
            if Txfreq == Rxfreq:
                Offset_s = ''
            elif abs(Offset) < 1.0:
                Offset_s = "%.0f kHz" % (abs(Offset)*1000.)
            else:
                Offset_s = "%.4f MHz" % abs(Offset)

            if Txfreq == Rxfreq:
                OpMode = "Simplex"
            elif Offset > 0:
                OpMode = "Plus"
            else:
                OpMode = "Minus"

            CTCSS = ''
            DCS = ''

            # There are nine possibilities for Txtone/Rxtone
            # This radio doesn't support different Tx/Rx tones.
            if not Txtone:
                ToneMode = 'None'   # Rx tone or DCS not supported
            elif Txtone[0] == 'D':
                DCS = Txtone[1:]
                if not Rxtone:
                    ToneMode = 'DCS'
                elif Rxtone[0] == 'D':
                    ToneMode = 'DCS'    # TODO: should this be 'D Code'?
                else:
                    CTCSS = Rxtone
                    ToneMode = 'D Tone'
            else:
                CTCSS = Txtone
                if not Rxtone:
                    ToneMode = 'Tone'   # Most common case
                elif Rxtone[0] == 'D':
                    DCS = Rxtone[1:]
                    ToneMode = 'T DCS'
                else:
                    ToneMode = 'T Sql'

            banklist = recFilter.get('banks')
            if banklist:
                banks = ['N']*10
                try:
                    for bank in banklist.split(','):
                        banks[int(bank)-1] = 'Y'
                except exception as e:
                    print(e)
                    banks = []
            else:
                banks = []

            self.Txtone = Txtone
            self.Rxtone = Rxtone
            self.Offset = Offset_s
            self.OpMode = OpMode
            self.ToneMode = ToneMode
            self.CTCSS = CTCSS
            self.DCS = DCS
            self.banks = banks
