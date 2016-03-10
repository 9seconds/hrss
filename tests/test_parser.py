# -*- coding: utf-8 -*-


import pytest

import sshrc.core.lexer as lexer
import sshrc.core.parser as parser


def is_trackable_host():
    assert parser.is_trackable_host("Host")
    assert not parser.is_trackable_host("Host-")


def get_host_tokens():
    text = """\
Host name
    Option 1

    Host 2
        Host 3
            Hello yes

    q 5
    """.strip()

    tokens = lexer.lex(text.split("\n"))
    tokens = tokens[1:]

    leveled_tokens = parser.get_host_tokens(1, tokens)
    assert len(leveled_tokens) == 4
    assert leveled_tokens[-1].option == "Hello"


def test_parse_options_big_config_with_star_host():
    text = """\
# Okay, rather big config but let's try to cover all cases here.
# Basically, I've been trying to split it to different test cases but it
# was really hard to maintain those tests. So there.

Compression yes
CompressionLevel 5

Host m
    Port 22

    Host e v
        User root
        HostName env10

        Host WWW
            TCPKeepAlive 5

    Host q
        Protocol 2

    -Host x
        SendEnv 12

        Host qex
            Port 35
            ViaJumpHost env312

Host *
    CompressionLevel 6

    """.strip()

    tokens = lexer.lex(text.split("\n"))
    tree = parser.parse(tokens)

    assert tree.name == ""
    assert tree.parent is None
    assert len(tree.hosts) == 2

    star_host = tree.hosts[0]
    assert star_host.trackable
    assert star_host.fullname == "*"
    assert star_host.options == {"Compression": "yes",
                                 "CompressionLevel": "6"}

    m_host = tree.hosts[1]
    assert m_host.trackable
    assert m_host.fullname == "m"
    assert m_host.options == {"Port": "22"}
    assert len(m_host.hosts) == 4

    me_host = m_host.hosts[0]
    assert me_host.trackable
    assert me_host.fullname == "me"
    assert me_host.options == {"Port": "22", "HostName": "env10",
                               "User": "root"}
    assert len(me_host.hosts) == 1

    meWWW_host = me_host.hosts[0]
    assert meWWW_host.trackable
    assert meWWW_host.fullname == "meWWW"
    assert meWWW_host.options == {"Port": "22", "TCPKeepAlive": "5",
                                  "HostName": "env10", "User": "root"}
    assert meWWW_host.hosts == []

    mq_host = m_host.hosts[1]
    assert mq_host.trackable
    assert mq_host.fullname == "mq"
    assert mq_host.options == {"Protocol": "2", "Port": "22"}
    assert mq_host.hosts == []

    mv_host = m_host.hosts[2]
    assert mv_host.trackable
    assert mv_host.fullname == "mv"
    assert mv_host.options == {"Port": "22", "HostName": "env10",
                               "User": "root"}
    assert len(mv_host.hosts) == 1

    mvWWW_host = mv_host.hosts[0]
    assert mvWWW_host.trackable
    assert mvWWW_host.fullname == "mvWWW"
    assert mvWWW_host.options == {"Port": "22", "TCPKeepAlive": "5",
                                  "HostName": "env10", "User": "root"}
    assert mvWWW_host.hosts == []

    mx_host = m_host.hosts[3]
    assert not mx_host.trackable
    assert mx_host.fullname == "mx"
    assert mx_host.options == {"SendEnv": "12", "Port": "22"}
    assert len(mx_host.hosts) == 1

    mxqex_host = mx_host.hosts[0]
    assert mxqex_host.trackable
    assert mxqex_host.fullname == "mxqex"
    assert mxqex_host.options == {"SendEnv": "12", "Port": "35", "ProxyCommand": "ssh -W %h:%p env312"}
    assert mxqex_host.hosts == []
