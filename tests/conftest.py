# -*- coding: utf-8 -*-


import os
import shutil
import unittest.mock

import pytest


def have_mocked(request, *mock_args, **mock_kwargs):
    if len(mock_args) > 1:
        method = unittest.mock.patch.object
    else:
        method = unittest.mock.patch

    patch = method(*mock_args, **mock_kwargs)
    mocked = patch.start()

    request.addfinalizer(patch.stop)

    return mocked


@pytest.fixture(scope="module", autouse=True)
def mock_logger(request):
    return have_mocked(request, "sshrc.utils.logger")


@pytest.fixture
def ptmpdir(request, tmpdir):
    for key in "TMP", "TEMPDIR", "TEMP":
        os.environ[key] = tmpdir.strpath

    request.addfinalizer(lambda: shutil.rmtree(tmpdir.strpath))

    return tmpdir
