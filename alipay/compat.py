#!/usr/bin/env python
# coding: utf-8
"""
    compat.py
    ~~~~~~~~~~

"""
import sys

if str(sys.version[0]) == "3":
    from urllib.parse import quote_plus
    from urllib.request import urlopen
    from base64 import decodebytes, encodebytes
    def u(s):
        return s
    def b(s):
        return s.encode("utf-8")
else:
    from urllib import quote_plus
    from urllib2 import urlopen
    from base64 import decodestring as decodebytes
    from base64 import encodestring as encodebytes
    def u(s):
        return unicode(s.replace(r'\\', r'\\\\'), "unicode_escape")
    def b(s):
        return s
