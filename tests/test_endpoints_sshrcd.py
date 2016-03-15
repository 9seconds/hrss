# -*- coding: utf-8 -*-


import os

import inotify_simple
import pytest

import sshrc
import sshrc.endpoints.cli as cli
import sshrc.endpoints.sshrcd as sshrcd
import sshrc.utils


FLAGS = inotify_simple.flags.MODIFY | inotify_simple.flags.CREATE


def get_app(*params):
    parser = cli.create_parser()
    parser = sshrcd.Daemon.specify_parser(parser)
    parsed = parser.parse_args()

    for param in params:
        if param:
            setattr(parsed, param.strip("-"), True)

    app = sshrcd.Daemon(parsed)

    return app


def test_create_app(cliargs_default, cliparam_systemd, cliparam_curlsh):
    app = get_app(cliparam_systemd, cliparam_curlsh)

    assert app.systemd == bool(cliparam_systemd)
    assert app.curlsh == bool(cliparam_curlsh)


def test_print_help(capfd, cliargs_default, cliparam_curlsh):
    app = get_app("--systemd", cliparam_curlsh)

    app.do()

    out, err = capfd.readouterr()
    out = out.split("\n")

    if cliparam_curlsh:
        for line in out:
            assert not line.startswith("$")
        else:
            assert line.startswith(("$", "Please")) or not line

    assert not err


@pytest.mark.parametrize(
    "main_method", (
        True, False))
def test_work(mock_mainfunc, ptmpdir, main_method):
    _, _, _, inotifier = mock_mainfunc

    app = get_app()
    app.destination_path = ptmpdir.join("filename").strpath

    if main_method:
        app.do()
    else:
        app.track()

    inotifier.add_watch.assert_called_once_with(sshrc.DEFAULT_SSHRC, FLAGS)
    assert not inotifier.v

    with sshrc.utils.topen(ptmpdir.join("filename").strpath) as filefp:
        assert 1 == sum(int(line.strip() == "Host *") for line in filefp)


def test_mainfunc_ok(mock_mainfunc):
    result = sshrcd.main()

    assert result is None or result == os.EX_OK


def test_mainfunc_exception(mock_mainfunc):
    _, _, _, inotifier = mock_mainfunc
    inotifier.read.side_effect = Exception

    result = sshrcd.main()

    assert result != os.EX_OK
