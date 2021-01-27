import os, pdb, sys
sys.path.append(os.path.dirname(sys.path[0]))

import random
import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import random_split
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
from sklearn.model_selection import train_test_split

from core.models import *
from core.trainers import *
from abc import ABC, abstractmethod

from glob import glob

#TODO: the graph parser should be only different in the way that the one for ip creates pair data additionally.
class GraphParser:

    def __init__(self, root_path:Path):
        self.root_path = root_path.resolve()
        self.data = []
        self.node_labels = set()
        self.train_data = []
        self.test_data = []
    
    def read_node_labels(self):

        for json_path in glob("%s/**/topModule.json" % str(self.root_path), recursive=True):
            json_file = open(str(json_path), 'r')
            edge_list_dict = json.loads(json_file.read())

            for src in edge_list_dict:
                self.node_labels.add(src.split(".")[-1].split("_")[0])

        self.label2idx = {v:k for k, v in enumerate(list(self.node_labels))}
        self.idx2label = {v:k for k, v in self.label2idx.items()}

    def read_hardware_designs(self, path, label, store_type="all"):

        for json_path in glob("%s/**/topModule.json" % str(self.root_path/path), recursive=True):

            json_file = open(str(json_path), 'r')
            folder_name = json_file.name.replace(str(self.root_path/path)+"/", "").replace("/topModule.json", "")

            G = nx.DiGraph()
            name2idx = dict()
            idx2name = dict()
            X = []
            edge_idx = []

            edge_list_dict = json.loads(json_file.read())
            for src in edge_list_dict:
                G.add_node(src, label=src.split(".")[-1].split("_")[0])
                assert(type(edge_list_dict[src]) == list)
                for neighbor in edge_list_dict[src]:
                    edge_label = neighbor[0]
                    dst = neighbor[1]
                    G.add_edge(src, dst)
            
            for idx, node in enumerate(G.nodes(data=True)):
                node_name = node[0]
                node_label = node[1]['label']

                name2idx[node_name] = idx
                idx2name[idx] = node_name
                X.append(self.label2idx[node_label])

            for src, dst in G.edges():
                edge_idx.append((name2idx[src], name2idx[dst]))

            X = F.one_hot(torch.LongTensor(X), num_classes=len(self.label2idx)).float()
            edge_idx = torch.transpose(torch.LongTensor(edge_idx), 0, 1)
            
            if store_type == "all":
                self.data.append((X, edge_idx, label, folder_name, idx2name))
            elif store_type == "train":
                self.train_data.append((X, edge_idx, label, folder_name, idx2name))
            elif store_type == "test":
                self.test_data.append((X, edge_idx, label, folder_name, idx2name))

    def split_dataset(self, ratio, seed):
        train_length = int(len(self.data) * ratio)
        
        class_0 = []
        class_1 = []

        for g in self.data:
            if g[2] == 0:
                class_0.append(g)
            elif g[2] == 1:
                class_1.append(g)
            
        y_0 = [0]*len(class_0)
        y_1 = [1]*len(class_1)

        self.train_data, self.test_data = train_test_split(self.data, train_size = train_length, 
                                                           shuffle=True, stratify=y_0+y_1, random_state=seed)