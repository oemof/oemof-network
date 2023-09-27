# -*- coding: utf-8 -*-

"""Modules for creating and analysing energy system graphs.

This file is part of project oemof (github.com/oemof/oemof). It's copyrighted
by the contributors recorded in the version control history of the file,
available from its original location oemof/oemof/graph.py

SPDX-FileCopyrightText: Simon Hilpert <>
SPDX-FileCopyrightText: Uwe Krien <krien@uni-bremen.de>
SPDX-FileCopyrightText: Patrik Schönfeldt <patrik.schoenfeld@dlr.de>

SPDX-License-Identifier: MIT
"""

import networkx as nx


def create_nx_graph(
    energy_system=None,
    remove_nodes=None,
    filename=None,
    remove_nodes_with_substrings=None,
    remove_edges=None,
):
    """
    Create a `networkx.DiGraph` for the passed energy system.
    See http://networkx.readthedocs.io/en/latest/ for more information.

    Parameters
    ----------
    energy_system : `oemof.solph.network.EnergySystem`

    filename : str
        Absolute filename (with path) to write your graph in the graphml
        format. If no filename is given no file will be written.

    remove_nodes: list of strings
        Nodes to be removed e.g. ['node1', node2')]

    remove_nodes_with_substrings: list of strings
        Nodes that contain substrings to be removed e.g. ['elec', 'heat')]

    remove_edges: list of string tuples
        Edges to be removed e.g. [('resource_gas', 'gas_balance')]

    Examples
    --------
    >>> import os
    >>> import pandas as pd
    >>> from oemof.network.network import Bus, Sink, Transformer
    >>> from oemof.network.energy_system import EnergySystem
    >>> import oemof.network.graph as grph
    >>> datetimeindex = pd.date_range('1/1/2017', periods=3, freq='H')
    >>> es = EnergySystem(timeindex=datetimeindex)
    >>> b_gas = Bus(label='b_gas', balanced=False)
    >>> bel1 = Bus(label='bel1')
    >>> bel2 = Bus(label='bel2')
    >>> demand_el = Sink(label='demand_el', inputs = [bel1])
    >>> pp_gas = Transformer(label=('pp', 'gas'),
    ...                      inputs=[b_gas],
    ...                      outputs=[bel1],
    ...                      conversion_factors={bel1: 0.5})
    >>> line_to2 = Transformer(label='line_to2', inputs=[bel1], outputs=[bel2])
    >>> line_from2 = Transformer(label='line_from2',
    ...                          inputs=[bel2], outputs=[bel1])
    >>> es.add(b_gas, bel1, demand_el, pp_gas, bel2, line_to2, line_from2)
    >>> my_graph = grph.create_nx_graph(es)
    >>> # export graph as .graphml for programs like Yed where it can be
    >>> # sorted and customized. this is especially helpful for large graphs
    >>> # grph.create_nx_graph(es, filename="my_graph.graphml")
    >>> [my_graph.has_node(n)
    ...  for n in ['b_gas', 'bel1', "('pp', 'gas')", 'demand_el', 'tester']]
    [True, True, True, True, False]
    >>> list(nx.attracting_components(my_graph))
    [{'demand_el'}]
    >>> sorted(list(nx.strongly_connected_components(my_graph))[1])
    ['bel1', 'bel2', 'line_from2', 'line_to2']
    >>> new_graph = grph.create_nx_graph(energy_system=es,
    ...                                  remove_nodes_with_substrings=['b_'],
    ...                                  remove_nodes=["('pp', 'gas')"],
    ...                                  remove_edges=[('bel2', 'line_from2')],
    ...                                  filename='test_graph')
    >>> [new_graph.has_node(n)
    ...  for n in ['b_gas', 'bel1', "('pp', 'gas')", 'demand_el', 'tester']]
    [False, True, False, True, False]
    >>> my_graph.has_edge("('pp', 'gas')", 'bel1')
    True
    >>> new_graph.has_edge('bel2', 'line_from2')
    False
    >>> os.remove('test_graph.graphml')

    Notes
    -----
    Needs graphviz and networkx (>= v.1.11) to work properly.
    Tested on Ubuntu 16.04 x64 and solydxk (debian 9).
    """
    # construct graph from nodes and flows
    grph = nx.DiGraph()

    # add nodes
    for n in energy_system.nodes:
        grph.add_node(str(n.label), label=str(n.label))

    # add labeled flows on directed edge if an optimization_model has been
    # passed or undirected edge otherwise
    for n in energy_system.nodes:
        for i in n.inputs.keys():
            weight = getattr(
                energy_system.flows()[(i, n)], "nominal_value", None
            )
            if weight is None:
                grph.add_edge(str(i.label), str(n.label))
            else:
                grph.add_edge(
                    str(i.label), str(n.label), weigth=format(weight, ".2f")
                )

    # remove nodes and edges based on precise labels
    if remove_nodes is not None:
        grph.remove_nodes_from(remove_nodes)
    if remove_edges is not None:
        grph.remove_edges_from(remove_edges)

    # remove nodes based on substrings
    if remove_nodes_with_substrings is not None:
        for i in remove_nodes_with_substrings:
            remove_nodes = [
                str(v.label) for v in energy_system.nodes if i in str(v.label)
            ]
            grph.remove_nodes_from(remove_nodes)

    if filename is not None:
        if filename[-8:] != ".graphml":
            filename = filename + ".graphml"
        nx.write_graphml(grph, filename)

    return grph


def positions(energy_system, nx_graph=None):
    """
    Get positions to draw nodes of `oemof.network.EnergySystem`.


    Parameters
    ----------
    energy_system : `oemof.solph.network.EnergySystem`

    nx_graph : `networkx.DiGraph` (optional)
        Existing `networkx.DiGraph` that can be used to optimise
        the positions of `Node`s that are not already set.
        If there are `Node`s without a given position and nx_graph
        is not given, a temporary `networkx.DiGraph` will be created.
    """
    fixed_positions = dict()

    nodes_with_position = list()
    for node in energy_system.nodes:
        position = node.position
        if position is not None:
            fixed_positions[str(node)] = position
            nodes_with_position.append(str(node))

    if len(nodes_with_position) == len(energy_system.nodes):
        all_positions = fixed_positions
    else:  # use networkx to optimise non-set positions
        # networkx.spring_layout cannot work with empty dicts
        if len(nodes_with_position) == 0:
            nodes_with_position = None
        if nx_graph is None:
            nx_graph = create_nx_graph(energy_system=energy_system)

        # There need to be positions for all Nodes.
        # We use them as basis for a graph considering fixed positions
        all_positions = nx.spring_layout(nx_graph)

        if fixed_positions:
            all_positions.update(fixed_positions)

            # we run this twice to get good positions based on the fixed ones
            all_positions = nx.spring_layout(
                nx_graph, pos=all_positions, fixed=nodes_with_position
            )

    return all_positions
