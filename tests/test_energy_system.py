# -*- coding: utf-8 -

"""Basic tests.

This file is part of project oemof.network (github.com/oemof/oemof-network).

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <krien@uni-bremen.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>

SPDX-License-Identifier: MIT
"""

from oemof.network import energy_system as es
from oemof.network.network import Edge
from oemof.network.network.nodes import Node


class TestsEnergySystem:
    def setup_method(self):
        self.es = es.EnergySystem()

    def test_add_nodes(self):
        assert not self.es.nodes

        node1 = Node(label="node1")
        self.es.add(node1)
        assert self.es.nodes
        assert node1 in self.es.nodes
        assert not self.es.flows()

        # Note that node2 is not added, but the Flow is already
        # registred. We do not assert the latter fact as this is not a
        # guaranteed functionality.
        node2 = Node(label="node2", inputs={node1: Edge()})
        assert node2 not in self.es.nodes

        # When both nodes are registred, also the Flow needs to be there.
        self.es.add(node2)
        assert node2 in self.es.nodes
        assert (node1, node2) in self.es.flows().keys()
