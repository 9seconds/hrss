#!/usr/bin/env python
# -*- coding: utf-8 -*-


import setuptools

from setuptools.command.test import test as TestCommand  # NOQA
import sys

try:
    import multiprocessing
    assert multiprocessing
except ImportError:
    pass


setuptools.setup(
    setup_requires=["pbr>=1.8"],
    pbr=True)
