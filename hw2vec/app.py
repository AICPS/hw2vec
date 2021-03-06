#!/usr/bin/env python
#title           :app.py
#description     :This file includes the application of hw2vec.
#author          :Shih-Yuan Yu
#date            :2021/03/05
#version         :0.2
#notes           :
#python_version  :3.6
#==============================================================================
import os, sys, itertools
sys.path.append(os.path.dirname(sys.path[0]))

from pathlib import Path
from hw2vec.graph2vec.trainers import *
from hw2vec.hw2graph import *
from hw2vec.graph2vec.config import *

TROJAN = 1
NON_TROJAN = 0

SIMILAR = 1
DISSIMILAR = -1

class GNN4TJ:
    def __init__(self, cfg):
        self.cfg = cfg
    
    def parse_from_json(self):
        if self.cfg.pkl_path.exists() is False:
            dataset = JsonGraphParser(self.cfg)
            dataset.read_node_labels("")

            for json_path in glob("%s/**/topModule.json" % str(dataset.root_path/"TjFree"), recursive=True):
                folder_name = "%s/%s" % (Path(json_path).parent.parent.name, Path(json_path).parent.name)

                hardware_graph = dataset.get_graph_from_json(json_path)
                node_embeddings, name2idx, idx2name = dataset.get_node_embeddeings(hardware_graph)
                edge_idxs = dataset.get_edge_idxs(hardware_graph, name2idx)
                dataset.append_graph_data((node_embeddings, edge_idxs, NON_TROJAN, folder_name, idx2name))

            for json_path in glob("%s/**/topModule.json" % str(dataset.root_path/"TjIn"), recursive=True):
                folder_name = "%s/%s" % (Path(json_path).parent.parent.name, Path(json_path).parent.name)

                hardware_graph = dataset.get_graph_from_json(json_path)
                node_embeddings, name2idx, idx2name = dataset.get_node_embeddeings(hardware_graph)
                edge_idxs = dataset.get_edge_idxs(hardware_graph, name2idx)
                dataset.append_graph_data((node_embeddings, edge_idxs, TROJAN, folder_name, idx2name))

            dataset.do_pickle_dataset()
    
    def init_trainer(self):
        self.trainer = GraphTrainer(self.cfg)
        self.trainer.build()

    def train(self):
        self.trainer.train()

    def evaluate(self):
        self.trainer.evaluate(self.cfg.epochs)


class GNN4IP: 
    def __init__(self, cfg):
        self.cfg = cfg

    def parse_from_json(self):
        if self.cfg.pkl_path.exists() is False:
            dataset = JsonGraphParser(self.cfg)
            dataset.read_node_labels("DFG")
                
            trunk = []

            for hw_cat_idx, hardware_root_path in enumerate(glob("%s/**" % str(self.cfg.raw_dataset_path/"DFG"), recursive=False)):
                
                for hardware_folder_path in glob("%s/**/topModule.json" % hardware_root_path, recursive=True):
                    folder_name = "%s/%s" % (Path(hardware_folder_path).parent.parent.name, Path(hardware_folder_path).parent.name)

                    G = dataset.get_graph_from_json(hardware_folder_path)
                    X, name2idx, idx2name = dataset.get_node_embeddeings(G)
                    edge_idx = dataset.get_edge_idxs(G, name2idx)          
                    
                    trunk.append(hw_cat_idx)
                    dataset.training_graph_count += 1

                    dataset.append_graph_data((X, edge_idx, folder_name))

            for idx_graph_a, idx_graph_b in itertools.combinations(range(len(trunk)), 2):
                if trunk[idx_graph_a] == trunk[idx_graph_b]:
                    dataset.append_graph_pair((idx_graph_a, idx_graph_b, SIMILAR))
                else:
                    dataset.append_graph_pair((idx_graph_a, idx_graph_b, DISSIMILAR))

            dataset.do_pickle_dataset()

    def init_trainer(self):
        self.trainer = PairwiseGraphTrainer(self.cfg)
        self.trainer.build()

    def train(self):
        self.trainer.train()

    def evaluate(self):
        self.trainer.evaluate(self.cfg.epochs)