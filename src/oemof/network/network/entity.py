# -*- coding: utf-8 -*-

"""This package contains the abstract entity classes used to model
energy systems.

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <uwe.krien@ifam.fraunhofer.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>

SPDX-License-Identifier: MIT
"""

from functools import total_ordering


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

    custom_properties: `dict`
        This dictionary that can be used to store information that can be used
        to easily attach custom information to any Entity.
    """

    def __init__(self, label, *, custom_properties=None):
        self._label = label
        if custom_properties is None:
            custom_properties = {}
        self.custom_properties = custom_properties

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
        try:
            return self._label if self._label is not None else self._id_label
        except AttributeError:  # Workaround for problems with pickle/dill
            return hash(self._id_label)

    @property
    def _id_label(self):
        return "<{} #0x{:x}>".format(type(self).__name__, id(self))
