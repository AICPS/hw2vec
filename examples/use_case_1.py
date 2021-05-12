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
    
    # evaluator = Evaluator(cfg, "TJ")
    # evaluator.build()
    # if Path(cfg.model_path)/"model" is not None:
    #     evaluator.load_saved_model(Path(cfg.model_path)/"model")
    # all_graphs = data_proc.graph_data
    # vis_loader   = DataLoader(all_graphs, batch_size=1)
    # embed = evaluator.get_embedding(vis_loader)
    # return embed

if __name__ == '__main__': 
    
    graph_emb = use_case_1(Config(sys.argv[1:]))
    
    print(graph_emb)
    # NOTE: Embedding is a vector of features, do any inspection on embedding for your own usage.