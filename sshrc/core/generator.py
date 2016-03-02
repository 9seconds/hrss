# -*- coding: utf-8 -*-


def generate(tree):
    for host in flat(tree):
        yield "Host {}".format(host.fullname)
        for option, value in sorted(host.options.items()):
            yield "    {} {}".format(option, value)
        yield ""


def flat(tree):
    for host in sorted(tree.childs, key=lambda h: (h.name == "*", h.name)):
        yield from flat_host_data(host)


def flat_host_data(tree):
    for host in tree.hosts:
        yield from flat_host_data(host)
    if tree.trackable:
        yield tree
