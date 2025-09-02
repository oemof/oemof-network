# -*- coding: utf-8 -

"""Test the hierarchical nodes.

This file is part of project oemof (github.com/oemof/oemof). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location
oemof/tests/test_hierachical_network_classes.py

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <krien@uni-bremen.de>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>
SPDX-FileCopyrightText: Pierre-Francois Duc<pierre-francois.duc@rl-institut.de>

SPDX-License-Identifier: MIT
"""

import pytest

from oemof.network.energy_system import EnergySystem
from oemof.network.network import AtomicNode
from oemof.network.network import Node
from oemof.network.network import SubNetwork
from oemof.network.network.helpers import HierachicalLabel


class TestsHierarchicalLabel:
    def setup_method(self):
        pass

    def test_instanciate_without_label_raises_type_error(self):
        with pytest.raises(TypeError):
            HierachicalLabel()

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

    def test_instanciate_without_label_raises_type_error(self):
        with pytest.raises(TypeError):
            AtomicNode()

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

    def test_forbid_atomic_node_to_be_parent_node(self):
        label_node = "label of the node"
        with pytest.raises(
            TypeError,
            match="The parent_node of an oemof.network.AtomicNode instance "
            "can only be of type oemof.network.SubNetwork",
        ):
            AtomicNode(label_node, parent_node=self.an)

    def test_check_preexisting_parent_of_label_is_of_type_subnetwork(self):
        label_node = "label of the node"
        hl_node = HierachicalLabel(label_node, parent=self.an)
        with pytest.raises(
            TypeError,
            match="The parent_node of an oemof.network.AtomicNode instance "
            "can only be of type oemof.network.SubNetwork",
        ):
            AtomicNode(hl_node)

    def test_allow_changing_parent_of_subnode_label(self):
        sn = SubNetwork("a subnetwork")
        atomic_node = AtomicNode(
            HierachicalLabel("hierarchical node"), parent_node=sn
        )
        assert atomic_node.label.parent == sn


class TestsSubNetwork:
    def setup_method(self):
        self.es = EnergySystem()
        self.sn_label = "label of the subnetwork"
        self.sn = SubNetwork(label=self.sn_label)
        self.subnode_label = "internal_bus"
        self.sn.subnode(Node, self.subnode_label)

    def test_instanciate_without_label_raises_type_error(self):
        with pytest.raises(TypeError):
            SubNetwork()

    def test_create_subnode(self):
        assert len(self.sn.subnodes) == 1

    def test_created_subnode_displays_with_parent_node_name_first(self):
        assert self.sn.subnodes[0].label.flat_label == (
            self.sn_label,
            self.subnode_label,
        )

    def test_created_subnode_depth_is_larger_than_parent_by_one(self):
        assert self.sn.subnodes[0].depth == self.sn.depth + 1

    def test_add_simple_node_with_str_label_as_subnode_fails(self):
        n = Node(label="just a simple Node")
        with pytest.raises(AttributeError):
            self.sn.subnodes.append(n)

    def test_add_node_to_subnetwork_via_append_fails(self):
        n_label = "node label"
        n = Node(label=n_label)
        with pytest.raises(AttributeError):
            self.sn.subnodes.append(n)

    def test_add_node_as_subnode_via_subnode_method(self):
        n_label = "node label"
        num_subnodes = len(self.sn.subnodes)
        self.sn.subnode(Node, label=n_label)
        assert len(self.sn.subnodes) == num_subnodes + 1

    def test_add_subnetwork_as_subnode_via_subnode_method(self):
        another_sn_label = "label of the other subnetwork"
        another_sn = self.sn.subnode(SubNetwork, label=another_sn_label)
        another_sn.subnode(Node, "another internal bus")
        assert another_sn.subnodes[0].depth == self.sn.depth + 2

    def test_subnode_of_subnetwork_added_as_subnode_have_updated_depth(self):
        another_sn_label = "label of the other subnetwork"
        another_sn = self.sn.subnode(SubNetwork, label=another_sn_label)
        another_sn.subnode(Node, "another internal bus")
        assert another_sn.subnodes[0].depth == self.sn.depth + 2

    def test_subnodes_added_to_energy_system_when_subnetwork_added(self):
        another_sn_label = "label of the other subnetwork"
        another_sn = self.sn.subnode(SubNetwork, label=another_sn_label)
        another_sn.subnode(Node, "another internal bus")
        self.es.add(self.sn)
        assert len(self.es.nodes) == 4
