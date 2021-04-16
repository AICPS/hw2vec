import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
from hw2vec.graph2vec.config import Config
from hw2vec.app import GNN4TJ
from hw2vec.hw2graph import JsonGraphParser
import pickle
import torch

TROJAN = 1
NON_TROJAN = 0

if __name__ == "__main__":
    cfg = Config("./example_gnn4tj.yaml")
    app = GNN4TJ(cfg)
    # dataset = app.parse_from_json()

    dataParser = JsonGraphParser(cfg)

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
    # app.visualize_embeddings("./")