# -*- coding: utf-8 -*-


import collections
import re

import concierge.core
import concierge.core.exceptions as exceptions
import concierge.utils


Token = collections.namedtuple(
    "Token",
    ["indent", "option", "values", "original", "lineno"])

RE_QUOTED_SINGLE = r"'(?:[^'\\]|\\.)*'"
RE_QUOTED_DOUBLE = r'"(?:[^"\\]|\\.)*"'
RE_UNQUOTED = r"(?:[^'\"\\ \r\n\t]|\\.)+"

RE_COMMENT = re.compile(r"#.*$")
RE_QUOTED = re.compile(
    r"(?:{0}|{1}|{2})".format(RE_QUOTED_SINGLE, RE_QUOTED_DOUBLE, RE_UNQUOTED))
RE_OPT_VALUE = re.compile(r"(-?\w+-?)\b\s*=?\s*([^= \r\n\t].*?)$")
RE_INDENT = re.compile(r"^\s+")

LOG = concierge.utils.logger(__name__)


def lex(lines):
    tokens = []

    LOG.info("Start lexing of %d lines.", len(lines))

    for index, line in enumerate(lines, start=1):
        LOG.debug("Process line %d '%s'.", index, line)
        processed_line = process_line(line)
        if processed_line:
            token = make_token(processed_line, line, index)
            LOG.debug("Processed line %d to token %s", index, token)
            tokens.append(token)
        else:
            LOG.debug("Processed line %d is empty, skip.", index)

    tokens = verify_tokens(tokens)

    LOG.info("Lexing is finished. Got %d tokens.", len(tokens))

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
    if indentation % concierge.core.INDENT_LENGTH:
        raise exceptions.LexerIncorrectIndentationLength(
            original_line, index, indentation)

    return Token(indentation // 4, option, values, original_line, index)


def verify_tokens(tokens):
    LOG.info("Verify %d tokens.", len(tokens))

    if not tokens:
        return []

    if tokens[0].indent:
        raise exceptions.LexerIncorrectFirstIndentationError(
            tokens[0].original, tokens[0].lineno)

    current_level = 0
    for token in tokens:
        if token.indent - current_level >= 2:
            LOG.warning("Token %s has incorrect indentation. "
                        "Previous level is %d.", token, current_level)
            raise exceptions.LexerIncorrectIndentationError(
                token.original, token.lineno)
        current_level = token.indent

    LOG.info("All %d tokens are fine.", len(tokens))

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
