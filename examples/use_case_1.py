import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

from hw2vec.hw2graph import *
from hw2vec.config import Config
from hw2vec.app import *

from torch_geometric.utils.convert import from_networkx

def hw2graph(verilog_path):
    preprocessor = PreprocessVerilog(input_path=verilog_path, target_path=verilog_path / "topModule.v")
    preprocessor.flatten()
    preprocessor.remove_comments()
    preprocessor.remove_underscores()
    preprocessor.rename_topModule()

    graph_generator = HW2GRAPH(cfg)
    hardware_graph = graph_generator.process(verilog_file=str(verilog_path) + '/topModule.v') #TODO: not implemented for CFG

    return hardware_graph

def graph2vec(cfg, graph, verilog_path):
    data_proc = DataProcessor(cfg)
    data_proc.normalize(nx_graph=graph, normalize=cfg.NORMALIZATION, graph_format=cfg.graph_type)
    data = from_networkx(graph)
    data.folder_name = verilog_path
    # data_proc.append_graph_data(data)

    #TODO; this needs to be tunable, app needs to be adjusted for getting embedding of one hardware design, this section still needs work.
    app = GNN4TJ(cfg)
    app.init_evaluator(pretrained_model_path=cfg.model_path / "model")
    embedding = app.get_embedding(vis_loader)

    return embedding

if __name__ == '__main__': 
    cfg = Config(sys.argv[1:])

    hw_code_path = "" #TODO: use this as the path.

    hw_graph  = hw2graph(verilog_path=cfg.raw_dataset_path)
    embedding = graph2vec(cfg, graph=hw_graph, verilog_path=cfg.raw_dataset_path / "topModule.v")

    # Embedding is a vector of features, do any inpsection on embedding for your own usage.