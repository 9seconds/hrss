# -*- coding: utf-8 -*-


import collections
import itertools
import json

import concierge.core.exceptions as exceptions
import concierge.utils


VALID_OPTIONS = set((
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
    "KexAlgorithms",
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
    "XAuthLocation",
    "User",
    "CertificateFile",
    "UseRoaming"
))

VIA_JUMP_HOST_OPTION = "ViaJumpHost"
VALID_OPTIONS.add(VIA_JUMP_HOST_OPTION)

LOG = concierge.utils.logger(__name__)


class Host(object):

    def __init__(self, name, parent, trackable=True):
        self.values = collections.defaultdict(set)
        self.childs = []
        self.name = name
        self.parent = parent
        self.trackable = trackable

    @property
    def fullname(self):
        if self.name != "" and self.name[0] == "_":
            return self.name[1:]
        parent_name = self.parent.fullname if self.parent else ""
        return parent_name + self.name

    @property
    def options(self):
        if self.parent:
            parent_options = self.parent.options
        else:
            parent_options = collections.defaultdict(set)

        for key, value in self.values.items():
            # Yes, =, not 'update'. this is done intentionally to
            # fix the situation when you might have some mutually exclusive
            # options like User.
            parent_options[key] = sorted(value)

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
        LOG.debug("Add host %s to %s.", name, self)

        host = self.__class__(name, self, trackable)
        self.childs.append(host)

        return host

    def __setitem__(self, key, value):
        self.values[key].add(value)

    def __getitem__(self, key):
        return self.options[key]

    def __str__(self):
        return "<Host {0}>".format(self.fullname)

    def __repr__(self, indent=True):
        indent = 4 if indent else None
        representation = json.dumps(self.struct, indent=indent)

        return representation


def parse(tokens):
    LOG.info("Start parsing %d tokens.", len(tokens))

    root_host = Host("", None)
    root_host = parse_options(root_host, tokens)
    root_host = fix_star_host(root_host)

    LOG.info("Finish parsing of %d tokens.", len(tokens))
    LOG.debug("Tree is %s", repr(root_host))

    return root_host


def parse_options(root, tokens):
    if not tokens:
        LOG.debug("No tokens for root %s.", root)
        return root

    current_level = tokens[0].indent
    LOG.debug("Indent level for root %s is %d.", root, current_level)

    tokens = collections.deque(tokens)
    while tokens:
        token = tokens.popleft()
        LOG.debug("Process token %s for root %s.", token, root)

        if token.option in ("Host", "-Host"):
            LOG.debug("Token %s is host token", token)

            host_tokens = get_host_tokens(current_level, tokens)
            LOG.debug("Found %d host tokens for token %s: %s.",
                      len(host_tokens), token, host_tokens)
            for name in token.values:
                host = root.add_host(name, is_trackable_host(token.option))
                parse_options(host, host_tokens)
            for _ in range(len(host_tokens)):
                tokens.popleft()
        elif token.option == VIA_JUMP_HOST_OPTION:
            LOG.debug("Special option %s in token %s is detected.",
                      VIA_JUMP_HOST_OPTION, token)
            root["ProxyCommand"] = "ssh -W %h:%p {0}".format(token.values[0])
        elif token.option not in VALID_OPTIONS:
            LOG.debug("Option %s in token %s is unknown.", token.option, token)
            raise exceptions.ParserUnknownOption(token.option)
        else:
            LOG.debug("Add option %s with values %s to host %s.",
                      token.option, token.values, root)
            root[token.option] = " ".join(token.values)

    return root


def fix_star_host(root):
    star_host = None

    for host in root.childs:
        if host.name == "*":
            LOG.debug("Detected known '*' host.")
            star_host = host
            break
    else:
        LOG.debug("Add new '*' host.")
        star_host = root.add_host("*")

    values = collections.defaultdict(set)
    values.update(root.values)
    values.update(star_host.values)
    star_host.values = values
    star_host.trackable = True
    root.values.clear()

    return root


def get_host_tokens(level, tokens):
    host_tokens = itertools.takewhile(lambda tok: tok.indent > level, tokens)
    host_tokens = list(host_tokens)

    return host_tokens


def is_trackable_host(name):
    return name != "-Host"
