import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

from hw2vec.hw2graph import *
from hw2vec.graph2vec.config import Config

from optparse import OptionParser
import shutil 
from glob import glob
from pathlib import Path
from pprint import pprint
import networkx as nx
from torch_geometric.utils.convert import from_networkx
from matplotlib import pylab
import matplotlib.pyplot as plt


if __name__ == '__main__': 
    dataset_directory = '../tests/data/IP-dataset/Verilog/C432/c432'
    output_path = './'

    graph_format = "DFG" # toggle this to select different graph generator.  
    cfg = Config("./example_gnn4tj.yaml") #TODO: temp cfg
    NORMALIZATION = "keep_variable" # or "type_only"

    parser = JsonGraphParser(cfg)

    nx_graphs = []
    for verilog_path in glob("%s/**/topModule.v" % str(dataset_directory), recursive=True):
        if graph_format == "DFG":
            graph_generator = DFGgenerator(verilog_path, output_path)
        elif graph_format == "AST":
            graph_generator = ASTgenerator(verilog_path, output_path)
        graph_generator.process()

        graph_json = graph_generator.get_graph_json()
        hardware_graph = parser.get_graph(graph_json)
        nx_graphs.append((hardware_graph, verilog_path))

    graph_data = []
    for hw_graph, verilog_path in nx_graphs:
        parser.normalize(hw_graph, normalize=NORMALIZATION)
        data = from_networkx(hw_graph)
        data.folder_name = verilog_path
        # data.label = xxx 
        graph_data.append(data)

    # pickle to a file.
