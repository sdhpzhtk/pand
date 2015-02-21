import json
from sys import *
import random
import sim

def read_graph(fname):
    ''' Reads a graph json file. Note the file should be under graph/
    
    Args:
        fname: string. The file name of the graph under the folder graph/.
    
    Returns
        A dict of adjacency lists.
    '''
    with open('graph/' + fname, 'r') as fin:
        data = json.load(fin)
    
    graph = {int(i): [int(j) for j in data[i]] for i in data}

    return graph

def write_seed(alg_name, fname, seeds):
    ''' Writes the selected seeds to file.
    
    Args:
        alg_name: the algorithm name, the file will be saved under alg_name 
                  folder
        fname: the file name
        seeds: [50 * num_seeds of seed id's]. Note seed id should be an int.
    '''
    with open(alg_name + '/' + fname, 'w') as fout:
        for seed in seeds:
            fout.write(str(seed) + '\n')

def deg(adj_dict, n):
    ''' Chooses n nodes based on the most degrees.
    
    Args:
        adj_dict: a dict of {seed_id: a list of adjacent seed_id's}
        
    Returns:
        seeds: 50 * [list of top n max-degree seed_id's]
    '''

    degs = sorted([(id, len(adj_dict[id])) for id in adj_dict],
                  key=lambda x: x[1], reverse=True)
    print degs
    seeds = [degs[i][0] for i in range(n)]
    return seeds * 50

def rand(adj_dict, n):
    ''' Randomly chooses no nodes from the graph
    '''
    seeds = []
    for _ in range(50):
        seeds += random.sample(adj_dict, n)
    return seeds * 50


# A dict of all algorithms for selection. {flag: (folder name, function name)}
algs = {'r': ('rand', rand),
        'd': ('deg', deg),
       }

if __name__ == '__main__':
    g_name = argv[1]
    n = int(g_name.split('.')[1])
    graph = read_graph(g_name)
    
    competitors = {}
    for flag in argv[2:]:
        if flag in algs:
            folder, f = algs[flag]
            seeds = f(graph, n)
            write_seed(folder, g_name, seeds)
            competitors[folder] = [seeds[:n]]
    print sim.run(graph, competitors, 1)


