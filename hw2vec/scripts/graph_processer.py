import os, sys
from pathlib import Path
sys.path.append(str(Path("../../")))
from hw2vec.hw2graph import *
from hw2vec.config import Config
from glob import glob
import pickle
from time import time

def process_graph(cfg, folder_path, profile=True):
    hw2graph = HW2GRAPH(cfg)
    
    if profile:
        start = time()

    if "topModule.v" not in [Path(x).name for x in glob("%s/*.v"%str(folder_path))]:
        code_path = hw2graph.preprocess(folder_path)
    else:
        code_path = folder_path / "topModule.v"

    hw_graph = hw2graph.process(str(code_path))
    
    if profile:
        end = time()
        print(str(code_path), ",", len(hw_graph.nodes), ",", len(hw_graph.edges), ",", end-start)

    return hw_graph

def process_graphs(cfg):
    data_proc = DataProcessor(cfg)
    
    for project in data_proc.find_projects():
        hw_graph = process_graph(cfg, project)
        data_proc.process(hw_graph)
    
    data_proc.cache_graph_data(cfg.data_pkl_path)

if __name__ == '__main__': 
    process_graphs(Config(sys.argv[1:]))