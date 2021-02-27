import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
from pathlib import Path
from hw2vec.graph2vec.trainers import GraphTrainer
from hw2vec.hw2graph import JsonGraphParser
from hw2vec.graph2vec.config import Config

TROJAN = 1
NON_TROJAN = 0

if __name__ == "__main__":
    cfg = Config("./example_config.yaml")

    if cfg.pkl_path.exists() is False:
        dataset = JsonGraphParser(cfg)
        dataset.read_node_labels("")

        for json_path in glob("%s/**/topModule.json" % str(dataset.root_path/"TjFree"), recursive=True):
            folder_name = "%s/%s" % (Path(json_path).parent.parent.name, Path(json_path).parent.name)

            hardware_graph = dataset.get_graph_from_json(json_path)
            node_embeddings, name2idx, idx2name = dataset.get_node_embeddeings(hardware_graph)
            edge_idxs = dataset.get_edge_idxs(hardware_graph, name2idx)
            dataset.append_graph_data((node_embeddings, edge_idxs, NON_TROJAN, folder_name, idx2name))

        for json_path in glob("%s/**/topModule.json" % str(dataset.root_path/"TjIn"), recursive=True):
            folder_name = "%s/%s" % (Path(json_path).parent.parent.name, Path(json_path).parent.name)

            hardware_graph = dataset.get_graph_from_json(json_path)
            node_embeddings, name2idx, idx2name = dataset.get_node_embeddeings(hardware_graph)
            edge_idxs = dataset.get_edge_idxs(hardware_graph, name2idx)
            dataset.append_graph_data((node_embeddings, edge_idxs, TROJAN, folder_name, idx2name))

        dataset.do_pickle_dataset()

    # initialize a graph trainer for graph classification on trojan classification
    trainer = GraphTrainer(cfg)

    # initialize the model according to cfg. 
    trainer.build()

    # train the model. 
    trainer.train()

    # do a final evaluation.
    trainer.evaluate(cfg.epochs)