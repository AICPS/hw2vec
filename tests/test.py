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
    app.parse_from_json()
    app.init_trainer()
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
    app.parse_from_json()
    app.init_trainer()
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
    app.parse_from_json()
    app.init_trainer()
    app.train()
    app.evaluate()

def test_GNN4TJ_yaml():
    cfg = Config("./example_gnn4tj.yaml")
    cfg.device = 'cpu'
    cfg.epochs = 1
    cfg.debug = True
    cfg.batch_size = 1
    app = GNN4TJ(cfg)
    app.parse_from_json()
    app.init_trainer()
    app.train()
    app.evaluate()