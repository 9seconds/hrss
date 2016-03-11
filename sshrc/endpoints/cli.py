# -*- coding: utf-8 -*-


import argparse

import sshrc


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--debug",
        help="Run %(prog)s in debug mode.",
        action="store_true",
        default=False)
    parser.add_argument(
        "-v", "--verbose",
        help="Run %(prog)s in verbose mode.",
        action="store_true",
        default=False)
    parser.add_argument(
        "-s", "--source-path",
        help="Path of sshrc. Default is {}".format(sshrc.DEFAULT_SSHRC),
        default=sshrc.DEFAULT_SSHRC)
    parser.add_argument(
        "-o", "--destination-path",
        help=("Path of ssh config. If nothing is set, then prints to stdout. "
              "Otherwise, stores into file."),
        default=None)
    parser.add_argument(
        "-b", "--boring-syntax",
        help="Use old boring syntax, described in 'man 5 ssh_config'.",
        action="store_true",
        default=False)
    parser.add_argument(
        "-a", "--add-header",
        help=("Prints header at the top of the file. "
              "If nothing is set, then the rule is: if DESTINATION_PATH "
              "is file, then this option is true by default. If "
              "DESTINATION_PATH is stdout, then this option is set to false."),
        action="store_true",
        default=None)

    if sshrc.EXTRAS["templater"].name:
        parser.add_argument(
            "-t", "--no-templater",
            help="Do not use {} templater for SOURCE_PATH.".format(
                sshrc.EXTRAS["templater"].name),
            action="store_true",
            default=False)

    return parser
