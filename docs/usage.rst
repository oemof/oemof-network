=====
Usage
=====

oemof.network
=============
The :ref:`oemof_network_label` library is part of the oemof installation. By now it can be used to define energy systems as a network with components and buses. Every component should be connected to one or more buses. After definition, a component has to explicitely be added to its energy system. Allowed components are sources, sinks and transformer.

.. 	image:: _files/example_network.svg
   :scale: 30 %
   :alt: alternate text
   :align: center

The code of the example above:

.. code-block:: python

    from oemof.network import *
    from oemof.energy_system import *

    # create the energy system
    es = EnergySystem()

    # create bus 1
    bus_1 = Bus(label="bus_1")

    # create bus 2
    bus_2 = Bus(label="bus_2")

    # add bus 1 and bus 2 to energy system
    es.add(bus_1, bus_2)

    # create and add sink 1 to energy system
    es.add(Sink(label='sink_1', inputs={bus_1: []}))

    # create and add sink 2 to energy system
    es.add(Sink(label='sink_2', inputs={bus_2: []}))

    # create and add source to energy system
    es.add(Source(label='source', outputs={bus_1: []}))

    # create and add transformer to energy system
    es.add(Transformer(label='transformer', inputs={bus_1: []}, outputs={bus_2: []}))

The network class is aimed to be very generic and might have some network analyse tools in the future. By now the network library is mainly used as the base for the solph library.

To use oemof.network in a project::

	import oemof.network


.. _oemof_network_label:

~~~~~~~~~~~~~~~~~~~~~~
oemof.network
~~~~~~~~~~~~~~~~~~~~~~

The modeling of energy supply systems and its variety of components has a clearly structured approach within the oemof framework. Thus, energy supply systems with different levels of complexity can be based on equal basic module blocks. Those form an universal basic structure.

A *node* is either a *bus* or a *component*. A bus is always connected with one or several components. Likewise components are always connected with one or several buses. Based on their characteristics components are divided into several sub types.

*Transformers* have any number of inputs and outputs, e.g. a CHP takes from a bus of type 'gas' and feeds into a bus of type 'electricity' and a bus of type 'heat'. With additional information like parameters and transfer functions input and output can be specified. Using the example of a gas turbine, the resource consumption (input) is related to the provided end energy (output) by means of an conversion factor. Components of type *transformer* can also be used to model transmission lines.

A *sink* has only an input but no output. With *sink* consumers like households can be modeled. But also for modelling excess energy you would use a *sink*.

A *source* has exactly one output but no input. Thus for example, wind energy and photovoltaic plants can be modeled.

Components and buses can be combined to an energy system. Components and buses are nodes, connected among each other through edges which are the inputs and outputs of the components. Such a model can be interpreted mathematically as bipartite graph as buses are solely connected to components and vice versa. Thereby the in- and outputs of the components are the directed edges of the graph. The components and buses themselves are the nodes of the graph.

**oemof.network is part of oemofs core and contains the base classes that are used in oemof-solph. You do not need to define your energy system on the network level as all components can be found in oemof-solph, too. You may want to inherit from oemof.network components if you want to create new components.**

.. _oemof_graph_label:

Graph
-----
In the graph module you will find a function to create a networkx graph from an energy system or solph model. The networkx package provides many features to analyse, draw and export graphs. See the `networkx documentation <https://networkx.org/documentation/>`_ for more details. See the API-doc of :py:mod:`~oemof.graph` for all details and an example. The graph module can be used with energy systems of solph as well.
