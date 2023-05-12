# -*- coding: utf-8 -*-

"""This package (along with its subpackages) contains the classes used to model
energy systems. An energy system is modelled as a graph/network of entities
with very specific constraints on which types of entities are allowed to be
connected.

This file is part of project oemof (github.com/oemof/oemof). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location oemof/oemof/network.py

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <krien@uni-bremen.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>

SPDX-License-Identifier: MIT
"""

from collections import UserDict
from collections import namedtuple
from collections.abc import Mapping
from collections.abc import MutableMapping
from functools import total_ordering


class Inputs(MutableMapping):
    """A special helper to map `n1.inputs[n2]` to `n2.outputs[n1]`."""

    def __init__(self, target):
        self.target = target

    def __getitem__(self, key):
        return key.outputs.__getitem__(self.target)

    def __delitem__(self, key):
        return key.outputs.__delitem__(self.target)

    def __setitem__(self, key, value):
        return key.outputs.__setitem__(self.target, value)

    def __iter__(self):
        return iter(self.target._in_edges)

    def __len__(self):
        return self.target._in_edges.__len__()

    def __repr__(self):
        return repr(
            "<{0.__module__}.{0.__name__}: {1!r}>".format(
                type(self), dict(self)
            )
        )


class Outputs(UserDict):
    """
    Helper that intercepts modifications to update `Inputs` symmetrically.
    """

    def __init__(self, source):
        self.source = source
        super().__init__()

    def __delitem__(self, key):
        key._in_edges.remove(self.source)
        return super().__delitem__(key)

    def __setitem__(self, key, value):
        key._in_edges.add(self.source)
        return super().__setitem__(key, value)


@total_ordering
class Entity:
    """Represents an Entity in an energy system graph.

    Abstract superclass of the general types of entities of an energy system
    graph, collecting attributes and operations common to all types of nodes.
    Users should neither instantiate nor subclass this, but use
    :class:`Component`, :class:`Bus`, :class:`Edge` or one of their subclasses
    instead.

    .. role:: python(code)
      :language: python

    Parameters
    ----------
    label: `hashable`, optional
        Used as the string representation of this node. If this parameter is
        not an instance of :class:`str` it will be converted to a string and
        the result will be used as this node's :attr:`label`, which should be
        unique with respect to the other nodes in the energy system graph this
        node belongs to. If this parameter is not supplied, the string
        representation of this node will instead be generated based on this
        nodes `class` and `id`.
    inputs: list or dict, optional
        Either a list of this nodes' input nodes or a dictionary mapping input
        nodes to corresponding inflows (i.e. input values).
    outputs: list or dict, optional
        Either a list of this nodes' output nodes or a dictionary mapping
        output nodes to corresponding outflows (i.e. output values).

    Attributes
    ----------
    __slots__: str or iterable of str
        See the Python documentation on `__slots__
        <https://docs.python.org/3/reference/datamodel.html#slots>`_ for more
        information.
    """

    __slots__ = ["_label", "_in_edges", "_inputs", "_outputs"]

    def __init__(self, *args, **kwargs):
        args = list(args)
        self._inputs = Inputs(self)
        self._outputs = Outputs(self)
        for optional in ["label"]:
            if optional in kwargs:
                if args:
                    raise (
                        TypeError(
                            (
                                "{}.__init__()\n"
                                "  got multiple values for argument '{}'"
                            ).format(type(self), optional)
                        )
                    )
                setattr(self, "_" + optional, kwargs[optional])
            else:
                if args:
                    setattr(self, "_" + optional, args.pop())
        self._in_edges = set()
        for i in kwargs.get("inputs", {}):
            if not isinstance(i, Entity):
                msg = (
                    "Input {!r} of {!r} not an instance of Entity but of {}."
                ).format(i, self, type(i))
                raise ValueError(msg)
            self._in_edges.add(i)
            try:
                flow = kwargs["inputs"].get(i)
            except AttributeError:
                flow = None
            edge = globals()["Edge"].from_object(flow)
            edge.input = i
            edge.output = self
        for o in kwargs.get("outputs", {}):
            if not isinstance(o, Entity):
                msg = (
                    "Output {!r} of {!r} not an instance of Entity but of {}."
                ).format(o, self, type(o))
                raise ValueError(msg)
            try:
                flow = kwargs["outputs"].get(o)
            except AttributeError:
                flow = None
            edge = globals()["Edge"].from_object(flow)
            edge.input = self
            edge.output = o
        """
        This could be slightly more efficient than the loops above, but doesn't
        play well with the assertions:

        inputs = kwargs.get('inputs', {})
        self.in_edges = {
            Edge(
                input=i,
                output=self,
                flow=None if not isinstance(inputs, MutableMapping)
                          else inputs[i]
            )
            for i in inputs
        }

        outputs = kwargs.get('outputs', {})
        self.out_edges = {
            Edge(
                input=self,
                output=o,
                flow=None if not isinstance(outputs, MutableMapping)
                          else outputs[o]
            )
            for o in outputs}
        self.edges = self.in_edges.union(self.out_edges)
        """

    def __eq__(self, other):
        return id(self) == id(other)

    def __lt__(self, other):
        return str(self) < str(other)

    def __hash__(self):
        return hash(self.label)

    def __str__(self):
        return str(self.label)

    def __repr__(self):
        return repr(
            "<{0.__module__}.{0.__name__}: {1!r}>".format(
                type(self), self.label
            )
        )

    @property
    def label(self):
        """
        If this node was given a `label` on construction, this
        attribute holds the actual object passed as a parameter. Otherwise
        `node.label` is a synonym for `str(node)`.
        """
        return (
            self._label
            if hasattr(self, "_label")
            else "<{} #0x{:x}>".format(type(self).__name__, id(self))
        )

    @label.setter
    def label(self, label):
        self._label = label

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


EdgeLabel = namedtuple("EdgeLabel", ["input", "output"])


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

    Label = EdgeLabel

    def __init__(
        self, input=None, output=None, flow=None, values=None, **kwargs
    ):
        if flow is not None and values is not None:
            raise ValueError(
                "\n\n`Edge`'s `flow` and `values` keyword arguments are "
                "aliases of each other,\nso they're mutually exclusive.\n"
                "You supplied:\n"
                + "    `flow`  : {}\n".format(flow)
                + "    `values`: {}\n".format(values)
                + "Choose one."
            )
        super().__init__(label=Edge.Label(input, output))
        self.values = values if values is not None else flow
        if input is not None and output is not None:
            input.outputs[output] = self

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
        self.label = Edge.Label(i, self.label.output)
        if old_input is None and i is not None and self.output is not None:
            i.outputs[self.output] = self

    @property
    def output(self):
        return self.label.output

    @output.setter
    def output(self, o):
        old_output = self.output
        self.label = Edge.Label(self.label.input, o)
        if old_output is None and o is not None and self.input is not None:
            o.inputs[self.input] = self


class Node(Entity):
    pass


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
