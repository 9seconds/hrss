# -*- coding: utf-8 -*-


import os

import concierge.endpoints.check


def test_mainfunc_ok(mock_mainfunc):
    main = concierge.endpoints.common.main(concierge.endpoints.check.CheckApp)
    result = main()

    assert result is None or result == os.EX_OK


def test_mainfunc_exception(mock_mainfunc):
    _, mock_get_content, _, _ = mock_mainfunc
    mock_get_content.side_effect = Exception

    main = concierge.endpoints.common.main(concierge.endpoints.check.CheckApp)

    assert main() != os.EX_OK
