# -*- coding: utf-8 -*-


import collections
import itertools
import json

import exceptions


VALID_OPTIONS = frozenset((
    "AddressFamily",
    "BatchMode",
    "BindAddress",
    "ChallengeResponseAuthentication",
    "CheckHostIP",
    "Cipher",
    "Ciphers",
    "Compression",
    "CompressionLevel",
    "ConnectionAttempts",
    "ConnectTimeout",
    "ControlMaster",
    "ControlPath",
    "DynamicForward",
    "EnableSSHKeysign",
    "EscapeChar",
    "ExitOnForwardFailure",
    "ForwardAgent",
    "ForwardX11",
    "ForwardX11Trusted",
    "GatewayPorts",
    "GlobalKnownHostsFile",
    "GSSAPIAuthentication",
    "GSSAPIKeyExchange",
    "GSSAPIClientIdentity",
    "GSSAPIDelegateCredentials",
    "GSSAPIRenewalForcesRekey",
    "GSSAPITrustDns",
    "HashKnownHosts",
    "HostbasedAuthentication",
    "HostKeyAlgorithms",
    "HostKeyAlias",
    "HostName",
    "IdentitiesOnly",
    "IdentityFile",
    "KbdInteractiveAuthentication",
    "KbdInteractiveDevices",
    "LocalCommand",
    "LocalForward",
    "LogLevel",
    "MACs",
    "NoHostAuthenticationForLocalhost",
    "NumberOfPasswordPrompts",
    "PasswordAuthentication",
    "PermitLocalCommand",
    "Port",
    "PreferredAuthentications",
    "Protocol",
    "ProxyCommand",
    "PubkeyAuthentication",
    "RekeyLimit",
    "RemoteForward",
    "RhostsRSAAuthentication",
    "RSAAuthentication",
    "SendEnv",
    "ServerAliveCountMax",
    "ServerAliveInterval",
    "SmartcardDevice",
    "StrictHostKeyChecking",
    "TCPKeepAlive",
    "Tunnel",
    "TunnelDevice",
    "UsePrivilegedPort",
    "UserKnownHostsFile",
    "VerifyHostKeyDNS",
    "VisualHostKey",
    "XAuthLocation"
))


VIA_JUMP_HOST_OPTION = "ViaJumpHost"
VALID_OPTIONS.add(VIA_JUMP_HOST_OPTION)


class Host(object):

    def __init__(self, name, parent, trackable=True):
        self.values = {}
        self.childs = []
        self.name = name
        self.parent = parent
        self.trackable = trackable

    @property
    def fullname(self):
        parent_name = self.parent.name if self.parent else ""
        return parent_name + self.name

    @property
    def options(self):
        parent_options = self.parent.options if self.parent else {}
        parent_options.update(self.values)

        return parent_options

    @property
    def hosts(self):
        return sorted(self.childs, key=lambda host: host.name)

    @property
    def struct(self):
        return {
            "*name*": self.fullname,
            "*options*": self.options,
            "*hosts*": [host.struct for host in self.childs]
        }

    def add_host(self, name, trackable=True):
        host = self.__class__(name, self, trackable)
        self.childs.append(host)

        return host

    def __setitem__(self, key, value):
        self.values[key] = value

    def __getitem__(self, key):
        return self.options[key]

    def __str__(self):
        return "<Host {}>".format(self.fullname)

    def __repr__(self, indent=True):
        indent = 4 if indent else None
        representation = json.dumps(self.struct, indent=indent)

        return representation


def parse(tokens):
    root_host = Host("", None)
    root_host = parse_options(root_host, tokens)
    root_host = fix_star_host(root_host)

    return root_host


def parse_options(root, tokens):
    if not tokens:
        return root

    current_level = tokens[0].indent
    tokens = collections.deque(tokens)

    while tokens:
        token = tokens.popleft()

        if token.option in ("Host", "Host-"):
            host_tokens = get_host_tokens(current_level, tokens)
            for name in token.values:
                host = root.add_host(name, is_trackable_host(token.option))
                parse_options(host, host_tokens)
            for _ in range(len(host_tokens)):
                tokens.popleft()
        elif token.option == VIA_JUMP_HOST_OPTION:
            root["ProxyCommand"] = "ssh -W %h:%p {}".format(token.values[0])
        elif token.option not in VALID_OPTIONS:
            raise exceptions.ParserUnknownOption(token.option)
        else:
            root[token.option] = " ".join(token.values)

    return root


def fix_star_host(root):
    star_host = None

    for host in root.childs:
        if host.name == "*":
            star_host = host
            break
    else:
        star_host = root.add_host("*")

    values = {}
    values.update(root.values)
    values.update(star_host.values)
    star_host.values = values
    star_host.trackable = True
    root.values = {}

    return root


def get_host_tokens(level, tokens):
    host_tokens = itertools.takewhile(lambda tok: tok.indent > level, tokens)
    host_tokens = list(host_tokens)

    return host_tokens


def is_trackable_host(name):
    return name != "Host-"
