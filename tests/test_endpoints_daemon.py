# -*- coding: utf-8 -*-


import errno
import itertools
import os
import os.path

import inotify_simple
import pytest

import concierge
import concierge.endpoints.cli as cli
import concierge.endpoints.daemon as daemon
import concierge.utils


def get_app(*params):
    parser = cli.create_parser()
    parser = daemon.Daemon.specify_parser(parser)
    parsed = parser.parse_args()

    for param in params:
        if param:
            setattr(parsed, param.strip("-"), True)

    app = daemon.Daemon(parsed)

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

    inotifier.add_watch.assert_called_once_with(
        os.path.dirname(concierge.DEFAULT_RC), daemon.INOTIFY_FLAGS)
    assert not inotifier.v

    with concierge.utils.topen(ptmpdir.join("filename").strpath) as filefp:
        assert 1 == sum(int(line.strip() == "Host *") for line in filefp)


def test_track_no_our_events(no_sleep, mock_mainfunc, ptmpdir):
    _, _, _, inotifier = mock_mainfunc

    inotifier.v.clear()
    inotifier.v.extend([inotify_simple.Event(0, 0, 0, "Fake")] * 3)

    app = get_app()
    app.destination_path = ptmpdir.join("filename").strpath
    app.track()

    assert not os.path.exists(ptmpdir.join("filename").strpath)


def test_track_cannot_read(no_sleep, mock_mainfunc, ptmpdir):
    _, _, _, inotifier = mock_mainfunc

    def add_watch(*args, **kwargs):
        exc = IOError("Hello?")
        exc.errno = errno.EPERM

        raise exc

    inotifier.add_watch.side_effect = add_watch

    app = get_app()
    app.destination_path = ptmpdir.join("filename").strpath

    with pytest.raises(IOError):
        app.track()


@pytest.mark.parametrize(
    "ev1, ev2",
    list(itertools.permutations(inotify_simple.flags, 2)))
def test_event_names(ev1, ev2):
    events = [
        inotify_simple.Event(0, ev1, 0, "ev1"),
        inotify_simple.Event(0, ev2, 0, "ev2"),
        inotify_simple.Event(0, ev1 | ev2, 0, "ev1ev2")]

    descriptions = daemon.Daemon.describe_events(events)

    assert len(descriptions) == len(events)

    assert "ev1" in descriptions[0]
    assert str(ev1) in descriptions[0]

    assert "ev2" in descriptions[1]
    assert str(ev2) in descriptions[1]

    assert "ev1" in descriptions[2]
    assert "ev2" in descriptions[2]
    assert str(ev1) in descriptions[2]
    assert str(ev2) in descriptions[2]


def test_mainfunc_ok(mock_mainfunc):
    result = daemon.main()

    assert result is None or result == os.EX_OK


def test_mainfunc_exception(mock_mainfunc):
    _, _, _, inotifier = mock_mainfunc
    inotifier.read.side_effect = Exception

    result = daemon.main()

    assert result != os.EX_OK
