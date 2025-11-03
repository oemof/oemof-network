# -*- coding: utf-8 -

"""Tests for the EnergySystem class.

This file is part of project oemof.network (github.com/oemof/oemof-network).

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <uwe.krien@ifam.fraunhofer.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>
SPDX-FileCopyrightText: Pierre-Francois Duc <pierre-francois@rl-institut.de>

SPDX-License-Identifier: MIT
"""

from pathlib import Path

import pytest
from networkx import DiGraph

from oemof.network import Edge
from oemof.network import Node
from oemof.network import graph
from oemof.network.energy_system import EnergySystem


def test_ensys_init():
    node = Node("label")
    ensys = EnergySystem(nodes=[node])
    assert node in ensys.nodes

    with pytest.warns(FutureWarning):
        ensys = EnergySystem(entities=[node])
        assert node in ensys.nodes


class TestDumpRestore:
    def setup_method(self):
        self.es = EnergySystem()

        node0 = Node(label="node0")
        node1 = Node(label="node1", inputs={node0: Edge()})
        self.es.add(node0, node1)

    def test_dump_restore_cwd(self):
        """Test dumping and restoring to and from current working directory."""

        filename = "./es_test_dump.oemof"

        msg = self.es.dump(
            filename=filename,
            consider_dpath=False,
        )

        assert filename in msg

        es = EnergySystem()
        msg = es.restore(
            filename=filename,
            consider_dpath=False,
        )

        assert filename in msg
        assert len(es.nodes) == 2
        assert isinstance(es.node["node0"], Node)

    def test_dump_restore_dpath_remapping(self):
        """Test dumping and restoring to and from current working directory."""

        filename = "./es_test_remap_dump.oemof"

        msg = self.es.dump(
            filename,
            consider_dpath=False,
        )

        assert filename in msg

        es = EnergySystem()
        msg = es.restore(
            filename,
            consider_dpath=False,
        )

        assert filename in msg
        assert len(es.nodes) == 2
        assert isinstance(es.node["node0"], Node)

    def test_dump_restore_default_filename(self):
        """Test dumping and restoring with default filename to custom dir."""

        default_filename = "es_dump.oemof"

        with pytest.warns(
            match="Parameter 'dpath' will be removed in a future",
        ):
            msg = self.es.dump(dpath="./")

        assert default_filename in msg

        es = EnergySystem()
        with pytest.warns(
            match="Parameter 'dpath' will be removed in a future",
        ):
            msg = es.restore(dpath="./")

        assert default_filename in msg
        assert len(es.nodes) == 2
        assert isinstance(es.node["node0"], Node)

    def test_dump_restore_dpath_filename(self):
        """Test dumping and restoring with filename and dir."""

        directory = "./"
        filename = "es_dump_dpath_filename.oemof"

        with pytest.warns(
            match="Parameter 'dpath' will be removed in a future",
        ):
            msg = self.es.dump(directory, filename)

        assert filename in msg

        es = EnergySystem()
        with pytest.warns(
            match="Parameter 'dpath' will be removed in a future",
        ):
            msg = es.restore(directory, filename)

        assert filename in msg
        assert len(es.nodes) == 2
        assert isinstance(es.node["node0"], Node)

    def test_dump_restore_default(self):
        """Test default dumping and restoring."""

        default_filename = "es_dump.oemof"

        with pytest.warns(
            match="Default directory for oemof dumps will change",
        ):
            msg = self.es.dump()

        assert default_filename in msg

        es = EnergySystem()
        with pytest.warns(
            match="Default directory for oemof dumps will change",
        ):
            msg = es.restore()

        assert default_filename in msg
        assert len(es.nodes) == 2
        assert isinstance(es.node["node0"], Node)

    def test_dump_restore_impossible_combination(self):
        """Test default dumping and restoring."""

        m = "You set filename and dpath but told that dpath should be ignored."
        with pytest.raises(ValueError, match=m):
            self.es.dump(filename="foo.dump", dpath="/", consider_dpath=False)

        es = EnergySystem()

        with pytest.raises(ValueError, match=m):
            es.restore(filename="foo.dump", dpath="/", consider_dpath=False)


class TestsEnergySystem:
    def setup_method(self):
        self.es = EnergySystem()

    def test_add_nodes(self):
        assert not self.es.nodes

        node1 = Node(label="node1")
        self.es.add(node1)
        assert self.es.nodes
        assert node1 in self.es.nodes
        assert not self.es.flows()

        # Note that node2 is not added, but the Flow is already
        # registred. We do not assert the latter fact as this is not a
        # guaranteed functionality.
        node2 = Node(label="node2", inputs={node1: Edge()})
        assert node2 not in self.es.nodes

        # When both nodes are registred, also the Flow needs to be there.
        self.es.add(node2)
        assert node2 in self.es.nodes
        assert (node1, node2) in self.es.flows().keys()

    def test_enforce_unique_labels(self):
        node1 = Node(label="node1")
        self.es.add(node1)

        node2 = Node(label="node1")
        with pytest.raises(
            ValueError,
            match="already contains",
        ):
            self.es.add(node2)

        node2 = Node(label="node2")
        self.es.add(node2)

        node3 = Node(label="node1")
        node4 = Node(label="node2")
        with pytest.raises(
            ValueError,
            match="already contains",
        ):
            self.es.add(node3, node4)

    def test_automatically_add_subnode(self):
        subnetwork = Node(label="root")
        self.es.add(subnetwork)
        assert len(self.es.nodes) == 1

        leaf1 = subnetwork.subnode(Node, local_name="leaf1")
        subnetwork.subnode(Node, local_name="leaf2")
        assert len(self.es.nodes) == 3

        assert self.es.node[("leaf1", "root")] == leaf1

    def test_add_populated_subnetwork(self):
        subnetwork = Node(label="root")
        leaf1 = subnetwork.subnode(Node, local_name="leaf1")
        subnetwork.subnode(Node, local_name="leaf2")

        self.es.add(subnetwork)
        assert len(self.es.nodes) == 3

        assert self.es.node[("leaf1", "root")] == leaf1

    def test_add_flow_assignment(self):
        assert not self.es.nodes

        node0 = Node(label="node0")
        node1 = Node(label="node1")
        node2 = Node(label="node2", inputs={node0: Edge()})

        self.es.add(node0, node1, node2)

        assert (node0, node2) in self.es.flows().keys()
        assert (node1, node2) not in self.es.flows().keys()
        assert (node2, node1) not in self.es.flows().keys()

        node2.inputs[node1] = Edge()

        assert (node0, node2) in self.es.flows().keys()
        assert (node1, node2) in self.es.flows().keys()
        assert (node2, node1) not in self.es.flows().keys()

        node2.outputs[node1] = Edge()
        assert (node0, node2) in self.es.flows().keys()
        assert (node1, node2) in self.es.flows().keys()
        assert (node2, node1) in self.es.flows().keys()

    def test_check_method(self):
        node0 = Node(label="node0")
        node1 = Node(label="node1")
        node2 = Node(label="node2")
        node3 = Node(label="node3", inputs={node2: Edge()})
        self.es.check()  # empty, no problem

        self.es.add(node0)
        self.es.check()  # single node, no problem

        node0.outputs[node1] = Edge()
        with pytest.raises(RuntimeError, match="not part of EnergySystem"):
            self.es.check()  # node1 needs to be added

        self.es.add(node1)
        self.es.check()  # consistent graph added, no problem

        # The check method is not needed for these cases.
        # I still add them to the test for completeness.
        with pytest.raises(KeyError):
            node2.outputs[node1]  # not allowed anyway
        with pytest.raises(KeyError):
            node1.inputs[node2]  # also not allowed
        self.es.check()  # graph still consistent

        self.es.add(node2)
        with pytest.raises(RuntimeError, match="not part of EnergySystem"):
            self.es.check()  # if node 2 is present, node3 also needs to be

        self.es.add(node3)
        self.es.check()  # Now, everything is fine.

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

        EnergySystem.signals[EnergySystem.add].connect(subscriber, sender=node)
        self.es.add(node)
        assert subscriber.called, (
            "\nExpected `subscriber.called` to be `True`.\n"
            "Got {}.\n"
            "Probable reason: `subscriber` didn't get called."
        ).format(subscriber.called)

    def test_graph(self):
        fpath = Path(Path.home(), "test_graph_x345_efhu73.graphml")
        my_graph = graph.create_nx_graph(self.es)
        assert isinstance(my_graph, DiGraph)

        # make sure that test does not pass because of pre-existing file
        assert not fpath.is_file()

        # create graph file
        my_graph = graph.create_nx_graph(self.es, filename=fpath)
        assert isinstance(my_graph, DiGraph)
        assert fpath.is_file()

        # clean up (delete graph file)
        fpath.unlink()
