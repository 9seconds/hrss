# -*- coding: utf-8 -*-


import sshrc.core.lexer as lexer

import pytest


@pytest.mark.parametrize("input_, output_", (
    ("", ""),
    ("       ", ""),
    ("       #", ""),
    ("#        ", ""),
    (" # dsfsdfsdf sdfsdfsd", ""),
    (" a", " a"),
    (" a# sdfsfdf", " a"),
    ("  a   # sdfsfsd x xxxxxxx # sdfsfd", "  a")
))
def test_clean_line(input_, output_):
    assert lexer.clean_line(input_) == output_
