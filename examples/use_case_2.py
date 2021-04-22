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


def use_case_2(cfg):
    pass


if __name__ == '__main__': 
    cfg = Config(sys.argv[1:])
    parser = JsonGraphParser(cfg)

    # for skipping buggy .v files in IP-RTL (gets pyverilog parse error or definition error)
    pyverilog_buggy_files = ["mips_single_cycle (114)", "mips_single_cycle (12)", "mips_single_cycle (132)", "mips_single_cycle (134)", "mips_single_cycle (138)", "mips_single_cycle (15)", 
    "mips_single_cycle (16)", "mips_single_cycle (26)", "mips_single_cycle (34)", "mips_single_cycle (41)", "mips_single_cycle (49)", "mips_single_cycle (68)", "mips_single_cycle (73)", 
    "mips_single_cycle (75)", "mips_single_cycle (78)", "mips_single_cycle (93)", "AES_2", "AES_6"]
    # for skipping .v files that were taking >5 min to extract graph in IP-RTL
    indefinite_extraction = ["AES_3", "DES_1", "AES_5", "dbg_bridge_1"]

    nx_graphs = []
    #skip = 1
    for verilog_path in glob("%s/**/topModule.v" % str(cfg.raw_dataset_path), recursive=True):
        print(verilog_path)
        # if skip == 1 and verilog_path.split('/')[-2] != "ft60x_axi_1":
        #     continue
        # else:
        #     skip = 0

        # if verilog_path.split('/')[-3] == "mips_single_cycle":
        #     continue

        if verilog_path.split('/')[-2] in pyverilog_buggy_files or verilog_path.split('/')[-2] in indefinite_extraction:
            continue
        if cfg.graph_type == "DFG":
            graph_generator = DFGgenerator(verilog_path, './')
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