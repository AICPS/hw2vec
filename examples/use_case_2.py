import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
from hw2vec.config import Config
from hw2vec.app import GNN4TJ
from hw2vec.hw2graph import *
import pickle
import torch
from glob import glob
from time import time


def use_case_2():
    pass

if __name__ == "__main__":
    cfg = Config(sys.argv[1:])
    app = GNN4TJ(cfg)
    data_proc = app.init_data_proc()
    app.init_trainer(data_proc)
    app.train()
    app.evaluate()
    app.visualize_embeddings("./")