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
    # step1: process graph with hw2graph     
    nx_graphs = []
    for verilog_path in glob("%s/**/topModule.v" % str(cfg.raw_dataset_path), recursive=True):
        print("Reading ", verilog_path)
        hw2graph = HW2GRAPH(cfg, verilog_path)
        hardware_graph = hw2graph.process() #TODO: not implemented for CFG.
        nx_graphs.append((hardware_graph, verilog_path)) 
    
    # step2: use data_proc to create the dataset.
    data_proc = DataProcessor(cfg)
    for hw_graph, verilog_path in nx_graphs:
        data_proc.normalize(hw_graph, normalize=cfg.NORMALIZATION, graph_format=cfg.graph_type)
        data = from_networkx(hw_graph)
        data.folder_name = verilog_path
        data_proc.append_graph_data(data)
    
    # step3: cache the whole data_proc.
    with open(cfg.data_pkl_path, 'wb+') as f:
        pickle.dump(data_proc, f)


if __name__ == '__main__': 
    cfg = Config(sys.argv[1:])
    process_graphs(cfg)