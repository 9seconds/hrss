# -*- coding: utf-8 -*-


import pkg_resources


TEMPLATER_NAMESPACE = "concierge.templater"
DEFAULT_RESOLVE_SEQ = "mako", "jinja"


def all_templaters():
    templaters = {"dummy": Templater}

    for plugin in pkg_resources.iter_entry_points(group=TEMPLATER_NAMESPACE):
        templaters[plugin.name] = plugin.load()

    return templaters


def resolve_templater(choose=None):
    templaters = all_templaters()
    found = None

    if choose:
        found = templaters[choose]
    else:
        for code in DEFAULT_RESOLVE_SEQ:
            if code in templaters:
                found = templaters[code]
                break
        else:
            found = Templater

    return found()


class Templater(object):

    name = "dummy"
    """The name of the templater to show."""

    def render(self, content):
        return content
