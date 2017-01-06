#!/usr/bin/env python
# coding: utf-8
"""
    helper.py
    ~~~~~~~~~~

"""
import os


current_dir = os.path.dirname(os.path.realpath(__file__))


def get_ali_certs():
    path = os.path.join(current_dir, "certs/ali")
    return (
        os.path.join(path, "ali_private_key.pem"),
        os.path.join(path, "ali_public_key.pem")
    )


def get_app_certs():
    path = os.path.join(current_dir, "certs/app")
    return (
        os.path.join(path, "app_private_key.pem"),
        os.path.join(path, "app_public_key.pem")
    )


def get_web_certs():
    path = os.path.join(current_dir, "certs/web")
    return (
        os.path.join(path, "web_private_key.pem"),
        os.path.join(path, "web_public_key.pem")
    )
