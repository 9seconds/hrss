from lexer import lex
from parser import parse
from generator import generate


TEST_DATA = """

Compression yes
Host m
    HostName 1

    Host 2
        CheckHostIP yes

    Host 3
        CheckHostIP yes

Host- d
    CompressionLevel 9

    Host xx
        ProxyCommand "ssh -w %h:%p"

    Host yy

"""


data = TEST_DATA.split("\n")

tokens = lex(data)
parsed = parse(tokens)
data = generate(parsed)

print("\n".join(data))
