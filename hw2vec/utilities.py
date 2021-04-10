import cProfile
import pstats
import io
import os
import sys
from matplotlib import pylab
import matplotlib.pyplot as plt
import networkx as nx

def profileit(func):
    def wrapper(*args, **kwargs):
        datafn = func.__name__ + ".txt" # Name the data file sensibly
        last_time = 0
        count = 0
        if os.path.exists(datafn):
            with open(datafn, 'r') as f: 
                line = f.readline().split(" ")
                count = int(line[0])
                last_time = float(line[1])
        pr = cProfile.Profile()
        retval = pr.runcall(func, *args, **kwargs)
        st = io.StringIO()
        ps = pstats.Stats(pr, stream=st).sort_stats('tottime')
        ps.print_stats()

        with open(datafn, 'w+') as f:
            new_time = float(st.getvalue().split('\n')[0].split(' ')[-2]) + last_time
            f.write(str(count+1) + " " + str(new_time))
        return retval
    wrapper.unwrapped = func
    return wrapper

def save_graph(nxgraph, file_name):
    plt.figure(num=None, figsize=(60, 60), dpi=80)
    plt.axis('off')
    fig = plt.figure(1)

    pos = nx.nx_pydot.graphviz_layout(nxgraph, prog="dot")
    nx.draw_networkx_nodes(nxgraph, pos, with_labels=False)
    nx.draw_networkx_edges(nxgraph, pos)
    labels = {}    
    for node in nxgraph.nodes(data=True):
        labels[node[0]] = node[1]['label']
    nx.draw_networkx_labels(nxgraph, pos, labels)
    plt.savefig(file_name, bbox_inches="tight")
    pylab.close()
    del fig
