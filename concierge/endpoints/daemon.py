#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""`concierge` daemon which converts ~/.conciergerc to ~/.ssh/config."""


import os
import os.path
import sys

import inotify_simple

import concierge.endpoints.common
import concierge.utils


LOG = concierge.utils.logger(__name__)


INOTIFY_FLAGS = (
    inotify_simple.flags.CREATE |
    inotify_simple.flags.MODIFY |
    inotify_simple.flags.MOVED_TO |
    inotify_simple.flags.EXCL_UNLINK
)


class Daemon(concierge.endpoints.common.App):

    @staticmethod
    def describe_events(events):
        descriptions = []

        for event in events:
            flags = inotify_simple.flags.from_mask(event.mask)
            flags = (str(flag) for flag in flags)

            descriptions.append(
                "Ev<(name={0}, flags={1})>".format(
                    event.name, ",".join(flags)))

        return descriptions

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

        script = concierge.endpoints.templates.make_systemd_script(
            self.templater_name)

        if not self.curlsh:
            script = [
                "Please execute following lines or compose script:",
                ""] + ["$ {0}".format(line) for line in script]

        print("\n".join(script))

    def track(self):
        with inotify_simple.INotify() as notify:
            self.add_watch(notify)
            self.manage_events(notify)

    def add_watch(self, notify):
        # there is a sad story on editors: some of them actually modify
        # files. But some write temporary files and rename. So it is
        # required to track directory where file is placed.
        path = os.path.abspath(self.source_path)
        path = os.path.dirname(path)
        notify.add_watch(path, INOTIFY_FLAGS)

    def manage_events(self, notify):
        filename = os.path.basename(self.source_path)

        while True:
            try:
                events = notify.read()
            except KeyboardInterrupt:
                return os.EX_OK
            else:
                LOG.debug("Caught %d events", len(events))

            events = self.filter_events(filename, events)
            descriptions = self.describe_events(events)
            LOG.debug("Got %d events after filtration: %s",
                      len(descriptions), descriptions)

            if events:
                self.output()

            LOG.info("Config was managed. Going to the next loop.")

    def filter_events(self, name, events):
        events = filter(lambda ev: ev.name == name, events)
        events = list(events)

        return events


main = concierge.endpoints.common.main(Daemon)


if __name__ == "__main__":
    sys.exit(main())
