import os, sys, itertools
sys.path.append(os.path.dirname(sys.path[0]))
from hw2vec.config import Config
from hw2vec.app import GNN4IP
from hw2vec.hw2graph import DataProcessor
import pickle
import torch
from pathlib import Path

SIMILAR = 1
DISSIMILAR = -1

def use_case_3():
    pass

if __name__ == "__main__":
    cfg = Config(sys.argv[1:])
    app = GNN4IP(cfg)


    with open(cfg.data_pkl_path, 'rb') as f:
        data_proc = pickle.load(f)

    for data in data_proc.graphs['all']:
        folder_name = data.folder_name
        class_name = folder_name.split("/")[-3]
        data.class_name = class_name
    
    for idx_graph_a, idx_graph_b in itertools.combinations(range(len(data_proc.graphs['all'])), 2):
        if data_proc.graphs['all'][idx_graph_a].class_name == data_proc.graphs['all'][idx_graph_b].class_name:
            data_proc.append_graph_pair((idx_graph_a, idx_graph_b, SIMILAR))
        else:
            data_proc.append_graph_pair((idx_graph_a, idx_graph_b, DISSIMILAR))
 
    app.init_trainer(data_proc)
    app.train()
    app.evaluate()
    app.visualize_embeddings("./")