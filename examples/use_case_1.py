import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

from hw2vec.hw2graph import *

from optparse import OptionParser
import shutil 
from glob import glob
from pathlib import Path
from pprint import pprint
import networkx as nx
from torch_geometric.utils.convert import from_networkx
from matplotlib import pylab
import matplotlib.pyplot as plt


#TODO: moved to utilities.py
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


if __name__ == '__main__':
    ''' 
        An example on how to genreate the data flow graph for one Verilog harwdare design
        USAGE:  python use_case_1.py 
    '''
    verilog_path = '../tests/data/IP-dataset/Verilog/C432/c432/topModule.v'
    output_path  = './' #TODO: eliminate the use of output_path
    
    g_form = "DFG" # toggle this to select different graph generator. 
    if g_form == "DFG":
        gen = DFGgenerator(verilog_path, output_path)
    elif g_form == "AST":
        gen = ASTgenerator(verilog_path, output_path)

    gen.process()
    g_json = gen.get_graph_json()
    pprint(g_json)
    
    #TODO: do some visualization