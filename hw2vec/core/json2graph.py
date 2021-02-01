import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

import torch
import torch.nn.functional as F
import itertools

from pathlib import Path
import json
import networkx as nx

from sklearn.model_selection import train_test_split

# from hw2vec.core.models import *
from hw2vec.graph2vec.trainers import *

from glob import glob

class BaseGraphParser:
    def __init__(self, root_path:Path):
        self.root_path = root_path.resolve()
        
        ''' self.graphs stores all the hardware graphs that can be parsed from the raw datatset folder. '''
        self.graphs = [] 

        self.node_labels = set()
        
        ''' for GNN4IP '''
        ''' self.graph_pairs/_train/_test stores the graph-pairing info. e.g. (0, 1, -1) means graph 0 and graph 1 is dissimilar. '''
        self.graph_pairs       = []
        self.graph_pairs_train = [] 
        self.graph_pairs_test  = []
        
        # self.trunk stores the hardware category information about each hardware design. e.g. in [0, 1, 1, 2, 3], hw #1 belongs to category 1.
        self.trunk = []

        # list to store names of graphs in each set
        self.training_graph_count = 0
        self.testing_graph_count = 0

        ''' For GNN4TJ '''
        self.train_data = []
        self.test_data = []

    def read_node_labels(self, key):
        # read thru all the node labels in a dataset. 
        for json_path in glob("%s/**/**/topModule.json" % str(self.root_path/key), recursive=True):
            with open(str(json_path), 'r') as json_file:
                edge_list_dict = json.loads(json_file.read())
                for src in edge_list_dict:
                    self.node_labels.add((src.split(".")[-1].split("_")[0]).lower())

        self.label2idx = {v:k for k, v in enumerate(list(self.node_labels))}
        self.idx2label = {v:k for k, v in self.label2idx.items()}

    def split_dataset(self, ratio, seed, dataset):
        train_size = int(len(dataset) * ratio)

        sim_diff_label = []

        for data in dataset:
            if data[2] == 1:
                sim_diff_label.append(1)
            else:
                sim_diff_label.append(-1)

        return train_test_split(dataset, train_size = train_size, shuffle = True, stratify=sim_diff_label, random_state=seed)

    def get_graph_from_json(self, json_path):
        json_file = open(str(json_path), 'r')
        hardware_graph = nx.DiGraph()
        edge_list_dict = json.loads(json_file.read())
        for src in edge_list_dict:
            hardware_graph.add_node(src, label=src.split(".")[-1].split("_")[0].lower())
            assert(type(edge_list_dict[src]) == list)
            for neighbor in edge_list_dict[src]:
                edge_label = neighbor[0]
                dst = neighbor[1]
                hardware_graph.add_edge(src, dst)

        return hardware_graph

    def get_node_embeddeings(self, graph):
        X=[]
        name2idx = {}
        idx2name = {}
        for idx, node in enumerate(graph.nodes(data=True)):
            node_name = node[0]
            node_label = node[1]['label']

            name2idx[node_name] = idx
            idx2name[idx] = node_name
            X.append(self.label2idx[node_label])
        
        X = F.one_hot(torch.LongTensor(X), num_classes=len(self.label2idx)).float()
        return X, name2idx, idx2name

    def get_edge_idxs(self, graph, name2idx):
        edge_idx = []
        for src, dst in graph.edges():
            edge_idx.append((name2idx[src], name2idx[dst]))
        edge_idx = torch.transpose(torch.LongTensor(edge_idx), 0, 1).detach()
        return edge_idx


class GraphParser_IP(BaseGraphParser):

    def __init__(self, root_path:Path):
        super().__init__(root_path)     

    def read_hardware_designs(self, key, do_pairing=False):
        for hw_cat_idx, hardware_root_path in enumerate(glob("%s/**" % str(self.root_path/key), recursive=False)):
            print("parsing %s" %str(hardware_root_path))
            
            for hardware_folder_path in glob("%s/**/topModule.json" % hardware_root_path, recursive=True):
                folder_name = "%s/%s" % (Path(hardware_folder_path).parent.parent.name, Path(hardware_folder_path).parent.name)

                G = self.get_graph_from_json(hardware_folder_path)
                X, name2idx, idx2name = self.get_node_embeddeings(G)
                edge_idx = self.get_edge_idxs(G, name2idx)          
                
                if do_pairing:
                    self.trunk.append(hw_cat_idx)
                    self.training_graph_count += 1
                else:
                    self.testing_graph_count += 1
                self.graphs.append((X, edge_idx, folder_name))
        
        if do_pairing:
            for idx_graph_a, idx_graph_b in itertools.combinations(range(len(self.trunk)), 2):
                if self.trunk[idx_graph_a] == self.trunk[idx_graph_b]:
                    self.graph_pairs.append((idx_graph_a, idx_graph_b, 1))
                else:
                    self.graph_pairs.append((idx_graph_a, idx_graph_b,-1))

class GraphParser_TJ(BaseGraphParser):

    def __init__(self, root_path:Path):
        super().__init__(root_path)

    def read_hardware_designs(self, path, label, store_type="all"):

        for json_path in glob("%s/**/topModule.json" % str(self.root_path/path), recursive=True):
            folder_name = "%s/%s" % (Path(json_path).parent.parent.name, Path(json_path).parent.name)

            hardware_graph = self.get_graph_from_json(json_path)
            X, name2idx, idx2name = self.get_node_embeddeings(hardware_graph)
            edge_idxs = self.get_edge_idxs(hardware_graph, name2idx)
                                    
            if store_type == "all":
                self.graphs.append((X, edge_idxs, label, folder_name, idx2name))
            elif store_type == "train":
                self.train_data.append((X, edge_idxs, label, folder_name, idx2name))
            elif store_type == "test":
                self.test_data.append((X, edge_idxs, label, folder_name, idx2name))