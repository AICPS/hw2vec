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
from hw2vec.config import *

from torch_geometric.utils.convert import from_networkx

TROJAN = 1
NON_TROJAN = 0

SIMILAR = 1
DISSIMILAR = -1

class GNN4TJ:
    def __init__(self, cfg):
        self.cfg = cfg

    def init_trainer(self, dataset, model_path=None):
        all_graphs = dataset.graphs['all'] 
        train_graphs, test_graphs = dataset.get_graphs()
        training_labels = [data.label for data in train_graphs]
        class_weights = torch.from_numpy(compute_class_weight('balanced', np.unique(training_labels), training_labels))

        if self.cfg.debug:
            train_graphs, test_graphs = train_graphs[:10], test_graphs[:10]
        
        print("Train on %d graphs, Test on %d graphs." % (len(train_graphs), len(test_graphs)))
        print("Class weights (Tj-free/Tj-in)", class_weights.detach().tolist())

        self.train_loader = DataLoader(train_graphs, shuffle=True, batch_size=self.cfg.batch_size)
        self.test_loader = DataLoader(test_graphs, shuffle=True, batch_size=1)
        self.vis_loader   = DataLoader(all_graphs, batch_size=1)

        self.cfg.num_feature_dim = dataset.num_node_labels
        self.cfg.labels = [TROJAN, NON_TROJAN]

        self.trainer = GraphTrainer(self.cfg, class_weights=class_weights)
        self.trainer.build()
        if model_path is not None:
            self.trainer.load_saved_model(model_path)

    def init_evaluator(self, pretrained_model_path=None):
        self.evaluator = Evaluator(self.cfg, "TJ")
        self.evaluator.build()
        if pretrained_model_path is not None:
            self.evaluator.load_saved_model(pretrained_model_path)

    def get_embedding(self):
        self.evaluator.get_embedding(self.vis_loader)

    def train(self):
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