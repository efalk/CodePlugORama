#!/usr/bin/env python3
# -*- coding: utf8 -*-


import csv
import decimal
import sys

from channel import Channel

# Chirp schema
#   0 Location      Memory location, starting at 1
#   1 Name          e.g. "PSRG"
#   2 Frequency     e.g. 146.960000
#   3 Duplex        off, +, -, or <blank>
#   4 Offset        e.g. 0.60000
#   5 Txtone        <blank> Tone TSQL DTCS TSQL-R DTCS-R Cross
#   6 rToneFreq
#   7 cToneFreq
#   8 DtcsCode      e.g. 023
#   9 DtcsPolarity  e.g. NN
#  10 RxDtcsCode    e.g. 023
#  11 CrossMode     Tone->Tone Tone->DTCS DTCS->Tone DTCS-> ->DTCS ->Tone DTCS->DTCS
#  12 Mode          WFM, FM, NFM
#  13 TStep         e.g. 5.00
#  14 Skip          <blank>, S
#  15 Power         e.g. 5.0W
#  16 Comment       any text
#  17 URCALL        <blank>
#  18 RPT1CALL      <blank>
#  19 RPT2CALL      <blank>
#  20 DVCODE        <blank>

ValidModes = ["WFM", "FM", "NFM", "AM", "NAM", "DV", "USB", "LSB", "CW", "RTTY",
                "DIG", "PKT", "NCW", "NCWR, CWR", "P25", "Auto", "RTTYR", "FSK",
                "FSKR", "DMR", "DN"]

class Chirp(Channel):

    # INPUT SECTION

    # List of columns we're interested in, and reasonable defaults if not
    # found. "None" indicates that the column is mandatory.
    columns = {"Location":'', "Name":'', "Frequency":None, "Duplex":None,
        "Offset":None, "Txtone":'', "rToneFreq":'88.5', "cToneFreq":'88.5',
        "DtcsCode":'023', "RxDtcsCode":'023', "CrossMode":'Tone->Tone',
        "Mode":'', "Skip":'', "Power":'5.0W', "Comment":''}

    def __init__(this, recFilter: dict, line):
        """Create a Chirp object from a list of csv values. Caller
        must have already vetted the input. The parse() function
        below can handle that."""

        Location, Name, Freq, Duplex, Offset, Tone, Rtone, \
            Ctone, DtcsCode, RxDtcsCode, CrossMode, \
            Mode, Skip, Power, Comment = this.fetchValues(line,
                "Location", "Name", "Frequency", "Duplex", "Offset",
                "Txtone", "rToneFreq", "cToneFreq", "DtcsCode",
                "RxDtcsCode", "CrossMode", "Mode", "Skip", "Power",
                "Comment")

        if Duplex == '+':
            pass
        elif Duplex == '-':
            Offset = '-' + Offset
        else:
            Offset = 0

        txtone = rxtone = ''
        if Tone == '':
            pass
        elif Tone == 'Tone':
            txtone = Rtone
        elif Tone == 'TSQL':
            txtone = rxtone = Rtone
        elif Tone == 'DTCS':
            txtone = rxtone = 'D' + DtcsCode
        elif Tone == 'TSQL-R':
            rxtone = Rtone
        elif Tone == 'DTCS-R':
            rxtone = 'D' + DtcsCode
        elif Tone == 'Cross':
            if CrossMode == 'Tone->Tone':       # TX rToneFreq; RX cToneFreq
                txtone = Rtone
                rxtone = Ctone
            elif CrossMode == 'Tone->DTCS':     # TX rToneFreq; RX DtcsCode
                txtone = Rtone
                rxtone = 'D' + DtcsCode
            elif CrossMode == 'DTCS->Tone':     # TX DtcsCode; RX rToneFreq
                txtone = 'D' + DtcsCode
                rxtone = Rtone
            elif CrossMode == 'DTCS->':         # TX DtcsCode
                txtone = 'D' + DtcsCode
            elif CrossMode == '->DTCS':         # RX DtcsCode
                rxtone = 'D' + DtcsCode
            elif CrossMode == '->Tone':         # RX rToneFreq
                rxtone = Rtone
            elif CrossMode == 'DTCS->DTCS':
                txtone = rxtone = 'D' + DtcsCode

        wide = 'W'
        if Mode.startswith('W'):
            Mode = Mode[1:]
        elif Mode.startswith('N'):
            wide = 'N'
            Mode = Mode[1:]

        Skip = 'Y' if Skip else ''

        super().__init__(recFilter, None, Location, Freq, None, Offset,
            Name, Comment, txtone, rxtone, Mode, wide, Power, Skip)


    @classmethod
    def parse(cls, line, recFilter):
        """Given a list, most likely provided by the csv module, return
        an RtSys object or None if the list can't be parsed."""

        Freq = cls.fetchValue(line, "Frequency")

        # line[2] is RX freq; if that's blank or not a number, then
        # the entire record is invalid
        if not Freq:
            return None
        try:
            rxfreq = float(Freq)
        except Exception as e:
            return None
        try:
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
        csvout.writerow(["Location","Name","Frequency","Duplex","Offset","Tone",
            "rToneFreq","cToneFreq","DtcsCode","DtcsPolarity","RxDtcsCode",
            "CrossMode","Mode","TStep","Skip","Power","Comment","URCALL",
            "RPT1CALL","RPT2CALL","DVCODE"])

    @staticmethod
    def write(rec: Channel, csvout: csv.writer, count: int, recFilter):
        """Write out one record. This may throw an exception if any of
        the ics-217 fields are not valid."""
        Chan = rec.Chan       # memory #, 0-based
        Name = rec.Name       # memory label
        Rxfreq = rec.Rxfreq       # RX freq
        Txfreq = rec.Txfreq       # TX freq
        Offset = rec.Offset
        Mode = rec.Mode
        Wide = rec.Wide
        Txtone = rec.Txtone
        Rxtone = rec.Rxtone
        Skip = 'S' if rec.Skip == 'Y' else ''

        # Derived values
        if recFilter.get('longName'): Name = rec.getLongName()
        #Offset = float(Txfreq) - float(Rxfreq)
        if Txfreq == Rxfreq: Duplex = ''
        elif Offset[0] == '-':
            Offset = Offset[1:]
            Duplex = '-'
        else: Duplex = '+'

        rToneFreq = '88.5'
        cToneFreq = '88.5'  # Only used on cross mode
        RxDtcsCode = '023'
        CrossMode = 'Tone->Tone'

        # There are nine possibilities for Txtone/Rxtone
        # (Actually ten because you could have Tone->Tone with
        # different frequencies)
        if not Txtone:
            if not Rxtone:
                ToneMode = ''
            elif Rxtone[0] == 'D':
                ToneMode = 'DTCS-R'
                RxDtcsCode = Rxtone[1:]
            else:
                rToneFreq = Rxtone
                ToneMode = 'TSQL-R'
        elif Txtone[0] == 'D':
            RxDtcsCode = Txtone[1:]
            if not Rxtone:
                ToneMode = 'DTCS'   # Chirp doesn't seem to support this case
            elif Rxtone[0] == 'D':
                ToneMode = 'DTCS'
            else:
                rToneFreq = Rxtone
                ToneMode = 'Cross'
                CrossMode = 'DTCS->Tone'
        else:
            rToneFreq = cToneFreq = Txtone
            if not Rxtone:
                ToneMode = 'Tone'   # Most common case
            elif Rxtone[0] == 'D':
                RxDtcsCode = Rxtone[1:]
                ToneMode = 'Cross'
                CrossMode = 'Tone->DTCS'
            else:
                if Rxtone == Txtone:
                    ToneMode = 'TSQL'
                else:
                    cToneFreq = Rxtone
                    ToneMode = 'Cross'

        Comment = rec.Comment
        DvMode = ''

        if Mode == 'FM':
            if Wide == 'N': Wide = 'NFM'
            else: Wide = 'FM'
        elif Mode == 'AM':
            if Wide == 'N': Wide = 'NAM'
            else: Wide = 'AM'
        elif Mode == 'DV':
            Wide = 'DV'
            DvMode = rToneFreq if rToneFreq else cToneFreq
            rToneFreq = cToneFreq = ''
        elif Mode == 'D':
            Wide = 'DIG'
        elif Mode in ValidModes:
            Wide = Mode
        else:
            Wide = 'DIG'
        # TODO: other modes? e.g. "MF" appears in the ACS database

        csvout.writerow([count, Name, Rxfreq, Duplex, Offset, ToneMode, rToneFreq, cToneFreq, RxDtcsCode, 'NN', RxDtcsCode, CrossMode, Wide, 5.00, Skip, '5.0W', Comment, '', '', '', DvMode])

