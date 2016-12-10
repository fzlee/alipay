#!/usr/bin/env python
# coding: utf-8
"""
    compat.py
    ~~~~~~~~~~

"""
import sys

if str(sys.version[0]) == "3":
    from urllib.parse import quote_plus
else:
    from urllib import quote_plus
