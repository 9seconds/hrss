# -*- coding: utf-8 -*-


import pytest

import concierge.templater as templater


class Plugin(object):

    def __init__(self, tpl):
        self.templater = tpl

    @property
    def name(self):
        return self.templater.name

    def load(self):
        return self.templater


def create_templater(name_):
    class Fake(templater.Templater):
        name = name_

        def render(self, content):
            return self.name + " " + content

    return Fake


@pytest.fixture
def mock_plugins(request, monkeypatch):
    templaters = [
        Plugin(create_templater(name))
        for name in ("mako", "jinja2")]

    monkeypatch.setattr(
        "pkg_resources.iter_entry_points",
        lambda *args, **kwargs: templaters)

    return templaters


def test_all_templaters(mock_plugins):
    tpls = templater.all_templaters()

    assert len(tpls) == 3
    assert tpls["dummy"] is templater.Templater
    assert tpls["mako"]().render("q") == "mako q"
    assert tpls["jinja2"]().render("q") == "jinja2 q"


def test_resolve_templater_none(mock_plugins):
    tpl = templater.resolve_templater("dummy")

    assert isinstance(tpl, templater.Templater)
    assert tpl.name == "dummy"


def test_resolve_templater_default(mock_plugins):
    assert templater.resolve_templater(None).name == "mako"
    del mock_plugins[0]

    assert templater.resolve_templater(None).name == "jinja2"
    del mock_plugins[0]

    assert templater.resolve_templater(None).name == "dummy"


@pytest.mark.parametrize("code", ("mako", "jinja2", "dummy"))
def test_resolve_templater_known(mock_plugins, code):
    assert templater.resolve_templater(code).name == code


def test_render_dummy_templater():
    tpl = templater.Templater()

    assert tpl.render("lalala") == "lalala"
