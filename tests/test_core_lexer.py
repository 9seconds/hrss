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


@pytest.mark.parametrize("input_, output_", (
    ("", ""),
    ("  ", "  "),
    ("    ", "    "),
    ("     ", "     "),
    ("\t    ", "        "),
    ("\t\t\t", 12 * " "),
    ("\t \t", "         "),
    ("\t\t\t ", "             "),
    (" \t\t\t ", "              ")
))
def test_reindent_line(input_, output_):
    assert lexer.reindent_line(input_) == output_
