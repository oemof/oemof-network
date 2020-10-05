# -*- coding: utf-8 -

""" Tests pertaining to :obj:`node <oemof.network.network.Node>` registration via :attr:`Node.registry <oemof.network.network.Node.registry>`.

This test suite (eventually) collects all tests revolving around automatically
registering :obj:`nodes <oemof.network.network.Node>` in an
:obj:`energy system <oemof.network.EnergySystem>`. Since this feature is
deprecated, having all tests pertaining to it in one file makes it easier to
remove them all at once, when the feature is romved.

This file is part of project oemof (github.com/oemof/oemof). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location oemof/tests/basic_tests.py

SPDX-License-Identifier: MIT
"""
import warnings

import pandas as pd
import pytest

from oemof.network.network import Node


class NodeRegistrationTests:

    # TODO: Move all other registration tests into this test suite.

    def setup(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            Node.registry = None

    def test_that_setting_a_node_registry_emits_a_warning(self):
        with pytest.warns(FutureWarning):
            Node.registry = 1

    def test_that_accessing_the_node_registry_emits_a_warning(self):
        with pytest.warns(FutureWarning):
            Node.registry

    def test_that_node_creation_does_not_emit_a_warning(self):
        with pytest.warns(None) as record:
            n = Node()

        recorded = [w for w in record.list if w.category is FutureWarning]
        if recorded:
            pytest.fail(
                "Creating a node emitted the following `FutureWarning`s\n"
                "although no warning was expected:\n{}".format(
                    "\n---\n".join([str(w.message) for w in recorded])
                )
            )
