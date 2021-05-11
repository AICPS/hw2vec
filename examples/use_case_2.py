import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
from hw2vec.config import Config
from hw2vec.app import GNN4TJ
from hw2vec.hw2graph import *
import pickle
import torch
from glob import glob
from time import time

TROJAN = 1
NON_TROJAN = 0

def process_graph(folder_path, profile=True):
    hw2graph = HW2GRAPH(cfg)
    
    if profile:
        start = time()

    if "topModule.v" not in [Path(x).name for x in glob("%s/*.v"%str(folder_path))]:
        code_path = hw2graph.preprocess(folder_path)
    else:
        code_path = folder_path / "topModule.v"

    hw_graph = hw2graph.process(str(code_path))
    
    if profile:
        end = time()
        print(str(code_path), ",", len(hw_graph.nodes), ",", len(hw_graph.edges), ",", end-start)

    return hw_graph

cfg = Config(sys.argv[1:])
data_proc = DataProcessor(cfg)
if cfg.data_pkl_path.exists():
    data_proc.read_graph_data_from_cache(cfg.data_pkl_path)
else:
    for project in data_proc.find_projects():
        hw_graph = process_graph(project)
        data_proc.process(hw_graph)

    data_proc.cache_graph_data(cfg.data_pkl_path)

for data in data_proc.graph_data:
    if "TjFree" == data.hw_type:
        data.label = NON_TROJAN
    else:
        data.label = TROJAN

all_graphs = data_proc.graph_data
train_graphs, test_graphs = data_proc.get_graphs()
class_weights = data_proc.get_class_weights(train_graphs)

train_loader = DataLoader(train_graphs, shuffle=True, batch_size=cfg.batch_size)
test_loader  = DataLoader(test_graphs, shuffle=True, batch_size=1)

trainer = GraphTrainer(cfg, class_weights=class_weights)
trainer.build()
# if model_path is not None:
    # trainer.load_saved_model(model_path)
trainer.train(train_loader, test_loader)
trainer.evaluate(cfg.epochs, train_loader, test_loader)

vis_loader = DataLoader(all_graphs, batch_size=1)
trainer.visualize_embeddings(vis_loader, "./")