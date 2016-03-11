# -*- coding: utf-8 -*-


import abc
import os

import sshrc.core.processor
import sshrc.endpoints.cli
import sshrc.endpoints.templates
import sshrc.utils


LOG = sshrc.utils.logger(__name__)


class App(metaclass=abc.ABCMeta):

    @classmethod
    def specify_parser(cls, parser):
        return parser

    def __init__(self, options):
        self.source_path = options.source_path
        self.destination_path = options.destination_path
        self.boring_syntax = options.boring_syntax
        self.add_header = options.add_header
        self.no_templater = getattr(options, "no_templater", False)

        if self.add_header is None:
            self.add_header = options.destination_path is not None

        sshrc.utils.configure_logging(
            options.debug,
            options.verbose,
            self.destination_path is None)

    @abc.abstractmethod
    def do(self):
        pass

    def output(self):
        content = self.get_new_config()

        if self.destination_path is None:
            print(content)
            return

        try:
            with sshrc.utils.topen(self.destination_path, True) as destfp:
                destfp.write(content)
        except Exception as exc:
            LOG.error("Cannot write to file %s: %s",
                      self.destination_path, exc)
            raise

    def get_new_config(self):
        content = self.fetch_content()

        if not self.no_templater:
            content = self.apply_template(content)
        else:
            LOG.info("No templating is used.")

        if not self.boring_syntax:
            content = self.process_syntax(content)
        else:
            LOG.info("Boring syntax was choosen, not processing is applied.")

        if self.add_header:
            content = self.attach_header(content)
        else:
            LOG.info("No need to attach header.")

        return content

    def fetch_content(self):
        LOG.info("Fetching content from %s", self.source_path)

        try:
            content = sshrc.utils.get_content(self.source_path)
        except Exception as exc:
            LOG.error("Cannot fetch content from %s: %s",
                      self.source_path, exc)
            raise

        LOG.info("Original content of %s:\n%s", self.source_path, content)

        return content

    def apply_template(self, content):
        LOG.info("Applying templater to content of %s.", self.source_path)

        try:
            content = sshrc.EXTRAS["templater"].render(content)
        except Exception as exc:
            LOG.error("Cannot process template (%s) in source file %s.",
                      self.source_path, sshrc.EXTRAS["templater"].name, exc)
            raise

        LOG.info("Templated content of %s:\n%s", self.source_path, content)

        return content

    def process_syntax(self, content):
        try:
            return sshrc.core.processor.process(content)
        except Exception as exc:
            LOG.error("Cannot parse content of source file %s: %s",
                      self.source_path, exc)

    def attach_header(self, content):
        header = sshrc.endpoints.templates.make_header(
            sshrc_file=self.source_path)
        content = header + content

        return content


class CheckApp(App):

    def do(self):
        return self.output()


def main(app_class):
    def main_func():
        parser = sshrc.endpoints.cli.create_parser()
        parser = app_class.specify_parser(parser)
        options = parser.parse_args()

        LOG.debug("Options: %s", options)

        app = app_class(options)

        try:
            return app.do()
        except Exception:
            return os.EX_SOFTWARE

    return main_func
