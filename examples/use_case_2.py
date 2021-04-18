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
import pickle


def use_case_2(cfg):
    pass


if __name__ == '__main__': 
    cfg = Config(sys.argv[1:])
    parser = JsonGraphParser(cfg)

    nx_graphs = []
    for verilog_path in glob("%s/**/topModule.v" % str(cfg.raw_dataset_path), recursive=True):
        if cfg.graph_type == "DFG":
            graph_generator = DFGgenerator(verilog_path, './')
            graph_generator.process()
            graph_json = graph_generator.get_graph_json()
            hardware_graph = parser.get_graph(graph_json)
            nx_graphs.append((hardware_graph, verilog_path))
        elif cfg.graph_type == "AST":
            graph_generator = ASTgenerator(verilog_path, './')
            graph_generator.generate_ast_json()
        break

    # import pdb; pdb.set_trace()

    # # graph_data = []
    # for hw_graph, verilog_path in nx_graphs:
    #     parser.normalize(hw_graph, normalize=cfg.NORMALIZATION)
    #     data = from_networkx(hw_graph)
    #     data.folder_name = verilog_path
    #     parser.append_graph_data(data)

    # with open(cfg.data_pkl_path, 'wb+') as f:
    #     pickle.dump(parser, f)