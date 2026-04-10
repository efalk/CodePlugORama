#!/usr/bin/env python3
# -*- coding: utf8 -*-

import signal
import sys

from channel import Channel
import common

def main():
    readers = common._readerList()
    test_set = []
    for reader in readers:
        if reader is Channel or reader.columns is not Channel.columns:
            l = reader.columns.items()
            l = set([item[0] for item in l if item[1] is None])
            test_set.append((reader, l))
    print(f"Testing these readers: {[item for item,s in test_set]}")
    for reader1,s1 in test_set:
        for reader2,s2 in test_set:
            if reader1 is not reader2 and s1.issubset(s2):
                print(f"BEWARE: {reader1} is a subset of {reader2}")



if __name__ == '__main__':
  signal.signal(signal.SIGPIPE, signal.SIG_DFL)
  try:
    sys.exit(main())
  except KeyboardInterrupt as e:
    print(file=sys.stderr)
    sys.exit(1)
