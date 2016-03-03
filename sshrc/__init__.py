# -*- coding: utf-8 -*-


import collections


Templater = collections.namedtuple("Templater", ["name", "render"])


EXTRAS = {
    "templater": Templater(None, lambda content: content)
}


try:
    import mako.template
except ImportError:
    pass
else:
    EXTRAS["templater"] = Templater(
        "Mako",
        lambda content: mako.template.Template(content).render_unicode())


if EXTRAS["templater"].name is None:
    try:
        import jinja2
    except ImportError:
        pass
    else:
        EXTRAS["templater"] = Templater(
            "Jinja2",
            lambda content: jinja2.Environment().from_string(content).render())
