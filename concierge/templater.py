# -*- coding: utf-8 -*-


import pkg_resources


TEMPLATER_NAMESPACE = "concierge.templater"


def all_templaters():
    templaters = {}

    for plugin in pkg_resources.iter_entry_points(group=TEMPLATER_NAMESPACE):
        templaters[plugin.name] = plugin.load()

    return templaters


def get_templater(code):
    if code is None:
        return Templater()

    return all_templaters()[code]



class Templater:

    code = None
    """Code for the templater to refer to."""

    name = "None"
    """The name of the templater to show."""

    def render(self, content):
        return content
