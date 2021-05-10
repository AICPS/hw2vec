import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

from hw2vec.hw2graph import *
from hw2vec.config import Config
from hw2vec.app import *

def use_case_1(cfg):
    hw2graph = HW2GRAPH(cfg)

    hw_design_dir_path = cfg.raw_dataset_path
    hw_design_path = hw2graph.preprocess(hw_design_dir_path)
    hardware_nxgraph = hw2graph.process(hw_design_path)

    data_proc = DataProcessor(cfg)
    data = data_proc.process(hardware_nxgraph)
    data_proc.append_graph_data(data)
    
    # app = GNN4TJ(cfg)
    # app.init_evaluator(pretrained_model_path=cfg.model_path / "model")
    # embedding = app.get_embedding(vis_loader)


if __name__ == '__main__': 
    
    graph_emb = use_case_1(Config(sys.argv[1:]))
    
    print(graph_emb)
    # NOTE: Embedding is a vector of features, do any inspection on embedding for your own usage.