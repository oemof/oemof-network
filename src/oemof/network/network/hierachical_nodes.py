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

from collections import deque

from .nodes import Node


class HierachicalLabel:
    # TODO: Find a better place for the `interface` parameter/attribute.
    #       (See the `git blame` of these lines for details.)
    def __init__(self, label, parent):
        """Create a special label for subnodes of a `SubNetwork`.

        In order to identify nodes which are part of a `SubNetwork`
        just by looking at the nodes, such nodes need to have special
        information attached. In order to create a uniform way of
        storing this information, a special `SubNetworkLabel` is used to
        `label` those nodes.

        Parameters
        ----------
        label : hashable
            The original label of the node. This is what would've been
            used to `label` the node if the node would not have been
            part of a `SubNetwork`.
        parent : oemof.network.SubNetwork
            The `SubNetwork` of which the node to which this label
            attached to is a part of.

        """
        self.label = label
        self.parent = parent

        if parent is not None:
            self.depth = parent.label.depth + 1
            self.flat_label = parent.label.flat_label + (label,)
        else:
            self.depth = 1
            self.flat_label = (label,)

    def __repr__(self):
        return repr(self.flat_label)

    def __str__(self):
        return str(self.flat_label)


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

        self.subnodes = []

        # TODO: Try to avoid this local `import`.
        from ..energy_system import EnergySystem

        EnergySystem.signals[EnergySystem.add].connect(
            self.add_subnodes, sender=self
        )

    def append_subnodes(self, *args):
        for sub_component in args:
            self.subnodes.append(sub_component)

    def add_subnodes(self, node, **kwargs):
        """Add subnodes to an EnergySystem.

        This is meant to be used as an event callback that is called when this
        node is added to an EnergySystem, to add the child nodes to the
        EnergySystem, too.
        """
        # TODO:
        #    Explain why the `node` argument is necessary.
        assert self is node
        deque(
            (kwargs["EnergySystem"].add(sn) for sn in self.subnodes), maxlen=0
        )

    def subnode(self, class_, label, *args, **kwargs):
        """Create a subnode and add it to this `SubNetwork`.

        Create a subnode by calling `class_(label, *args, **kwargs)` and
        `append` the result to `self.subnodes`.
        The purpose of this wrapper is to make sure that subnodes are
        always `label`led with a `SubNetworkLabel`. While not as
        convenient as simply instantiating nodes and adding them to a
        `SubNetwork` yourself, using this is as easy as replacing e.g.
        the sequence

        ..code:: python
            bus = Bus("bus", inputs={input: x}, outputs={output: y})
            subnetwork.subnodes.append(bus)

        with

        ..code:: python
            subnetwork.subnode(
                Bus, "bus", inputs={input: x}, outputs={output: y}
            )

        """
        subnode = class_(
            label=HierachicalLabel(label=label, parent=self), *args, **kwargs
        )
        self.subnodes.append(subnode)
        return subnode
