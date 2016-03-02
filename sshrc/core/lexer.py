# -*- coding: utf-8 -*-


import collections
import re

import sshrc.core
import sshrc.core.exceptions as exceptions


Token = collections.namedtuple(
    "Token",
    ["indent", "option", "values", "original", "lineno"])

RE_QUOTED_SINGLE = r"'(?:[^'\\]|\\.)+'"
RE_QUOTED_DOUBLE = r'"(?:[^"\\]|\\.)+"'

RE_COMMENT = re.compile(r"#.*$")
RE_QUOTED = re.compile(
    r"(?:{0}|{1}|\S+)".format(RE_QUOTED_SINGLE, RE_QUOTED_DOUBLE))
RE_OPT_VALUE = re.compile(r"(\w+-?)\s+(.*?)\s*$")
RE_INDENT = re.compile(r"^\s+")


def lex(lines):
    tokens = []

    for index, line in enumerate(lines):
        processed_line = process_line(line)
        if processed_line:
            tokens.append(make_token(processed_line, line, index))

    tokens = verify_tokens(tokens)

    return tokens


def process_line(line):
    if not line:
        return ""

    line = reindent_line(line)
    line = clean_line(line)

    return line


def make_token(line, original_line, index):
    indentation, content = split_indent(line)

    matcher = RE_OPT_VALUE.match(content)
    if not matcher:
        raise exceptions.LexerIncorrectOptionValue(original_line, index)

    option, values = matcher.groups()
    values = RE_QUOTED.findall(values)

    indentation = len(indentation)
    if indentation % sshrc.core.INDENT_LENGTH:
        raise exceptions.LexerIncorrectIndentationLength(
            original_line, index, indentation)

    return Token(indentation // 4, option, values, original_line, index)


def verify_tokens(tokens):
    if tokens[0].indent:
        raise exceptions.LexerIncorrectFirstIndentationError(
            tokens[0].original, tokens[0].lineno)

    current_level = 0
    for token in tokens:
        if token.indent - current_level >= 2:
            raise exceptions.LexerIncorrectIndentationError(
                token.original, token.lineno)
        current_level = token.indent

    return tokens


def split_indent(line):
    indentation = get_indent(line)
    content = line[len(indentation):]

    return indentation, content


def get_indent(line):
    indentations = RE_INDENT.findall(line)

    if indentations:
        return indentations[0]

    return ""


def reindent_line(line):
    indentation, content = split_indent(line)
    if not indentation:
        return line

    indentation = indentation.replace("\t", "    ")
    line = indentation + content

    return line


def clean_line(line):
    line = RE_COMMENT.sub("", line)
    line = line.rstrip()

    return line
