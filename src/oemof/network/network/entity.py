# -*- coding: utf-8 -*-

"""This package contains the abstract entity classes used to model
energy systems.

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <krien@uni-bremen.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>

SPDX-License-Identifier: MIT
"""

from functools import total_ordering

from .helpers import Inputs
from .helpers import Outputs


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
