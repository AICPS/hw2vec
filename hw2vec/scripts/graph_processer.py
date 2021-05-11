import os, sys
from pathlib import Path
sys.path.append(str(Path("../../")))
from hw2vec.hw2graph import *
from hw2vec.config import Config
from glob import glob
import pickle
from time import time

def process_graph(cfg, code_path, profile=True):
    hw2graph = HW2GRAPH(cfg)
    
    if profile:
        start = time()

    hw_graph = hw2graph.process(code_path) #TODO: not implemented for CFG.
    
    if profile:
        end = time()
        print(code_path, ",", len(hw_graph.nodes), ",", len(hw_graph.edges), ",", end-start)

    return hw_graph

def process_graphs(cfg):
    data_proc = DataProcessor(cfg)

    for verilog_path in glob("%s/**/topModule.v" % str(cfg.raw_dataset_path), recursive=True):
        hw_graph = process_graph(cfg, verilog_path)
        data_proc.process(hw_graph)
    
    with open(cfg.data_pkl_path, 'wb+') as f:
        pickle.dump(data_proc, f)


if __name__ == '__main__': 
    process_graphs(Config(sys.argv[1:]))