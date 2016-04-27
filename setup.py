#!/usr/bin/env python
# -*- coding: utf-8 -*-


import setuptools

from setuptools.command.test import test as TestCommand  # NOQA
import sys


class Tox(TestCommand):

    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import shlex
        import tox

        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)


try:
    import multiprocessing
    assert multiprocessing
except ImportError:
    pass


setuptools.setup(
    setup_requires=["pbr>=1.8"],
    tests_require=["tox"],
    cmdclass={'test': Tox},
    pbr=True)
