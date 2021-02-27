import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
import warnings
warnings.filterwarnings('ignore')

from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from hw2vec.graph2vec.trainers import *
from hw2vec.hw2graph import *
import itertools
from hw2vec.graph2vec.config import *

SIMILAR = 1
DISSIMILAR = -1

if __name__ == "__main__":
    cfg = Config("./example_gnn4ip.yaml")
   
    if cfg.pkl_path.exists() is False:
        dataset = JsonGraphParser(cfg)
        dataset.read_node_labels("DFG")
            
        trunk = []
        for hw_cat_idx, hardware_root_path in enumerate(glob("%s/**" % str(cfg.raw_dataset_path/"DFG"), recursive=False)):
            # print("parsing %s" %str(hardware_root_path))
            
            for hardware_folder_path in glob("%s/**/topModule.json" % hardware_root_path, recursive=True):
                folder_name = "%s/%s" % (Path(hardware_folder_path).parent.parent.name, Path(hardware_folder_path).parent.name)

                G = dataset.get_graph_from_json(hardware_folder_path)
                X, name2idx, idx2name = dataset.get_node_embeddeings(G)
                edge_idx = dataset.get_edge_idxs(G, name2idx)          
                
                trunk.append(hw_cat_idx)
                dataset.training_graph_count += 1

                dataset.append_graph_data((X, edge_idx, folder_name))

        for idx_graph_a, idx_graph_b in itertools.combinations(range(len(trunk)), 2):
            if trunk[idx_graph_a] == trunk[idx_graph_b]:
                dataset.append_graph_pair((idx_graph_a, idx_graph_b, SIMILAR))
            else:
                dataset.append_graph_pair((idx_graph_a, idx_graph_b, DISSIMILAR))

        dataset.do_pickle_dataset()

    trainer = PairwiseGraphTrainer(cfg)
    trainer.build()
    trainer.train()
    trainer.evaluate(cfg.epochs)