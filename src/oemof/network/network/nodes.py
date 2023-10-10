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

import warnings

from .edge import Edge
from .entity import Entity


class Node(Entity):
    r"""A Node of an energy system graph.

    Parameters
    ----------
    label : (See documentation of class `Entity`)
    inputs: list or dict, optional
        Either a list of this nodes' input nodes or a dictionary mapping input
        nodes to corresponding inflows (i.e. input values).
        List will be converted to dictionary with values set to None.
    outputs: list or dict, optional
        Either a list of this nodes' output nodes or a dictionary mapping
        output nodes to corresponding outflows (i.e. output values).
        List will be converted to dictionary with values set to None.

    Attributes
    ----------
    inputs: dict
        A dictionary mapping input nodes to corresponding inflows.
    outputs: dict
        A dictionary mapping output nodes to corresponding outflows.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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


_deprecation_warning = (
    "Usage of {} is deprecated. Use oemof.network.Node instead."
)


class Bus(Node):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            _deprecation_warning.format(type(self)),
            FutureWarning,
        )
        super().__init__(*args, **kwargs)


class Component(Node):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            _deprecation_warning.format(type(self)),
            FutureWarning,
        )
        super().__init__(*args, **kwargs)


class Sink(Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Source(Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Transformer(Component):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
