# -*- coding: utf-8 -*-


import pytest

import concierge.endpoints.templates as templates
import concierge.templater


@pytest.mark.parametrize(
    "filename", (
        None, "filename"))
@pytest.mark.parametrize(
    "date", (
        None, "2016"))
def test_make_header(filename, date):
    kwargs = {}

    if filename is not None:
        kwargs["rc_file"] = filename
    if date is not None:
        kwargs["date"] = date

    header = templates.make_header(**kwargs)

    if filename is None:
        assert "???" in header
    else:
        assert filename in header

    if date is not None:
        assert date in header


def test_make_systemd_script():
    list(templates.make_systemd_script(concierge.templater.Templater))
