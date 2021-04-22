#!/usr/bin/env python
#title           :test.py
#description     :This file includes the test cases of hw2vec.
#author          :Shih-Yuan Yu
#date            :2021/03/05
#version         :0.2
#notes           :
#python_version  :3.6
#==============================================================================
import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
import warnings
warnings.filterwarnings('ignore')

<<<<<<< HEAD
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from hw2vec.graph2vec.trainers import *
from hw2vec.hw2graph import *
import itertools

class Config:
    '''Configuration and Argument Parser for script to train the IP piracy detection.'''
    def __init__(self, args_parsed):
        for arg_name in vars(args_parsed):
            self.__dict__[arg_name] = getattr(args_parsed, arg_name)
        self.raw_dataset_path = Path(self.raw_dataset_path).resolve()
        self.pkl_path = Path(self.pkl_path).resolve()

def test_GNN4TIP():
    parser = ArgumentParser(description="scripts for generating datasets", formatter_class=RawTextHelpFormatter)
    parser.add_argument('--learning_rate', default=0.001, type=float, help='The initial learning rate for GCN.')
    parser.add_argument('--seed', type=int, default=random.randint(0,2**32), help='Random seed.')
    parser.add_argument('--epochs', type=int, default=200, help='Number of epochs to train.')
    parser.add_argument('--hidden', type=int, default=200, help='Number of hidden units.')
    parser.add_argument('--dropout', type=float, default=0.5, help='Dropout rate (1 - keep probability).')
    parser.add_argument('--embed_dim', type=int, default=32, help="The dimension of graph embeddings.")
    parser.add_argument('--batch_size', type=int, default=4, help='Number of graphs in a batch.')
    parser.add_argument('--device', type=str, default="cpu", help='The device to run on models (cuda or cpu) cpu in default.')
    parser.add_argument('--model', type=str, default="gcn", help="Model to be used intrinsically.")
    parser.add_argument('--num_layers', type=int, default=5, help="Number of layers in the neural network.")
    parser.add_argument('--test_step', type=int, default=10, help="The interval between mini evaluation along the training process.")
    parser.add_argument('--pooling_type', type=str, default="sagpool", help="Graph pooling type.")
    parser.add_argument('--readout_type', type=str, default="max", help="Readout type.")
    parser.add_argument('--ratio', type=float, default=0.8, help="Dataset splitting ratio")
    parser.add_argument('--poolratio', type=float, default=0.75, help="Ratio for graph pooling.")
    parser.add_argument('--raw_dataset_path', type=str, default='../data/IP-datasets/data_DFG/', help="Path to raw dataset for parsing if no precache.")
    parser.add_argument('--pkl_path', type=str, default='./dataset_rtl.pkl', help="Path to hardware graphs for parsing.")
    parser.add_argument('--debug', type=lambda x: (str(x).lower() == 'true'), default=False, help='debug mode.')

    args_parsed = parser.parse_args([])
    cfg = Config(args_parsed)
    cfg.raw_dataset_path = (Path('..')/"data"/"IP-datasets"/"data_DFG").resolve()
    cfg.pkl_path = (Path('.')/'gnn4iprtl.pkl').resolve()
    cfg.epochs = 1
    cfg.debug = True

    SIMILAR = 1
    DISSIMILAR = -1
    
    dataset = DataProcessor(cfg)
    dataset.read_node_labels("RTL")
    dataset.read_node_labels("subgraph")

    trunk = []
    for hw_cat_idx, hardware_root_path in enumerate(glob("%s/**" % str(cfg.raw_dataset_path/"RTL"), recursive=False)):
        
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

    for hw_cat_idx, hardware_root_path in enumerate(glob("%s/**" % str(cfg.raw_dataset_path/"subgraph"), recursive=False)):
        
        for hardware_folder_path in glob("%s/**/topModule.json" % hardware_root_path, recursive=True):
            folder_name = "%s/%s" % (Path(hardware_folder_path).parent.parent.name, Path(hardware_folder_path).parent.name)

            G = dataset.get_graph_from_json(hardware_folder_path)
            X, name2idx, idx2name = dataset.get_node_embeddeings(G)
            edge_idx = dataset.get_edge_idxs(G, name2idx)          
            
            dataset.testing_graph_count += 1
            dataset.append_graph_data((X, edge_idx, folder_name))

    dataset.do_pickle_dataset()

    trainer = PairwiseGraphTrainer(cfg)
    trainer.build()
    trainer.train()
    trainer.evaluate(cfg.epochs)

def test_GNN4TJ():
    parser = ArgumentParser(description='scripts for generating datasets.', formatter_class=RawTextHelpFormatter)
    parser.add_argument('--learning_rate', default=0.001, type=float, help='The initial learning rate for GCN.')
    parser.add_argument('--seed', type=int, default=random.randint(0,2**32), help='Random seed.')
    parser.add_argument('--epochs', type=int, default=200, help='Number of epochs to train.')
    parser.add_argument('--weight_decay', type=float, default=5e-4, help='Weight decay (L2 loss on parameters).')
    parser.add_argument('--hidden', type=int, default=200, help='Number of hidden units.')
    parser.add_argument('--dropout', type=float, default=0.5, help='Dropout rate (1 - keep probability).')
    parser.add_argument('--nclass', type=int, default=8, help="The number of classes for node.")
    parser.add_argument('--recursive', type=lambda x: (str(x).lower() == 'true'), default=True, help='Recursive loading scenegraphs')
    parser.add_argument('--batch_size', type=int, default=4, help='Number of graphs in a batch.')
    parser.add_argument('--device', type=str, default="cpu", help='The device to run on models (cuda or cpu) cpu in default.')
    parser.add_argument('--model', type=str, default="gcn", help="Model to be used intrinsically.")
    parser.add_argument('--num_layers', type=int, default=5, help="Number of layers in the neural network.")
    parser.add_argument('--hidden_dim', type=int, default=32, help="Hidden dimension in GIN.")
    parser.add_argument('--test_step', type=int, default=10, help="The interval between mini evaluation along the training process.")
    parser.add_argument('--pooling_type', type=str, default="sagpool", help="Graph pooling type.")
    parser.add_argument('--readout_type', type=str, default="max", help="Readout type.")
    parser.add_argument('--splitted', type=bool, default=False, help="Indicating whether the target path has been splitted.")
    parser.add_argument('--ratio', type=float, default=0.7, help="Dataset splitting ratio")
    parser.add_argument('--poolratio', type=float, default=0.8, help="Ratio for graph pooling.")
    parser.add_argument('--pkl_path', type=str, default='./hardware_cache.pkl', help="Path to hardware graphs for parsing.")
    parser.add_argument('--raw_dataset_path', type=str, default='../data/TJ-datasets/data_graphs/data_ready_FIXED/', help="Path to raw dataset for parsing if no pkl.")
    parser.add_argument('--embed_dim', type=int, default=2, help="The dimension of graph embeddings.")
    parser.add_argument('--debug', type=lambda x: (str(x).lower() == 'true'), default=True, help='debug mode.')

    args_parsed = parser.parse_args([])
    cfg = Config(args_parsed)
    cfg.device = 'cuda'
    cfg.raw_dataset_path = Path('../data/TJ-datasets/data_graphs/HTD-test1').resolve()
    cfg.pkl_path = Path('./htd-test1.pkl').resolve()
    cfg.epochs = 1
    cfg.debug = True

    '''
        Commands for running the experiments:
            Exp 1: python .\gnn4tj.py --device cuda --raw_dataset_path ..\data\TJ-datasets\data_graphs\HTD-test1 --pkl_path htd-test1.pkl
            Exp 2: python .\gnn4tj.py --device cuda --raw_dataset_path ..\data\TJ-datasets\data_graphs\HTD-test2 --pkl_path htd-test2.pkl
            Exp 3: python .\gnn4tj.py --device cuda --raw_dataset_path ..\data\TJ-datasets\data_graphs\data_ready_FIXED --pkl_path dataready-fixed.pkl
            Exp 4: python .\gnn4tj.py --device cuda --raw_dataset_path ..\data\TJ-datasets\data_graphs\complete_dataset --pkl_path completedataset.pkl
    '''

    TROJAN = 1
    NON_TROJAN = 0

    
    dataset = DataProcessor(cfg)
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

    # initialize a graph trainer for graph classification on trojan classification
    trainer = GraphTrainer(cfg)

    # initialize the model according to cfg. 
    trainer.build()

    # train the model. 
    trainer.train()

    # do a final evaluation.
    trainer.evaluate(cfg.epochs)
=======
from pathlib import Path
from hw2vec.graph2vec.trainers import *
from hw2vec.hw2graph import *
from hw2vec.graph2vec.config import *
from hw2vec.app import GNN4TJ, GNN4IP

def test_GNN4IP():
    cfg = Config({})
    cfg.raw_dataset_path = (Path('..')/"tests"/"data"/"IP-dataset").resolve()
    cfg.pkl_path = (Path('.')/'gnn4ip.pkl').resolve()
    cfg.epochs = 1
    cfg.debug = True
    cfg.batch_size = 1
    app = GNN4IP(cfg)
    dataset = app.parse_from_json()
    app.init_trainer(dataset)
    app.train()
    app.evaluate()

def test_GNN4IP_yaml():
    cfg = Config("./example_gnn4ip.yaml")
    cfg.device = 'cpu'
    cfg.epochs = 1
    cfg.debug = True
    cfg.batch_size = 1
    cfg.raw_dataset_path = (Path('..')/"tests"/"data"/"IP-dataset").resolve()
    cfg.pkl_path = (Path('.')/'gnn4ip.pkl').resolve()
    app = GNN4IP(cfg)
    dataset = app.parse_from_json()
    app.init_trainer(dataset)
    app.train()
    app.evaluate()

def test_GNN4TJ():
    cfg = Config({})
    cfg.raw_dataset_path = (Path('..')/"tests"/"data"/"TJ-dataset").resolve()
    cfg.pkl_path = (Path('.')/'gnn4tj.pkl').resolve()
    cfg.epochs = 1
    cfg.debug = True
    cfg.batch_size = 1
    app = GNN4TJ(cfg)
    dataset = app.parse_from_json()
    app.init_trainer(dataset)
    app.train()
    app.evaluate()

def test_GNN4TJ_yaml():
    cfg = Config("./example_gnn4tj.yaml")
    cfg.device = 'cpu'
    cfg.epochs = 1
    cfg.debug = True
    cfg.batch_size = 1
    app = GNN4TJ(cfg)
    dataset = app.parse_from_json()
    app.init_trainer(dataset)
    app.train()
    app.evaluate()
>>>>>>> master
