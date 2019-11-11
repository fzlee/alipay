#!/usr/bin/env python
# coding: utf-8
"""
    helper.py
    ~~~~~~~~~~

"""
import os

current_dir = os.path.dirname(os.path.realpath(__file__))


def get_app_certs():
    path = os.path.join(current_dir, "certs/app")
    return (
        os.path.join(path, "app_private_key.pem"),
        os.path.join(path, "app_public_key.pem")
    )
