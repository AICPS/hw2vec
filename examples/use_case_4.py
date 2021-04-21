import os, sys, itertools
sys.path.append(os.path.dirname(sys.path[0]))
from hw2vec.config import Config
from hw2vec.app import GNN4IP
from hw2vec.hw2graph import JsonGraphParser
import pickle
import torch
from pathlib import Path

SIMILAR = 1
DISSIMILAR = -1

if __name__ == "__main__":
    #cfg = Config("./example_gnn4ip.yaml")
    cfg = Config(sys.argv[1:])
    app = GNN4IP(cfg)
    # dataset = app.parse_from_json()


    with open(cfg.data_pkl_path, 'rb') as f:
        dataParser = pickle.load(f)

    for data in dataParser.graphs['all']:
        folder_name = data.folder_name
        #class_name = folder_name[folder_name.index('/Verilog_temp/')+14:]
        #class_name = class_name[:class_name.index('/')]
        class_name = folder_name.split("/")[-3]
        data.class_name = class_name
    
    for idx_graph_a, idx_graph_b in itertools.combinations(range(len(dataParser.graphs['all'])), 2):
        if dataParser.graphs['all'][idx_graph_a].class_name == dataParser.graphs['all'][idx_graph_b].class_name:
            dataParser.append_graph_pair((idx_graph_a, idx_graph_b, SIMILAR))
        else:
            dataParser.append_graph_pair((idx_graph_a, idx_graph_b, DISSIMILAR))
        # if len(dataParser.graph_pairs) == 2:
        #     break
 
    app.init_trainer(dataParser)
    model_path = "./AST_IP_RTL_model/"
    #model_path = "./AST_IP_NetList_model/"
    if Path(model_path+"model").exists():
        app.trainer.load_saved_model(model_path+"model")
    else:
        app.train()
        app.trainer.save_model(model_path)
    app.evaluate()
    app.visualize_embeddings("./")