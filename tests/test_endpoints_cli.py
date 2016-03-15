# -*- coding: utf-8 -*-


import sshrc
import sshrc.endpoints.cli as cli


def test_parser_default(cliargs_default, templater):
    parser = cli.create_parser()
    parsed = parser.parse_args()

    assert not parsed.debug
    assert not parsed.verbose
    assert parsed.source_path == sshrc.DEFAULT_SSHRC
    assert parsed.destination_path is None
    assert not parsed.boring_syntax
    assert parsed.add_header is None

    if templater.name:
        assert not parsed.no_templater
    else:
        assert not hasattr(parsed, "no_templater")
