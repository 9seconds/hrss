# -*- coding: utf-8 -*-


import sshrc
import sshrc.core.processor
import sshrc.endpoints.templates
import sshrc.utils


LOG = sshrc.utils.logger(__name__)


def process_sequence(options):
    sequence = (
        get_content,
        apply_template,
        process_syntax,
        add_header,
        print_content)

    content = options.source_path
    for func in sequence:
        content = func(options, content)


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
                  options.source_path, sshrc.EXTRAS["templater"].name, exc)
        raise

    LOG.debug("Processed content is \n%s", content)

    return content


def process_syntax(options, content):
    if options.boring_syntax:
        LOG.debug("Boring syntax is used.")
        return content

    try:
        return sshrc.core.processor.parse(content)
    except Exception as exc:
        LOG.exception("Cannot parse content in source file %s: %s",
                  options.source_path, exc)
        raise


def add_header(options, content):
    add_header = options.add_header
    if add_header is None:
        add_header = options.destination_path is not None

    if add_header:
        header = sshrc.endpoints.templates.make_header(
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
