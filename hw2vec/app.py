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

from torch_geometric.utils.convert import from_networkx

TROJAN = 1
NON_TROJAN = 0

SIMILAR = 1
DISSIMILAR = -1

class GNN4TJ:
    def __init__(self, cfg):
        self.cfg = cfg
    
    def process_a_json(self, dataset, json_path):
        folder_name = "%s/%s" % (Path(json_path).parent.parent.name, Path(json_path).parent.name)
        hardware_graph = dataset.get_graph_from_json(json_path)
        data = from_networkx(hardware_graph)
        data.folder_name = folder_name
        return data

    def parse_from_json(self):
        dataset = JsonGraphParser(self.cfg)
        dataset.read_node_labels("")

        for json_path in glob("%s/**/topModule.json" % str(dataset.root_path/"TjFree"), recursive=True):
            data = self.process_a_json(dataset, json_path)
            data.label = NON_TROJAN
            dataset.append_graph_data(data)

        for json_path in glob("%s/**/topModule.json" % str(dataset.root_path/"TjIn"), recursive=True):
            data = self.process_a_json(dataset, json_path)
            data.label = TROJAN
            dataset.append_graph_data(data)

        return dataset

    def init_trainer(self, dataset):
        train_graphs, test_graphs = dataset.get_graphs()
        training_labels = [data.label for data in train_graphs]
        class_weights = torch.from_numpy(compute_class_weight('balanced', np.unique(training_labels), training_labels))

        if self.cfg.debug:
            train_graphs, test_graphs = train_graphs[:10], test_graphs[:10]
        
        print("Train on %d graphs, Test on %d graphs." % (len(train_graphs), len(test_graphs)))
        print("Class weights (Tj-free/Tj-in)", class_weights.detach().tolist())

        self.train_loader = DataLoader(train_graphs, shuffle=True, batch_size=self.cfg.batch_size)
        self.test_loader = DataLoader(test_graphs, shuffle=True, batch_size=1)

        self.cfg.num_feature_dim = len(dataset.label2idx)

        self.trainer = GraphTrainer(self.cfg, class_weights=class_weights)
        self.trainer.build()

    def train(self):
        self.trainer.train(self.train_loader, self.test_loader)

    def evaluate(self):
        self.trainer.evaluate(self.cfg.epochs, self.train_loader, self.test_loader)


class GNN4IP: 
    def __init__(self, cfg):
        self.cfg = cfg

    def process_a_json(self, dataset, json_path):
        folder_name = "%s/%s" % (Path(json_path).parent.parent.name, Path(json_path).parent.name)
        hardware_graph = dataset.get_graph_from_json(json_path)
        data = from_networkx(hardware_graph)
        data.folder_name = folder_name
        return data

    def parse_from_json(self):
        dataset = JsonGraphParser(self.cfg)
        dataset.read_node_labels("DFG")
                
        trunk = []

        for hw_cat_idx, hardware_root_path in enumerate(glob("%s/**" % str(self.cfg.raw_dataset_path/"DFG"), recursive=False)):
            for hardware_folder_path in glob("%s/**/topModule.json" % hardware_root_path, recursive=True):
                data = self.process_a_json(dataset, hardware_folder_path)
                trunk.append(hw_cat_idx)
                dataset.append_graph_data(data)
        
        for idx_graph_a, idx_graph_b in itertools.combinations(range(len(trunk)), 2):
            if trunk[idx_graph_a] == trunk[idx_graph_b]:
                dataset.append_graph_pair((idx_graph_a, idx_graph_b, SIMILAR))
            else:
                dataset.append_graph_pair((idx_graph_a, idx_graph_b, DISSIMILAR))
        
        return dataset

    def init_trainer(self, dataset):
        graph_pairs_train, graph_pairs_test = dataset.get_pairs()
        
        train_pairs = []
        test_pairs = []
        data = dataset.graphs['all']

        train_list = graph_pairs_train if not self.cfg.debug else graph_pairs_train[:1000]
        test_list = graph_pairs_test if not self.cfg.debug else graph_pairs_test[:1000]
        train_pairs = [(data[pairs[0]], data[pairs[1]], pairs[2]) for pairs in train_list]
        test_pairs = [(data[pairs[0]], data[pairs[1]], pairs[2]) for pairs in test_list]
        for pairs in test_list:
            test_pairs.append((data[pairs[0]], data[pairs[1]], pairs[2]))
                
        train_loader = DataLoader(train_pairs, batch_size=self.cfg.batch_size)
        test_loader  = DataLoader(test_pairs, batch_size=self.cfg.batch_size)
        
        self.cfg.num_feature_dim = len(dataset.node_labels)

        self.trainer = PairwiseGraphTrainer(self.cfg)
        self.trainer.train_loader = train_loader
        self.trainer.test_loader = test_loader

        self.trainer.build()

    def train(self):
        self.trainer.train()

    def evaluate(self):
        self.trainer.evaluate(self.cfg.epochs)