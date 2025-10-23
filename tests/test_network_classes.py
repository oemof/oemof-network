# -*- coding: utf-8 -

"""Test the created constraints against approved constraints.

This file is part of project oemof (github.com/oemof/oemof). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location oemof/tests/test_network_classes.py

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <uwe.krien@ifam.fraunhofer.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>

SPDX-License-Identifier: MIT
"""

from traceback import format_exception_only as feo

import pytest

from oemof.network.energy_system import EnergySystem
from oemof.network.network import Bus
from oemof.network.network import Sink
from oemof.network.network import Source
from oemof.network.network import Transformer
from oemof.network.network.edge import Edge
from oemof.network.network.entity import Entity
from oemof.network.network.nodes import Node


class TestsNode:
    def setup_method(self):
        self.energysystem = EnergySystem()

    def test_entity_initialisation(self):
        entity = Entity(label="foo")
        assert entity.label == "foo"

    def test_symmetric_input_output_assignment(self):
        n1 = Node(label="<N1>")

        n2 = Node(label="<From N1>", inputs=[n1])
        assert n1 in n2.inputs, (
            "{0} not in {1}.inputs, ".format(n1, n2)
            + "although it should be by construction."
        )

        assert (
            n2 in n1.outputs
        ), "{0} in {1}.inputs but {1} not in {0}.outputs.".format(n1, n2)

        n3 = Node(label="<To N1>", outputs=[n1])
        assert n1 in n3.outputs, (
            "{0} not in {1}.outputs, ".format(n1, n3)
            + "although it should be by construction.",
        )
        assert n3 in n1.inputs, (
            "{0} in {1}.outputs but {1} not in {0}.inputs.".format(n1, n3),
        )

    def test_accessing_outputs_of_a_node_without_output_flows(self):
        n = Node(label="node")
        exception = None
        outputs = None
        try:
            outputs = n.outputs
        except Exception as e:
            exception = e
        assert exception is None, (
            "\n  Test accessing `outputs` on {} having no outputs.".format(n)
            + "\n  Got unexpected exception:\n"
            + "\n      {}".format(feo(type(exception), exception)[0]),
        )
        assert len(outputs) == 0, (
            "\n  Failure when testing `len(outputs)`."
            + "\n  Expected: 0."
            + "\n  Got     : {}".format(len(outputs)),
        )

    def test_accessing_inputs_of_a_node_without_input_flows(self):
        n = Node(label="node")
        exception = None
        inputs = None
        try:
            inputs = n.inputs
        except Exception as e:
            exception = e
        assert exception is None, (
            "\n  Test accessing `inputs` on {} having no inputs.".format(n)
            + "\n  Got unexpected exception:\n"
            + "\n      {}".format(feo(type(exception), exception)[0]),
        )
        assert len(inputs) == 0, (
            "\n  Failure when testing `len(inputs)`."
            + "\n  Expected: 0."
            + "\n  Got     : {}".format(len(inputs)),
        )

    def test_that_the_outputs_attribute_of_a_node_is_a_mapping(self):
        n = Node(label="node")
        exception = None
        try:
            n.outputs.values()
        except AttributeError as e:
            exception = e
        assert exception is None, (
            "\n  Test accessing `outputs.values()`"
            + " on {} having no inputs.".format(n)
            + "\n  Got unexpected exception:\n"
            + "\n      {}".format(feo(type(exception), exception)[0]),
        )

    def test_that_nodes_do_not_get_undead_flows(self):
        """Newly created nodes should only have flows assigned to them.

        A new node `n`, which re-used a previously used label `l`, retained the
        flows of those nodes which where labeled `l` before `n`. This incorrect
        behaviour is a problem if somebody wants to use different nodes with
        the same label in multiple energy systems. While this feature currently
        isn't used, it also lead to weird behaviour when running tests.

        This test ensures that new nodes only have those flows which are
        assigned to them on construction.
        """
        flow = object()
        old = Node(label="A reused label")
        bus = Node(label="bus", inputs={old: flow})
        assert bus.inputs[old].flow == flow, (
            ("\n  Expected: {0}" + "\n  Got     : {1} instead").format(
                flow, bus.inputs[old].flow
            ),
        )
        assert old.outputs[bus].flow == flow, (
            ("\n  Expected: {}" + "\n  Got     : {} instead").format(
                flow, old.outputs[bus].flow
            ),
        )
        new = Node(label="A reused label")
        assert new.outputs == {}, (
            "\n  Expected an empty dictionary of outputs."
            + "\n  Got: {} instead".format(new.outputs),
        )

    def test_modifying_outputs_after_construction(self):
        """One should be able to add and delete outputs of a node."""
        node = Node("N1")
        bus = Node("N2")
        flow = "flow"
        assert node.outputs == {}, (
            "\n  Expected an empty dictionary of outputs."
            + "\n  Got: {} (== {}) instead".format(
                node.outputs, dict(node.outputs)
            ),
        )
        node.outputs[bus] = flow
        assert node.outputs == {bus: flow}, (
            "\n  Expected {} as `node.outputs`."
            + "\n  Got    : {} (== {}) instead"
        ).format({bus: flow}, node.outputs, dict(node.outputs))

        assert node.outputs[bus] == flow, (
            "\n  Expected {} as `node.outputs[bus]`."
            + "\n  Got    : {} instead"
        ).format(flow, node.outputs[bus])

        del node.outputs[bus]
        assert node.outputs == {}, (
            "\n  Expected an empty dictionary of outputs."
            + "\n  Got: {} (== {}) instead"
        ).format(node.outputs, dict(node.outputs))

    def test_modifying_inputs_after_construction(self):
        """One should be able to add and delete inputs of a node."""
        node = Node("N1")
        bus = Node("N2")
        flow = "flow"

        assert node.inputs == {}, (
            "\n  Expected an empty dictionary of inputs."
            + "\n  Got: {} (== {}) instead"
        ).format(node.inputs, dict(node.inputs))

        node.inputs[bus] = flow
        assert node.inputs == {bus: flow}, (
            "\n  Expected {} as `node.inputs`."
            + "\n  Got    : {} (== {}) instead"
        ).format({bus: flow}, node.inputs, dict(node.inputs))
        assert node.inputs[bus] == flow, (
            "\n  Expected {} as `node.inputs[bus]`."
            + "\n  Got    : {} instead"
        ).format(flow, node.inputs[bus])
        del node.inputs[bus]
        assert node.inputs == {}, (
            "\n  Expected an empty dictionary of inputs."
            + "\n  Got: {} (== {}) instead"
        ).format(node.inputs, dict(node.inputs))

    def test_output_input_symmetry_after_modification(self):
        n1 = Node("N1")
        n2 = Node("N2")
        flow = "flow"

        n1.outputs[n2] = flow
        assert n2.inputs == {n1: flow}

    def test_input_output_symmetry_after_modification(self):
        n1 = Node("N1")
        n2 = Node("N2")
        flow = "flow"

        n1.inputs[n2] = flow
        assert n2.outputs == {n1: flow}

    def test_updating_inputs(self):
        n1 = Node("N1")
        n2 = Node("N2")
        n1n2 = "n1n2"

        n2.inputs.update({n1: n1n2})
        assert n2.inputs == {n1: n1n2}
        assert n2.inputs[n1] == n1n2
        assert n1.outputs == {n2: n1n2}
        assert n1.outputs[n2] == n1n2

    def test_updating_outputs(self):
        n1 = Node("N1")
        n2 = Node("N2")
        n1n2 = "n1n2"

        n1.outputs.update({n2: n1n2})
        assert n2.inputs == {n1: n1n2}
        assert n2.inputs[n1] == n1n2
        assert n1.outputs == {n2: n1n2}
        assert n1.outputs[n2] == n1n2

    def test_error_for_duplicate_label_argument(self):
        """
        `Node.__init__` should fail if positional and keyword args collide.
        """
        with pytest.raises(TypeError):
            Node("Positional Label", label="Keyword Label")

    def test_entity_input_output_type_assertions(self):
        """
        `'Node'` should only accept `Node` instances
        as input/output targets.
        """
        with pytest.raises(ValueError):
            Node("An entity with an output", outputs={"Not a Node": "A Flow"})

        with pytest.raises(ValueError):
            Node("An entity with an input", inputs={"Not a Node": "A Flow"})

    def test_node_requires_label(self):
        """
        A `Node` without `label` cannot be constructed.
        """
        with pytest.raises(TypeError):
            _ = Node()

    def test_node_label_if_its_not_explicitly_specified(self):
        """If not explicitly given, a `Node`'s label is based on its `id`."""
        n = Node(label=None)
        assert "0x{:x}>".format(id(n)) in n.label

    def test_depth_default(self):
        n = Node(label="node")
        assert n.depth == 0


class TestsEdge:
    def setup_method(self):
        pass

    def test_edge_construction_side_effects(self):
        """Constructing an `Edge` should affect it's input/output `Node`s.

        When constructing an `Edge`, the `inputs` and `outputs` of its output
        and input `Node`s should be set appropriately.
        """
        source = Node(label="source")
        target = Node(label="target")
        edge = Edge(input_node=source, output_node=target)
        assert target in source.outputs, (
            "{} not in {} after constructing {}.".format(
                target, source.outputs, edge
            ),
        )
        assert source in target.inputs, (
            "{} not in {} after constructing {}.".format(
                source, target.outputs, edge
            ),
        )

    def test_label_as_positional_argument(self):
        o = object()
        n = Node(o)
        assert n.label is o, (
            "Setting `label` as positional parameter argument failed."
            "\n  Expected: {!r}"
            "\n  Got     : {!r}"
        ).format(o, n.label)

    def test_edge_failure_for_colliding_arguments(self):
        """
        `Edge` initialisation fails when colliding arguments are supplied.
        """
        with pytest.raises(ValueError):
            Edge(flow=object(), values=object())

    def test_alternative_edge_construction_from_mapping(self):
        """`Edge.from_object` treats mappings as keyword arguments."""
        i, o, f = (Node("input"), Node("output"), "flow")
        with pytest.raises(ValueError):
            Edge.from_object({"flow": i, "values": o})
        edge = Edge.from_object({"input_node": i, "output_node": o, "flow": f})
        assert edge.input == i
        assert edge.output == o
        assert edge.values == f
        assert edge.flow == f

    def test_flow_setter(self):
        """`Edge.flow`'s setter relays to `values`."""
        e = Edge(values="initial values")
        assert e.flow == "initial values"
        assert e.values == "initial values"
        e.flow = "new values set via `e.flow`"
        assert e.flow == "new values set via `e.flow`"
        assert e.values == "new values set via `e.flow`"


class TestsEnergySystemNodesIntegration:
    def setup_method(self):
        self.es = EnergySystem()

    def test_entity_registration(self):
        n1 = Node(label="<B1>")
        self.es.add(n1)
        assert self.es.node["<B1>"] == n1

        n2 = Node(label="<B2>")

        n3 = Node(label="<TF1>", inputs=[n1], outputs=[n2])
        self.es.add(n3, n2)
        assert self.es.node["<B2>"] == n2
        assert self.es.node["<TF1>"] == n3


def test_deprecated_classes():
    with pytest.warns(FutureWarning):
        Bus("bus")
    with pytest.warns(FutureWarning):
        Sink("sink")
    with pytest.warns(FutureWarning):
        Source("source")
    with pytest.warns(FutureWarning):
        Transformer("transformer")


def test_custom_properties():
    node0 = Node("n0")

    assert not node0.custom_properties

    node1 = Node(
        "n1",
        custom_properties={
            "foo": "bar",
            1: 2,
        },
    )
    assert node1.custom_properties["foo"] == "bar"
    assert node1.custom_properties[1] == 2


def test_comparision():
    node0 = Node(label=0)
    node1 = Node(label=2)
    node2 = Node(label=-5)

    assert node0 < node1
    assert node0 > node2
