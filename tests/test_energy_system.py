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
from itertools import chain

from oemof.network import energy_system as es
from oemof.network.groupings import Flows
from oemof.network.groupings import FlowsWithNodes as FWNs
from oemof.network.network import Bus
from oemof.network.network.nodes import Node


class TestsEnergySystem:
    def setup_method(self):
        self.es = es.EnergySystem()

    def test_flows(self):
        key = object()
        ensys = es.EnergySystem(groupings=[Flows(key)])
        bus = Bus(label="A Bus")
        node = Node(label="A Node", inputs={bus: None}, outputs={bus: None})
        ensys.add(bus, node)
        assert ensys.groups[key] == set(
            chain(bus.inputs.values(), bus.outputs.values())
        )

    def test_flows_with_nodes(self):
        key = object()
        ensys = es.EnergySystem(groupings=[FWNs(key)])
        bus = Bus(label="A Bus")
        node = Node(label="A Node", inputs={bus: None}, outputs={bus: None})
        ensys.add(bus, node)
        assert ensys.groups[key], {
            (bus, node, bus.outputs[node]),
            (node, bus, node.outputs[bus]),
        }

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

        es.EnergySystem.signals[es.EnergySystem.add].connect(
            subscriber, sender=node
        )
        self.es.add(node)
        assert subscriber.called, (
            "\nExpected `subscriber.called` to be `True`.\n"
            "Got {}.\n"
            "Probable reason: `subscriber` didn't get called."
        ).format(subscriber.called)
