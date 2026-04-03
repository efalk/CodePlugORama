#!/usr/bin/env python3
# -*- coding: utf8 -*-

import csv
import errno
import getopt
import os
import signal
import string
import sys

import common

# These are used for both reading and writing, so import them
# now. Other plugins only imported on demand. This lets us leave
# out unneeded plugins for special purposes, e.g. the WWARA
# update script which only needs to read WWARA formatted files.
from chirp import Chirp
from rtsys import RtSys
from icom import Icom
from anytone import Anytone

# TODO: add filtering for Yaesu Fusion, NXDN, etc.

usage = f"""Convert CSV file from ACS 217 spreadsheet to formats radios use

  {sys.argv[0]} [options] inputfile.csv > outputfile.csv

  Options:
    Input filtering:
        -b <bands>      Any combination of the letters VULTDG, or "all"
                                V = VHF (2m band)
                                U = UHF (70cm band)
                                L = Low frequency (6m band and below)
                                T = 220 MHz band (1.25m band)
                                D = digital
                                G = GMRS
                            Default is all
        -m <modes>      Filter by mode. Any combination of the following:
                                A = AM
                                F = FM
                                L = lsb
                                U = usb
                                C = CW
                                D = DMR
                                S = DSTAR
                                V = Digital Voice (DV)
                                d = other digital
        -N              Use the 'U..N' entries (default is don't use)
        -R <regex>      Use regex to select entries, e.g. 'V' or 'U..N'

    Output format:
        --Chirp         Output for Chirp (default)
        --RtSys         Output for RT Systems
        --Icom          Output for Icom
        --Anytone       Output for Icom (experimental)
        --IC-92         Output for Icom-92, RT Systems
        -l              Long names, for radios that can take them
        -s <n>          Start numbering at <n>; default is 1
        --sparse        Leave gaps in record numbers where
                        there are gaps in the input
        --skip          Set the "scan skip" flag for all entries
        -B <bank,…>     Select banks for devices that use it (i.e. FT-60)
        -v              Increase verbosity

Generates CSV files to be used as code plugs.  These files
should work with any radio, but if not, please contact Ed Falk,
KK7NNS au gmail.com directly and we'll figure it out.

This program recognizes the input formats used by AARL, Seattle
ACS, Chirp, RT Systems, NERD, and Repeater Roundabout. Contact
the author if you have another format you'd like to add; it's not
hard.
"""

def main():
    global verbose
    ifile = sys.stdin

    csvout = csv.writer(sys.stdout)
    writer = Chirp

    start = 1
    recFilter = {}
    try:
        (optlist, args) = getopt.getopt(sys.argv[1:], 'hb:m:s:B:R:lv',
            ['help', 'Chirp', 'RtSys', 'Icom', 'Anytone', 'IC-92', 'sparse', 'skip'])
        for flag, value in optlist:
            if flag in ('-h', '--help'):
                print(usage)
                return 0
            elif flag == '-b':
                recFilter['bands'] = None if value == "all" else value
            elif flag == '-m':
                recFilter['modes'] = None if value == "all" else value
            elif flag == '-R':
                recFilter['regex'] = re.compile(value)
            elif flag == '-B':
                recFilter['banks'] = value
            elif flag == '--skip':
                recFilter['skip'] = True
            elif flag == '-s':
                start = getInt(value)
                if start is None:
                    print(f"-s '{value}' needs to be an integer", file=sys.stderr)
                    return 2
            elif flag == '-l':
                recFilter['longName'] = True
            elif flag == '--sparse':
                recFilter['sparse'] = True
            elif flag == '-v':
                verbose += 1
            elif flag == '--Chirp':
                writer = Chirp
            elif flag == '--RtSys':
                writer = RtSys
            elif flag == '--Icom':
                writer = Icom
            elif flag == '--Anytone':
                writer = Anytone
            elif flag == '--IC-92':
                from rt_ic92 import RtSysIc92
                writer = RtSysIc92
    except getopt.GetoptError as e:
        print(e, file=sys.stderr)
        print(usage, file=sys.stderr)
        return 2

    if args:
        ifile = open(args[0],'r')
    csvin = csv.reader(ifile)

    return common.process(csvin, None, csvout, writer, start, recFilter)


if __name__ == '__main__':
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)
  try:
    sys.exit(main())
  except KeyboardInterrupt as e:
    print(file=sys.stderr)
    sys.exit(1)
