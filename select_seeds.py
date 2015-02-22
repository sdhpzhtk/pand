import json
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
        return_subgraph: bool, True if want to returnthe subgraph of the top nodes
    
    Returns:
    
    '''
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

# A dict of all the centrality measures. {measure_flag: (measure_name, measure_function)}
measures = {'d': ('deg', nx.degree_centrality),
            'b': ('btw', nx.betweenness_centrality),
            'c': ('clu', nx.clustering),
            'l': ('clo', nx.closeness_centrality),
           }

# A dict of function for generating 50 rounds of seeds
# {gen_flag: gen_function}
gen_50 = {'': top_measure_same_50,
          'p': top_measure_rand_50,
         }

# A dict of all algorithms for selection. {flag: (folder name, function name)}
algs = {}

# Algorithms for pure measures
for m in measures:
    m_name, m_f = measures[m]
    algs[m] = (m_name, lambda graph, n: top_measure_same_50(top_n_measure(m_f, graph.copy(), n), n))

# Algorithms for pure measures with random generation (using top 1.5 * n nodes)
for m in measures:
    m_name, m_f = measures[m]
    g = 'p'
    gen_f = gen_50['p']
    algs[m+g] = (m_name + g, lambda graph, n: gen_f(top_n_measure(m_f, graph.copy(), int(n * 1.5)), n))

# Algorithms for first degree measure filter and then with other measures and random generation
for m in measures:
    m_name, m_f = measures[m]
    algs['d'+m] = ('deg' + m_name , lambda graph, n: top_measure_same_50(top_n_measure(m_f, top_n_measure(nx.degree_centrality, graph.copy(), n * 3, True)[1], n), n))

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
            folder, f = algs[flag]
            seeds = f(graph.copy(), n)
            write_seed(folder, g_name, seeds)
            competitors[folder] = [seeds[n * i : n * (i + 1)] for i in range(50)]

    results = sim.run(adj_list, competitors, 50)
    for alg in competitors:
        competitors[alg] = 0
    for result in results:
        competitors[max(result[0].items(), key=lambda x: x[1])[0]] += 1
    print competitors


