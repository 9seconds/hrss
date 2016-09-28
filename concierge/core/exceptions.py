# -*- coding: utf-8 -*-


import concierge.core


class ConciergeError(Exception):
    pass


class ReaderError(ConciergeError):
    pass


class LexerError(ValueError, ReaderError):
    pass


class LexerIncorrectOptionValue(LexerError):

    MESSAGE = "Cannot find correct option/value pair on line {0} '{1}'"

    def __init__(self, line, lineno):
        super().__init__(self.MESSAGE.format(lineno, line))


class LexerIncorrectIndentationLength(LexerError):

    MESSAGE = ("Incorrect indentation on line {0} '{1}'"
               "({2} spaces, has to be divisible by {3})")

    def __init__(self, line, lineno, indentation_value):
        super().__init__(
            self.MESSAGE.format(
                lineno, line,
                indentation_value,
                concierge.core.INDENT_LENGTH))


class LexerIncorrectFirstIndentationError(LexerError):

    MESSAGE = "Line {0} '{1}' has to have no indentation at all"

    def __init__(self, line, lineno):
        super().__init__(self.MESSAGE.format(lineno, line))


class LexerIncorrectIndentationError(LexerError):

    MESSAGE = "Incorrect indentation on line {0} '{1}'"

    def __init__(self, line, lineno):
        super().__init__(self.MESSAGE.format(lineno, line))


class ParserError(ValueError, ReaderError):
    pass


class ParserUnknownOption(ParserError):

    MESSAGE = "Unknown option {0}"

    def __init__(self, option):
        super().__init__(self.MESSAGE.format(option))
