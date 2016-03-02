# -*- coding: utf-8 -*-


EXTRAS = {
    "templater": None
}


try:
    import mako.template
except ImportError:
    EXTRAS["templater"] = None
else:
    def templater(filename):
        template = mako.template.Template(filename=filename)
        rendered = template.render()

        return rendered

    EXTRAS["templater"] = {
        "name": "Mako",
        "func": templater
    }
