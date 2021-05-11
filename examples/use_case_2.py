import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
from hw2vec.config import Config
from hw2vec.hw2graph import *


cfg = Config(sys.argv[1:])

''' prepare graph data '''
if not cfg.data_pkl_path.exists():
    ''' converting graph using hw2graph '''
    nx_graphs = []
    hw2graph = HW2GRAPH(cfg)
    for hw_project_path in hw2graph.find_hw_project_folders():
        hw_graph = hw2graph.code2graph(hw_project_path)
        nx_graphs.append(hw_graph)
    
    data_proc = DataProcessor(cfg)
    for hw_graph in nx_graphs:
        data_proc.process(hw_graph)
    data_proc.cache_graph_data(cfg.data_pkl_path)
    
else:
    ''' reading graph data from cache '''
    data_proc = DataProcessor(cfg)
    data_proc.read_graph_data_from_cache(cfg.data_pkl_path)
    

''' prepare dataset '''
TROJAN = 1
NON_TROJAN = 0

all_graphs = data_proc.graph_data
for data in all_graphs:
    if "TjFree" == data.hw_type:
        data.label = NON_TROJAN
    else:
        data.label = TROJAN

train_graphs, test_graphs = data_proc.get_datasets()
train_loader = DataLoader(train_graphs, shuffle=True, batch_size=cfg.batch_size)
valid_loader = DataLoader(test_graphs, shuffle=True, batch_size=1)


''' training '''
class_weights = data_proc.get_class_weights(train_graphs)
trainer = GraphTrainer(cfg, class_weights=class_weights)
trainer.build()
# if model_path is not None:
    # trainer.load_saved_model(model_path)
trainer.train(train_loader, valid_loader)

''' evaluating and inspecting '''
trainer.evaluate(cfg.epochs, train_loader, valid_loader)
vis_loader = DataLoader(all_graphs, shuffle=False, batch_size=1)
trainer.visualize_embeddings(vis_loader, "./")