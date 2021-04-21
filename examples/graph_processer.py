import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

from hw2vec.hw2graph import *
from hw2vec.config import Config

from optparse import OptionParser
import shutil 
from glob import glob
from pathlib import Path
from pprint import pprint
import networkx as nx
from torch_geometric.utils.convert import from_networkx
from matplotlib import pylab
import matplotlib.pyplot as plt
import pickle


def process_graphs(cfg):
    parser = JsonGraphParser(cfg)

    nx_graphs = []
    for verilog_path in glob("%s/**/topModule.v" % str(cfg.raw_dataset_path), recursive=True):
        print(verilog_path)
        
        if cfg.graph_type == "DFG":
            graph_generator = DFGgenerator(verilog_path)
            graph_generator.process()
            graph_json = graph_generator.get_graph_json()
            hardware_graph = parser.get_graph(graph_json)
            nx_graphs.append((hardware_graph, verilog_path))

        elif cfg.graph_type == "AST":
            graph_generator = ASTgenerator(verilog_path)
            hardware_graph, verilog_path = graph_generator.process()
            #hardware_graph = parser.get_graph(graph_generator.ast_dict, cfg.graph_type)
            #nx_graphs.append((hardware_graph, verilog_path))

            parser.normalize(hardware_graph, normalize=cfg.NORMALIZATION, graph_format=cfg.graph_type)
            data = from_networkx(hardware_graph)
            data.folder_name = verilog_path
            parser.append_graph_data(data)

    # for hw_graph, verilog_path in nx_graphs:
    #     parser.normalize(hw_graph, normalize=cfg.NORMALIZATION, graph_format=cfg.graph_type)
    #     data = from_networkx(hw_graph)
    #     data.folder_name = verilog_path
    #     parser.append_graph_data(data)

    with open(cfg.data_pkl_path, 'wb+') as f:
        pickle.dump(parser, f)


if __name__ == '__main__': 
    cfg = Config(sys.argv[1:])
    
    process_graphs(cfg)