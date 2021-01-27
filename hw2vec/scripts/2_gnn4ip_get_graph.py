import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
import warnings
warnings.filterwarnings('ignore')

from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

from utils.json2graph_ip import *

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
        self.parser.add_argument('--raw_dataset_path', type=str, default='../../data/IP-datasets/data_DFG/', help="Path to raw dataset for parsing if no precache.")
        self.parser.add_argument('--precache_path', type=str, default='./dataset_rtl.pkl', help="Path to hardware graphs for parsing.")
        self.parser.add_argument('--dataset_name', type=str, default='RTL', help="name of hardware design languages." )

        args_parsed = self.parser.parse_args(args)
        for arg_name in vars(args_parsed):
            self.__dict__[arg_name] = getattr(args_parsed, arg_name)
        
        self.raw_dataset_path = Path(self.raw_dataset_path).resolve()
        self.precache_path = Path(self.precache_path).resolve()


if __name__ == "__main__":
    ''' scripts for generating datasets: 
        for generating RTL dataset 
            => python 0_run_json2graph.py --raw_dataset_path ../data/data_DFG --precache_path dataset_rtl.pkl --dataset_name RTL
        for generating Netlist dataset 
            => python 0_run_json2graph.py --raw_dataset_path ../data/data_DFG --precache_path dataset_netlist.pkl --dataset_name Netlist
    '''
    cfg = Config(sys.argv[1:])

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
    
    import pdb; pdb.set_trace()