from oemof.network.network.hierachical_nodes import AtomicNode
from oemof.network.network.hierachical_nodes import SubNetwork


class TestAtomicNode:
    """Tests for the AtomicNode class"""

    def test_init_without_parent_node(self):
        """Initialisation without parent_node"""
        node = AtomicNode("atomic_test")

        assert node.label == "atomic_test"
        assert node.parent is None
        assert node.depth == 1

    def test_init_with_parent_node(self):
        """Initialisation with parent_node"""
        parent = SubNetwork("parent_subnet")
        node = AtomicNode("atomic_child", parent_node=parent)

        assert node.label == "atomic_child"
        assert node.parent == parent
        assert node.depth == 2

    def test_init_with_custom_properties(self):
        """Initialisation with custom_properties"""
        props = {"custom_key": "custom_value"}
        node = AtomicNode("test", custom_properties=props)

        assert node.custom_properties == props


class TestSubNetwork:
    """Tests for SubNetwork class"""

    def test_init_basic(self):
        """Basic initialisation"""
        subnet = SubNetwork("test_subnet")

        assert subnet.label == "test_subnet"
        assert subnet.parent is None
        assert subnet.depth == 1
        assert len(subnet.subnodes) == 0

    def test_init_with_parent_node(self):
        """Initialisation with parent_node"""
        parent = SubNetwork("parent")
        child = SubNetwork("child", parent_node=parent)

        assert child.parent == parent
        assert child.depth == 2

    def test_subnode_creation(self):
        """Create Subnode with subnode() method"""
        subnet = SubNetwork("parent")

        subnode = subnet.subnode(AtomicNode, "child")

        assert isinstance(subnet.subnodes, tuple)
        assert len(subnet.subnodes) == 1
        assert subnet.subnodes[0] == subnode
        assert isinstance(subnode, AtomicNode)
        assert subnode.parent == subnet
        assert subnode.depth == 2
        assert subnode.label == ("parent", "child")

    def test_subnode_nested_tuples(self):
        """Add Subnode with subnode() method and tuples as labels"""
        subnet = SubNetwork(("parent", "electricity"))

        subnode = subnet.subnode(AtomicNode, ("child", "electricity"))

        assert isinstance(subnet.subnodes, tuple)
        assert len(subnet.subnodes) == 1
        assert subnet.subnodes[0] == subnode
        assert isinstance(subnode, AtomicNode)
        assert subnode.parent == subnet
        assert subnode.depth == 2
        assert subnode.label == (
            ("parent", "electricity"),
            ("child", "electricity"),
        )

    def test_subnode_with_args_kwargs(self):
        """Subnode creation with extra arguments"""
        subnet = SubNetwork("parent")
        custom_props = {"test": "value"}

        subnode = subnet.subnode(
            AtomicNode, "child", custom_properties=custom_props
        )

        assert subnode.custom_properties == custom_props
        assert subnode.parent == subnet

    def test_multiple_subnodes(self):
        """Create many Subnodes"""
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
        """Nested SubNetworks"""
        root = SubNetwork("root")
        level1 = root.subnode(SubNetwork, "level1")
        level2 = level1.subnode(SubNetwork, "level2")
        leaf = level2.subnode(AtomicNode, "leaf")

        assert root.depth == 1
        assert level1.depth == 2
        assert level2.depth == 3
        assert leaf.depth == 4

        assert leaf.label == ("root", "level1", "level2", "leaf")

    def test_complex_hierarchy(self):
        """Complex hierarchical structure"""
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
        assert coal_plant.label == (
            "sub_energy_system",
            "power",
            "coal_plant",
        )
        assert heat_pump.label == (
            "sub_energy_system",
            "heat",
            "heat_pump",
        )
