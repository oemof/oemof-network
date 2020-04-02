=====
Usage
=====

oemof-network
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
