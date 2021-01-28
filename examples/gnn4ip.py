import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
import warnings
warnings.filterwarnings('ignore')

from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

from hw2vec.core.trainers import *
# from hw2vec.utils.json2graph_ip import *

import pickle

class Config:
    '''Configuration and Argument Parser for script to train the IP piracy detection.'''
    def __init__(self, args):
        self.parser = ArgumentParser(description='''
scripts for generating datasets.
    for generating RTL dataset
        => python 0_run_json2graph.py --raw_dataset_path ../data/data_DFG --precache_path dataset_rtl.pkl --dataset_name RTL
    for generating Netlist dataset
        => python 0_run_json2graph.py --raw_dataset_path ../data/data_DFG --precache_path dataset_netlist.pkl --dataset_name Netlist
        ''', formatter_class=RawTextHelpFormatter)

        self.parser.add_argument('--input_path', type=str, default="../input/synthesis_data/lane-change/", help="Path to code directory.")
        self.parser.add_argument('--learning_rate', default=0.001, type=float, help='The initial learning rate for GCN.')
        self.parser.add_argument('--seed', type=int, default=random.randint(0,2**32), help='Random seed.')
        self.parser.add_argument('--epochs', type=int, default=200, help='Number of epochs to train.')
        self.parser.add_argument('--weight_decay', type=float, default=5e-4, help='Weight decay (L2 loss on parameters).')
        self.parser.add_argument('--hidden', type=int, default=200, help='Number of hidden units.')
        self.parser.add_argument('--dropout', type=float, default=0.5, help='Dropout rate (1 - keep probability).')
        self.parser.add_argument('--embed_dim', type=int, default=32, help="The dimension of graph embeddings.")
        self.parser.add_argument('--batch_size', type=int, default=4, help='Number of graphs in a batch.')
        self.parser.add_argument('--device', type=str, default="cpu", help='The device to run on models (cuda or cpu) cpu in default.')
        self.parser.add_argument('--model', type=str, default="gcn", help="Model to be used intrinsically.")
        self.parser.add_argument('--num_layers', type=int, default=5, help="Number of layers in the neural network.")
        self.parser.add_argument('--test_step', type=int, default=10, help="The interval between mini evaluation along the training process.")
        self.parser.add_argument('--pooling_type', type=str, default="sagpool", help="Graph pooling type.")
        self.parser.add_argument('--readout_type', type=str, default="max", help="Readout type.")
        self.parser.add_argument('--splitted', type=bool, default=False, help="Indicating whether the target path has been splitted.")

        self.parser.add_argument('--dataset_path', type=str, default='./dataset_rtl.pkl', help="Path to dataset.")
        self.parser.add_argument('--ratio', type=float, default=0.8, help="Dataset splitting ratio")
        self.parser.add_argument('--poolratio', type=float, default=0.75, help="Ratio for graph pooling.")
        self.parser.add_argument('--debug', type=bool, default=False, help="Train on all pairs in debug mode.")
 

        self.parser.add_argument('--raw_dataset_path', type=str, default='../data/IP-datasets/data_DFG/', help="Path to raw dataset for parsing if no precache.")
        self.parser.add_argument('--precache_path', type=str, default='./dataset_rtl.pkl', help="Path to hardware graphs for parsing.")
        self.parser.add_argument('--dataset_name', type=str, default='RTL', help="name of hardware design languages." )

        args_parsed = self.parser.parse_args(args)
        for arg_name in vars(args_parsed):
            self.__dict__[arg_name] = getattr(args_parsed, arg_name)
        
        self.raw_dataset_path = Path(self.raw_dataset_path).resolve()
        self.precache_path = Path(self.precache_path).resolve()
        self.input_base_dir = Path(self.input_path).resolve()
        self.dataset_path = Path(self.dataset_path).resolve()


if __name__ == "__main__":
    ''' scripts for generating datasets: 
        for generating RTL dataset 
            => python 0_run_json2graph.py --raw_dataset_path ../data/data_DFG --precache_path dataset_rtl.pkl --dataset_name RTL
        for generating Netlist dataset 
            => python 0_run_json2graph.py --raw_dataset_path ../data/data_DFG --precache_path dataset_netlist.pkl --dataset_name Netlist
    '''
    cfg = Config(sys.argv[1:])
    if cfg.dataset_path.exists() is False:
        #TODO: confusing use of GraphParser
        parser = GraphParser(cfg.raw_dataset_path)
        
        if cfg.dataset_name == "RTL":
            parser.read_node_labels("RTL")
            parser.read_node_labels("subgraph")
            parser.read_hardware_designs("RTL", do_pairing=True)
            parser.read_hardware_designs("subgraph", do_pairing=False)

        elif cfg.dataset_name == "Netlist":
            parser.read_node_labels("Obfuscated")
            parser.read_hardware_designs("Obfuscated", do_pairing=True)
        parser.print_data_statistics()
        with open(cfg.precache_path, "wb") as f:
            pickle.dump(parser, f)

    trainer = PairwiseGraphTrainer(cfg)
    trainer.build()
    trainer.train()
    trainer.evaluate(cfg.epochs)    
    