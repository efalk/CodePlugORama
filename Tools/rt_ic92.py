#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Convert CSV file from ACS 217 spreadsheet to format RT Systems uses for FT-60

import csv

import channel
from rtsys import RtSys

class RtSysIc92(channel.Channel):
    """This is the "generic" RT Systems code. It generates output that
    both Yaesu FT-60 and QRZ-1 are happy with. Other radios might
    want something different; we may make subclasses for those
    radios at some later date."""
    # Output schema is based on the Yaesu FT-60, without bank select
    # TODO: RxTone, RxDCS. For now, always set to CSQ.

    @staticmethod
    def header(csvout: csv.writer, recFilter):
        """Write out the header line for the CSV file."""
        banks = recFilter.get('banks')
        if banks:
            Banks = [f"Bank {i}," for i in range(1,11)]
        else:
            Banks = []
        csvout.writerow(["Ch #", "", "RX Freq", "TX Freq", "offset freq", "offset dir", "Mode", "Name", "tone?", "tone CTCSS", "rxctss", "dcs", "dcs polar", "skip", "step", "bank", "bankch", "Comment", "Digital Squelch", "Digital Code", "Your Callsign", "Rpt-1 CallSign", "Rpt-2 CallSign"])

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

        derived = RtSys.Derived(rec, recFilter)
        Txtone = derived.Txtone
        Rxtone = derived.Rxtone
        Offset_s = derived.Offset
        OpMode = derived.OpMode
        ToneMode = derived.ToneMode

        CTCSS = derived.CTCSS
        if CTCSS: CTCSS += " Hz"
        DCS = derived.DCS

        # Ch #          channel, e.g. "V01" or "0"
        # ''            slot # in radio, e.g. 0
        # RX Freq       Downlink freq, e.g. 146.520 or 145.130
        # TX Freq       Uplink freq, e.g. 146.520 or 144.530
        # offset freq   downlink - uplink, e.g. "000 kHz" or "600 kHz"
        # offset dir    sign of offset, e.g. "Simplex", "Plus", "Minus"
        # Mode          e.g. "FM"
        # Name          e.g. "[ ]" or "V01 PSR"
        # tone?         "None", "Tone", etc.
        # tone CTCSS    e.g. "141.3 Hz"
        # rxctss        e.g. "88.5"
        # dcs           e.g. "23"
        # dcs polar     e.g. "Both N"
        # skip          e.g. "Off"
        # step          e.g. "5 kHz"
        # bank                                  
        # bankch                                        
        # Comment
        # Digital Squelch                                       
        # Digital Code                                  
        # Your Callsign                                 
        # Rpt-1 CallSign                                        
        # Rpt-2 CallSign                                        

        csvout.writerow([Chan, count, Rxfreq, Txfreq, Offset_s, OpMode, rec.Mode, Name, ToneMode,
            CTCSS, CTCSS, DCS, "Both N", "Off", "5 kHz", "","", Comment, "","","","",""])
