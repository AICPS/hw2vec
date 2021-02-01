import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

import torch
import torch.nn.functional as F

import json
import networkx as nx

from sklearn.model_selection import train_test_split
from glob import glob

from hw2vec.graph2vec.trainers import *


class GraphParser:
    def __init__(self, cfg):
        self.cfg = cfg
        self.root_path = self.cfg.raw_dataset_path.resolve()

        ''' self.graphs is a dict that stores all the hardware graphs that can be parsed from the raw datatset folder. 
            'all': means it is a collection of all graph datasets.
            'train' and 'test': store the collection of graph instances according to a prespliting result.
        '''
        self.graphs = {}

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


    def append_training_graph_data(self, data):
        if 'train' not in self.graphs: 
            self.graphs['train'] = []
        self.graphs['train'].append(data)

    def append_testing_graph_data(self, data):
        if 'test' not in self.graphs: 
            self.graphs['test'] = []
        self.graphs['test'].append(data)
    
    def append_graph_data(self, data):
        if 'all' not in self.graphs: 
            self.graphs['all'] = []
        self.graphs['all'].append(data)

    def append_graph_pair(self, pair):
        self.graph_pairs.append(pair)

    def get_graphs(self):
        if 'train' in self.graphs and 'test' in self.graphs:
            return self.graphs['train'], self.graphs['test']
        elif 'all' in self.graphs:
            return self.split_dataset(ratio=self.cfg.ratio, seed=self.cfg.seed, dataset=self.graphs['all'])

    def do_pickle_dataset(self):
        with open(self.cfg.pkl_path, 'wb') as f:
            pkl.dump(self, f)

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