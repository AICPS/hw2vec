#!/usr/bin/env python
#title           :app.py
#description     :This file includes the application of hw2vec.
#author          :Shih-Yuan Yu
#date            :2021/03/05
#version         :0.2
#notes           :
#python_version  :3.6
#==============================================================================
import os, sys, itertools, time
sys.path.append(os.path.dirname(sys.path[0]))

from pathlib import Path
from hw2vec.graph2vec.trainers import *
from hw2vec.hw2graph import *
from hw2vec.config import *

from torch_geometric.utils.convert import from_networkx

TROJAN = 1
NON_TROJAN = 0

SIMILAR = 1
DISSIMILAR = -1

class GNN4TJ:
    def __init__(self, cfg):
        self.cfg = cfg

    def init_trainer(self, data_proc, model_path=None):
        all_graphs = data_proc.graph_data
        train_graphs, test_graphs = data_proc.get_graphs()
        class_weights = data_proc.get_class_weights(train_graphs)

        self.train_loader = DataLoader(train_graphs, shuffle=True, batch_size=self.cfg.batch_size)
        self.test_loader  = DataLoader(test_graphs, shuffle=True, batch_size=1)
        self.vis_loader   = DataLoader(all_graphs, batch_size=1)
        self.trainer = GraphTrainer(self.cfg, class_weights=class_weights)
        self.trainer.build()
        if model_path is not None:
            self.trainer.load_saved_model(model_path)

    def process_graph(self, folder_path, profile=True):
        hw2graph = HW2GRAPH(self.cfg)
        
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

    def init_data_proc(self):
        data_proc = DataProcessor(self.cfg)

        if self.cfg.data_pkl_path.exists():
            data_proc.read_graph_data_from_cache(self.cfg.data_pkl_path)
        else:
            for project in data_proc.find_projects():
                hw_graph = self.process_graph(self.cfg, project)
                data_proc.process(hw_graph)

            data_proc.cache_graph_data(self.cfg.data_pkl_path)

        for data in data_proc.graph_data:
            if "TjFree" == data.hw_type:
                data.label = NON_TROJAN
            else:
                data.label = TROJAN
        return data_proc

    def init_evaluator(self, pretrained_model_path=None):
        self.evaluator = Evaluator(self.cfg, "TJ")
        self.evaluator.build()
        if pretrained_model_path is not None:
            self.evaluator.load_saved_model(pretrained_model_path)

    def get_embedding(self):
        self.evaluator.get_embedding(self.vis_loader)

    def train(self):
        # print("Train on %d graphs, Test on %d graphs." % (len(train_graphs), len(test_graphs)))
        # print("Class weights (Tj-free/Tj-in)", class_weights.detach().tolist())
        self.trainer.train(self.train_loader, self.test_loader)

    def evaluate(self):
        self.trainer.evaluate(self.cfg.epochs, self.train_loader, self.test_loader)

    def visualize_embeddings(self, path):
        self.trainer.visualize_embeddings(self.vis_loader, path)

class GNN4IP: 
    def __init__(self, cfg):
        self.cfg = cfg

    def init_trainer(self, dataset):
        graph_pairs_train, graph_pairs_test = dataset.get_pairs()
        train_pairs = []
        test_pairs = []
        data = dataset.graphs['all'] 
        train_list = graph_pairs_train if not self.cfg.debug else graph_pairs_train[:1000]
        test_list = graph_pairs_test if not self.cfg.debug else graph_pairs_test[:250]
        train_pairs = [(data[pairs[0]], data[pairs[1]], pairs[2]) for pairs in train_list]
        test_pairs = [(data[pairs[0]], data[pairs[1]], pairs[2]) for pairs in test_list]               
        self.train_loader = DataLoader(train_pairs, batch_size=self.cfg.batch_size)
        self.test_loader  = DataLoader(test_pairs, batch_size=self.cfg.batch_size)
        self.vis_loader   = DataLoader(data, batch_size=1)
        
        self.cfg.num_feature_dim = dataset.num_node_labels
        self.cfg.labels = [SIMILAR, DISSIMILAR]

        self.trainer = PairwiseGraphTrainer(self.cfg)
        self.trainer.build()
        

    def train(self):
        self.trainer.train(self.train_loader, self.test_loader)

    def evaluate(self):
        self.trainer.evaluate(self.cfg.epochs, self.train_loader, self.test_loader)

    def visualize_embeddings(self, path):
        self.trainer.visualize_embeddings(self.vis_loader, path)