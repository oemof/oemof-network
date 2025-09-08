from unittest.mock import Mock

import pytest

from oemof.network.network.helpers import HierachicalLabel
from oemof.network.network.hierachical_nodes import AtomicNode
from oemof.network.network.hierachical_nodes import SubNetwork
from oemof.network.network.nodes import Node


# class TestCheckParentNodeAndLabelArgs:
#     """Tests für _check_parent_node_and_label_args Hilfsfunktion"""
#
#     def test_create_hierarchical_label_from_string(self):
#         """Erstelle HierachicalLabel aus String und parent_node"""
#         parent = Mock(spec=SubNetwork)
#         parent_label = Mock()
#         parent_label.depth = 1
#         parent_label.flat_label = ("parent",)
#         parent.label = parent_label
#
#         result = _check_parent_node_and_label_args(
#             "test_label", parent, "TestNode"
#         )
#
#         assert isinstance(result, HierachicalLabel)
#         assert result.label == "test_label"
#         assert result.parent == parent
#         assert result.depth == 2
#         assert result.flat_label == ("parent", "test_label")
#
#     def test_use_existing_hierarchical_label(self):
#         """Verwende existierendes HierachicalLabel ohne parent_node"""
#         label = HierachicalLabel("test", parent=None)
#         result = _check_parent_node_and_label_args(label, None, "TestNode")
#
#         assert result is label
#         assert result.label == "test"
#
#     def test_update_parent_of_existing_label_with_warning(self):
#         """Update parent von existierendem Label mit Warnung"""
#         parent = Mock(spec=SubNetwork)
#         parent_label = Mock()
#         parent_label.depth = 1
#         parent_label.flat_label = ("parent",)
#         parent.label = parent_label
#
#         label = HierachicalLabel("test", parent=None)
#
#         with pytest.warns(UserWarning, match="The parent of the TestNode"):
#             result = _check_parent_node_and_label_args(
#                 label, parent, "TestNode"
#             )
#
#         assert result.parent == parent
#
#     def test_invalid_parent_node_type_raises_error(self):
#         """Fehler bei ungültigem parent_node Typ"""
#         # Mock der explizit NICHT SubNetwork ist
#         invalid_parent = Mock()
#         invalid_parent.__class__.__name__ = "NotSubNetwork"
#
#         with pytest.raises(TypeError):
#             _check_parent_node_and_label_args(
#                 "test", invalid_parent, "TestNode"
#             )


class TestAtomicNode:
    """Tests für AtomicNode Klasse"""

    def test_init_without_parent_node(self):
        """Initialisierung ohne parent_node"""
        node = AtomicNode("atomic_test")

        assert node.label == "atomic_test"
        assert node.parent is None
        assert node.depth == 1

    def test_init_with_parent_node(self):
        """Initialisierung mit parent_node"""
        parent = SubNetwork("parent_subnet")
        node = AtomicNode("atomic_child", parent_node=parent)

        assert node.parent == parent
        assert node.depth == 2

    def test_init_with_hierarchical_label(self):
        """Initialisierung mit existierendem HierachicalLabel"""
        parent = SubNetwork("parent")
        label = "atomic"
        node = AtomicNode(label, parent_node=parent)

        assert node.label == label
        assert node.parent == parent

    def test_init_with_custom_properties(self):
        """Initialisierung mit custom_properties"""
        props = {"custom_key": "custom_value"}
        node = AtomicNode("test", custom_properties=props)

        assert node.custom_properties == props

    # def test_invalid_parent_type_raises_error(self):
    #     """Fehler bei ungültigem parent_node Typ"""
    #     # Echtes Node-Objekt als invalid parent
    #     invalid_parent = Node("invalid")
    #
    #     with pytest.raises(
    #         AttributeError, match="object has no attribute 'depth'"
    #     ):
    #         AtomicNode("test", parent_node=invalid_parent)


class TestSubNetwork:
    """Tests für SubNetwork Klasse"""

    def test_init_basic(self):
        """Grundlegende Initialisierung"""
        subnet = SubNetwork("test_subnet")

        assert subnet.label == "test_subnet"
        assert subnet.parent is None
        assert subnet.depth == 1
        assert len(subnet.subnodes) == 0

    def test_init_with_parent_node(self):
        """Initialisierung mit parent_node"""
        parent = SubNetwork("parent")
        child = SubNetwork("child", parent_node=parent)

        assert child.parent == parent
        assert child.depth == 2

    def test_subnodes_property_is_tuple(self):
        """subnodes Property gibt Tuple zurück"""
        subnet = SubNetwork("test")

        assert isinstance(subnet.subnodes, tuple)
        assert len(subnet.subnodes) == 0

    def test_subnode_creation(self):
        """Erstelle Subnode mit subnode() Methode"""
        subnet = SubNetwork("parent")

        subnode = subnet.subnode(AtomicNode, "child")

        assert len(subnet.subnodes) == 1
        assert subnet.subnodes[0] == subnode
        assert isinstance(subnode, AtomicNode)
        assert subnode.parent == subnet
        assert subnode.depth == 2

    def test_subnode_with_args_kwargs(self):
        """Subnode creation mit zusätzlichen Argumenten"""
        subnet = SubNetwork("parent")
        custom_props = {"test": "value"}

        subnode = subnet.subnode(
            AtomicNode, "child", custom_properties=custom_props
        )

        assert subnode.custom_properties == custom_props
        assert subnode.parent == subnet

    def test_multiple_subnodes(self):
        """Mehrere Subnodes erstellen"""
        subnet = SubNetwork("parent")

        child1 = subnet.subnode(AtomicNode, "child1")
        child2 = subnet.subnode(AtomicNode, "child2")
        child3 = subnet.subnode(SubNetwork, "child_subnet")

        assert len(subnet.subnodes) == 3
        assert child1 in subnet.subnodes
        assert child2 in subnet.subnodes
        assert child3 in subnet.subnodes

        # Alle sollten subnet als parent haben
        for child in subnet.subnodes:
            assert child.parent == subnet

    def test_nested_subnets(self):
        """Verschachtelte SubNetworks"""
        root = SubNetwork("root")
        level1 = root.subnode(SubNetwork, "level1")
        level2 = level1.subnode(SubNetwork, "level2")
        leaf = level2.subnode(AtomicNode, "leaf")

        assert root.depth == 1
        assert level1.depth == 2
        assert level2.depth == 3
        assert leaf.depth == 4

        assert leaf.hierarchical_label == ("root", "level1", "level2", "leaf")

    def test_complex_hierarchy(self):
        """Komplexe hierarchische Struktur"""
        # Erstelle komplexe Hierarchie
        root = SubNetwork("sub_energy_system")

        power_sector = root.subnode(SubNetwork, "power")
        heat_sector = root.subnode(SubNetwork, "heat")

        coal_plant = power_sector.subnode(AtomicNode, "coal_plant")

        heat_pump = heat_sector.subnode(AtomicNode, "heat_pump")

        # Validiere Struktur
        assert len(root.subnodes) == 2
        assert len(power_sector.subnodes) == 1
        assert len(heat_sector.subnodes) == 1

        # Validiere Tiefen
        assert root.depth == 1
        assert power_sector.depth == 2
        assert coal_plant.depth == 3

        # Validiere flat_labels
        assert coal_plant.hierarchical_label == (
            "sub_energy_system",
            "power",
            "coal_plant",
        )
        assert heat_pump.hierarchical_label == (
            "sub_energy_system",
            "heat",
            "heat_pump",
        )
