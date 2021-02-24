import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
import warnings
warnings.filterwarnings('ignore')

from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from hw2vec.graph2vec.trainers import *
from hw2vec.hw2graph import *
from hw2vec.graph2vec.config import *


if __name__ == "__main__":   
    parser = ArgumentParser(description='scripts for generating datasets.', formatter_class=RawTextHelpFormatter)
    parser.add_argument('--config_path', default='./example_config.yaml', help='path to the config file.')
    
    args_parsed = parser.parse_args(sys.argv[1:])

    args={}
    args['config_path'] = Path(getattr(args_parsed, 'config_path')).resolve()

    cfg = Config(args['config_path'])

    '''
        Commands for running the experiments:
            Exp 1: python gnn4tj.py --config_path ./example_config.yaml

    '''

    TROJAN = 1
    NON_TROJAN = 0

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

# from collections import Counter
# def parse_attn_weights(node_attns, batches):

#     original_batch = node_attns['original_batch']
#     pool_perm = node_attns['pool_perm']
#     pool_batch = node_attns['pool_batch']
#     pool_score = node_attns['pool_score']
#     batch_counter = Counter(original_batch)
#     batch_deduct = {0: 0}
    
#     node_attns_list = []
#     for idx in range(1, len(batches.idx)):
#         batch_deduct[idx] = batch_deduct[idx-1]+batch_counter[idx-1]
    
#     node_index = {}
#     node_dict= {}
#     for idx, (p, b, s) in enumerate(zip(pool_perm, pool_batch, pool_score)):
#         try:
#             node_index[idx] = p - batch_deduct[b]
#             if b not in node_dict:
#                 node_dict[b] = []
#             node_dict[b].append("%s:%f"%(batches.idx[b][node_index[idx]], s))
#         except Exception as e:
#             import pdb; pdb.set_trace()
#     node_attns_list.append(node_dict)

#     return node_attns_list

    # temporary code for localization.
    # train_loss, train_labels, _, train_preds, train_node_attns = trainer.inference(trainer.train_loader)
    # test_loss, test_labels, _, test_preds, test_node_attns = trainer.inference(trainer.test_loader)

    # node_attns_train_proc = []
    # for i, data in enumerate(trainer.train_loader):
    #     # for i, data in enumerate(dataset): # iterate through graphs
    #     node_attns_train_proc += parse_attn_weights(train_node_attns[i], data)
    # # import pdb; pdb.set_trace()
    # node_attns_test_proc = []
    # for i in tqdm(range(len(trainer.test_loader))):
    #     node_attns_test_proc += parse_attn_weights(test_node_attns[i], data)



# else:
#             # assuming the dataset hasn't been properly splited. 
#             # 1) we will read all the labels from the nodes in dataset.root_path and build the dictionary of node labels.
#             # 2) we will read hardware designs and assign labels for each of them.
#             #   [root_path]/TjFree contains all hardware designs w/o a trojan.
#             #   [root_path]/TjIn  contains all hardware designs w/ a trojan.
#             # 3) we will perform a stratified split over the dataset.data

#             dataset.read_node_labels("")
#             dataset.read_hardware_designs("TjFree", 0, store_type="all")
#             dataset.read_hardware_designs("TjIn", 1, store_type="all")