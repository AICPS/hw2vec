import os, sys
from pathlib import Path
sys.path.append(str(Path("../../")))
from hw2vec.hw2graph import *
from hw2vec.config import Config
from glob import glob
import pickle
from time import time

def process_graph(cfg, folder_path, hw2graph, profile=True):
    
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
    hw2graph = HW2GRAPH(cfg)
    data_proc = DataProcessor(cfg)
    
    for project in hw2graph.find_hw_project_folders():
        hw_graph = process_graph(cfg, project, hw2graph)
        data_proc.process(hw_graph)
    
    data_proc.cache_graph_data(cfg.data_pkl_path)

if __name__ == '__main__': 
    process_graphs(Config(sys.argv[1:]))