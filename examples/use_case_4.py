import os, sys, itertools
sys.path.append(os.path.dirname(sys.path[0]))
from hw2vec.graph2vec.config import Config
from hw2vec.app import GNN4IP
from hw2vec.hw2graph import JsonGraphParser
import pickle

SIMILAR = 1
DISSIMILAR = -1

if __name__ == "__main__":
    #TODO: use the pickle file genreated from use_case 2 to run gnn4ip.    
    cfg = Config("./example_gnn4ip.yaml")
    app = GNN4IP(cfg)
    # dataset = app.parse_from_json()

    dataParser = JsonGraphParser(cfg)
    with open(cfg.data_pkl_path, 'rb') as f:
        dataset = pickle.load(f)

    for data in dataset:
        folder_name = data.folder_name
        class_name = folder_name[folder_name.index('/Verilog/')+9:]
        class_name = class_name[:class_name.index('/')]
        data.class_name = class_name
        dataParser.append_graph_data(data)
    
    for idx_graph_a, idx_graph_b in itertools.combinations(range(len(dataParser.graphs['all'])), 2):
        if dataParser.graphs['all'][idx_graph_a].class_name == dataParser.graphs['all'][idx_graph_b].class_name:
            dataParser.append_graph_pair((idx_graph_a, idx_graph_b, SIMILAR))
        else:
            dataParser.append_graph_pair((idx_graph_a, idx_graph_b, DISSIMILAR))
 
    app.init_trainer(dataParser)
    app.train()
    app.evaluate()
    # app.visualize_embeddings("./")