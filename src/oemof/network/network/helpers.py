# -*- coding: utf-8 -*-

"""This package contains helpers used by Entities of the energy systems.

SPDX-FileCopyrightText: Stephan Günther <>
SPDX-FileCopyrightText: Uwe Krien <krien@uni-bremen.de>
SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Cord Kaldemeyer <>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeldt@dlr.de>

SPDX-License-Identifier: MIT
"""

from collections import UserDict
from collections.abc import MutableMapping


class Inputs(MutableMapping):
    """A special helper to map `n1.inputs[n2]` to `n2.outputs[n1]`."""

    def __init__(self, target):
        self.target = target

    def __getitem__(self, key):
        return key.outputs.__getitem__(self.target)

    def __delitem__(self, key):
        return key.outputs.__delitem__(self.target)

    def __setitem__(self, key, value):
        return key.outputs.__setitem__(self.target, value)

    def __iter__(self):
        return iter(self.target._in_edges)

    def __len__(self):
        return self.target._in_edges.__len__()

    def __repr__(self):
        return repr(
            "<{0.__module__}.{0.__name__}: {1!r}>".format(
                type(self), dict(self)
            )
        )


class Outputs(UserDict):
    """
    Helper that intercepts modifications to update `Inputs` symmetrically.
    """

    def __init__(self, source):
        self.source = source
        super().__init__()

    def __delitem__(self, key):
        key._in_edges.remove(self.source)
        return super().__delitem__(key)

    def __setitem__(self, key, value):
        key._in_edges.add(self.source)
        return super().__setitem__(key, value)


class HierachicalLabel:
    # TODO: Find a better place for the `interface` parameter/attribute.
    #       (See the `git blame` of these lines for details.)
    def __init__(self, label, parent=None):
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
