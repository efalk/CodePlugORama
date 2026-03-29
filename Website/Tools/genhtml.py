#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""Read a config file and use it to process .ezt => .html"""

import csv
import re
import signal
import sys

from ezt import Template

def main():
    # Intended to be run from the Makefile with fixed arguments;
    # I'm not going to bother validating anything here.
    configfilename = sys.argv[1]
    inputfilename = sys.argv[2]
    configreader = csv.reader(open(configfilename, "r"), dialect=csv.excel_tab)

    sources = []
    for line in configreader:
        if line[0].startswith('#'): continue
        if line[0] == 'source':
            sources.append(line[1])

    ezt_data = {'sources': sources}

    template = Template(inputfilename)
    template.generate(sys.stdout, ezt_data)

    return 0


if __name__ == '__main__':
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)
  try:
    sys.exit(main())
  except KeyboardInterrupt as e:
    print(file=sys.stderr)
    sys.exit(1)
