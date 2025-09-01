# -*- coding: utf-8 -

"""Test the hierarchical nodes.

This file is part of project oemof (github.com/oemof/oemof). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location oemof/tests/test_hierachical_network_classes.py

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <krien@uni-bremen.de>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>
SPDX-FileCopyrightText: Pierre-Francois Duc <pierre-francois.duc@rl-institut.de>

SPDX-License-Identifier: MIT
"""

import pytest

from oemof.network.network.helpers import HierachicalLabel
from oemof.network.energy_system import EnergySystem
from oemof.network.network import AtomicNode
from oemof.network.network import SubNetwork


class TestsHierarchicalLabel:
    def setup_method(self):
        pass

    def test_turn_label_rep_into_tuple(self):
        label = "label1"
        hl = HierachicalLabel(label)
        assert hl.flat_label == (label,)

    def test_default_depth_of_one(self):
        label = "label1"
        hl = HierachicalLabel(label)
        assert hl.depth == 1

    def test_sequence_labels_display_parent_first(self):
        label_sn = "label of the subnetwork"
        hl_sn = HierachicalLabel(label_sn)
        sn = SubNetwork(label=hl_sn)
        label_node = "label of the node"
        hl_node = HierachicalLabel(label_node, parent=sn)

        assert hl_node.flat_label == (label_sn, label_node)

    def test_depth_of_direct_child_is_larger_than_parent_by_one(self):
        label_sn = "label of the subnetwork"
        hl_sn = HierachicalLabel(label_sn)
        sn = SubNetwork(label=hl_sn)
        label_node = "label of the node"
        hl_node = HierachicalLabel(label_node, parent=sn)

        assert hl_node.depth == hl_sn.depth + 1


class TestsAtomicNode:
    def setup_method(self):
        self.an = AtomicNode("label")

    def test_label_is_herarchical(self):
        assert isinstance(self.an.label, HierachicalLabel)

    def test_default_depth_of_one(self):
        assert self.an.depth == 1

    def test_parent_of_label_is_none(self):
        assert self.an.label.parent is None

    def test_depth_of_direct_child_is_larger_than_parent_by_one(self):
        label_sn = "label of the subnetwork"
        sn = SubNetwork(label=label_sn)
        label_node = "label of the node"
        atomic_node = AtomicNode(label_node, parent_node=sn)

        assert atomic_node.depth == sn.depth + 1

    def test_forbid_atomic_node_to_be_parent(self):
        label_node = "label of the node"
        with pytest.raises(
            TypeError,
            match="The parent_node of an oemof.network.Node instance can only be of type oemof.network.SubNetwork",
        ):
            AtomicNode(label_node, parent_node=self.an)
