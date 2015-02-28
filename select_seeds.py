"""Takes a graph file (adjacency lists in JSON) and produces the required number
of contagion seed nodes based on a selected strategy. The seed nodes are
outputted into a folder of the corresponding strategy. There is no variability
in the seed nodes in the 50 rounds per game."""

import json
import os
from sys import *
import random
import sim
import networkx as nx
import heapq

def read_graph(fname):
    ''' Reads a graph json file. Note the file should be under graph/
    
    Args:
        fname: string. The file name of the graph under the folder graph/.
    
    Returns
        A dict of adjacency lists.
    '''
    with open('graph/' + fname + '.json' , 'r') as fin:
        data = json.load(fin)

    return data

def read_seeds(folder, gname):
    '''Reads the seeds from file.
    
    Args:
        folder: string, the folder name/strategy name
        gname: string, the file name of the graph
    
    Returns:
        a list of node id's in unicode
    '''

    with open('%s/%s.txt' %(folder, gname)) as fin:
        seeds = map(lambda line: unicode(line.strip()), fin.readlines())
    return seeds

def write_seed(alg_name, fname, seeds):
    ''' Writes the selected seeds to file.
    
    Args:
        alg_name: the algorithm name, the file will be saved under alg_name 
                  folder
        fname: the file name
        seeds: [50 * num_seeds of seed id's]. Note seed id should be an int.
    '''
    with open(alg_name + '/' + fname + '.txt', 'w') as fout:
        for seed in seeds:
            fout.write(str(seed) + '\n')

def top_n_measure(measure, graph, n, return_subgraph=False):
    ''' Returns the top n centrality-measure nodes
    
    Args:
        measure: the centrality measure function, takes in a nx.Graph
        graph: an nx.Graph object
        n: int, the top n nodes that should be returned
        return_subgraph: bool, True to return subgraph of top nodes
    
    Returns:
    
    '''
    # Remove loops if measuring k-values (core numbers).
    if measure == nx.core_number:
        graph.remove_edges_from(graph.selfloop_edges())

    vals = measure(graph)
    tops = heapq.nlargest(n, vals.items(), key=lambda x: x[1])
    tops = [tup[0] for tup in tops]

    if not return_subgraph:
        return tops
    else:
        return tops, graph.subgraph(tops)

def top_measure_same_50(seeds, n):
    '''
    Generates 50 rounds of seeds with the same seeds
    
    Args:
        seeds: a list of node id's
    
    Returns:
        a list of node id's
    '''
    return seeds[:n] * 50

def top_measure_rand_50(tops, n):
    '''
    Generates 50 rounds of seeds randomly choosen from tops
    
    Args:
        tops: a list of node id's
        n: number of seeds for each rounds
    
    Returns:
        a list of node id's
    '''
    seeds = []
    for _ in range(50):
        seeds += random.sample(tops, n)
    return seeds

def kshell_support(graph, n):
    """Selects top n/5 k-value nodes, along with 4 neighbors."""
    tops = algs['k'][1](graph, n)
    seeds = set([])

    i = 0
    j = 0
    while len(seeds) < n:
        seeds.add(tops[i])
        neighs = graph.neighbors(tops[i])
        seeds.add(neighs[j])

        if j < 3:
            j += 1
        else:
            i += 1
            j = 0

    return top_measure_same_50(list(seeds), n)
        

def alt_deg2(graph, n):
    """ Return two highest-degree neighbors of the top highest-degree nodes.
    This strategy aims to capture the high-degree nodes after one iteration,
    since the high-degree nodes are generally unattainable as seed nodes."""
    
    # Gather top 2n highest-degree nodes.
    degs = nx.degree_centrality(graph)
    tops = heapq.nlargest(2*n, degs.items(), key=lambda x: x[1])
    tops = [tup[0] for tup in tops]

    # Do not consider the top 2n highest-degree nodes as possible seeds.
    for node in tops[:n]:
        del degs[node]

    # Gather the two highest-degree neighbors from the highest-degree nodes,
    # until n nodes have been accumulated.
    seeds = set()
    i = 0
    while len(seeds) < n:
        if i >= n:
            seeds.add(tops[i])
        else:
            neighs = graph.neighbors(tops[i])
            nei_deg = [(node, degs[node]) for node in neighs if node in degs]
            two_tops = heapq.nlargest(2, nei_deg, key=lambda x: x[1])
            for node, _ in two_tops:
                seeds.add(node)
                del degs[node]
        i += 1

    # Use the same seeds for all 50 rounds.
    return top_measure_same_50(list(seeds), n)

def alt_deg1(graph, n):
    """ Return one highest-degree neighbor of the top highest-degree nodes.
    This strategy aims to capture the high-degree nodes after one iteration,
    since the high-degree nodes are generally unattainable as seed nodes."""
    
    # Gather top 2n highest-degree nodes.
    degs = nx.degree_centrality(graph)
    tops = heapq.nlargest(2*n, degs.items(), key=lambda x: x[1])
    tops = [tup[0] for tup in tops]

    # Do not consider the top 2n highest-degree nodes as possible seeds.
    for node in tops[:n]:
        del degs[node]

    # Gather the highest-degree neighbor from the highest-degree nodes, until
    # n nodes have been accumulated.    
    seeds = set()
    i = 0
    while len(seeds) < n:
        if i >= n:
            seeds.add(tops[i])
        else:
            neighs = graph.neighbors(tops[i])
            nei_deg = [(node, degs[node]) for node in neighs if node in degs]
            two_tops = heapq.nlargest(1, nei_deg, key=lambda x: x[1])
            for node, _ in two_tops:
                seeds.add(node)
                del degs[node]
        i += 1

    # Use the same seeds for all 50 rounds.
    return top_measure_same_50(list(seeds), n)


def alt2_kshp(graph, n):
    """Combine a random sample of seeds chosen based on alt_deg2 and degree-
    filtered, k-shell strategies."""
    global algs
    tops = set(alt_deg2(graph, n)[:n])
    tops.union(set(algs['dk'][1](graph, n)[:n]))
    seeds = []
    for _ in range(50):
        seeds += random.sample(tops, n)
    return seeds

def alt2_ksh(graph, n):
    """Uniformly combine seeds chosen based on alt_deg2 and degree-filtered,
    k-shell strategies."""    
    global algs
    top_deg2 = alt_deg2(graph, n)[:n]
    top_dk = algs['dk'][1](graph, n)[:n]
    seeds = set()

    i = 0
    while len(seeds) < n:
        if i:
            seeds.add(top_deg2[i/2])
        else:
            seeds.add(top_dk[i/2])
        i += 1

    return list(seeds) * 50
                     
# A dict of all the centrality measures.
# {measure_flag: (measure_name, measure_function)}
measures = {'d': ('deg', nx.degree_centrality),
            'b': ('btw', nx.betweenness_centrality),
            'c': ('clu', nx.clustering),
            'l': ('clo', nx.closeness_centrality),
            'k': ('ksh', nx.core_number)
           }

# A dict of function for generating 50 rounds of seeds
# {gen_flag: gen_function}
gen_50 = {'': top_measure_same_50,
          'p': top_measure_rand_50,
         }

# A dict of all algorithms for selection. {flag: (folder name, function name)}
algs = {}


# Algorithms for pure measures.
pure_measure_func = lambda m_f: (lambda g, n: top_measure_same_50(
    top_n_measure(m_f, g.copy(), n), n))
for m in measures:
    m_name, m_f = measures[m]
    algs[m] = (m_name, pure_measure_func(m_f))


deg_flter = lambda m_f: (lambda g, n: top_measure_same_50(top_n_measure(m_f,
    top_n_measure(nx.degree_centrality, g.copy(), 3000, True)[1].copy(), n), n))


# Algorithms for degree-filtered measures and others.
for m in measures:
    m_name, m_f = measures[m]
    algs['d'+m] = ('deg' + m_name , deg_flter(m_f))
algs['a2'] = ('altdeg2', alt_deg2)
algs['a1'] = ('altdeg1', alt_deg1)
algs['a2kp'] = ('alt2kshp', alt2_kshp)
algs['a2k'] = ('alt2ksh', alt2_ksh)

algs['ks'] = ('kshell_support', kshell_support)


if __name__ == '__main__':
    # name of the graph, excluding '.json'
    g_name = argv[1]
    # number of seeds
    n = int(g_name.split('.')[1])
    
    adj_list = read_graph(g_name)
    graph = nx.Graph(adj_list)
    
    competitors = {}
    if argv[2] == 'all':
        flagged_algs = algs.keys()
    else:
        flagged_algs = argv[2:]

    for flag in flagged_algs:
        if flag in algs:
            print flag
            folder, f = algs[flag]
            if os.path.exists('%s/%s.txt' %(folder, g_name)):
                seeds = read_seeds(folder, g_name)
            else:
                seeds = f(graph.copy(), n)
            write_seed(folder, g_name, seeds)
            competitors[folder] = \
                [seeds[n * i : n * (i + 1)] for i in range(50)]
            print '-----'


    # Show the performance of the various chosen algorithms when competing
    # against each other.
    results = sim.run(adj_list, competitors, 1)
    print results
