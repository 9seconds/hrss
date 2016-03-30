# -*- coding: utf-8 -*-


import concierge.core.lexer as lexer
import concierge.core.parser as parser
import concierge.core.processor as process


CONTENT = """\
Compression yes

Host q
    Port 22

    -Host e
        Protocol 2

        Host h
            HostName hew
            LocalForward 22 b:22
            LocalForward 23 b:23

    Host q
        HostName qqq
""".strip()


def test_generate():
    tokens = lexer.lex(CONTENT.split("\n"))
    tree = parser.parse(tokens)
    new_config = list(process.generate(tree))

    assert new_config == [
        "Host qeh",
        "    HostName hew",
        "    LocalForward 22 b:22",
        "    LocalForward 23 b:23",
        "    Port 22",
        "    Protocol 2",
        "",
        "Host qq",
        "    HostName qqq",
        "    Port 22",
        "",
        "Host q",
        "    Port 22",
        "",
        "Host *",
        "    Compression yes",
        ""]


def test_process():
    assert process.process(CONTENT) == """\
Host qeh
    HostName hew
    LocalForward 22 b:22
    LocalForward 23 b:23
    Port 22
    Protocol 2

Host qq
    HostName qqq
    Port 22

Host q
    Port 22

Host *
    Compression yes
"""
