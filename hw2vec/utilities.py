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
        datafn = func.__name__ + ".txt" 
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

# profiler for graph extraction 
def profilegraph(func):
    def wrapper(*args, **kwargs):
        datafn = func.__name__ + ".txt" 
        #disable stdout
        f_null = open(os.devnull, 'w')
        sys.stdout = f_null
        
        pr = cProfile.Profile()
        pr.enable()

        result_parser = func(*args, **kwargs)

        pr.disable()
        # re-enable stdout
        sys.stdout = sys.__stdout__

        result_graph = result_parser.dfg_graph_generator.graph
        hardware_name = result_parser.verilog_file[:result_parser.verilog_file.index('/topModule.v')].split('/')[-1]
        node_num = len(result_graph.nodes())
        edge_num = len(result_graph.edges())

        st = io.StringIO()
        ps = pstats.Stats(pr, stream=st).sort_stats('tottime')
        ps.print_stats()

        with open(datafn, 'a') as f:
            time = float(st.getvalue().split('\n')[0].split(' ')[-2])
            f.write(str(hardware_name) + " " + str(node_num) + " " + str(edge_num) + " " + str(time) + "\n")
        return result_parser
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

def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
