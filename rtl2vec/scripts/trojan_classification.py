import os, pdb, sys
sys.path.append(os.path.dirname(sys.path[0]))

import random
import torch
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import scipy.sparse as sp
import pandas as pd


from argparse import ArgumentParser
from pathlib import Path
from tqdm import tqdm
import json
import networkx as nx

from torch_geometric.data import Data, DataLoader
from sklearn.utils.class_weight import compute_class_weight

from core.gcn import *
from core.gin import *
from core.trainer import *
from abc import ABC, abstractmethod

        
if __name__ == "__main__":
    root_trojan = Path("../data/data_ready_FIXED/")
    
    json_path = Path("../data/data_ready_FIXED/TjFree/AES-T100/topModule.json").resolve()       
    
    with open(str(json_path), 'r') as json_file:
        G = nx.DiGraph()
        edge_list_dict = json.loads(json_file.read())
        for src in edge_list_dict:
            assert(type(edge_list_dict[src]) == list)
            for neighbor in edge_list_dict[src]:
                label = neighbor[0]
                dst = neighbor[1]
                G.add_edge(src, dst)
    
    name2idx = dict()
    idx2name = dict()
    X = []
    for idx, node in enumerate(G.nodes):
        name2idx[node] = idx
        idx2name[idx] = node
        X.append(idx)
    
    edge_idx = []
    for src, dst in G.edges():
        edge_idx.append((name2idx[src], name2idx[dst]))

    X = F.one_hot(torch.LongTensor(X)).float()
    edge_idx = torch.transpose(torch.LongTensor(edge_idx), 0, 1)
    trainer = GraphTrainer(sys.argv[1:], [(X, edge_idx)])
    trainer.build()
    trainer.train()

            
    import pdb; pdb.set_trace() 
