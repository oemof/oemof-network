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
