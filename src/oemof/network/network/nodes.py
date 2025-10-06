# -*- coding: utf-8 -*-
"""This package contains the differnt types of Node for
modelling an energy system graph.

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <uwe.krien@ifam.fraunhofer.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>
SPDX-FileCopyrightText: Pierre-Francois Duc <pierre-francois@rl-institut.de>

SPDX-License-Identifier: MIT
"""

import warnings
from collections import deque

from .edge import Edge
from .entity import Entity
from .helpers import Inputs
from .helpers import Outputs


class QualifiedLabel(tuple):
    """Alias class to allow tuples in labels"""

    pass


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

    def __init__(
        self,
        label,
        *,
        inputs=None,
        outputs=None,
        parent_node=None,
        custom_properties=None,
    ):
        super().__init__(label=label, custom_properties=custom_properties)

        self._inputs = Inputs(self)
        self._outputs = Outputs(self)
        self._in_edges = set()

        self.parent = parent_node

        if self.parent is not None:
            self._depth = self.parent.depth + 1
        else:
            self._depth = 0

        self.__subnodes = []
        self.__energy_system = None

        # TODO: Try to avoid this local `import`.
        from ..energy_system import EnergySystem

        EnergySystem.signals[EnergySystem.add].connect(
            self._add_subnodes, sender=self
        )

        if inputs is None:
            inputs = {}
        if outputs is None:
            outputs = {}

        msg = "{} {!r} of {!r} not an instance of Node but of {}."

        for i in inputs:
            if not isinstance(i, Node):
                raise ValueError(msg.format("Input", i, self, type(i)))
            self._in_edges.add(i)
            try:
                flow = inputs.get(i)
            except AttributeError:
                flow = None
            edge = Edge.from_object(flow)
            edge.input = i
            edge.output = self
        for o in outputs:
            if not isinstance(o, Node):
                raise ValueError(msg.format("Output", o, self, type(o)))
            try:
                flow = outputs.get(o)
            except AttributeError:
                flow = None
            edge = Edge.from_object(flow)
            edge.input = self
            edge.output = o

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

    @property
    def depth(self) -> int:
        """
        The :class:`Node` instances have a depth defined
        as the depth of their parent (if any) + 1."""
        return self._depth

    @property
    def subnodes(self):
        """Subnodes of the Node

        It is deliberately provided as a tuple to prevent user to append
        subnodes other than with API methods.
        """
        return tuple([sn for sn in self.__subnodes])

    def add(self, *subnodes):
        """Add subnodes to this `Node`."""
        for subnode in subnodes:
            subnode.parent = self
            subnode._depth = self.depth + 1
            self.__subnodes.append(subnode)
            if self.__energy_system is not None:
                self.__energy_system.add(subnode)

    def subnode(self, class_, local_name, *args, **kwargs):
        """Create a subnode and add it to this `Node`.

        Create a subnode by calling `class_(label, *args, **kwargs)` and
        `append` the result to `self.__subnodes`.
        The purpose of this wrapper is to make sure that subnodes are
        always `label`led with a unique label.
        This is useful because this allows giving the same `local_name`
        to distinct sub-`Node`s in different `Node` s.

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
        `subnodes` of this `Node`.

        When
        >>> from oemof.network import Node, Edge
        >>> subnetwork = Node("subnetwork")
        >>> input = output = Node("input")
        >>> # Create a subnode of type `Node` using this convenience function
        >>> bus = subnetwork.subnode(
        ...     Node, "bus", inputs={input: Edge()}, outputs={output: Edge()}
        ... )
        """
        if isinstance(self.label, QualifiedLabel):
            label = QualifiedLabel([local_name, *self.label])
        else:
            label = QualifiedLabel([local_name, self.label])
        subnode = class_(
            label=label,
            parent_node=self,
            *args,
            **kwargs,
        )
        self.add(subnode)
        return subnode

    def _add_subnodes(self, node, **kwargs):
        """Add subnodes to an EnergySystem.

        This is meant to be used as an event callback that is called when this
        node is added to an EnergySystem, to add the child nodes to the
        EnergySystem, too.
        """
        # TODO:
        #    Explain why the `node` argument is necessary.
        if self is not node:
            raise ValueError("Call needs to be obj._add_subnodes(obj).")
        self.__energy_system = kwargs["EnergySystem"]
        deque(
            (kwargs["EnergySystem"].add(sn) for sn in self.__subnodes),
            maxlen=0,
        )


_deprecation_warning = (
    "Usage of {} is deprecated. Use oemof.network.Node instead."
)


class Bus(Node):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            _deprecation_warning.format("oemof.network.Bus"),
            FutureWarning,
        )
        super().__init__(*args, **kwargs)


class Component(Node):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            _deprecation_warning.format("oemof.network.Component"),
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
