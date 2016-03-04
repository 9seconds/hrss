# -*- coding: utf-8 -*-


import sshrc.core.generator
import sshrc.core.lexer
import sshrc.core.parser


def parse(content):
    content = content.split("\n")
    content = sshrc.core.lexer.lex(content)
    content = sshrc.core.parser.parse(content)
    content = sshrc.core.generator.generate(content)
    content = "\n".join(content)

    return content
