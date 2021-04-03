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

class Config:
    def internal_init(self, list_of_args):
        self.learning_rate = list_of_args['learning_rate'] if ('learning_rate' in list_of_args and list_of_args['learning_rate']!=None ) else 0.001
        self.seed = list_of_args['seed'] if ('seed' in list_of_args and list_of_args['seed']!=None ) else random.randint(0,2**32)
        self.epochs = list_of_args['epochs'] if ('epochs' in list_of_args and list_of_args['epochs']!=None ) else 200
        self.weight_decay = list_of_args['weight_decay'] if ('weight_decay' in list_of_args and list_of_args['weight_decay']!=None ) else 5e-4
        self.hidden = list_of_args['hidden'] if ('hidden' in list_of_args and list_of_args['hidden']!=None ) else 200
        self.dropout = list_of_args['dropout'] if ('dropout' in list_of_args and list_of_args['dropout']!=None ) else 0.5
        self.nclass = list_of_args['nclass'] if ('nclass' in list_of_args and list_of_args['nclass']!=None ) else 8
        self.recursive = list_of_args['recursive'] if ('recursive' in list_of_args and list_of_args['recursive']!=None ) else True
        self.batch_size = list_of_args['batch_size'] if ('batch_size' in list_of_args and list_of_args['batch_size']!=None ) else 4
        self.device = list_of_args['device'] if ('device' in list_of_args and list_of_args['device']!=None ) else "cpu"
        self.model = list_of_args['model'] if ('model' in list_of_args and list_of_args['model']!=None ) else "gcn"
        self.num_layer = list_of_args['num_layer'] if ('num_layer' in list_of_args and list_of_args['num_layer']!=None ) else 5
        self.hidden_dim = list_of_args['hidden_dim'] if ('hidden_dim' in list_of_args and list_of_args['hidden_dim']!=None ) else 32
        self.test_step = list_of_args['test_step'] if ('test_step' in list_of_args and list_of_args['test_step']!=None ) else 10
        self.pooling_type = list_of_args['pooling_type'] if ('pooling_type' in list_of_args and list_of_args['pooling_type']!=None ) else "sagpool"
        self.readout_type = list_of_args['readout_type'] if ('readout_type' in list_of_args and list_of_args['readout_type']!=None ) else "max"
        self.splitted = list_of_args['splitted'] if ('splitted' in list_of_args and list_of_args['splitted']!=None ) else False
        self.ratio = list_of_args['ratio'] if ('ratio' in list_of_args and list_of_args['ratio']!=None ) else 0.7
        self.poolratio = list_of_args['poolratio'] if ('poolratio' in list_of_args and list_of_args['poolratio']!=None ) else 0.8
        self.pkl_path = list_of_args['pkl_path'] if ('pkl_path' in list_of_args and list_of_args['pkl_path']!=None ) else "./hardware_cache.pkl"
        self.raw_dataset_path = list_of_args['raw_dataset_path'] if ('raw_dataset_path' in list_of_args and list_of_args['raw_dataset_path']!=None ) else "../data/TJ-datasets"
        self.embed_dim = list_of_args['embed_dim'] if ('embed_dim' in list_of_args and list_of_args['embed_dim']!=None ) else 2
        self.debug = list_of_args['debug'] if ('debug' in list_of_args and list_of_args['debug']!=None ) else False
        self.data_pkl_path = list_of_args['data_pkl_path'] if ('data_pkl_path' in list_of_args and list_of_args['data_pkl_path']!=None ) else "./graph.pkl"

        self.raw_dataset_path = Path(self.raw_dataset_path).resolve()
        self.pkl_path = Path(self.pkl_path).resolve()


    def __init__(self, args):
        if isinstance(args, dict) :
            self.internal_init(args)
        elif isinstance(args, str):
            yaml_path = Path(args).resolve()
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
            self.internal_init(data)    