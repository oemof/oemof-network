import pandas as pd
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt

from oemof.network.network import Bus, Sink, Transformer
from oemof.network.energy_system import EnergySystem
import oemof.network.graph as on_graph

matplotlib.use('Qt5Agg')

date_time_index = pd.date_range('1/1/2017', periods=3, freq='H')
es = EnergySystem(timeindex=date_time_index)
b_gas = Bus(label='b_gas', balanced=False)
bel1 = Bus(label='bel1')
bel2 = Bus(label='bel2')
demand_el = Sink(label='demand_el', inputs=[bel1])
pp_gas = Transformer(label=('pp', 'gas'),
                     inputs=[b_gas],
                     outputs=[bel1],
                     conversion_factors={bel1: 0.5})
line_to2 = Transformer(label='line_to2',
                       inputs=[bel1],
                       outputs=[bel2],
                       position=(0, -3))
line_from2 = Transformer(label='line_from2',
                         inputs=[bel2],
                         outputs=[bel1],
                         position=(0, 3))
es.add(b_gas, bel1, demand_el, pp_gas, bel2, line_to2, line_from2)
my_graph = on_graph.create_nx_graph(es)
positions = on_graph.positions(es, my_graph)

nx.draw(my_graph, pos=positions, with_labels=True)
plt.show()
