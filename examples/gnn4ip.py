import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
from hw2vec.graph2vec.config import Config
from hw2vec.app import GNN4IP

if __name__ == "__main__":
    cfg = Config("./example_gnn4ip.yaml")
    app = GNN4IP(cfg)
    dataset = app.parse_from_json()
    app.init_trainer(dataset)
    app.train()
    app.evaluate()
    # app.visualize_embeddings("./")