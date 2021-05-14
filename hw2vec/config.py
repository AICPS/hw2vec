#!/usr/bin/env python
#title           :config.py
#description     :This file includes the configs of hw2vec.
#author          :Qingrong Zhou
#date            :2021/03/05
#version         :0.2
#notes           :
#python_version  :3.6
#==============================================================================
import yaml, os, sys
sys.path.append(os.path.dirname(sys.path[0]))
from pathlib import Path
from argparse import ArgumentParser

class Config:
    def __init__(self, args):
        ap = ArgumentParser(description='The parameters for general arguments.')
        ap.add_argument('--yaml_path', type=str, default="./example_gnn4tj.yaml", help="The path of yaml config file.")
        ap.add_argument('--raw_dataset_path', type=str, default="../../assets/data/TJ-RTL-toy/", help="The path to raw dataset for parsing.")
        ap.add_argument('--data_pkl_path', type=str, default="./DFG-TJ-RTL.pkl", help="The path to the pickle file storing the graph dataset.")
        ap.add_argument('--model_path', type=str, default="", help="Pretrained IP model ../assets/pretrained_ip_model/, Pretrained TJ model ../assets/pretrained_tj_model/")
        ap.add_argument('--graph_type', type=str, default="DFG", help="The graph type to retrieve for inspection or training/evaluating.")
        ap.add_argument('--device',    type=str, default="cpu", help="The device for training/evaluating.")
        args_parsed = ap.parse_args(args)
        for arg_name in vars(args_parsed):
            self.__dict__[arg_name] = getattr(args_parsed, arg_name)
        
        self.yaml_path = Path(self.yaml_path).resolve()
        with open(self.yaml_path, 'r') as f:
            yaml_configs = yaml.safe_load(f)
        for arg_name, arg_value in yaml_configs.items():
            self.__dict__[arg_name] = arg_value

        self.raw_dataset_path = Path(self.raw_dataset_path).resolve() 
        self.data_pkl_path = Path(self.data_pkl_path).resolve()
        self.model_path_obj = Path(self.model_path).resolve()