import os, sys, itertools
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
SIMILAR = 1
DISSIMILAR = -1

all_graphs = data_proc.graph_data
for idx_graph_a, idx_graph_b in itertools.combinations(range(len(all_graphs)), 2):
    if all_graphs[idx_graph_a].hw_type == all_graphs[idx_graph_b].hw_type:
        data_proc.append_graph_pair((idx_graph_a, idx_graph_b, SIMILAR))
    else:
        data_proc.append_graph_pair((idx_graph_a, idx_graph_b, DISSIMILAR))

train_pairs, test_pairs = data_proc.get_pairs()
train_loader = DataLoader(train_pairs, shuffle=True, batch_size=cfg.batch_size)
test_loader  = DataLoader(test_pairs, shuffle=True, batch_size=cfg.batch_size)

''' training '''
trainer = PairwiseGraphTrainer(cfg)
trainer.build()
# if model_path is not None:
#     trainer.load_saved_model(model_path)
trainer.train(train_loader, test_loader)

''' evaluating and inspecting '''
trainer.evaluate(cfg.epochs, train_loader, test_loader)
vis_loader   = DataLoader(all_graphs, shuffle=False, batch_size=1)
trainer.visualize_embeddings(vis_loader, "./")