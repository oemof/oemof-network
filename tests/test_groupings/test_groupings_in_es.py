# -*- coding: utf-8 -

"""Basic tests.

This file is part of project oemof.network (github.com/oemof/oemof-network).

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <uwe.krien@ifam.fraunhofer.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>

SPDX-License-Identifier: MIT
"""
from itertools import chain

from oemof.network import energy_system as es
from oemof.network.groupings import Flows
from oemof.network.groupings import FlowsWithNodes
from oemof.network.network.nodes import Node


def test_flows():
    key = object()
    ensys = es.EnergySystem(groupings=[Flows(key)])
    bus = Node(label="A Bus")
    node = Node(label="A Node", inputs={bus: None}, outputs={bus: None})
    ensys.add(bus, node)
    assert ensys.groups[key] == set(
        chain(bus.inputs.values(), bus.outputs.values())
    )


def test_flows_with_nodes():
    key = object()
    ensys = es.EnergySystem(groupings=[FlowsWithNodes(key)])
    bus = Node(label="A Bus")
    node = Node(label="A Node", inputs={bus: None}, outputs={bus: None})
    ensys.add(bus, node)
    assert ensys.groups[key], {
        (bus, node, bus.outputs[node]),
        (node, bus, node.outputs[bus]),
    }
