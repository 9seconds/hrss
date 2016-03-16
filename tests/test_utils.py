# -*- coding: utf-8 -*-


import pytest

import concierge.utils as utils


def test_topen_write_read(ptmpdir):
    filename = ptmpdir.join("test")
    filename.write_text("TEST", "utf-8")

    with utils.topen(filename.strpath) as filefp:
        with pytest.raises(IOError):
            filefp.write("1")
        assert filefp.read() == "TEST"


def test_topen_write_ok(ptmpdir):
    filename = ptmpdir.join("test")
    filename.write_text("TEST", "utf-8")

    with utils.topen(filename.strpath, True) as filefp:
        filefp.write("1")

    with utils.topen(filename.strpath) as filefp:
        assert filefp.read() == "1"


@pytest.mark.parametrize(
    "content", (
        "1", "", "TEST"))
def test_get_content(ptmpdir, content):
    filename = ptmpdir.join("test")
    filename.write_text(content, "utf-8")

    assert utils.get_content(filename.strpath) == content


@pytest.mark.parametrize(
    "name, address", (
        ("linux", "/dev/log"),
        ("linux2", "/dev/log"),
        ("linux3", "/dev/log"),
        ("darwin", "/var/run/syslog"),
        ("windows", ("localhost", 514))))
def test_get_syslog_address(monkeypatch, name, address):
    monkeypatch.setattr("sys.platform", name)

    assert utils.get_syslog_address() == address


@pytest.mark.parametrize(
    "debug", (
        True, False))
@pytest.mark.parametrize(
    "verbose", (
        True, False))
@pytest.mark.parametrize(
    "stderr", (
        True, False))
@pytest.mark.no_mock_log_configuration
def test_configure_logging(debug, verbose, stderr):
    utils.configure_logging(debug, verbose, stderr)
