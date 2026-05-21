from oemof.network import EnergySystem
from oemof.network import Node


class TestNodeIntegration:
    def test_energy_system_reference(self):
        """Create Subnode with subnode() method"""
        es = EnergySystem()

        subnet = Node("parent")

        subnode1 = Node("child1")
        subnet.add(subnode1)
        assert subnode1._energy_system is None

        subnode2 = subnet.subnode(Node, "child2")
        assert subnode2._energy_system is None

        es.add(subnet)

        assert subnet._energy_system == es
        assert subnode1._energy_system == es
        assert subnode2._energy_system == es

        subnode3 = Node("child3")
        subnet.add(subnode3)
        assert subnode3._energy_system == es

        subnode4 = subnet.subnode(Node, "child4")
        assert subnode4._energy_system == es
