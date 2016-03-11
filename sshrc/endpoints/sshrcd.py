#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""`sshrcd` daemon which converts ~/.sshrc to ~/.ssh/config."""


import os
import sys

import inotify_simple

import sshrc.endpoints.common
import sshrc.utils


LOG = sshrc.utils.logger(__name__)


class Daemon(sshrc.endpoints.common.App):

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
        super(Daemon, self).__init__(options)

        self.systemd = options.systemd
        self.curlsh = options.curlsh

    def do(self):
        if not self.systemd:
            return self.track()

        script = sshrc.endpoints.templates.make_systemd_script()

        if not self.curlsh:
            script = [
                "Please execute following lines or compose script:",
                ""] + ["$ {0}".format(line) for line in script]

        print("\n".join(script))

    def track(self):
        with inotify_simple.INotify() as notify:
            notify.add_watch(
                self.source_path,
                inotify_simple.flags.MODIFY | inotify_simple.flags.CREATE)

            while True:
                try:
                    events = notify.read()
                except KeyboardInterrupt:
                    return os.EX_OK

                LOG.debug("Got %d events. First is %s", len(events), events[0])

                try:
                    self.output()
                except Exception:
                    return os.EX_SOFTWARE

                LOG.info("Config was managed. Going to the next loop.")


main = sshrc.endpoints.common.main(Daemon)


if __name__ == "__main__":
    sys.exit(main())
