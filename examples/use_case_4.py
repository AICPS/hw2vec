import os, sys, itertools
sys.path.append(os.path.dirname(sys.path[0]))
from hw2vec.graph2vec.config import Config
from hw2vec.app import GNN4IP
from hw2vec.hw2graph import JsonGraphParser
import pickle
import torch

SIMILAR = 1
DISSIMILAR = -1

if __name__ == "__main__":
    cfg = Config("./example_gnn4ip.yaml")
    app = GNN4IP(cfg)
    # dataset = app.parse_from_json()


    with open(cfg.data_pkl_path, 'rb') as f:
        dataParser = pickle.load(f)

    for data in dataParser.graphs['all']:
        folder_name = data.folder_name
        class_name = folder_name[folder_name.index('/Verilog_temp/')+14:]
        class_name = class_name[:class_name.index('/')]
        data.class_name = class_name
    
    for idx_graph_a, idx_graph_b in itertools.combinations(range(len(dataParser.graphs['all'])), 2):
        if dataParser.graphs['all'][idx_graph_a].class_name == dataParser.graphs['all'][idx_graph_b].class_name:
            dataParser.append_graph_pair((idx_graph_a, idx_graph_b, SIMILAR))
        else:
            dataParser.append_graph_pair((idx_graph_a, idx_graph_b, DISSIMILAR))
 
    app.init_trainer(dataParser)
    app.train()
    app.evaluate()
    # app.visualize_embeddings("./")