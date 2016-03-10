#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""`sshrcd` daemon which converts ~/.sshrc to ~/.ssh/config."""


import os
import sys

import inotify_simple

import sshrc.endpoints.cli
import sshrc.endpoints.sequence
import sshrc.endpoints.templates
import sshrc.utils


LOG = sshrc.utils.logger(__name__)


def main():
    options = sshrc.endpoints.cli.create_parser()
    options.add_argument(
        "--systemd",
        help="Print out instruction to set daemon with systemd.",
        action="store_true",
        default=False)
    options.add_argument(
        "--curlsh",
        help="I do not care and want simple install.",
        action="store_true",
        default=False)
    options = options.parse_args()

    sshrc.utils.configure_logging(debug=options.debug)

    LOG.debug("Options are %s", options)

    if options.systemd:
        print(sshrc.endpoints.templates.make_systemd_instruction())
        return os.EX_OK

    return track(options)


def track(options):
    with inotify_simple.INotify() as notify:
        notify.add_watch(
            options.source_path,
            inotify_simple.flags.MODIFY | inotify_simple.flags.CREATE)

        while True:
            try:
                events = notify.read()
            except KeyboardInterrupt:
                return os.EX_OK

            LOG.debug("Got %d events. First is %s", len(events), events[0])

            try:
                sshrc.endpoints.sequence.process_sequence(options)
            except Exception:
                return os.EX_SOFTWARE


if __name__ == "__main__":
    sys.exit(main())
