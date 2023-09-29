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
from .helpers import Inputs
from .helpers import Outputs


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

    __slots__ = ["_in_edges", "_inputs", "_outputs"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._inputs = Inputs(self)
        self._outputs = Outputs(self)
        self._in_edges = set()

        msg = "{} {!r} of {!r} not an instance of Node but of {}."

        for i in kwargs.get("inputs", {}):
            if not isinstance(i, Node):
                raise ValueError(msg.format("Input", i, self, type(i)))
            self._in_edges.add(i)
            try:
                flow = kwargs["inputs"].get(i)
            except AttributeError:
                flow = None
            edge = Edge.from_object(flow)
            edge.input = i
            edge.output = self
        for o in kwargs.get("outputs", {}):
            if not isinstance(o, Node):
                raise ValueError(msg.format("Output", o, self, type(o)))
            try:
                flow = kwargs["outputs"].get(o)
            except AttributeError:
                flow = None
            edge = Edge.from_object(flow)
            edge.input = self
            edge.output = o

    @property
    def inputs(self):
        """dict:
        Dictionary mapping input :class:`Entities <Entity>` :obj:`n` to
        :class:`Edge`s from :obj:`n` into :obj:`self`.
        If :obj:`self` is an :class:`Edge`, returns a dict containing the
        :class:`Edge`'s single input node as the key and the flow as the value.
        """
        return self._inputs

    @property
    def outputs(self):
        """dict:
        Dictionary mapping output :class:`Entities <Entity>` :obj:`n` to
        :class:`Edges` from :obj:`self` into :obj:`n`.
        If :obj:`self` is an :class:`Edge`, returns a dict containing the
        :class:`Edge`'s single output node as the key and the flow as the
        value.
        """
        return self._outputs


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
