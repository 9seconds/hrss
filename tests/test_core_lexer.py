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


@pytest.mark.parametrize("indent_", (
    "",
    " ",
    "    ",
    "\t",
    "\t\t",
    "\t \t",
    "\t\t ",
    " \t\t"
))
@pytest.mark.parametrize("content_", (
    "",
    "a"
))
def test_get_split_indent(indent_, content_):
    text = indent_ + content_

    assert lexer.get_indent(text) == indent_
    assert lexer.split_indent(text) == (indent_, content_)


@pytest.mark.parametrize("text", (
    "#",
    "#   ",
    "# sdfsdf #",
    "## sdfsfdf",
    "# #sdf #    #"
))
def test_regexp_comment_ok(text):
    assert lexer.RE_COMMENT.match(text)


@pytest.mark.parametrize("text", (
    "",
    "sdfdsf",
    "sdfsdf#",
    "dzfsdfsdf#sdfsdf",
    "sdf #",
    "  #"
))
def test_regexp_comment_nok(text):
    assert not lexer.RE_COMMENT.match(text)


@pytest.mark.parametrize("text", (
    " ",
    "    ",
    "     ",
    "\t"
))
def test_regexp_indent_ok(text):
    assert lexer.RE_INDENT.match(text)


@pytest.mark.parametrize("text", (
    "",
    "sdf",
    "sdfs ",
    "sdfsfd dsfx"
))
def test_regexp_indent_nok(text):
    assert not lexer.RE_INDENT.match(text)


@pytest.mark.parametrize("text", (
    "''",
    "'sdf'",
    "'sdfsf\'sfdsf'",
    "'sdfsd\'\'sdfsf\'sdf\'sdfxx'"
    '""',
    '"sdf"',
    '"sdfsf\"fdsf"',
    '"sdfsd\"\"sdfsf\"sdf\"sdfx"',
    "'\"'",
    "'sdfsdf' \"sdfsdf\"",
    "'sdfx\"sdx' 'sdfdf\"' \"sdfx'sdfffffdf\" \"sdfsdf'sdxx'ds\""
))
def test_regexp_quoted_ok(text):
    assert lexer.RE_QUOTED.match(text)


@pytest.mark.parametrize("text", (
    "'xx\"",
    "\"sdfk'"
))
def test_regexp_quoted_nok(text):
    assert not lexer.RE_QUOTED.match(text)


@pytest.mark.parametrize("text", (
    "hhh x",
    "hhh   x",
    "hhh \tx",
    "hhh=x",
    "hhh =sdfsf",
    "sdf= sdfx",
    "sdf =  sdf",
    "hhh     x",
    "sdfsf-  x"
))
def test_regexp_optvalue_ok(text):
    assert lexer.RE_OPT_VALUE.match(text)


@pytest.mark.parametrize("text", (
    "",
    "hhx",
    "sdfsf ",
    " sdfsfdf",
    "sdfsf =",
    "sdfsf= ",
    "sdfsdf = ",
    " "
))
def test_regexp_optvalue_nok(text):
    assert not lexer.RE_OPT_VALUE.match(text)
