#!/usr/bin/env python3
# -*- coding: utf8 -*-


import csv
import decimal
import re
import sys

from channel import Channel
import common

ValidModes = ["WFM", "FM", "NFM", "AM", "NAM", "DV", "USB", "LSB", "CW", "RTTY",
                "DIG", "PKT", "NCW", "NCWR, CWR", "P25", "Auto", "RTTYR", "FSK",
                "FSKR", "DMR", "DN"]

power_re = re.compile('[\d.]+')

# Latest known schema:
# Note: the software that uses this pops up a warning about how this format is
# subject to change. This is likely not worth pursuing.
#  0  No.                               1
#  1  Channel Name                      V01PSR
#  2  Receive Frequency                 146.96000
#  3  Transmit Frequency                146.36000
#  4  Channel Type                      A-Analog
#  5  Transmit Power                    High
#  6  Band Width                        25K
#  7  CTCSS/DCS Decode                  Off
#  8  CTCSS/DCS Encode                  103.5
#  9  Contact                           Contact 1
# 10  Contact Call Type                 Group Call
# 11  Contact TG/DMR ID                 1
# 12  Radio ID                          WW7PSR
# 13  Busy Lock/TX Permit               Off
# 14  Squelch Mode                      Carrier
# 15  Optional Signal                   Off
# 16  DTMF ID                           1
# 17  2Tone ID                          1
# 18  5Tone ID                          1
# 19  PTT ID                            Off
# 20  Color Code                        1
# 21  Slot                              1
# 22  Scan List                         None
# 23  Receive Group List                None
# 24  PTT Prohibit                      Off
# 25  Reverse                           Off
# 26  Simplex TDMA                      Off
# 27  Slot Suit                         Off
# 28  AES Digital Encryption            Normal Encryption
# 29  Digital Encryption                Off
# 30  Call Confirmation                 Off
# 31  Talk Around(Simplex)              Off
# 32  Work Alone                        Off
# 33  Custom CTCSS                      1.0
# 34  2TONE Decode                      0
# 35  Ranging                           Off
# 36  Through Mode                      Off
# 37  APRS RX                           Off
# 38  Analog APRS PTT Mode              Off
# 39  Digital APRS PTT Mode             Off
# 40  APRS Report Type                  Off
# 41  Digital APRS Report Channel       1
# 42  Correct Frequency[Hz]             0
# 43  SMS Confirmation                  Off
# 44  Exclude channel from roaming      0
# 45  DMR MODE                          0
# 46  DataACK Disable                   0
# 47  R5toneBot                         0
# 48  R5ToneEot                         0
# 49  Auto Scan                         0
# 50  Ana Aprs Mute                     0
# 51  Send Talker Alias                 0

_header = [ "No.", "Channel Name", "Receive Frequency", "Transmit Frequency",
	      "Channel Type", "Transmit Power", "Band Width",
	      "CTCSS/DCS Decode", "CTCSS/DCS Encode", "Contact",
	      "Contact Call Type", "Contact TG/DMR ID", "Radio ID",
	      "Busy Lock/TX Permit", "Squelch Mode", "Optional Signal",
          "DTMF ID", "2Tone ID", "5Tone ID", "PTT ID",
	      "Color Code", "Slot", "Scan List", "Receive Group List",
          "PTT Prohibit", "Reverse", "Simplex TDMA",
	      "Slot Suit", "AES Digital Encryption", "Digital Encryption",
          "Call Confirmation", "Talk Around(Simplex)",
	      "Work Alone", "Custom CTCSS", "2TONE Decode", "Ranging",
	      "Through Mode", "APRS RX", "Analog APRS PTT Mode",
	      "Digital APRS PTT Mode", "APRS Report Type",
          "Digital APRS Report Channel", "Correct Frequency[Hz]",
          "SMS Confirmation", "Exclude channel from roaming",
          "DMR MODE", "DataACK Disable", "R5toneBot", "R5ToneEot",
	      "Auto Scan", "Ana Aprs Mute", "Send Talker Alias",]



class Anytone(Channel):
    """CSV files used by Anytone 878. May work with other radios."""

    # INPUT SECTION

    @staticmethod
    def probe(line: list):
        """Examine line to see if the input is in Anytone format. Return
        None if not. Anything else is true."""
        return len(line) >= 17 and \
            line[0] == "No." and \
            line[1] == "Channel Name" and \
            line[2] == "Receive Frequency" and \
            line[3] == "Transmit Frequency" and \
            line[4] == "Channel Type" and \
            line[5] == "Transmit Power" and \
            line[6] == "Band Width" and \
            line[7] == "CTCSS/DCS Decode" and \
            line[8] == "CTCSS/DCS Encode" and \
            line[12] == "Radio ID"


    def __init__(this, recFilter: dict, line):
        """Create an Anytone object from a list of csv values. Caller
        must have already vetted the input. The parse() function
        below can handle that."""

        # These are the inputs
        Chan = line[0]
        Name = line[1]
        Rxfreq = line[2]
        Txfreq = line[3]
        Type = line[4]      # "D-Digital" or "A-Analog"
        Power = line[5]    # E.g. "High"
        Bandwidth = line[6]    # e.g. 12.5K
        RxCode = line[7]    # "Tone Squelch": squelch tone (RX)
        TxCode = line[8]
        Contact = line[9]
        ID = line[12]
        Squelch = line[14]  # "Carrier", "CTCSS/DCS"

        # Map to values used in Channel object
        group = None

        if Squelch == "Carrier":
            RxCode = None

        if RxCode == 'Off': RxCode = None
        if TxCode == 'Off': TxCode = None

        if Type.startswith('A'):
            mode = 'AM' if float(Rxfreq) < 100.00 else 'FM'
        else:
            mode = 'DIG'    # TODO: determine what kind of digital

        wide = 'W' if Bandwidth == '25K' else 'N'

        super().__init__(recFilter, None, Chan, Txfreq, Rxfreq, None,
            Name, ID, TxCode, RxCode, mode, wide, Power)


    @staticmethod
    def parse(line, recFilter, cls=None):
        """Given a list, most likely provided by the csv module, return
        an RtSys object or None if the list can't be parsed."""
        if not cls: cls = Anytone
        if len(line) < 17: return None
        # line[2] is RX freq; if that's blank or not a number, then
        # the entire record is invalid
        if not line[2]:
            return None
        try:
            rxfreq = float(line[2])
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

#    Looks like we don't need this
#    @classmethod
#    def getWriter(cls, ifile):
#        return csv.writer(ifile, quoting=csv.QUOTE_ALL)

    @staticmethod
    def header(csvout: csv.writer, recFilter):
        """Write out the header line for the CSV file."""
        csvout.writerow(_header)

    @staticmethod
    def write(rec: Channel, csvout: csv.writer, count: int, recFilter):
        """Write out one record. There are 56 fields in this code
        plug, most of them not relevant or I don't understand them.
        Those will receive default values."""

        Chan = rec.Chan       # memory #, 0-based
        Name = rec.Name       # memory label
        Rxfreq = rec.Rxfreq
        Txfreq = rec.Txfreq
        Mode = rec.Mode
        Wide = rec.Wide
        Txtone = rec.Txtone
        Rxtone = rec.Rxtone
        Power = rec.Power
        Skip = 'S' if rec.Skip else ''

        # Derived values
        if recFilter.get('longName'): Name = rec.getLongName()
        Squelch = 'Carrier' if not Rxtone else 'CTCSS/DCS'
        if not Rxtone: Rxtone = 'Off'
        if not Txtone: Txtone = 'Off'
        Type = 'A-Analog' if Mode in ('AM','FM') else 'D-Digital'
        Bandwidth = '12.5K' if Wide == 'N' else '25K'
        ID = common.findCallsign(Name, rec.Comment)
        if not ID: ID = ''
        DMR_MODE = '1' if Mode == 'DMR' else '0'    # TODO: confirm this
        # TODO: can Anytone take numeric values? For now, anything over 2W is "High"
        if Power and Power[0].isdigit():
            mo = power_re.match(Power)
            if mo:
                p = float(mo.group())
                Power = 'High' if p >= 2.0 else 'Low'

        outrow = [count, Name, Rxfreq, Txfreq, Type, Power, Bandwidth,
            Rxtone, Txtone, '', '', '', ID, 'Off', Squelch,
            'Off', '1', '1', '1', 'Off',
            '1',      # TODO color code?
            '1', 'None', 'None', 'Off', 'Off', 'Off', 'Off',
            'Normal Encryption', 'Off', 'Off', 'Off', 'Off', '1.0',
            '0', 'Off', 'Off', 'Off', 'Off', 'Off', 'Off', '1', '0',
            'Off', '0', '0', '0', '0', '0', '0', '0', '0']
        csvout.writerow(outrow)

