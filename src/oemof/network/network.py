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

import warnings
from collections import UserDict as UD
from collections import namedtuple as NT
from collections.abc import Mapping
from collections.abc import MutableMapping as MM
from contextlib import contextmanager
from functools import total_ordering

# TODO:
#
#   * Only allow setting a Node's label if `_delay_registration_` is active
#     and/or the node is not yet registered.
#   * Only allow setting an Edge's input/output if it is None
#   * Document the `register` method. Maybe also document the
#     `_delay_registration_` attribute and make it official. This could also be
#     a good chance to finally use `blinker` to put an event on
#     `_delay_registration_` for deletion/assignment to trigger registration.
#     I always had the hunch that using blinker could help to straighten out
#     that delayed auto registration hack via partial functions. Maybe this
#     could be a good starting point for this.
#   * Finally get rid of `Entity`.
#


class Inputs(MM):
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


class Outputs(UD):
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


class Metaclass(type):
    """The metaclass for objects in an oemof energy system."""

    @property
    def registry(cls):
        warnings.warn(cls.registry_warning)
        return cls._registry

    @registry.setter
    def registry(cls, registry):
        warnings.warn(cls.registry_warning)
        cls._registry = registry


@total_ordering
class Node(metaclass=Metaclass):
    """Represents a Node in an energy system graph.

    Abstract superclass of the two general types of nodes of an energy system
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

    registry_warning = FutureWarning(
        "\nAutomatic registration of `Node`s is deprecated in favour of\n"
        "explicitly adding `Node`s to an `EnergySystem` via "
        "`EnergySystem.add`.\n"
        "This feature, i.e. the `Node.registry` attribute and functionality\n"
        "pertaining to it, will be removed in future versions.\n"
    )

    _registry = None
    __slots__ = ["_label", "_in_edges", "_inputs", "_outputs"]

    def __init__(self, *args, **kwargs):
        args = list(args)
        args.reverse
        self._inputs = Inputs(self)
        self._outputs = Outputs(self)
        self.cell_list = kwargs.get('cell_list', [])
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
            assert isinstance(i, Node), (
                "\n\nInput\n\n  {!r}\n\nof\n\n  {!r}\n\n"
                "not an instance of Node, but of {}."
            ).format(i, self, type(i))
            self._in_edges.add(i)
            try:
                flow = kwargs["inputs"].get(i)
            except AttributeError:
                flow = None
            edge = globals()["Edge"].from_object(flow)
            edge.input = i
            edge.output = self
        for o in kwargs.get("outputs", {}):
            assert isinstance(o, Node), (
                "\n\nOutput\n\n  {!r}\n\nof\n\n  {!r}\n\n"
                "not an instance of Node, but of {}."
            ).format(o, self, type(o))
            try:
                flow = kwargs["outputs"].get(o)
            except AttributeError:
                flow = None
            edge = globals()["Edge"].from_object(flow)
            edge.input = self
            edge.output = o

        self.register()
        """
        This could be slightly more efficient than the loops above, but doesn't
        play well with the assertions:

        inputs = kwargs.get('inputs', {})
        self.in_edges = {
                Edge(input=i, output=self,
                    flow=None if not isinstance(inputs, MM) else inputs[i])
                for i in inputs}

        outputs = kwargs.get('outputs', {})
        self.out_edges = {
                Edge(input=self, output=o,
                    flow=None if not isinstance(outputs, MM) else outputs[o])
                for o in outputs}
        self.edges = self.in_edges.union(self.out_edges)
        """

    def register(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            registry = __class__.registry

        if registry is not None and not getattr(
            self, "_delay_registration_", False
        ):
            __class__.registry.add(self)

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
        """object :
        If this node was given a `label` on construction, this
        attribute holds the actual object passed as a parameter. Otherwise
        :py:`node.label` is a synonym for :py:`str(node)`.
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
        Dictionary mapping input :class:`Nodes <Node>` :obj:`n` to
        :class:`Edge`s from :obj:`n` into :obj:`self`.
        If :obj:`self` is an :class:`Edge`, returns a dict containing the
        :class:`Edge`'s single input node as the key and the flow as the value.
        """
        return self._inputs

    @property
    def outputs(self):
        """dict:
        Dictionary mapping output :class:`Nodes <Node>` :obj:`n` to
        :class:`Edges` from :obj:`self` into :obj:`n`.
        If :obj:`self` is an :class:`Edge`, returns a dict containing the
        :class:`Edge`'s single output node as the key and the flow as the
        value.
        """
        return self._outputs


EdgeLabel = NT("EdgeLabel", ["input", "output"])


class Edge(Node):
    """
    :class:`Bus`es/:class:`Component`s are always connected by an
    :class:`Edge`.

    :class:`Edge`s connect a single non-:class:`Edge` Node with another. They
    are directed and have a (sequence of) value(s) attached to them so they can
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
        if input is None or output is None:
            self._delay_registration_ = True
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
            argument to `Edge`s constructor.
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
            del self._delay_registration_
            self.register()
            i.outputs[self.output] = self

    @property
    def output(self):
        return self.label.output

    @output.setter
    def output(self, o):
        old_output = self.output
        self.label = Edge.Label(self.label.input, o)
        if old_output is None and o is not None and self.input is not None:
            del self._delay_registration_
            self.register()
            o.inputs[self.input] = self


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


@contextmanager
def registry_changed_to(r):
    """
    Override registry during execution of a block and restore it afterwards.
    """
    backup = Node.registry
    Node.registry = r
    yield
    Node.registry = backup


def temporarily_modifies_registry(f):
    """Decorator that disables `Node` registration during `f`'s execution.

    It does so by setting `Node.registry` to `None` while `f` is executing, so
    `f` can freely set `Node.registry` to something else. The registration's
    original value is restored afterwards.
    """

    def result(*xs, **ks):
        with registry_changed_to(None):
            return f(*xs, **ks)

    return result
