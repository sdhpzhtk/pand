"""Parses data from previous rounds and simulates generated data against
competitors' seed nodes.

Parameters: graph name, n, data filename, strategy flag."""

import json, sim, sys
import select_seeds
import networkx as nx

# Name of file containing graph information.
graph_file = sys.argv[1]
graph = select_seeds.read_graph(graph_file)
n_graph = nx.Graph(graph)

# Number of seed nodes.
n = int(sys.argv[2])

# Name of file containing previous round's data.
data_file = sys.argv[3]
with open(data_file, 'r') as f:
    data = json.load(f)
    
# Strategy flag to try and corresponding algorithm.
strategy = sys.argv[4]
algorithm = select_seeds.algs[strategy][1]

# Create seed nodes for 50 rounds.
seeds = algorithm(n_graph, n)
seeds = seeds[0:50]
seed_nodes = []
for i in range(50):
    seed_nodes.append(list(seeds))

del data['CaltechFTW']

unique_seeds = set(seeds)
for opp_seeds in data.itervalues():
    unique_seeds = unique_seeds.difference(set(opp_seeds[0]))

data['CaltechFTW'] = seed_nodes

print len(unique_seeds)
print unique_seeds

results = sim.run(graph, data, 5)
for i in range(5):
    print results[i][0]