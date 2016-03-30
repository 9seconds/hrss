# -*- coding: utf-8 -*-


import pytest

import concierge.core.parser as parser


@pytest.mark.parametrize(
    "name", (
        "", "name"))
@pytest.mark.parametrize(
    "parent", (
        None, "", object()))
@pytest.mark.parametrize(
    "trackable", (
        True, False))
def test_init(name, parent, trackable):
    obj = parser.Host(name, parent, trackable)

    assert obj.values == {}
    assert obj.childs == []
    assert obj.name == name
    assert obj.parent == parent
    assert obj.trackable == trackable


def test_fullname():
    host1 = parser.Host("a", None)
    host2 = parser.Host("b", host1)
    host3 = parser.Host("c", host2)

    assert host1.name == "a"
    assert host1.fullname == "a"

    assert host2.name == "b"
    assert host2.fullname == "ab"

    assert host3.name == "c"
    assert host3.fullname == "abc"


def test_fullname_dynamic():
    host1 = parser.Host("a", None)
    host2 = parser.Host("b", host1)
    host3 = parser.Host("c", host2)

    assert host3.fullname == "abc"

    host3.parent = host1

    assert host3.fullname == "ac"


def test_options():
    host1 = parser.Host("a", None)

    assert host1.values == {}
    assert host1.options == {}

    host1["a"] = 1

    assert len(host1.values) == len(host1.options)
    for key, value in host1.values.items():
        assert sorted(value) == sorted(host1.options[key])
    assert host1.options == {"a": [1]}

    assert host1["a"] == [1]


def test_options_several():
    host = parser.Host("a", None)

    host["a"] = 1
    assert host.options == {"a": [1]}

    host["a"] = 3
    assert host.options == {"a": [1, 3]}

    host["a"] = 2
    assert host.options == {"a": [1, 2, 3]}


def test_options_overlap():
    host1 = parser.Host("a", None)
    host2 = parser.Host("b", host1)

    host1["a"] = 1
    host1["b"] = 2
    assert host2.options == {"a": [1], "b": [2]}

    host2["c"] = 3
    assert host1.options == {"a": [1], "b": [2]}
    assert host2.options == {"a": [1], "b": [2], "c": [3]}

    host2["b"] = "q"
    assert host1.options == {"a": [1], "b": [2]}
    assert host2.options == {"a": [1], "b": ["q"], "c": [3]}


def test_add_host():
    root = parser.Host("root", None)

    for name in "child1", "child2", "child0":
        host = root.add_host(name)

        assert host.fullname == "root" + name


def test_hosts_names():
    root = parser.Host("root", None)

    for name in "child1", "child2", "child0":
        root.add_host(name)

    names = [host.name for host in root.childs]
    host_names = [host.name for host in root.hosts]

    assert names != host_names
    assert sorted(names) == host_names


def test_beat_coverage():
    root = parser.Host("root", None)
    repr(root)
    str(root)

    for name in "child1", "child2", "child0":
        root.add_host(name)
    repr(root)
    str(root)
