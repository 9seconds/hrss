# -*- coding: utf-8 -*-


import sys

import pytest

import sshrc
import sshrc.endpoints.cli as cli


class FakeTemplater(object):

    def __init__(self):
        self.name = None
        self.render = None


@pytest.fixture
def sysargv(monkeypatch):
    argv = ["sshrcd"]

    monkeypatch.setattr(sys, "argv", argv)

    return argv


@pytest.fixture
def templater(monkeypatch):
    templater = FakeTemplater()
    templater.name = sshrc.EXTRAS["templater"].name
    templater.render = sshrc.EXTRAS["templater"].render

    monkeypatch.setitem(sshrc.EXTRAS, "templater", templater)

    return templater


@pytest.mark.parametrize(
    "with_templater", (
        True, False))
def test_parser_default(sysargv, templater, with_templater):
    if with_templater:
        templater.name = "Mako"
    else:
        templater.name = None

    parser = cli.create_parser()
    parsed = parser.parse_args()

    assert not parsed.debug
    assert not parsed.verbose
    assert parsed.source_path == sshrc.DEFAULT_SSHRC
    assert parsed.destination_path is None
    assert not parsed.boring_syntax
    assert parsed.add_header is None

    if with_templater:
        assert not parsed.no_templater
    else:
        assert not hasattr(parsed, "no_templater")


@pytest.mark.parametrize(
    "debug", (
        None, "-d", "--debug"))
@pytest.mark.parametrize(
    "verbose", (
        None, "-v", "--verbose"))
@pytest.mark.parametrize(
    "source_path", (
        None, "-s", "--source-path"))
@pytest.mark.parametrize(
    "destination_path", (
        None, "-o", "--destination-path"))
@pytest.mark.parametrize(
    "boring_syntax", (
        None, "-b", "--boring-syntax"))
@pytest.mark.parametrize(
    "add_header", (
        None, "-a", "--add-header"))
@pytest.mark.parametrize(
    "no_templater", (
        None, "-t", "--no-templater"))
@pytest.mark.parametrize(
    "with_templater", (
        True, False))
def test_parser_option_set(sysargv, templater, debug, verbose, source_path,
                           destination_path, boring_syntax, add_header,
                           no_templater, with_templater):
    if with_templater:
        templater.name = "Mako"
    else:
        templater.name = None

    for param in debug, verbose, boring_syntax, add_header:
        if param:
            sysargv.append(param)

    for param in source_path, destination_path:
        if param:
            sysargv.append(param)
            sysargv.append("/path/to")

    if with_templater and no_templater:
        sysargv.append(no_templater)

    parser = cli.create_parser()
    parsed = parser.parse_args()

    assert parsed.debug == bool(debug)
    assert parsed.verbose == bool(verbose)
    assert parsed.boring_syntax == bool(boring_syntax)

    if add_header is not None:
        assert parsed.add_header
    else:
        parsed.add_header is None

    if source_path:
        assert parsed.source_path == "/path/to"
    else:
        assert parsed.source_path == sshrc.DEFAULT_SSHRC

    if destination_path:
        assert parsed.destination_path == "/path/to"
    else:
        assert parsed.destination_path is None

    if not with_templater:
        assert not hasattr(parsed, "no_templater")
    else:
        assert parsed.no_templater == bool(no_templater)
