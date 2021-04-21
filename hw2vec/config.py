#!/usr/bin/env python
#title           :config.py
#description     :This file includes the configs of hw2vec.
#author          :Qingrong Zhou
#date            :2021/03/05
#version         :0.2
#notes           :
#python_version  :3.6
#==============================================================================
import yaml
import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
import random
from pathlib import Path
from argparse import ArgumentParser


class Config:
    def __init__(self, args):
        ap = ArgumentParser(description='The parameters for general arugments.')
        ap.add_argument('--yaml_path', type=str, default="./IP-NetList.yaml", help="The path of yaml config file.")
        ap.add_argument('--debug',     type=bool, default=False, help="The flag for enabling debug mode.")
        args_parsed = ap.parse_args(args)
        for arg_name in vars(args_parsed):
            self.__dict__[arg_name] = getattr(args_parsed, arg_name)
        
        self.yaml_path = Path(self.yaml_path).resolve()
        with open(self.yaml_path, 'r') as f:
            yaml_configs = yaml.safe_load(f)
        for arg_name, arg_value in yaml_configs.items():
            self.__dict__[arg_name] = arg_value

        self.raw_dataset_path = Path(self.raw_dataset_path).resolve() 
        self.pkl_path = Path(self.pkl_path).resolve()
        self.data_pkl_path = Path(self.data_pkl_path).resolve()