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


def test_parser_option_fullset(cliargs_fullset, templater):
    _, options = cliargs_fullset

    parser = cli.create_parser()
    parsed = parser.parse_args()

    assert parsed.debug == bool(options["debug"])
    assert parsed.verbose == bool(options["verbose"])
    assert parsed.boring_syntax == bool(options["boring_syntax"])

    if options["add_header"] is not None:
        assert parsed.add_header
    else:
        parsed.add_header is None

    if options["source_path"]:
        assert parsed.source_path == "/path/to"
    else:
        assert parsed.source_path == sshrc.DEFAULT_SSHRC

    if options["destination_path"]:
        assert parsed.destination_path == "/path/to"
    else:
        assert parsed.destination_path is None

    if templater.name:
        assert parsed.no_templater == bool(options["no_templater"])
    else:
        assert not hasattr(parsed, "no_templater")
