This subdirectory contains things that are needed at runtime by the tool
and is uploaded to the server.

Csv2Csv.py			Read CSV file, write programming plugins
channel.py			Generic channel base class
				Also reads its own simple format.
chirp.py			Read/write Chirp format
rtsys.py			Read/write RT systems format
icom.py				Write Icom format
ics217.py			Reads 217 spreadsheet csv
nerd.py				Reads New England Repeater Directory
rr.py				Reads Repeater Roundabout spreadsheet
wwara.py			Reads Western Washington Amateur Relay Association
common.py			Common code for converters


The Csv2Csv.py program reads a csv file in one of several formats
and writes out a csv file compatible with RT Systems, Chirp, or
Icom, respectively.

Run Csv2Csv --help for full command line options.

