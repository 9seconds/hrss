#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
`gen` command for sshrc.

sshrc-gen takes ~/.sshrc and generates
"""


import os
import sys

import sshrc.endpoints.cli
import sshrc.endpoints.sequence
import sshrc.utils


LOG = sshrc.utils.logger(__name__)


def main():
    options = sshrc.endpoints.cli.create_parser().parse_args()
    sshrc.utils.configure_logging(debug=options.debug)

    LOG.debug("Options are %s", options)

    try:
        sshrc.endpoints.sequence.process_sequence(options)
    except Exception:
        return os.EX_SOFTWARE

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
