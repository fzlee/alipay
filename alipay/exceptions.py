#!/usr/bin/env python
# coding: utf-8
"""
    exceptions.py
    ~~~~~~~~~~

"""
import sys


class AliPayException(Exception):
    def __init__(self, code, message):
        self.__code = code
        self.__message = message


    if sys.version_info[0] >= 3:
        def to_unicode(self):
            return "AliPayException: code:{}, message:{}".format(self.__code, self.__message)

        def __str__(self):
            return self.to_unicode()

        def __repr__(self):
            return self.to_unicode()
    else:
        def to_unicode(self):
            return u"AliPayException: code:{}, message:{}".format(self.__code, self.__message.decode("utf8"))
        def __str__(self):
            return self.to_unicode().encode('utf8')

        def __repr__(self):
            return self.to_unicode().encode('utf8')


class AliPayValidationError(Exception):
    pass
