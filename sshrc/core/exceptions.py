# -*- coding: utf-8 -*-


import sshrc.core


class SSHRCError(Exception):
    pass


class ReaderError(SSHRCError):
    pass


class LexerError(ReaderError):
    pass


class LexerIncorrectOptionValue(LexerError):

    MESSAGE = "Cannot find correct option/value pair on line {} '{}'"

    def __init__(self, line, lineno):
        super(LexerIncorrectOptionValue, self).__init__(
            self.MESSAGE.format(lineno, line))


class LexerIncorrectIndentationLength(LexerError):

    MESSAGE = ("Incorrect indentation on line {} '{}'"
               "({} spaces, has to be divisible by {})")

    def __init__(self, line, lineno, indentation_value):
        super(LexerIncorrectIndentationLength, self).__init__(
            self.MESSAGE.format(lineno, line,
                                indentation_value, sshrc.core.INDENT_LENGTH))


class LexerIncorrectFirstIndentationError(LexerError):

    MESSAGE = "Line {} '{}' has to have no indentation at all"

    def __init__(self, line, lineno):
        super(LexerIncorrectFirstIndentationError, self).__init__(
            self.MESSAGE.format(lineno, line))


class LexerIncorrectIndentationError(LexerError):

    MESSAGE = "Incorrect indentation on line {} '{}'"

    def __init__(self, line, lineno):
        super(LexerIncorrectIndentationError, self).__init__(
            self.MESSAGE.format(lineno, line))


class ParserError(ReaderError):
    pass


class ParserUnknownOption(ParserError):

    MESSAGE = "Unknown option {}"

    def __init__(self, option):
        super(ParserUnknownOption, self).__init__(self.MESSAGE.format(option))
