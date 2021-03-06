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
print seed_nodes

data['CaltechFTW'] = seed_nodes

# Compute the number of unique seeds each team would have had in the previous
# competition if we chose seeds based on the selected strategy.
num_unique_seeds = {}
for team in data.iterkeys():
    num_unique_seeds[team] = []

    for i in range(50):
        team_seeds = set(data[team][i])

        for opponent, opp_seeds in data.iteritems():
            if opponent != team:
                team_seeds = team_seeds.difference(set(opp_seeds[i]))

        num_unique_seeds[team].append(len(team_seeds))

print num_unique_seeds

# Determine results of past competition had we used the selected strategy.
results = sim.run(graph, data, 5)
for i in range(5):
    print results[i][0]
