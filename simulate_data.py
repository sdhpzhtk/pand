"""Parses data from previous rounds and simulates generated data against
competitors' seed nodes.

Parameters: graph name, data filename, strategy flag."""

import json, sim, sys
import select_seeds as ss

# Name of file containing previous round's data.
filename = sys.argv[1]
with open(filename, 'r') as f:
    data = json.load(f)
    
# Strategy flag to try and corresponding algorithm.
strategy = sys.argv[2]
algorithm = ss.algs[strategy][1][1]

seeds = algorithm