# -*- coding: utf-8 -*-

"""Basic EnergySystem class

This file is part of project oemof.network. It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location oemof/oemof/energy_system.py

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <uwe.krien@ifam.fraunhofer.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>

SPDX-License-Identifier: MIT
"""

import logging
import os
import warnings
from collections import deque

import blinker
import dill as pickle
import networkx

from oemof.network.groupings import DEFAULT as BY_UID
from oemof.network.groupings import Entities
from oemof.network.groupings import Grouping


class EnergySystem:
    r"""Defining an energy system to use oemof's solver libraries.

    Parameters
    ----------
    groupings : list
        The elements of this list are used to construct :class:`Groupings
        <oemof.core.energy_system.Grouping>` or they are used directly if they
        are instances of :class:`Grouping <oemof.core.energy_system.Grouping>`.
        These groupings are then used to aggregate the Nodes added to this
        energy system into :attr:`groups`.
        By default, there'll always be one group for each :attr:`uid
        <oemof.network.Node.uid>` containing exactly the entity with the
        given :attr:`uid <oemof.network.Node.uid>`.
        See the :ref:`examples <energy-system-examples>` for more information.
    nodes : list of :class:`Node <oemof.core.network.Node>`, optional
        A list containing the already existing :class:`Entities
        <oemof.network.Node>` that should be part of the energy system.
        Stored in the :attr:`nodes` attribute.
        Defaults to `[]` if not supplied.

    Attributes
    ----------
    nodes : list of :class:`Node <oemof.network.Node>`
        A list containing the :class:`Entities <oemof.network.Node>`
        that comprise the energy system.
    groups : dict


    .. _energy-system-examples:
    Examples
    --------

    Regardles of additional groupings, :class:`Nodes
    <oemof.network.Node>` will always be grouped by their :attr:`uid
    <oemof.network.Node.uid>`:

    >>> from oemof.network.network import Node
    >>> es = EnergySystem()
    >>> bus = Node(label='electricity')
    >>> es.add(bus)
    >>> bus is es.groups['electricity']
    True
    >>> es.dump("test.dump", consider_dpath=False)  # doctest: +ELLIPSIS
    'Attributes dumped to ...
    >>> es = EnergySystem()
    >>> es.restore("test.dump", consider_dpath=False)  # doctest: +ELLIPSIS
    'Attributes restored from ...
    >>> bus is es.groups['electricity']
    False
    >>> es.groups['electricity']
    "<oemof.network.network.nodes.Node: 'electricity'>"

    For simple user defined groupings, you can just supply a function that
    computes a key from an :class:`entity <oemof.network.Node>` and the
    resulting groups will be sets of :class:`Nodes
    <oemof.network.Entity>` stored under the returned keys, like in this
    example, where :class:`Nodes <oemof.network.Entity>` are grouped by
    their `type`:

    >>> es = EnergySystem(groupings=[type])
    >>> buses = set(Node(label="Node {}".format(i)) for i in range(9))
    >>> es.add(*buses)
    >>> class Sink(Node):
    ...     pass
    >>> components = set(Sink(label="Component {}".format(i))
    ...                   for i in range(9))
    >>> es.add(*components)
    >>> buses == es.groups[Node]
    True
    >>> components == es.groups[Sink]
    True

    """

    signals = {}
    """A dictionary of blinker_ signals emitted by energy systems.

    Currently only one signal is supported. This signal is emitted whenever a
    `node <oemof.network.Node>` is `add`ed to an energy system. The
    signal's `sender` is set to the `node <oemof.network.Node>` that got
    added to the energy system so that `node <oemof.network.Node>` have an
    easy way to only receive signals for when they themselves get added to an
    energy system.

    .. _blinker: https://blinker.readthedocs.io/en/stable/
    """

    def __init__(
        self,
        *,
        groupings=None,
        results=None,
        timeindex=None,
        timeincrement=None,
        temporal=None,
        nodes=None,
        entities=None,
    ):
        if groupings is None:
            groupings = []
        if entities is not None:
            warnings.warn(
                "Parameter 'entities' is deprecated, use 'nodes'"
                + " instead. Will overwrite nodes.",
                FutureWarning,
            )
            nodes = entities
        if nodes is None:
            nodes = []

        self._first_ungrouped_node_index_ = 0
        self._groups = {}
        self._groupings = [BY_UID] + [
            g if isinstance(g, Grouping) else Entities(g) for g in groupings
        ]
        self._nodes = {}
        self._node_strings = set()

        for attr in ["results", "timeindex", "timeincrement", "temporal"]:
            if eval(attr) is not None:
                warnings.warn(
                    f"Setting {attr} of an EnergySystem at the level of"
                    + " oemof.network is deprecated, as it is not used"
                    + " by this library.",
                    category=FutureWarning,
                )
                setattr(self, attr, eval(attr))

        self.add(*nodes)

    def add(self, *nodes):
        """Add :class:`nodes <oemof.network.Node>` to this energy system."""
        new_nodes = {node.label: node for node in nodes}
        new_node_strings = {str(node) for node in nodes}
        if self._node_strings.isdisjoint(new_node_strings):
            self._node_strings.update(new_node_strings)
            self._nodes.update(new_nodes)
        else:
            common_strings = sorted(
                list(self._node_strings & new_node_strings)
            )
            raise ValueError(
                "EnergySystem already contains Node(s) with the following"
                + ' string representation: "'
                + '", "'.join(common_strings)
                + '". This can be because'
                + " a) you try to add one Node more than once, "
                + " b) multiple Nodes have identical labels, or"
                + " c) multiple labels have the same string representation."
            )
        self._nodes.update(new_nodes)
        for n in nodes:
            self.signals[type(self).add].send(n, EnergySystem=self)

    signals[add] = blinker.signal(add)

    @property
    def groups(self):
        gs = self._groups
        deque(
            (
                g(n, gs)
                for g in self._groupings
                for n in list(self.nodes)[self._first_ungrouped_node_index_ :]
            ),
            maxlen=0,
        )
        self._first_ungrouped_node_index_ = len(self.nodes)
        return self._groups

    @property
    def node(self):
        return self._nodes

    @property
    def nodes(self):
        return self._nodes.values()

    def flows(self):
        return {
            (source, target): source.outputs[target]
            for source in self.nodes
            for target in source.outputs
        }

    def check(self):
        error_message = (
            "Node {n} not part of EnergySystem but Flow ({i}, {o}) exists."
        )

        for n in self.nodes:
            for o in n.outputs.keys():
                if o not in self.nodes:
                    raise RuntimeError(error_message.format(n=n, i=n, o=o))
            for i in n.inputs.keys():
                if i not in self.nodes:
                    raise RuntimeError(error_message.format(n=n, i=i, o=n))

    def to_networkx(
        self,
        add_implicit_edges: bool = False,
    ) -> networkx.DiGraph:
        """
        Create a `networkx.DiGraph` from the EnergySystem.
        See https://networkx.org/documentation/ for more information.
        """
        graph = networkx.DiGraph()

        for label in self._node_strings:
            graph.add_node(label, label=label)

        explicit_edges = self.flows()
        edges = set(explicit_edges)

        if add_implicit_edges:
            for s, t in explicit_edges:
                graph.add_edge(str(s), str(t))
                s_p = s.parent
                while s_p is not None:
                    edges.add((str(s_p), str(t)))
                    s_p = s_p.parent
                    t_p = t.parent
                    while t_p is not None:
                        edges.add((str(s_p), str(t_p)))
                        t_p = t_p.parent

        for s, t in edges:
            graph.add_edge(s, t)

        return graph

    # Begin: to be removed in a future version
    @staticmethod
    def _deprecated_path_handling(dpath, filename, consider_dpath):
        if consider_dpath:
            if dpath is None:
                bpath = os.path.join(os.path.expanduser("~"), ".oemof")
                if not os.path.isdir(bpath):
                    os.mkdir(bpath)
                dpath = os.path.join(bpath, "dumps")
                if not os.path.isdir(dpath):
                    os.mkdir(dpath)

                warnings.warn(
                    "Default directory for oemof dumps will change"
                    + " from ~/.oemof/dumps/ to ./ in a future version."
                    + " Set 'consider_dpath' to False to already use"
                    + " the new default.",
                    FutureWarning,
                )
            else:
                warnings.warn(
                    "Parameter 'dpath' will be removed in a future"
                    + " version. You can give the directory as part"
                    + " of the filename and set 'consider_dpath' to"
                    + " False to suppress this waring.",
                    FutureWarning,
                )
            if filename is None:
                filename = "es_dump.oemof"

            filename = os.path.join(dpath, filename)
        else:
            if dpath is not None:
                if filename is None:
                    # Interpret dpath as intended to be filename,
                    # as it might be given as positional argument.
                    filename = dpath
                else:
                    raise ValueError(
                        "You set filename and dpath but told that"
                        + " dpath should be ignored."
                    )

        return filename
        # End: to be removed in a future version

    def dump(
        self,
        dpath=None,  # to be removed in a future version
        filename=None,
        consider_dpath=True,  # to be removed in a future version
    ):
        """Dump an EnergySystem instance.

        Parameters
        ----------
        dpath : str
            Path to write your dump in.
        filename : str
            Filename to write your dump to.
        consider_dpath : bool
            Use separate parameters for path (default: ~/.oemof/) and filename.
        """
        # Start: to be removed in a future version
        filename = self._deprecated_path_handling(
            dpath, filename, consider_dpath
        )
        # End: to be removed in a future version

        pickle.dump(self.__dict__, open(filename, "wb"))

        msg = f"Attributes dumped to {filename}."
        logging.debug(msg)
        return msg

    def restore(
        self,
        dpath=None,  # to be removed in a future version
        filename=None,
        consider_dpath=True,  # to be removed in a future version
    ):
        """Restore an EnergySystem instance.

        Parameters
        ----------
        dpath : str
            Path to write your dump in.
        filename : str
            Filename to write your dump to.
        consider_dpath : bool
            Use separate parameters for path (defualt: ~/.oemof/) and filename.
        """
        logging.info(
            "Restoring attributes will overwrite existing attributes."
        )
        # Start: to be removed in a future version
        filename = self._deprecated_path_handling(
            dpath, filename, consider_dpath
        )
        # End: to be removed in a future version

        self.__dict__ = pickle.load(open(filename, "rb"))

        msg = f"Attributes restored from {filename}."
        logging.debug(msg)
        return msg
