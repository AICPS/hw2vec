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
    #TODO: use the pickle file genreated from use_case 2 to run gnn4tj.
    cfg = Config("./example_gnn4tj.yaml")
    app = GNN4TJ(cfg)
    # dataset = app.parse_from_json()

    dataParser = JsonGraphParser(cfg)

    with open(cfg.data_pkl_path, 'rb') as f:
        dataset = pickle.load(f)
    
    dataParser.num_node_labels = 1

    for data in dataset:
        if "TJFree" in data.folder_name:
            data.label = NON_TROJAN
        else:
            data.label = TROJAN
        dataParser.append_graph_data(data)

    app.init_trainer(dataParser)
    app.train()
    app.evaluate()
    # app.visualize_embeddings("./")