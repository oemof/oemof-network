# -*- coding: utf-8 -

"""Basic tests.

This file is part of project oemof (github.com/oemof/oemof). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location oemof/tests/basic_tests.py

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <krien@uni-bremen.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>

SPDX-License-Identifier: MIT
"""
from collections.abc import Iterable
from itertools import chain
from pprint import pformat

from oemof.network import energy_system as es
from oemof.network.groupings import Entities
from oemof.network.groupings import Flows
from oemof.network.groupings import FlowsWithNodes as FWNs
from oemof.network.groupings import Grouping
from oemof.network.network import Bus
from oemof.network.network import Node


class TestsEnergySystem:
    def setup(self):
        self.es = es.EnergySystem()

    def test_entity_grouping_on_construction(self):
        bus = Bus(label="test bus")
        ensys = es.EnergySystem(entities=[bus])
        assert ensys.groups[bus.label] is bus

    def test_that_none_is_not_a_valid_group(self):
        def by_uid(n):
            if "Not in 'Group'" in n.uid:
                return None
            else:
                return "Group"

        ensys = es.EnergySystem(groupings=[by_uid])

        ungrouped = [
            Node(uid="Not in 'Group': {}".format(i)) for i in range(10)
        ]
        grouped = [Node(uid="In 'Group': {}".format(i)) for i in range(10)]
        assert None not in ensys.groups
        for g in ensys.groups.values():
            for e in ungrouped:
                if isinstance(g, Iterable) and not isinstance(g, str):
                    assert e not in g
            for e in grouped:
                if isinstance(g, Iterable) and not isinstance(g, str):
                    assert e in g

    def test_defining_multiple_groupings_with_one_function(self):
        def assign_to_multiple_groups_in_one_go(n):
            g1 = n.label[-1]
            g2 = n.label[0:3]
            return [g1, g2]

        ensy = es.EnergySystem(groupings=[assign_to_multiple_groups_in_one_go])
        nodes = [
            Node(
                label=("Foo: " if i % 2 == 0 else "Bar: ")
                + "{}".format(i)
                + ("A" if i < 5 else "B")
            )
            for i in range(10)
        ]
        ensy.add(*nodes)
        for group in ["Foo", "Bar", "A", "B"]:
            assert len(ensy.groups[group]) == 5, (
                "\n  Failed testing length of group '{}'."
                + "\n  Expected: 5"
                + "\n  Got     : {}"
                + "\n  Group   : {}"
            ).format(
                group,
                len(ensy.groups[group]),
                sorted([e.label for e in ensy.groups[group]]),
            )

    def test_grouping_filter_parameter(self):
        g1 = Grouping(
            key=lambda e: "The Special One",
            filter=lambda e: "special" in str(e),
        )
        g2 = Entities(
            key=lambda e: "A Subset", filter=lambda e: "subset" in str(e)
        )
        ensys = es.EnergySystem(groupings=[g1, g2])
        special = Node(label="special")
        subset = set(Node(label="subset: {}".format(i)) for i in range(10))
        others = set(Node(label="other: {}".format(i)) for i in range(10))
        ensys.add(special, *subset)
        ensys.add(*others)
        assert ensys.groups["The Special One"] == special
        assert ensys.groups["A Subset"] == subset

    def test_proper_filtering(self):
        """`Grouping.filter` should not be "all or nothing".

        There was a bug where, if `Grouping.filter` returned `False` only for
        some elements of `Grouping.value(e)`, those elements where actually
        retained.
        This test makes sure that the bug doesn't resurface again.
        """
        g = Entities(
            key="group",
            value=lambda _: {1, 2, 3, 4},
            filter=lambda x: x % 2 == 0,
        )
        ensys = es.EnergySystem(groupings=[g])
        special = Node(label="object")
        ensys.add(special)
        assert ensys.groups["group"] == {2, 4}

    def test_non_callable_group_keys(self):
        collect_everything = Entities(key="everything")
        g1 = Grouping(
            key="The Special One", filter=lambda e: "special" in e.label
        )
        g2 = Entities(key="A Subset", filter=lambda e: "subset" in e.label)
        ensys = es.EnergySystem(groupings=[g1, g2, collect_everything])
        special = Node(label="special")
        subset = set(Node(label="subset: {}".format(i)) for i in range(2))
        others = set(Node(label="other: {}".format(i)) for i in range(2))
        everything = subset.union(others)
        everything.add(special)
        ensys.add(*everything)
        assert ensys.groups["The Special One"] == special
        assert ensys.groups["A Subset"] == subset
        assert ensys.groups["everything"] == everything

    def test_grouping_laziness(self):
        """Energy system `groups` should be fully lazy.

        `Node`s added to an energy system should only be tested for and put
        into their respective groups right before the `groups` property of an
        energy system is accessed.
        """
        group = "Group"
        g = Entities(key=group, filter=lambda n: getattr(n, "group", False))
        self.es = es.EnergySystem(groupings=[g])
        buses = [Bus("Grouped"), Bus("Ungrouped one"), Bus("Ungrouped two")]
        self.es.add(buses[0])
        buses[0].group = True
        self.es.add(*buses[1:])
        assert group in self.es.groups, (
            (
                "\nExpected to find\n\n  `{!r}`\n\n"
                "in `es.groups`.\nGot:\n\n  `{}`"
            ).format(
                group,
                "\n   ".join(pformat(set(self.es.groups.keys())).split("\n")),
            ),
        )
        assert buses[0] in self.es.groups[group], (
            "\nExpected\n\n  `{}`\n\nin `es.groups['{}']`:\n\n  `{}`".format(
                "\n   ".join(pformat(buses[0]).split("\n")),
                group,
                "\n   ".join(pformat(self.es.groups[group]).split("\n")),
            ),
        )

    def test_constant_group_keys(self):
        """Callable keys passed in as `constant_key` should not be called.

        The `constant_key` parameter can be used to specify callable group keys
        without having to worry about `Grouping`s trying to call them. This
        test makes sure that the parameter is handled correctly.
        """

        def everything():
            return "everything"

        collect_everything = Entities(constant_key=everything)
        ensys = es.EnergySystem(groupings=[collect_everything])
        node = Node(label="A Node")
        ensys.add(node)
        assert "everything" not in ensys.groups
        assert everything in ensys.groups
        assert ensys.groups[everything] == {node}
        assert everything() == "everything"

    def test_flows(self):
        key = object()
        ensys = es.EnergySystem(groupings=[Flows(key)])
        bus = Bus(label="A Bus")
        node = Node(label="A Node", inputs={bus: None}, outputs={bus: None})
        ensys.add(bus, node)
        assert ensys.groups[key] == set(
            chain(bus.inputs.values(), bus.outputs.values())
        )

    def test_flows_with_nodes(self):
        key = object()
        ensys = es.EnergySystem(groupings=[FWNs(key)])
        bus = Bus(label="A Bus")
        node = Node(label="A Node", inputs={bus: None}, outputs={bus: None})
        ensys.add(bus, node)
        assert ensys.groups[key], {
            (bus, node, bus.outputs[node]),
            (node, bus, node.outputs[bus]),
        }

    def test_that_node_additions_are_signalled(self):
        """
        When a node gets `add`ed, a corresponding signal should be emitted.
        """
        node = Node(label="Node")

        def subscriber(sender, **kwargs):
            assert sender is node
            assert kwargs["EnergySystem"] is self.es
            subscriber.called = True

        subscriber.called = False

        es.EnergySystem.signals[es.EnergySystem.add].connect(
            subscriber, sender=node
        )
        self.es.add(node)
        assert subscriber.called, (
            "\nExpected `subscriber.called` to be `True`.\n"
            "Got {}.\n"
            "Probable reason: `subscriber` didn't get called."
        ).format(subscriber.called)
