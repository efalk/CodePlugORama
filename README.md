
This is a tool that converts from one of several CSV database formats
to a format that can be read by Chirp, RT Systems, or Icom.

As of this writing, there are parsers for Chirp, RT Systems,
ARRL, New England Repeater Database, and a "generic" format.
See the [Accepted Formats](https://github.com/efalk/CodePlugORama/blob/main/Website/help.md#accepted-formats)
section of Website/help.md for a more complete list.

The subdirectories within this repository are as follows:

* Tools — Csv2Csv.py conversion tool plus plugins. Run the tool with --help for full instructions.
* Website — Source for the web site. You can customize this for your own purposes and then place on your own server
* Sources — Some source databases. Add your own and edit Website/config.txt to customize.

More to come. Contact me through github or at KK7NNS at gmail for more information.

Adding new formats for read and/or write is nearly trivial. Contact me if you have a new
format you want to add, or if you're good at coding feel free to write your own, using
chirp.py as a good starting point. Send the new plugin to me or fork this repository and
I'll probably add it right in.
