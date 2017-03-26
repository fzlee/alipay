#!/usr/bin/env python
# coding: utf-8
"""
    exceptions.py
    ~~~~~~~~~~

"""


class AliPayException(Exception):
    def __init__(self, code, message):
        self.__code = code
        self.__message = message

    def __repr__(self):
        return u"AliPayException<code:{}, message:{}>".format(self.__code, self.__message)

    def __unicode__(self):
        return u"AliPayException<code:{}, message:{}>".format(self.__code, self.__message)


class AliPayValidationError(Exception):
    pass
