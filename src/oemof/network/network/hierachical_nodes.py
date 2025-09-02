# -*- coding: utf-8 -*-
"""This package contains the differnt types of hierachical Nodes for
modelling an energy system graph.

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <krien@uni-bremen.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>

SPDX-License-Identifier: MIT
"""

from .helpers import HierachicalLabel
from .nodes import Node


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
        if not isinstance(label, HierachicalLabel):
            if parent_node is not None:
                if not isinstance(parent_node, SubNetwork):
                    raise TypeError(
                        "The parent_node of an oemof.network.Node instance "
                        "can only be of type oemof.network.SubNetwork"
                    )
            label = HierachicalLabel(label=label, parent=parent_node)
        super().__init__(
            label=label,
            inputs=inputs,
            outputs=outputs,
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
        if not isinstance(label, HierachicalLabel):
            label = HierachicalLabel(label=label, parent=parent_node)
        super().__init__(label=label, custom_properties=custom_properties)

        self.__subnodes = []

    @property
    def subnodes(self):
        """Subnodes of the SubNetwork

        It is deliberate provided as a tuple to prevent user to append subnodes
        other than with API methods
        """
        return tuple([sn for sn in self.__subnodes])

    def subnode(self, class_, label, *args, **kwargs):
        """Create a subnode and add it to this `SubNetwork`.

        Create a subnode by calling `class_(label, *args, **kwargs)` and
        `append` the result to `self.subnodes`.
        The purpose of this wrapper is to make sure that subnodes are
        always `label`led with a `HierachicalLabel`.
        This is useful to ensure that the `label` of the subnode is unique
        within the `SubNetwork` and that it can be identified as a subnode of
        the `SubNetwork`.

        Parameters
        ----------
        class_: type
            The class of the subnode to create. This class must be a subclass
            of `Node`.
        label: hashable
            The label to use for the subnode.
        *args, **kwargs:
            Additional positional and keyword arguments that will be passed to
            the constructor of `class_` when creating the subnode.

        Returns
        -------
        :class:`Node`
            The newly created subnode, which is also appended to
            `self.subnodes`.


        Examples
        --------
        Create a subnode of type `Bus` with the given `label`, `inputs` and
        `outputs` and append it to the `subnodes` of this `SubNetwork`.

        When
        >>> from oemof.network import SubNetwork, Node, Edge
        >>> subnetwork = SubNetwork("subnetwork")
        >>> input = output = Node("input")
        >>>
        >>> # Create a subnode of type `Node` using this convenience function
        ... bus = subnetwork.subnode(
        ...     Node, "bus", inputs={input: Edge()}, outputs={output: Edge()}
        ... )

        """
        subnode = class_(
            label=HierachicalLabel(label=label, parent=self), *args, **kwargs
        )
        self.__subnodes.append(subnode)
        return subnode
