# -*- coding: utf-8 -*-
"""This package contains the differnt types of hierachical Nodes for
modelling an energy system graph.

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <krien@uni-bremen.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>
SPDX-FileCopyrightText: Pierre-Francois Duc <pierre-francois@rl-institut.de>

SPDX-License-Identifier: MIT
"""
from collections import deque

from .nodes import Node


class HierachicalLabel(tuple):
    """Alias class to allow tuples in labels"""

    pass


class AtomicNode(Node):
    def __init__(
        self,
        label,
        *,
        inputs=None,
        outputs=None,
        parent_node=None,
        custom_properties=None,
    ):
        super().__init__(
            label=label,
            inputs=inputs,
            outputs=outputs,
            parent_node=parent_node,
            custom_properties=custom_properties,
        )


class SubNetwork(Node):
    def __init__(
        self,
        label,
        *,
        parent_node=None,
        custom_properties=None,
    ):
        super().__init__(
            label=label,
            parent_node=parent_node,
            custom_properties=custom_properties,
        )

        self.__subnodes = []
        self.__energy_system = None

        # TODO: Try to avoid this local `import`.
        from ..energy_system import EnergySystem

        EnergySystem.signals[EnergySystem.add].connect(
            self.add_subnodes, sender=self
        )

    @property
    def subnodes(self):
        """Subnodes of the SubNetwork

        It is deliberately provided as a tuple to prevent user to append
        subnodes other than with API methods.
        """
        return tuple([sn for sn in self.__subnodes])

    def add_subnodes(self, node, **kwargs):
        """Add subnodes to an EnergySystem.

        This is meant to be used as an event callback that is called when this
        node is added to an EnergySystem, to add the child nodes to the
        EnergySystem, too.
        """
        # TODO:
        #    Explain why the `node` argument is necessary.
        if self is not node:
            raise ValueError("Call needs to be obj.add_subnodes(obj).")
        self.__energy_system = kwargs["EnergySystem"]
        deque(
            (kwargs["EnergySystem"].add(sn) for sn in self.__subnodes),
            maxlen=0,
        )

    def subnode(self, class_, local_name, *args, **kwargs):
        """Create a subnode and add it to this `SubNetwork`.

        Create a subnode by calling `class_(label, *args, **kwargs)` and
        `append` the result to `self.__subnodes`.
        The purpose of this wrapper is to make sure that subnodes are
        always `label` led with a unique label.
        This is useful because this allows giving the same `local_name`
        to `Node`s in multiple `SubNetwork` s.

        Parameters
        ----------
        class_: type
            The class of the subnode to create. This class must be a subclass
            of `Node`.
        local_name: hashable
            The label to use for the subnode.
        *args, **kwargs:
            Additional positional and keyword arguments that will be passed to
            the constructor of `class_` when creating the subnode.

        Returns
        -------
        :class: Node
            The newly created subnode, which is also appended to
            `self.subnodes`.


        Examples
        --------
        Create a subnode of type `Bus` with a `label` based on the the given
        `local_name`, `inputs` and `outputs` and append it to the
        `subnodes` of this `SubNetwork`.

        When
        >>> from oemof.network import SubNetwork, Node, Edge
        >>> subnetwork = SubNetwork("subnetwork")
        >>> input = output = Node("input")
        >>> # Create a subnode of type `Node` using this convenience function
        >>> bus = subnetwork.subnode(
        ...     Node, "bus", inputs={input: Edge()}, outputs={output: Edge()}
        ... )
        """
        if isinstance(self.label, HierachicalLabel):
            label = HierachicalLabel([*self.label, local_name])
        else:
            label = HierachicalLabel([self.label, local_name])
        subnode = class_(
            label=label,
            parent_node=self,
            *args,
            **kwargs,
        )
        self.__subnodes.append(subnode)
        if self.__energy_system is not None:
            self.__energy_system.add(subnode)
        return subnode
