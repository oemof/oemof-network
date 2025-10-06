from oemof.network import Node


class TestNode:
    """Tests for Node class"""

    def test_init_basic(self):
        """Basic initialisation"""
        subnet = Node("test_subnet")

        assert subnet.label == "test_subnet"
        assert subnet.parent is None
        assert subnet.depth == 0
        assert len(subnet.subnodes) == 0

    def test_init_with_parent_node(self):
        """Initialisation with parent_node"""
        parent = Node("parent")
        child = Node("child", parent_node=parent)

        assert child.parent == parent
        assert child.depth == 1

    def test_init_with_custom_properties(self):
        """Initialisation with custom_properties"""
        props = {"custom_key": "custom_value"}
        node = Node("test", custom_properties=props)

        assert node.custom_properties == props

    def test_subnode_addition(self):
        """Add existing Node"""
        subnet = Node("parent")

        # add single Node
        subnode = Node("child")
        subnet.add(subnode)

        assert isinstance(subnet.subnodes, tuple)
        assert len(subnet.subnodes) == 1
        assert subnet.subnodes[0] == subnode
        assert subnode.parent == subnet
        assert subnode.depth == 1
        assert subnode.label == "child"

        # add multiple Nodes
        subnode2 = Node("child2")
        subnode3 = Node("child3")
        subnet.add(subnode2, subnode3)

        assert isinstance(subnet.subnodes, tuple)
        assert len(subnet.subnodes) == 3

        # labels are unchanged
        assert subnode2.label == "child2"
        assert subnode3.label == "child3"

        # hierachy properties are adjusted
        assert subnode2.parent == subnet
        assert subnode3.parent == subnet
        assert subnode2.depth == 1
        assert subnode3.depth == 1

    def test_subnode_creation(self):
        """Create Subnode with subnode() method"""
        subnet = Node("parent")

        subnode = subnet.subnode(Node, "child")

        assert isinstance(subnet.subnodes, tuple)
        assert len(subnet.subnodes) == 1
        assert subnet.subnodes[0] == subnode
        assert isinstance(subnode, Node)
        assert subnode.parent == subnet
        assert subnode.depth == 1
        assert subnode.label == ("child", "parent")

    def test_subnode_nested_tuples(self):
        """Add Subnode with subnode() method and tuples as labels"""
        subnet = Node(("parent", "electricity"))

        subnode = subnet.subnode(Node, ("child", "electricity"))

        assert isinstance(subnet.subnodes, tuple)
        assert len(subnet.subnodes) == 1
        assert subnet.subnodes[0] == subnode
        assert isinstance(subnode, Node)
        assert subnode.parent == subnet
        assert subnode.depth == 1
        assert subnode.label == (
            ("child", "electricity"),
            ("parent", "electricity"),
        )

    def test_subnode_with_args_kwargs(self):
        """Subnode creation with extra arguments"""
        subnet = Node("parent")
        custom_props = {"test": "value"}

        subnode = subnet.subnode(Node, "child", custom_properties=custom_props)

        assert subnode.custom_properties == custom_props
        assert subnode.parent == subnet

    def test_multiple_subnodes(self):
        """Create many Subnodes"""
        subnet = Node("parent")

        child1 = subnet.subnode(Node, "child1")
        child2 = subnet.subnode(Node, "child2")
        child3 = subnet.subnode(Node, "child_subnet")

        assert len(subnet.subnodes) == 3
        assert child1 in subnet.subnodes
        assert child2 in subnet.subnodes
        assert child3 in subnet.subnodes

        # Alle sollten subnet als parent haben
        for child in subnet.subnodes:
            assert child.parent == subnet

    def test_nested_subnets(self):
        """Nested Nodes"""
        root = Node("root")
        level1 = root.subnode(Node, "level1")
        level2 = level1.subnode(Node, "level2")
        leaf = level2.subnode(Node, "leaf")

        assert root.depth == 0
        assert level1.depth == 1
        assert level2.depth == 2
        assert leaf.depth == 3

        assert leaf.label == ("leaf", "level2", "level1", "root")

    def test_complex_hierarchy(self):
        """Complex hierarchical structure"""
        root = Node("sub_energy_system")

        power_sector = root.subnode(Node, "power")
        heat_sector = root.subnode(Node, "heat")

        coal_plant = power_sector.subnode(Node, "coal_plant")

        heat_pump = heat_sector.subnode(Node, "heat_pump")

        # Validiere Struktur
        assert len(root.subnodes) == 2
        assert len(power_sector.subnodes) == 1
        assert len(heat_sector.subnodes) == 1

        # Validiere Tiefen
        assert root.depth == 0
        assert power_sector.depth == 1
        assert coal_plant.depth == 2

        # Validiere flat_labels
        assert coal_plant.label == (
            "coal_plant",
            "power",
            "sub_energy_system",
        )
        assert heat_pump.label == (
            "heat_pump",
            "heat",
            "sub_energy_system",
        )
