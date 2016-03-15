# -*- coding: utf-8 -*-


import os

import sshrc.endpoints.check


def test_mainfunc_ok(mock_mainfunc):
    main = sshrc.endpoints.common.main(sshrc.endpoints.check.CheckApp)
    result = main()

    assert result is None or result == os.EX_OK


def test_mainfunc_exception(mock_mainfunc):
    _, mock_get_content, _, _ = mock_mainfunc
    mock_get_content.side_effect = Exception

    main = sshrc.endpoints.common.main(sshrc.endpoints.check.CheckApp)

    assert main() != os.EX_OK
