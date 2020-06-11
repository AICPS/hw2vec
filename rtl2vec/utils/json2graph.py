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

from glob import glob


def read_hardware_designs(path, label):
    data = []

    for json_path in glob("%s/**/*.json" % str(path), recursive=True):

        json_file = open(str(json_path), 'r')

        G = nx.DiGraph()
        name2idx = dict()
        idx2name = dict()
        X = []
        edge_idx = []

        edge_list_dict = json.loads(json_file.read())
        for src in edge_list_dict:
            assert(type(edge_list_dict[src]) == list)
            for neighbor in edge_list_dict[src]:
                edge_label = neighbor[0]
                dst = neighbor[1]
                G.add_edge(src, dst)
    
        for idx, node in enumerate(G.nodes):
            name2idx[node] = idx
            idx2name[idx] = node
            X.append(idx)
        
        for src, dst in G.edges():
            edge_idx.append((name2idx[src], name2idx[dst]))

        X = F.one_hot(torch.LongTensor(X)).float()
        edge_idx = torch.transpose(torch.LongTensor(edge_idx), 0, 1)
        
        data.append((X, edge_idx, label))

    return data