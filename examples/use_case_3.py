import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
from hw2vec.graph2vec.config import Config
from hw2vec.app import GNN4TJ


if __name__ == "__main__":
    #TODO: use the pickle file genreated from use_case 2 to run gnn4tj.
    cfg = Config("./example_gnn4tj.yaml")
    app = GNN4TJ(cfg)
    dataset = app.parse_from_json()
    app.init_trainer(dataset)
    app.train()
    app.evaluate()
    # app.visualize_embeddings("./")