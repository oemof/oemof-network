# -*- coding: utf-8 -*-
"""This package contains the differnt types of hierachical Nodes for
modelling an energy system graph.

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <uwe.krien@ifam.fraunhofer.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>
SPDX-FileCopyrightText: Pierre-Francois Duc <pierre-francois@rl-institut.de>

SPDX-License-Identifier: MIT
"""

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
