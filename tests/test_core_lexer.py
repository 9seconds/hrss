# -*- coding: utf-8 -*-


import sshrc.core.exceptions as exceptions
import sshrc.core.lexer as lexer

import pytest


def make_token(indent_lvl=0):
    token_name = "a{0}".format(0)

    return lexer.Token(indent_lvl, token_name, [token_name], token_name, 0)


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


@pytest.mark.parametrize("input_, output_", (
    ("", ""),
    ("a", "a"),
    (" a", " a"),
    ("    a", "    a"),
    ("\ta", "    a"),
    (" \ta", "     a"),
    (" \t a", "      a"),
    (" \t a ", "      a"),
    (" \t a #sdfds", "      a"),
    (" \t a #sdfds #", "      a"),
    ("a\t", "a"),
    ("a\t\r", "a"),
    ("a\r", "a"),
    ("a\n", "a")
))
def test_process_line(input_, output_):
    assert lexer.process_line(input_) == output_


@pytest.mark.parametrize("text, indent_len, option, values", (
    ("\ta 1", 1, "a", "1"),
    ("\ta 1 2", 1, "a", ["1", "2"]),
    ("\t\ta 1 2", 2, "a", ["1", "2"]),
    ("a 1 2 'cv'", 0, "a", ["1", "2", "'cv'"]),
    ("a 1 2 \"cv\"", 0, "a", ["1", "2", '"cv"']),
    ("a 1 2 \"cv\" 3", 0, "a", ["1", "2", '"cv"', "3"]),
    ("\ta=1", 1, "a", "1"),
    ("\ta =1 2", 1, "a", ["1", "2"]),
    ("\t\ta= 1 2", 2, "a", ["1", "2"]),
    ("a = 1 2 'cv'", 0, "a", ["1", "2", "'cv'"])
))
def test_make_token_ok(text, indent_len, option, values):
    processed_line = lexer.process_line(text)
    token = lexer.make_token(processed_line, text, 1)

    if not isinstance(values, (list, tuple)):
        values = [values]

    assert token.indent == indent_len
    assert token.option == option
    assert token.values == values
    assert token.original == text


@pytest.mark.parametrize("text", (
    "",
    "a",
    "a=",
    "a =",
    "a  ",
    "=",
    "==",
    " =asd"
))
def test_make_token_incorrect_value(text):
    with pytest.raises(exceptions.LexerIncorrectOptionValue):
        lexer.make_token(text, text, 1)


@pytest.mark.parametrize("offset", (
    1, 2, 3, 5, 6, 7
))
def test_make_token_incorrect_indentation(offset):
    text = " " * offset + "a = 1"

    with pytest.raises(exceptions.LexerIncorrectIndentationLength):
        lexer.make_token(text, text, 1)


def test_verify_tokens_empty():
    assert lexer.verify_tokens([]) == []


def test_verify_tokens_one_token():
    token = make_token(indent_lvl=0)

    assert lexer.verify_tokens([token]) == [token]


@pytest.mark.parametrize("level", list(range(1, 4)))
def test_verify_tokens_one_token_incorrect_level(level):
    token = make_token(indent_lvl=level)

    with pytest.raises(exceptions.LexerIncorrectFirstIndentationError):
        assert lexer.verify_tokens([token]) == [token]


def test_verify_tokens_ladder_level():
    tokens = [make_token(indent_lvl=level) for level in range(5)]

    assert lexer.verify_tokens(tokens) == tokens


@pytest.mark.parametrize("level", list(range(2, 7)))
def test_verify_tokens_big_level_gap(level):
    tokens = [make_token(indent_lvl=0), make_token(indent_lvl=level)]

    with pytest.raises(exceptions.LexerIncorrectIndentationError):
        assert lexer.verify_tokens(tokens) == tokens


@pytest.mark.parametrize("level", list(range(5)))
def test_verify_tokens_dedent(level):
    tokens = [make_token(indent_lvl=lvl) for lvl in range(5)]
    tokens.append(make_token(indent_lvl=level))

    assert lexer.verify_tokens(tokens) == tokens
