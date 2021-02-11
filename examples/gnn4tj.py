import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
import warnings
warnings.filterwarnings('ignore')

from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from hw2vec.graph2vec.trainers import *
from hw2vec.hw2graph import *
from config import *

class Config:
    '''Configuration and Argument Parser for script to train the IP piracy detection.'''
    def __init__(self, args_parsed):
        for arg_name in vars(args_parsed):
            self.__dict__[arg_name] = getattr(args_parsed, arg_name)
        self.raw_dataset_path = Path(self.raw_dataset_path).resolve()
        self.pkl_path = Path(self.pkl_path).resolve()


if __name__ == "__main__":   
    # parser = ArgumentParser(description='scripts for generating datasets.', formatter_class=RawTextHelpFormatter)
    # parser.add_argument('--learning_rate', default=0.001, type=float, help='The initial learning rate for GCN.')
    # parser.add_argument('--seed', type=int, default=random.randint(0,2**32), help='Random seed.')
    # parser.add_argument('--epochs', type=int, default=200, help='Number of epochs to train.')
    # parser.add_argument('--weight_decay', type=float, default=5e-4, help='Weight decay (L2 loss on parameters).')
    # parser.add_argument('--hidden', type=int, default=200, help='Number of hidden units.')
    # parser.add_argument('--dropout', type=float, default=0.5, help='Dropout rate (1 - keep probability).')
    # parser.add_argument('--nclass', type=int, default=8, help="The number of classes for node.")
    # parser.add_argument('--recursive', type=lambda x: (str(x).lower() == 'true'), default=True, help='Recursive loading scenegraphs')
    # parser.add_argument('--batch_size', type=int, default=4, help='Number of graphs in a batch.')
    # parser.add_argument('--device', type=str, default="cpu", help='The device to run on models (cuda or cpu) cpu in default.')
    # parser.add_argument('--model', type=str, default="gcn", help="Model to be used intrinsically.")
    # parser.add_argument('--num_layers', type=int, default=5, help="Number of layers in the neural network.")
    # parser.add_argument('--hidden_dim', type=int, default=32, help="Hidden dimension in GIN.")
    # parser.add_argument('--test_step', type=int, default=10, help="The interval between mini evaluation along the training process.")
    # parser.add_argument('--pooling_type', type=str, default="sagpool", help="Graph pooling type.")
    # parser.add_argument('--readout_type', type=str, default="max", help="Readout type.")
    # parser.add_argument('--splitted', type=bool, default=False, help="Indicating whether the target path has been splitted.")
    # parser.add_argument('--ratio', type=float, default=0.7, help="Dataset splitting ratio")
    # parser.add_argument('--poolratio', type=float, default=0.8, help="Ratio for graph pooling.")
    # parser.add_argument('--pkl_path', type=str, default='./hardware_cache.pkl', help="Path to hardware graphs for parsing.")
    # parser.add_argument('--raw_dataset_path', type=str, default='../data/TJ-datasets/data_graphs/data_ready_FIXED/', help="Path to raw dataset for parsing if no pkl.")
    # parser.add_argument('--embed_dim', type=int, default=2, help="The dimension of graph embeddings.")
    # parser.add_argument('--debug', type=lambda x: (str(x).lower() == 'true'), default=True, help='debug mode.')

    # args_parsed = parser.parse_args(sys.argv[1:])
    # cfg = Config(args_parsed)
    cfg = YamlConfig("config.yaml")

    '''
        Commands for running the experiments:
            Exp 1: python .\gnn4tj.py --device cuda --raw_dataset_path ..\data\TJ-datasets\data_graphs\HTD-test1 --pkl_path htd-test1.pkl
            Exp 2: python .\gnn4tj.py --device cuda --raw_dataset_path ..\data\TJ-datasets\data_graphs\HTD-test2 --pkl_path htd-test2.pkl
            Exp 3: python .\gnn4tj.py --device cuda --raw_dataset_path ..\data\TJ-datasets\data_graphs\data_ready_FIXED --pkl_path dataready-fixed.pkl
            Exp 4: python .\gnn4tj.py --device cuda --raw_dataset_path ..\data\TJ-datasets\data_graphs\complete_dataset --pkl_path completedataset.pkl

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