# -*- coding: utf-8 -*-
"""This package contains the differnt types of Node for
modelling an energy system graph.

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <krien@uni-bremen.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>

SPDX-License-Identifier: MIT
"""

from .edge import Edge
from .entity import Entity


def _convert_to_dict(arg):
    if isinstance(arg, dict):
        return arg
    else:
        return dict.fromkeys(arg)


_msg = "{} {!r} of {!r} not an instance of Node but of {}."


class Node(Entity):
    r"""A Node of an energy system graph.

    Parameters
    ----------
    label : (See documentation of class `Entity`)
    inputs: list or dict, optional
        Either a list of this nodes' input nodes or a dictionary mapping input
        nodes to corresponding inflows (i.e. input values).
    outputs: list or dict, optional
        Either a list of this nodes' output nodes or a dictionary mapping
        output nodes to corresponding outflows (i.e. output values).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._in_edges = set()

        inputs = kwargs.get("inputs", {})
        outputs = kwargs.get("outputs", {})
        self.add_inputs(inputs)
        self.add_outputs(outputs)

    def add_inputs(self, inputs):
        input_dict = _convert_to_dict(inputs)
        for i, e in input_dict.items():
            if not isinstance(i, Node):
                raise ValueError(_msg.format("Input", i, self, type(i)))
            self._in_edges.add(i)

            edge = Edge.from_object(e)
            edge.input = i
            edge.output = self

    def add_outputs(self, outputs):
        output_dict = _convert_to_dict(outputs)
        for o, f in output_dict.items():
            if isinstance(o, Node):
                o.add_inputs({self: f})
            else:
                raise ValueError(_msg.format("Input", o, self, type(o)))


class Bus(Node):
    pass


class Component(Node):
    pass


class Sink(Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Source(Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Transformer(Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
