import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
from hw2vec.config import Config
from hw2vec.app import GNN4TJ
from hw2vec.hw2graph import DataProcessor
import pickle
import torch

TROJAN = 1
NON_TROJAN = 0

def use_case_2():
    pass

if __name__ == "__main__":
    cfg = Config(sys.argv[1:])
    app = GNN4TJ(cfg)

    dataParser = DataProcessor(cfg)

    with open(cfg.data_pkl_path, 'rb') as f:
        dataParser = pickle.load(f)

    for data in dataParser.graphs['all']:
        if "TjFree" in data.folder_name:
            data.label = NON_TROJAN
        else:
            data.label = TROJAN

    app.init_trainer(dataParser)
    app.train()
    app.evaluate()
    app.visualize_embeddings("./")