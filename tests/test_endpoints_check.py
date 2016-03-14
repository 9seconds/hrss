# -*- coding: utf-8 -*-


import os

import sshrc.endpoints.check


def test_mainfunc_ok(cliargs_default, templater, mock_get_content):
    mock_get_content.return_value = """\
Compression yes

Host q
    HostName e

    Host b
        HostName lalala
    """

    main = sshrc.endpoints.common.main(sshrc.endpoints.check.CheckApp)
    result = main()

    assert result is None or result == os.EX_OK


def test_mainfunc_exception(cliargs_default, templater, mock_get_content):
    mock_get_content.side_effect = Exception

    main = sshrc.endpoints.common.main(sshrc.endpoints.check.CheckApp)

    assert main() != os.EX_OK
