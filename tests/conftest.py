# -*- coding: utf-8 -*-


import os
import shutil
import sys
import unittest.mock

import sshrc

import pytest


class FakeTemplater(object):

    @staticmethod
    def render(content):
        return content

    def __init__(self, name):
        self.name = name


def have_mocked(request, *mock_args, **mock_kwargs):
    if len(mock_args) > 1:
        method = unittest.mock.patch.object
    else:
        method = unittest.mock.patch

    patch = method(*mock_args, **mock_kwargs)
    mocked = patch.start()

    request.addfinalizer(patch.stop)

    return mocked


@pytest.fixture(scope="session", autouse=True)
def mock_logger(request):
    return have_mocked(request, "sshrc.utils.logger")


@pytest.fixture(autouse=True)
def mock_log_configuration(request):
    marker = request.node.get_marker("no_mock_log_configuration")

    if not marker:
        return have_mocked(request, "sshrc.utils.configure_logging")


@pytest.fixture
def ptmpdir(request, tmpdir):
    for key in "TMP", "TEMPDIR", "TEMP":
        os.environ[key] = tmpdir.strpath

    request.addfinalizer(lambda: shutil.rmtree(tmpdir.strpath))

    return tmpdir


@pytest.fixture
def sysargv(monkeypatch):
    argv = ["sshrcd"]

    monkeypatch.setattr(sys, "argv", argv)

    return argv


@pytest.fixture(params=(None, "Fake"))
def templater(request, monkeypatch):
    templater = FakeTemplater(request.param)

    monkeypatch.setitem(sshrc.EXTRAS, "templater", templater)

    return templater


@pytest.fixture(params=(None, "-d", "--debug"))
def cliparam_debug(request):
    return request.param


@pytest.fixture(params=(None, "-v", "--verbose"))
def cliparam_verbose(request):
    return request.param


@pytest.fixture(params=(None, "-s", "--source-path"))
def cliparam_source_path(request):
    return request.param


@pytest.fixture(params=(None, "-o", "--destination-path"))
def cliparam_destination_path(request):
    return request.param


@pytest.fixture(params=(None, "-b", "--boring-syntax"))
def cliparam_boring_syntax(request):
    return request.param


@pytest.fixture(params=(None, "-a", "--add-header"))
def cliparam_add_header(request):
    return request.param


@pytest.fixture(params=(None, "-t", "--no-templater"))
def cliparam_no_templater(request):
    return request.param


@pytest.fixture
def cliargs_default(sysargv):
    return sysargv


@pytest.fixture
def cliargs_fullset(sysargv, templater, cliparam_debug, cliparam_verbose,
                    cliparam_source_path, cliparam_destination_path,
                    cliparam_boring_syntax, cliparam_add_header,
                    cliparam_no_templater):
    options = {
        "debug": cliparam_debug,
        "verbose": cliparam_verbose,
        "source_path": cliparam_source_path,
        "destination_path": cliparam_destination_path,
        "add_header": cliparam_add_header,
        "boring_syntax": cliparam_boring_syntax,
        "no_templater": cliparam_no_templater}
    bool_params = (
        cliparam_debug, cliparam_verbose, cliparam_boring_syntax,
        cliparam_add_header)
    value_params = (
        cliparam_source_path, cliparam_destination_path)

    for param in bool_params:
        if param:
            sysargv.append(param)

    for param in value_params:
        if param:
            sysargv.append(param)
            sysargv.append("/path/to")

    if templater.name and cliparam_no_templater:
        sysargv.append(cliparam_no_templater)

    return sysargv, options
