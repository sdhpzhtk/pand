"""Parses data from previous rounds and simulates generated data against
competitors' seed nodes.

Parameters: graph name, n, data filename, strategy flag."""

import json, sim, sys
import select_seeds

# Name of file containing graph information.
graph_file = sys.argv[1]
with open(graph_file, 'r') as f:
    graph = json.load(f)
    
# Number of seed nodes.
n = int(sys.argv[2])

# Name of file containing previous round's data.
data_file = sys.argv[3]
with open(filename, 'r') as f:
    data = json.load(f)
    
# Strategy flag to try and corresponding algorithm.
strategy = sys.argv[4]
algorithm = select_seeds.algs[strategy][1][1]

# Create seed nodes for 50 rounds.
seeds = algorithm(graph, n)
seed_nodes = []
for i in range(50):
    seed_nodes.append(list(seeds))

data['CaltechFTW'] = seed_nodes

results = sim(graph, data, 1)
print results