#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""`concierge` daemon which converts ~/.conciergerc to ~/.ssh/config."""


import errno
import os
import sys
import time

import inotify_simple

import concierge.endpoints.common
import concierge.utils


LOG = concierge.utils.logger(__name__)


class Daemon(concierge.endpoints.common.App):

    INOTIFY_FLAGS = inotify_simple.flags.CREATE | inotify_simple.flags.MODIFY

    @classmethod
    def specify_parser(cls, parser):
        parser.add_argument(
            "--systemd",
            help="Printout instructions to set deamon with systemd.",
            action="store_true",
            default=False)
        parser.add_argument(
            "--curlsh",
            help="I do not care and want curl | sh.",
            action="store_true",
            default=False)

        return parser

    def __init__(self, options):
        super().__init__(options)

        self.systemd = options.systemd
        self.curlsh = options.curlsh

    def do(self):
        if not self.systemd:
            return self.track()

        script = concierge.endpoints.templates.make_systemd_script()

        if not self.curlsh:
            script = [
                "Please execute following lines or compose script:",
                ""] + ["$ {0}".format(line) for line in script]

        print("\n".join(script))

    def track(self):
        with inotify_simple.INotify() as notify:
            while True:
                try:
                    notify.add_watch(self.source_path, self.INOTIFY_FLAGS)
                except IOError as exc:
                    if exc.errno != errno.ENOENT:
                        raise

                    LOG.info("Config file is not created yet. Wait.")
                    time.sleep(1)
                else:
                    break

            while True:
                try:
                    events = notify.read()
                except KeyboardInterrupt:
                    return os.EX_OK

                LOG.debug("Got %d events. First is %s", len(events), events[0])

                self.output()

                LOG.info("Config was managed. Going to the next loop.")


main = concierge.endpoints.common.main(Daemon)


if __name__ == "__main__":
    sys.exit(main())
