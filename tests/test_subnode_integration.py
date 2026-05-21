from oemof.network import EnergySystem
from oemof.network import Node


class TestNodeIntegration:
    def test_energy_system_reference(self):
        """Create Subnode with subnode() method"""
        es = EnergySystem()

        subnet = Node("parent")

        subnode1 = Node("child1")
        subnet.add(subnode1)

        assert isinstance(subnet.subnodes, tuple)
        assert len(subnet.subnodes) == 1
        assert subnet.subnodes[-1] == subnode1
        assert subnode1.parent == subnet
        assert subnode1.depth == 1
        assert subnode1.label == "child1"
        assert subnode1._energy_system is None

        subnode2 = subnet.subnode(Node, "child2")

        assert isinstance(subnet.subnodes, tuple)
        assert len(subnet.subnodes) == 2
        assert subnet.subnodes[-1] == subnode2
        assert isinstance(subnode2, Node)
        assert subnode2.parent == subnet
        assert subnode2.depth == 1
        assert subnode2.label == ("child2", "parent")
        assert subnode2._energy_system is None

        es.add(subnet)

        assert subnet._energy_system == es
        assert subnode1._energy_system == es
        assert subnode2._energy_system == es

        subnode3 = Node("child3")
        subnet.add(subnode3)

        assert isinstance(subnet.subnodes, tuple)
        assert len(subnet.subnodes) == 3
        assert subnet.subnodes[-1] == subnode3
        assert subnode3.parent == subnet
        assert subnode3.depth == 1
        assert subnode3.label == "child3"
        assert subnode3._energy_system == es

        subnode4 = subnet.subnode(Node, "child4")

        assert isinstance(subnet.subnodes, tuple)
        assert len(subnet.subnodes) == 4
        assert subnet.subnodes[-1] == subnode4
        assert isinstance(subnode4, Node)
        assert subnode4.parent == subnet
        assert subnode4.depth == 1
        assert subnode4.label == ("child4", "parent")
        assert subnode4._energy_system == es
