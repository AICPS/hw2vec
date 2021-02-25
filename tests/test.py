import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
import warnings
warnings.filterwarnings('ignore')

from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from hw2vec.graph2vec.trainers import *
from hw2vec.hw2graph import *
import itertools
from hw2vec.graph2vec.config import *

class ConfigHelper:
    '''Configuration and Argument Parser for script to train the IP piracy detection.'''
    def __init__(self, args_parsed):
        for arg_name in vars(args_parsed):
            self.__dict__[arg_name] = getattr(args_parsed, arg_name)
        # self.raw_dataset_path = Path(self.raw_dataset_path).resolve()
        # self.pkl_path = Path(self.pkl_path).resolve()
        self.config_path = Path(self.config_path).resolve()

def test_GNN4IP():
    cfg = Config({})
    cfg.raw_dataset_path = (Path('..')/"data"/"IP-dataset").resolve()
    cfg.pkl_path = (Path('.')/'gnn4ip.pkl').resolve()
    cfg.epochs = 1
    cfg.debug = True
    cfg.batch_size = 1

    SIMILAR = 1
    DISSIMILAR = -1
    
    dataset = JsonGraphParser(cfg)
    dataset.read_node_labels("DFG")

    trunk = []
    count = 0
    for hw_cat_idx, hardware_root_path in enumerate(glob("%s/**" % str(cfg.raw_dataset_path/"DFG"), recursive=False)):
        if count > 10:
            break
        for hardware_folder_path in glob("%s/**/topModule.json" % hardware_root_path, recursive=True):
            if count > 10:
                break
            folder_name = "%s/%s" % (Path(hardware_folder_path).parent.parent.name, Path(hardware_folder_path).parent.name)

            G = dataset.get_graph_from_json(hardware_folder_path)
            X, name2idx, idx2name = dataset.get_node_embeddeings(G)
            edge_idx = dataset.get_edge_idxs(G, name2idx)          
            
            trunk.append(hw_cat_idx)
            dataset.training_graph_count += 1

            dataset.append_graph_data((X, edge_idx, folder_name))
            count = count + 1

    for idx_graph_a, idx_graph_b in itertools.combinations(range(len(trunk)), 2):
        if trunk[idx_graph_a] == trunk[idx_graph_b]:
            dataset.append_graph_pair((idx_graph_a, idx_graph_b, SIMILAR))
        else:
            dataset.append_graph_pair((idx_graph_a, idx_graph_b, DISSIMILAR))

    dataset.do_pickle_dataset()

    trainer = PairwiseGraphTrainer(cfg)
    trainer.build()
    trainer.train()
    trainer.evaluate(cfg.epochs)

def test_GNN4IP_yaml():
    parser = ArgumentParser(description="scripts for generating datasets", formatter_class=RawTextHelpFormatter)
    parser.add_argument('--config_path', default='../examples/example_config.yaml', help='path to the config file.')
    
    args_parsed = parser.parse_args([])
    args={}
    args['config_path'] = Path(getattr(args_parsed, 'config_path')).resolve()

    cfg = Config(args['config_path'])

    cfg.device = 'cpu'
    cfg.epochs = 1
    cfg.debug = True
    cfg.batch_size = 1
    cfg.raw_dataset_path = (Path('..')/"data"/"IP-dataset").resolve()
    cfg.pkl_path = (Path('.')/'gnn4ip.pkl').resolve()

    SIMILAR = 1
    DISSIMILAR = -1
    
    dataset = JsonGraphParser(cfg)
    dataset.read_node_labels("DFG")

    trunk = []

    count = 0
    for hw_cat_idx, hardware_root_path in enumerate(glob("%s/**" % str(cfg.raw_dataset_path/"DFG"), recursive=False)):
        if count > 10:
            break
        for hardware_folder_path in glob("%s/**/topModule.json" % hardware_root_path, recursive=True):
            if count > 10:
                break
            folder_name = "%s/%s" % (Path(hardware_folder_path).parent.parent.name, Path(hardware_folder_path).parent.name)

            G = dataset.get_graph_from_json(hardware_folder_path)
            X, name2idx, idx2name = dataset.get_node_embeddeings(G)
            edge_idx = dataset.get_edge_idxs(G, name2idx)          
            
            trunk.append(hw_cat_idx)
            dataset.training_graph_count += 1

            dataset.append_graph_data((X, edge_idx, folder_name))
            count = count + 1

    for idx_graph_a, idx_graph_b in itertools.combinations(range(len(trunk)), 2):
        if trunk[idx_graph_a] == trunk[idx_graph_b]:
            dataset.append_graph_pair((idx_graph_a, idx_graph_b, SIMILAR))
        else:
            dataset.append_graph_pair((idx_graph_a, idx_graph_b, DISSIMILAR))

    dataset.do_pickle_dataset()

    trainer = PairwiseGraphTrainer(cfg)
    trainer.build()
    trainer.train()
    trainer.evaluate(cfg.epochs)

def test_GNN4TJ():
    cfg = Config({})
    cfg.raw_dataset_path = (Path('..')/"data"/"TJ-dataset").resolve()
    cfg.pkl_path = (Path('.')/'gnn4tj.pkl').resolve()
    cfg.epochs = 1
    cfg.debug = True
    cfg.batch_size = 1

    TROJAN = 1
    NON_TROJAN = 0

    
    dataset = JsonGraphParser(cfg)
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

def test_GNN4TJ_yaml():
    parser = ArgumentParser(description="scripts for generating datasets", formatter_class=RawTextHelpFormatter)
    parser.add_argument('--config_path', default='../examples/example_config.yaml', help='path to the config file.')
    
    args_parsed = parser.parse_args([])
    cfg_helper = ConfigHelper(args_parsed)

    cfg = Config(cfg_helper.config_path)

    cfg.device = 'cpu'
    cfg.epochs = 1
    cfg.debug = True
    cfg.batch_size = 1

    TROJAN = 1
    NON_TROJAN = 0

    
    dataset = JsonGraphParser(cfg)
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
