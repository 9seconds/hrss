#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
`gen` command for sshrc.

sshrc-gen takes ~/.sshrc and generates
"""


import argparse
import os
import os.path
import sys

import sshrc


HOME_DIR = os.path.expanduser("~")
DEFAULT_SSHRC = os.path.join(HOME_DIR, ".sshrc")


def main():
    options = get_options()
    print(options)

    return os.EX_OK


def get_options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--source-path",
        help="Path of sshrc. Default is {}".format(DEFAULT_SSHRC),
        default=DEFAULT_SSHRC)
    parser.add_argument(
        "-d", "--destination-path",
        help=("Path of ssh config. If nothing is set, then prints to stdout."
              " Otherwise, stores into file."),
        default=None)
    parser.add_argument(
        "-b", "--boring-syntax",
        help="Use old boring syntax, described in 'man 5 ssh_config'.",
        action="store_true",
        default=False)

    if sshrc.EXTRAS["templater"]:
        parser.add_argument(
            "-t", "--no-templater",
            help="Do not use {} templater for SOURCE_PATH.".format(
                sshrc.EXTRAS["templater"]["name"]),
            action="store_false",
            default=False
        )

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
