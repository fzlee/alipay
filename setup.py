#!/usr/bin/env python
# coding: utf-8
"""
    setup.py
    ~~~~~~~~~~

"""
from setuptools import setup
import unittest


def alipay_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests')
    return test_suite


setup(
    name="python-alipay-sdk",
    version="1.4.1",
    author="fzlee",
    author_email="fzleee@gmail.com",
    description="Python SDK for AliPay, RSA is the only sign method we support",
    license="BSD",
    keywords="python sdk alipay",
    url="https://github.com/fzlee/alipay",
    packages=['alipay'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    install_requires=["pycryptodome"],
    test_suite="setup.alipay_test_suite"
)
