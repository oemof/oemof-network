"""Specific tests for the `oemof.groupings` module.

Most parts of the `groupings` module are tested via other tests, but certain
code paths don't get covered by those, which is what this module is for.

This file is part of project oemof (github.com/oemof/oemof). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location oemof/tests/tests_groupings.py

SPDX-License-Identifier: MIT
"""

from types import MappingProxyType as MaProTy

import pytest

from oemof.network.groupings import Grouping


def test_initialization_argument_checks():
    """`Grouping` constructor should raise `TypeError` on bad arguments."""

    message = "Grouping constructor missing required argument"
    with pytest.raises(TypeError, match=message):
        Grouping()

    message = (
        "Grouping arguments `key` and `constant_key` are  mutually exclusive."
    )
    with pytest.raises(TypeError, match=message):
        Grouping(key=lambda x: x, constant_key="key")


def test_notimplementederrors():
    """`Grouping` should raise an error when reaching unreachable code."""

    message = "There is no default implementation for `Groupings.key`."
    with pytest.raises(NotImplementedError, match=message):
        g = Grouping(key="key")
        del g.key
        g.key("dummy argument")

    message = "`Groupings.filter` called without being overridden."
    with pytest.raises(NotImplementedError, match=message):
        g = Grouping(key="key")
        del g.filter
        g.filter("dummy argument")


def test_mutable_mapping_groups():
    g = Grouping(
        key=lambda x: len(x),
        value=lambda x: {y: len([z for z in x if z == y]) for y in x},
    )
    groups = {}
    expected = {3: {"o": 2, "f": 1}}
    g("foo", groups)
    assert groups == expected, "\n  Expected: {} \n  Got     : {}".format(
        expected, groups
    )


def test_immutable_mapping_groups():
    g = Grouping(
        key=lambda x: len(x),
        value=lambda x: MaProTy({y: len([z for z in x if z == y]) for y in x}),
    )
    groups = {}
    expected = {3: MaProTy({"o": 2, "f": 1})}
    g("foo", groups)
    assert groups == expected, "\n  Expected: {} \n  Got     : {}".format(
        expected, groups
    )
