import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
from hw2vec.graph2vec.config import Config
from hw2vec.app import GNN4TJ

if __name__ == "__main__":
    cfg = Config("./example_gnn4tj.yaml")
    app = GNN4TJ(cfg)
    app.parse_from_json()
    app.init_trainer()
    app.train()
    app.evaluate()