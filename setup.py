#!/usr/bin/env python
# coding: utf-8
"""
    setup.py
    ~~~~~~~~~~

"""
import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="python-alipay-sdk",
    version="0.1",
    author="fzlee",
    author_email="fzleee@gmail.com",
    description="Python SDK for alipay, RSA is the only sign method we support",
    license="BSD",
    keywords="python sdk alipay",
    url="https://github.com/fzlee/alipay",
    packages=['alipay'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
