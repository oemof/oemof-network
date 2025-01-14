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

import pytest

from oemof.network.energy_system import EnergySystem
from oemof.network.network import Edge
from oemof.network.network.nodes import Node


def test_ensys_init():
    node = Node("label")
    ensys = EnergySystem(nodes=[node])
    assert node in ensys.nodes

    with pytest.warns(FutureWarning):
        ensys = EnergySystem(entities=[node])
        assert node in ensys.nodes


class TestsEnergySystem:
    def setup_method(self):
        self.es = EnergySystem()

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

    def test_add_flow_assignment(self):
        assert not self.es.nodes

        node0 = Node(label="node0")
        node1 = Node(label="node1")
        node2 = Node(label="node2", inputs={node0: Edge()})

        self.es.add(node0, node1, node2)

        assert (node0, node2) in self.es.flows().keys()
        assert (node1, node2) not in self.es.flows().keys()
        assert (node2, node1) not in self.es.flows().keys()

        node2.inputs[node1] = Edge()

        assert (node0, node2) in self.es.flows().keys()
        assert (node1, node2) in self.es.flows().keys()
        assert (node2, node1) not in self.es.flows().keys()

        node2.outputs[node1] = Edge()
        assert (node0, node2) in self.es.flows().keys()
        assert (node1, node2) in self.es.flows().keys()
        assert (node2, node1) in self.es.flows().keys()

    def test_check_method(self):
        node0 = Node(label="node0")
        node1 = Node(label="node1")
        node2 = Node(label="node2")
        node3 = Node(label="node3", inputs={node2: Edge()})
        self.es.check()  # empty, no problem

        self.es.add(node0)
        self.es.check()  # single node, no problem

        node0.outputs[node1] = Edge()
        with pytest.raises(RuntimeError, match="not part of EnergySystem"):
            self.es.check()  # node1 needs to be added

        self.es.add(node1)
        self.es.check()  # consistent graph added, no problem

        # The check method is not needed for these cases.
        # I still add them to the test for completeness.
        with pytest.raises(KeyError):
            node2.outputs[node1]  # not allowed anyway
        with pytest.raises(KeyError):
            node1.inputs[node2]  # also not allowed
        self.es.check()  # graph still consistent

        self.es.add(node2)
        with pytest.raises(RuntimeError, match="not part of EnergySystem"):
            self.es.check()  # if node 2 is present, node3 also needs to be

        self.es.add(node3)
        self.es.check()  # Now, everything is fine.

    def test_that_node_additions_are_signalled(self):
        """
        When a node gets `add`ed, a corresponding signal should be emitted.
        """
        node = Node(label="Node")

        def subscriber(sender, **kwargs):
            assert sender is node
            assert kwargs["EnergySystem"] is self.es
            subscriber.called = True

        subscriber.called = False

        EnergySystem.signals[EnergySystem.add].connect(subscriber, sender=node)
        self.es.add(node)
        assert subscriber.called, (
            "\nExpected `subscriber.called` to be `True`.\n"
            "Got {}.\n"
            "Probable reason: `subscriber` didn't get called."
        ).format(subscriber.called)
