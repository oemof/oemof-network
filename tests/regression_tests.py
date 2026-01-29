# -*- coding: utf-8 -

"""Regression tests.

This file is part of project oemof (github.com/oemof/oemof). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location oemof/tests/regression_tests.py

SPDX-License-Identifier: MIT
"""

import pandas as pd
import pytest

from oemof.network.energy_system import EnergySystem
from oemof.network.network import Node
from oemof.network.network.nodes import QualifiedLabel


def test_duplicate_label():
    datetimeindex = pd.date_range("1/1/2012", periods=12, freq="h")
    es = EnergySystem(timeindex=datetimeindex)
    my_label1 = "test_01"
    my_label2 = "test_02"
    es.add(Node(label=my_label1))
    es.add(Node(label=my_label2))
    msg = (
        r"EnergySystem already contains Node\(s\) with the following string"
        + r' representation: "test_01", "test_02"'
    )
    with pytest.raises(ValueError, match=msg):
        es.add(Node(label=my_label1), Node(label=my_label2))


def test_duplicate_qualified_label():
    datetimeindex = pd.date_range("1/1/2012", periods=12, freq="h")
    es = EnergySystem(timeindex=datetimeindex)
    my_label1 = QualifiedLabel(
        ("test_01",),
    )
    my_label2 = QualifiedLabel(
        ("test_02",),
    )
    es.add(Node(label=my_label1))
    es.add(Node(label=my_label2))
    msg = (
        r"EnergySystem already contains Node\(s\) with the following string"
        + r" representation: \"\('test_01',\)\", \"\('test_02',\)\""
    )
    with pytest.raises(ValueError, match=msg):
        es.add(Node(label=my_label1), Node(label=my_label2))
