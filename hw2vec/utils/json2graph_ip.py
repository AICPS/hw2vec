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
import itertools

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

import pickle

class GraphParser:

    def __init__(self, root_path:Path):
        self.root_path = root_path.resolve()

        # self.data is a list of graph instances (four-tuple)
        # Each tuple contains (X, edge_idx, folder_name, idx2name)
        self.data = []

        # self.pair_list stores the graph-pairing info. e.g. (0, 1, -1) means graph 0 and graph 1 is dissimilar.
        self.pair_list = []
        
        # self.trunk stores the hardware category information about each hardware design. e.g. in [0, 1, 1, 2, 3], hw #1 belongs to category 1.
        self.trunk = []

        # self.node_labels stores a set of node labels when the parser iterates through the whole dataset.
        self.node_labels = set()
        
        # pair list splitted into train and test sets
        self.train_pair_list = []
        self.test_pair_list = []

        # list to store names of graphs in each set
        self.training_graph_count = 0
        self.testing_graph_count = 0
    
    def read_node_labels(self, key):
        # read thru all the node labels in a dataset. 
        for json_path in glob("%s/**/**/topModule.json" % str(self.root_path/key), recursive=True):
            with open(str(json_path), 'r') as json_file:
                edge_list_dict = json.loads(json_file.read())
                for src in edge_list_dict:
                    self.node_labels.add((src.split(".")[-1].split("_")[0]).lower())

        self.label2idx = {v:k for k, v in enumerate(list(self.node_labels))}
        self.idx2label = {v:k for k, v in self.label2idx.items()}
        
    def split_dataset(self, ratio, seed):
        train_size = int(len(self.pair_list) * ratio)

        sim_diff_label = []

        for pairs in self.pair_list:
            if pairs[2] == 1:
                sim_diff_label.append(1)
            else:
                sim_diff_label.append(-1)

        self.train_pair_list, self.test_pair_list, y_train, y_test = train_test_split(self.pair_list, sim_diff_label, train_size = train_size,
                                                                     shuffle = True, stratify=sim_diff_label, random_state=seed)

    def read_hardware_designs(self, key, do_pairing=False):
        for hw_cat_idx, hardware_root_path in enumerate(glob("%s/**" % str(self.root_path/key), recursive=False)):
            print("parsing %s" %str(hardware_root_path))
            
            for hardware_folder_path in glob("%s/**/topModule.json" % hardware_root_path, recursive=True):
                with open(str(hardware_folder_path), 'r') as json_file:
                    folder_name = "%s/%s" % (Path(hardware_folder_path).parent.parent.name, Path(hardware_folder_path).parent.name)

                    G = nx.DiGraph()
                    name2idx = dict()
                    idx2name = dict()
                    X = []
                    edge_idx = []

                    edge_list_dict = json.loads(json_file.read())
                    for src in edge_list_dict:
                        G.add_node(src, label=src.split(".")[-1].split("_")[0].lower())
                        assert(type(edge_list_dict[src]) == list)
                        for neighbor in edge_list_dict[src]:
                            edge_label = neighbor[0]
                            dst = neighbor[1]
                            G.add_edge(src, dst)
                    
                    # creating X (initial node embedding) e.g [1, 2, 3, 4, 5]
                    for idx, node in enumerate(G.nodes(data=True)):
                        node_name = node[0]
                        node_label = node[1]['label']

                        name2idx[node_name] = idx
                        idx2name[idx] = node_name
                        X.append(self.label2idx[node_label])
                    X = torch.LongTensor(X).detach()

                    # creating A (initial node adjancency information)
                    for src, dst in G.edges():
                        edge_idx.append((name2idx[src], name2idx[dst]))
                    edge_idx = torch.transpose(torch.LongTensor(edge_idx), 0, 1).detach()
                    
                    if do_pairing:
                        self.trunk.append(hw_cat_idx)
                        self.training_graph_count += 1
                    else:
                        self.testing_graph_count += 1
                    self.data.append((X, edge_idx, folder_name))
        
        if do_pairing:
            for idx_graph_a, idx_graph_b in itertools.combinations(range(len(self.trunk)), 2):
                if self.trunk[idx_graph_a] == self.trunk[idx_graph_b]:
                    self.pair_list.append((idx_graph_a, idx_graph_b, 1))
                else:
                    self.pair_list.append((idx_graph_a, idx_graph_b,-1))


    def cache_dataset(self, spliting_ratio=0.8):
        with open("all_data.pkl", "wb") as mapping_file:
            pickle.dump(self.data, mapping_file)

        with open("all_pairing.pkl", "wb") as pairing_file:
            pickle.dump(self.pair_list, pairing_file)

    def print_data_statistics(self):
        avg_num_nodes = sum([item[0].shape[0] for item in self.data]) / len(self.data)
        avg_num_edges = sum([item[1].shape[1] for item in self.data]) / len(self.data)
        similar_pairs_count = sum([item[2] == 1 for item in self.pair_list])
        dissimilar_pairs_count = sum([item[2] == -1 for item in self.pair_list])
        print("avg. # of nodes per graph: %f" % (avg_num_nodes) )
        print("avg. # of edges per graph: %f" % (avg_num_edges) )
        print("total graphs for training: %d" % (self.training_graph_count))
        print("total graphs for testing: %d" % (self.testing_graph_count))
        print("total pairs for training: %d" % (len(self.train_pair_list)))
        print("total pairs for testing: %d" % (len(self.test_pair_list)))
        print("# of different hardware categories: %d" % (max(self.trunk)))
        print("proportion of similar/disimilar in training set: %d/%d" %(similar_pairs_count, dissimilar_pairs_count))        