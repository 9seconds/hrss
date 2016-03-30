# -*- coding: utf-8 -*-


import pytest

import concierge.core.exceptions as exceptions
import concierge.core.lexer as lexer
import concierge.core.parser as parser


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
    assert star_host.options == {"Compression": ["yes"],
                                 "CompressionLevel": ["6"]}

    m_host = tree.hosts[1]
    assert m_host.trackable
    assert m_host.fullname == "m"
    assert m_host.options == {"Port": ["22"]}
    assert len(m_host.hosts) == 4

    me_host = m_host.hosts[0]
    assert me_host.trackable
    assert me_host.fullname == "me"
    assert me_host.options == {"Port": ["22"], "HostName": ["env10"],
                               "User": ["root"]}
    assert len(me_host.hosts) == 1

    mewww_host = me_host.hosts[0]
    assert mewww_host.trackable
    assert mewww_host.fullname == "meWWW"
    assert mewww_host.options == {"Port": ["22"], "TCPKeepAlive": ["5"],
                                  "HostName": ["env10"], "User": ["root"]}
    assert mewww_host.hosts == []

    mq_host = m_host.hosts[1]
    assert mq_host.trackable
    assert mq_host.fullname == "mq"
    assert mq_host.options == {"Protocol": ["2"], "Port": ["22"]}
    assert mq_host.hosts == []

    mv_host = m_host.hosts[2]
    assert mv_host.trackable
    assert mv_host.fullname == "mv"
    assert mv_host.options == {"Port": ["22"], "HostName": ["env10"],
                               "User": ["root"]}
    assert len(mv_host.hosts) == 1

    mvwww_host = mv_host.hosts[0]
    assert mvwww_host.trackable
    assert mvwww_host.fullname == "mvWWW"
    assert mvwww_host.options == {"Port": ["22"], "TCPKeepAlive": ["5"],
                                  "HostName": ["env10"], "User": ["root"]}
    assert mvwww_host.hosts == []

    mx_host = m_host.hosts[3]
    assert not mx_host.trackable
    assert mx_host.fullname == "mx"
    assert mx_host.options == {"SendEnv": ["12"], "Port": ["22"]}
    assert len(mx_host.hosts) == 1

    mxqex_host = mx_host.hosts[0]
    assert mxqex_host.trackable
    assert mxqex_host.fullname == "mxqex"
    assert mxqex_host.options == {"SendEnv": ["12"], "Port": ["35"],
                                  "ProxyCommand": ["ssh -W %h:%p env312"]}
    assert mxqex_host.hosts == []


def test_parse_options_star_host_invariant():
    no_star_host = """\
Compression yes
CompressionLevel 6
    """.strip()

    star_host = """\
Compression yes

Host *
    CompressionLevel 6
    """.strip()

    star_host_only = """\
Host *
    Compression yes
    CompressionLevel 6
    """.strip()

    no_star_host = parser.parse(lexer.lex(no_star_host.split("\n")))
    star_host = parser.parse(lexer.lex(star_host.split("\n")))
    star_host_only = parser.parse(lexer.lex(star_host_only.split("\n")))

    assert no_star_host.struct == star_host.struct
    assert no_star_host.struct == star_host_only.struct


def test_parse_multiple_options():
    config = """\

Host q
    User root

Host name
    User rooter

    LocalForward 80 brumm:80
    LocalForward 443 brumm:443
    LocalForward 22 brumm:23
""".strip()

    parsed = parser.parse(lexer.lex(config.split("\n")))
    assert sorted(parsed.hosts[1].options["LocalForward"]) == [
        "22 brumm:23",
        "443 brumm:443",
        "80 brumm:80"]


@pytest.mark.parametrize(
    "empty_lines", list(range(5)))
def test_nothing_to_parse(empty_lines):
    root = parser.parse(lexer.lex([""] * empty_lines))

    assert len(root.hosts) == 1
    assert root.hosts[0].fullname == "*"
    assert root.hosts[0].options == {}
    assert root.hosts[0].hosts == []


def test_unknown_option():
    tokens = lexer.lex(["ASDF 1"])

    with pytest.raises(exceptions.ParserUnknownOption):
        parser.parse(tokens)
