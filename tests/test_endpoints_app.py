# -*- coding: utf-8 -*-


import os

import pytest

import concierge
import concierge.endpoints.cli as cli
import concierge.endpoints.common as common


def get_app():
    parser = cli.create_parser()
    parser = SimpleApp.specify_parser(parser)
    parsed = parser.parse_args()
    app = SimpleApp(parsed)

    return app


class SimpleApp(common.App):

    def do(self):
        return self.output()


def test_fetch_content_ok(cliargs_default, templater,
                          mock_get_content):
    mock_get_content.return_value = "Content"

    app = get_app()
    assert app.fetch_content() == mock_get_content.return_value


def test_fetch_content_exception(cliargs_default, templater,
                                 mock_get_content):
    mock_get_content.side_effect = Exception

    app = get_app()
    with pytest.raises(Exception):
        app.fetch_content()


def test_apply_content_ok(monkeypatch, cliargs_default, templater):
    monkeypatch.setattr(templater, "render", lambda param: param.upper())

    app = get_app()
    assert app.apply_template("hello") == "HELLO"


def test_apply_content_exception(monkeypatch, cliargs_default, templater):
    def badfunc(content):
        raise Exception

    monkeypatch.setattr(templater, "render", badfunc)

    app = get_app()
    with pytest.raises(Exception):
        app.apply_template("hello")


def test_process_syntax_ok(cliargs_default):
    content = """\
Host n
    ViaJumpHost x
    """

    app = get_app()
    assert app.process_syntax(content) == (
        "Host n\n"
        "    ProxyCommand ssh -W %h:%p x\n")


def test_process_syntax_exception(cliargs_default):
    app = get_app()

    with pytest.raises(Exception):
        app.process_syntax("WTF")


def test_attach_header(cliargs_default):
    app = get_app()
    assert app.attach_header("Content").startswith("#")


@pytest.mark.parametrize(
    "no_templater", (
        True, False))
@pytest.mark.parametrize(
    "boring_syntax", (
        True, False))
@pytest.mark.parametrize(
    "add_header", (
        True, False))
def test_get_new_config(monkeypatch, cliargs_default, templater,
                        mock_get_content, no_templater, boring_syntax,
                        add_header):
    monkeypatch.setattr(templater, "render", lambda param: param.upper())
    mock_get_content.return_value = """\
Compression yes

Host q
    HostName e

    Host b
        HostName lalala
    """

    app = get_app()
    app.no_templater = no_templater
    app.boring_syntax = boring_syntax
    app.add_header = add_header

    if not no_templater and not boring_syntax:
        with pytest.raises(Exception):
            app.get_new_config()
    else:
        result = app.get_new_config()

        if not no_templater:
            assert "COMPRESSION YES" in result
        else:
            assert "Compression yes" in result

        if boring_syntax:
            assert "Host qb" not in result
        else:
            assert "Host qb" in result

        if add_header:
            assert result.startswith("#")
        else:
            assert not result.startswith("#")


def test_output_stdout(capfd, monkeypatch, cliargs_default, templater,
                       mock_get_content):
    mock_get_content.return_value = """\
Compression yes

Host q
    HostName e

    Host b
        HostName lalala
    """

    app = get_app()
    app.destination_path = None

    app.output()

    out, err = capfd.readouterr()
    assert out == """\
Host qb
    HostName lalala

Host q
    HostName e

Host *
    Compression yes

"""
    assert not err


def test_output_file(cliargs_default, ptmpdir, templater, mock_get_content):
    mock_get_content.return_value = """\
Compression yes

Host q
    HostName e

    Host b
        HostName lalala
    """

    app = get_app()
    app.destination_path = ptmpdir.join("config").strpath

    app.output()

    with open(ptmpdir.join("config").strpath, "r") as filefp:
        assert filefp.read()


def test_output_file_exception(monkeypatch, cliargs_default, ptmpdir,
                               templater, mock_get_content):
    def write_fail(*args, **kwargs):
        raise Exception

    monkeypatch.setattr("concierge.utils.topen", write_fail)
    mock_get_content.return_value = """\
Compression yes

Host q
    HostName e

    Host b
        HostName lalala
    """

    app = get_app()
    app.destination_path = ptmpdir.join("config").strpath

    with pytest.raises(Exception):
        app.output()


@pytest.mark.longrun
def test_create_app(cliargs_fullset, templater, mock_log_configuration):
    _, options = cliargs_fullset

    parser = cli.create_parser()
    parsed = parser.parse_args()

    app = SimpleApp(parsed)

    assert app.boring_syntax == bool(options["boring_syntax"])

    if options["source_path"]:
        assert app.source_path == "/path/to"
    else:
        assert app.source_path == concierge.DEFAULT_RC

    if options["destination_path"]:
        assert app.destination_path == "/path/to"
    else:
        assert app.destination_path is None

    if options["add_header"] is not None:
        assert app.add_header
    else:
        assert app.add_header == (options["destination_path"] is not None)

    if templater.name:
        assert app.no_templater == bool(options["no_templater"])
    else:
        assert not app.no_templater

    assert mock_log_configuration.called


def test_mainfunc_ok(cliargs_default, templater, mock_get_content):
    mock_get_content.return_value = """\
Compression yes

Host q
    HostName e

    Host b
        HostName lalala
    """

    main = concierge.endpoints.common.main(SimpleApp)
    result = main()

    assert result is None or result == os.EX_OK


def test_mainfunc_exception(cliargs_default, templater, mock_get_content):
    mock_get_content.side_effect = Exception

    main = concierge.endpoints.common.main(SimpleApp)

    assert main() != os.EX_OK


def test_mainfunc_keyboardinterrupt(cliargs_default, templater,
                                    mock_get_content):
    mock_get_content.side_effect = KeyboardInterrupt

    main = concierge.endpoints.common.main(SimpleApp)
    result = main()

    assert result is None or result == os.EX_OK
