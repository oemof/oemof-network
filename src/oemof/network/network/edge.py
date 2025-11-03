# -*- coding: utf-8 -*-

"""This package contains the class Edge used to model
energy systems.

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <uwe.krien@ifam.fraunhofer.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>

SPDX-License-Identifier: MIT
"""

from collections import namedtuple
from collections.abc import Mapping

from .entity import Entity


class Edge(Entity):
    """
    :class:`Bus`es/:class:`Component`s are always connected by an
    :class:`Edge`.

    :class:`Edge`s connect a single :class:`Node` with another. They are
    directed and have a (sequence of) value(s) attached to them, so they can
    be used to represent a flow from a source/an input to a target/an output.

    Parameters
    ----------
    input, output: :class:`Bus` or :class:`Component`, optional
    flow, values: object, optional
        The (list of) object(s) representing the values flowing from this
        edge's input into its output. Note that these two names are aliases of
        each other, so `flow` and `values` are mutually exclusive.

    Note that all of these parameters are also set as attributes with the same
    name.
    """

    Label = namedtuple("EdgeLabel", ["input", "output"])

    def __init__(
        self,
        input_node=None,
        output_node=None,
        flow=None,
        values=None,
        *,
        custom_properties=None,
    ):
        if flow is not None and values is not None:
            raise ValueError(
                "\n\n`Edge`'s `flow` and `values` keyword arguments are "
                "aliases of each other,\nso they're mutually exclusive.\n"
                "You supplied:\n"
                f"    `flow`  : {flow}\n"
                f"    `values`: {values}\n"
                "Choose one."
            )
        super().__init__(
            label=Edge.Label(input_node, output_node),
            custom_properties=custom_properties,
        )
        self.values = values if values is not None else flow
        if input_node is not None and output_node is not None:
            input_node.outputs[output_node] = self

    @classmethod
    def from_object(cls, o):
        """Creates an `Edge` instance from a single object.

        This method inspects its argument and does something different
        depending on various cases:

          * If `o` is an instance of `Edge`, `o` is returned unchanged.
          * If `o` is a `Mapping`, the instance is created by calling
            `cls(**o)`,
          * In all other cases, `o` will be used as the `values` keyword
            argument to `Edge`'s constructor.
        """
        if isinstance(o, Edge):
            return o
        elif isinstance(o, Mapping):
            return cls(**o)
        else:
            return Edge(values=o)

    @property
    def flow(self):
        return self.values

    @flow.setter
    def flow(self, values):
        self.values = values

    @property
    def input(self):
        return self.label.input

    @input.setter
    def input(self, i):
        old_input = self.input
        self._label = Edge.Label(i, self.label.output)
        if old_input is None and i is not None and self.output is not None:
            i.outputs[self.output] = self

    @property
    def output(self):
        return self.label.output

    @output.setter
    def output(self, o):
        old_output = self.output
        self._label = Edge.Label(self.label.input, o)
        if old_output is None and o is not None and self.input is not None:
            o.inputs[self.input] = self
