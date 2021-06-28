# -*- coding: utf-8 -

""" Tests pertaining to :obj:`node {}` registration via
:attr:`Node.registry <oemof.network.network.Node.registry>`.

This test suite (eventually) collects all tests revolving around automatically
registering :obj:`nodes <oemof.network.network.Node>` in an
:obj:`energy system <oemof.network.EnergySystem>`. Since this feature is
deprecated, having all tests pertaining to it in one file makes it easier to
remove them all at once, when the feature is romved.

This file is part of project oemof (github.com/oemof/oemof). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location oemof/tests/basic_tests.py

SPDX-License-Identifier: MIT
""".format(
    "<oemof.network.network.Node>"
)

import warnings

import pandas as pd
import pytest

from oemof.network.energy_system import EnergySystem
from oemof.network.network import Bus
from oemof.network.network import Node
from oemof.network.network import Transformer


class NodeRegistrationTests:

    # TODO: Move all other registration tests into this test suite.

    @classmethod
    def setup_class(cls):
        cls.timeindex = pd.date_range("1/1/2012", periods=5, freq="H")

    def setup(self):
        self.es = EnergySystem()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            Node.registry = None

    def test_entity_registration(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            Node.registry = self.es
            bus = Bus(label="bus-uid", type="bus-type")
            assert self.es.nodes[0] == bus
            bus2 = Bus(label="bus-uid2", type="bus-type")
            assert self.es.nodes[1] == bus2
            t1 = Transformer(label="pp_gas", inputs=[bus], outputs=[bus2])
            assert t1 in self.es.nodes
            self.es.timeindex = self.timeindex
            assert len(self.es.timeindex) == 5

    def test_that_setting_a_node_registry_emits_a_warning(self):
        with pytest.warns(FutureWarning):
            Node.registry = 1

    def test_that_accessing_the_node_registry_emits_a_warning(self):
        with pytest.warns(FutureWarning):
            Node.registry

    def test_that_node_creation_does_not_emit_a_warning(self):
        with pytest.warns(None) as record:
            Node()

        recorded = [w for w in record.list if w.category is FutureWarning]
        if recorded:
            pytest.fail(
                "Creating a node emitted the following `FutureWarning`s\n"
                "although no warning was expected:\n{}".format(
                    "\n---\n".join([str(w.message) for w in recorded])
                )
            )

    def test_that_node_creation_emits_a_warning_if_registry_is_not_none(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            Node.registry = EnergySystem()

        with pytest.warns(FutureWarning):
            Node()
