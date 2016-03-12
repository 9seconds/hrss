# -*- coding: utf-8 -*-


import pytest

import sshrc
import sshrc.endpoints.cli as cli
import sshrc.endpoints.common as common


class SimpleApp(common.App):

    def do(self):
        return self.output()


@pytest.mark.longtest
def test_create_app(cliargs_fullset, templater):
    _, options = cliargs_fullset

    parser = cli.create_parser()
    parsed = parser.parse_args()

    app = SimpleApp(parsed)

    assert app.boring_syntax == bool(options["boring_syntax"])

    if options["source_path"]:
        assert app.source_path == "/path/to"
    else:
        assert app.source_path == sshrc.DEFAULT_SSHRC

    if options["destination_path"]:
        assert app.destination_path == "/path/to"
    else:
        assert app.destination_path is None

    if options["add_header"] is not None:
        assert app.add_header
    else:
        assert app.add_header == (options["destination_path"] is not None)

    if templater.name:
        assert app.no_templater == bool(options["no_templater"])
    else:
        assert not app.no_templater
