#!/usr/bin/env python3
# -*- coding: utf8 -*-


import csv
import decimal
import re
import sys

from channel import Channel
import common

power_re = re.compile('[\d.]+')

# CPS-generated output.
# Schema:
#   0 A     No. (channel number)
#   1 B     Channel Name (Channel 114)
#   2 C     Channel Type (analog/digital)
#   3 D     RX Frequency[MHz] (146.96, 152.1525)
#   4 E     TX Frequency[MHz] (ditto, don’t need trailing zeros)
#   5 F     Power (Low, Middle, High)
#   6 G     Bandwidth (12.5KHz, 25KHz)
#   7 H     Scan List (None, Scan List 1, Scan List 2)
#   8 I     TX Admit (Allow TX
#   9 J     Emergency System (None)
#  10 K     Squelch Level (0, 1, 2, 3, …)
#  11 L     APRS Report Type (blank)
#  12 M     Forbid TX (0, 1, ?)
#  13 N     APRS Receive (0)
#  14 O     Forbit Talkaround (0)
#  15 P     Auto Scan (0)
#  16 Q     Lone Work (0)
#  17 R     Emergency Indicator (0)
#  18 S     Emergency ACK (0)
#  19 S     Analog APRS PTT Mode (0)
#  20 U     Digital APRS PTT Mode (0)
#  21 V     TX Contact (Contacts 1)
#  22 W     RX Group List (None)
#  23 X     Color Code (0)
#  24 Y     Time Slot (Slot 1)
#  25 Z     Encryption (0)
#  26 AA    Encryption ID (None)
#  27 AB    APRS Report Channel (xxx 3 digits)
#  28 AC    Direct Dual Mode (0)
#  29 AD    Private Confirm (0)
#  30 AE    Short Data Confirm (0)
#  31 AF    DMR ID   (Radio 1)
#  32 AG    CTC/DCS Decode (None)
#  33 AH    CTC/DCS Encode (103.5)
#  34 AI    Scramble (None)
#  35 AJ    RX Squelch (Carrier/CTC)
#  36 AK    Signalling Type (None)
#  37 AL    PTT ID (OFF)
#  38 AM    VOX Function (0)
#  39 AN    PTT ID Display (0)



class DM32(Channel):
    """CSV files used by CPS/DM32. May work with other radios."""

    # INPUT SECTION

    # List of columns we're interested in, and reasonable defaults if not
    # found. "None" indicates that the column is mandatory.

    columns = {"No.":"",
        "Channel Name":"",
        "Channel Type":None,
        "RX Frequency[MHz]":None,
        "TX Frequency[MHz]":"",
        "Power":"Middle",
        "Band Width":"25KHz",
        "Scan List":"None",
        "TX Admit":"Allow TX",
        "Emergency System":"None",
        "Squelch Level":"3",
        "APRS Report Type":"Off",
        "Color Code":"1",
        "Encryption":"0",
        "DMR ID":"Radio 1",
        "CTC/DCS Decode":"None",
        "CTC/DCS Encode":"None",
        "RX Squelch Mode":""}

    def __init__(this, recFilter: dict, line):
        """Create a DM32 object from a list of csv values. Caller
        must have already vetted the input. The parse() function
        below can handle that."""

        Chan, Name, Type, Rxfreq, Txfreq, Power, Bandwidth, ColorCode, \
            DmrID, RxCode, TxCode, Squelch = this.fetchValues(line,
                "No.", "Channel Name", "Channel Type", "RX Frequency[MHz]",
                "TX Frequency[MHz]", "Power", "Band Width", "Color Code",
                "DMR ID", "CTC/DCS Decode", "CTC/DCS Encode", "RX Squelch Mode")

        # Map to values used in Channel object
        group = None

        if not Squelch or Squelch == "Carrier":
            RxCode = None

        if RxCode == 'None': RxCode = None
        if TxCode == 'None': TxCode = None

        if Type.startswith('A'):
            mode = 'AM' if float(Rxfreq) < 100.00 else 'FM'
        else:
            mode = 'DIG'    # TODO: determine what kind of digital

        wide = 'W' if Bandwidth.startswith('25K') else 'N'

        super().__init__(recFilter, None, Chan, Rxfreq, Txfreq, None,
            Name, DmrID, TxCode, RxCode, mode, wide, Power, '')

    @classmethod
    def parse(cls, line, recFilter):
        """Given a list, most likely provided by the csv module, return
        an RtSys object or None if the list can't be parsed."""
        # line[2] is RX freq; if that's blank or not a number, then
        # the entire record is invalid
        Freq = cls.fetchValue(line, "RX Frequency[MHz]")
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

#    Looks like we don't need this
#    @classmethod
#    def getWriter(cls, ifile):
#        return csv.writer(ifile, quoting=csv.QUOTE_ALL)

    @staticmethod
    def header(csvout: csv.writer, recFilter):
        """Write out the header line for the CSV file."""
        csvout.writerow(["No.", "Channel Name", "Channel Type",
            "RX Frequency[MHz]", "TX Frequency[MHz]", "Power",
            "Band Width", "Scan List", "TX Admit", "Emergency System",
            "Squelch Level", "APRS Report Type", "Forbid TX", "APRS Receive",
            "Forbid Talkaround", "Auto Scan", "Lone Work",
            "Emergency Indicator", "Emergency ACK", "Analog APRS PTT Mode",
            "Digital APRS PTT Mode", "TX Contact", "RX Group List",
            "Color Code", "Time Slot", "Encryption", "Encryption ID",
            "APRS Report Channel", "Direct Dual Mode", "Private Confirm",
            "Short Data Confirm", "DMR ID", "CTC/DCS Decode",
            "CTC/DCS Encode", "Scramble", "RX Squelch Mode",
            "Signaling Type", "PTT ID", "VOX Function", "PTT ID Display"])

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
        Skip = 'S' if rec.Skip == 'Y' else ''

        # Derived values
        if recFilter.get('longName'): Name = rec.getLongName()
        if not Rxtone: Squelch = 'Carrier'
        elif Rxtone.startswith('D'): Squelch = 'Carrier/CTC'    # TODO confirm this:
        else: Squelch = 'Carrier/CTC'
        if not Rxtone: Rxtone = 'None'
        if not Txtone: Txtone = 'None'
        Type = 'Analog' if Mode in ('AM','FM') else 'Digital'
        Bandwidth = '12.5K' if Wide == 'N' else '25K'
        ID = common.findCallsign(Name, rec.Comment)
        if not ID: ID = rec.Comment
        DMR_MODE = '1' if Mode == 'DMR' else '0'    # TODO: confirm this
        # TODO: can DM-32 take numeric values? For now, anything over 2W is "High"
        if Power and Power[0].isdigit():
            mo = power_re.match(Power)
            if mo:
                p = float(mo.group())
                if p >= 4.0: Power = 'High'
                elif p >= 2.0: Power = 'Middle'
                else: Power = 'Low'

        outrow = [count, Name, Type, Rxfreq, Txfreq, Power, Bandwidth,
            "None", "Allow TX", "None", "3", "Off", "0", "0", "0", "0",
            "0", "0", "0", "0", "0", "Contacts 1", "None", "0", "Slot 1",
            "0", "None", "1", "0", "0", "0", "Radio 1", Rxtone, Txtone,
            "None", Squelch, "None", "OFF", "0", "0"]
        csvout.writerow(outrow)
