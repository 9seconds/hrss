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
import sshrc.endpoints.common
import sshrc.utils


HOME_DIR = os.path.expanduser("~")
DEFAULT_SSHRC = os.path.join(HOME_DIR, ".sshrc")
LOG = sshrc.utils.logger(__name__)


def main():
    options = get_options()
    sshrc.utils.configure_logging(debug=options.debug)

    LOG.debug("Options are %s", options)

    sequence = (
        get_content,
        apply_template,
        process_syntax,
        add_header,
        print_content
    )

    content = options.source_path
    try:
        for func in sequence:
            content = func(options, content)
    except Exception:
        return os.EX_SOFTWARE

    return os.EX_OK


def get_content(options, filename):
    try:
        content = sshrc.utils.get_content(options.source_path)
    except Exception as exc:
        LOG.error("Cannot parse source file %s: %s", options.source_path, exc)
        raise

    LOG.debug("Original content is \n%s", content)

    return content


def apply_template(options, content):
    if options.no_templater:
        LOG.debug("No templating is used.")
        return content

    try:
        content = sshrc.EXTRAS["templater"].render(content)
    except Exception as exc:
        LOG.error("Cannot process template in source file %s. "
                  "Templater is %s: %s",
                  options.source_path, sshrc.EXTRAS["templater"].name,
                  exc)
        raise

    LOG.debug("Processed content is \n%s", content)

    return content


def process_syntax(options, content):
    if options.boring_syntax:
        LOG.debug("Boring syntax is used.")
        return content

    try:
        return sshrc.endpoints.common.parse(content)
    except Exception as exc:
        LOG.error("Cannot parse content in source file %s: %s",
                  options.source_path, exc)
        raise


def add_header(options, content):
    add_header = options.add_header
    if add_header is None:
        add_header = options.destination_path is not None

    if add_header:
        header = sshrc.endpoints.common.make_header(
            sshrc_file=options.source_path)
        content = header + content

    return content


def print_content(options, content):
    if options.destination_path is None:
        print(content)
        return content

    try:
        with sshrc.utils.topen(options.destination_path, True) as destfp:
            destfp.write(content)
    except Exception as exc:
        LOG.error("Cannot write to file %s: %s", options.destination_path, exc)
        raise
    else:
        return content


def get_options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--debug",
        help="Run %(prog)s in debug mode.",
        action="store_true",
        default=False)
    parser.add_argument(
        "-s", "--source-path",
        help="Path of sshrc. Default is {}".format(DEFAULT_SSHRC),
        default=DEFAULT_SSHRC)
    parser.add_argument(
        "-o", "--destination-path",
        help=("Path of ssh config. If nothing is set, then prints to stdout."
              " Otherwise, stores into file."),
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

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
