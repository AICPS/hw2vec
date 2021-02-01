import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
import warnings
warnings.filterwarnings('ignore')

from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

from hw2vec.graph2vec.trainers import *
from hw2vec.core.json2graph import *


class Config:
    '''Configuration and Argument Parser for script to train the IP piracy detection.'''
    def __init__(self, args):
        self.parser = ArgumentParser(description='scripts for generating datasets.', formatter_class=RawTextHelpFormatter)
        self.parser.add_argument('--input_path', type=str, default="../input/synthesis_data/lane-change/", help="Path to code directory.")
        self.parser.add_argument('--learning_rate', default=0.001, type=float, help='The initial learning rate for GCN.')
        self.parser.add_argument('--seed', type=int, default=random.randint(0,2**32), help='Random seed.')
        self.parser.add_argument('--epochs', type=int, default=200, help='Number of epochs to train.')
        self.parser.add_argument('--weight_decay', type=float, default=5e-4, help='Weight decay (L2 loss on parameters).')
        self.parser.add_argument('--hidden', type=int, default=200, help='Number of hidden units.')
        self.parser.add_argument('--dropout', type=float, default=0.5, help='Dropout rate (1 - keep probability).')
        self.parser.add_argument('--nclass', type=int, default=8, help="The number of classes for node.")
        self.parser.add_argument('--recursive', type=lambda x: (str(x).lower() == 'true'), default=True, help='Recursive loading scenegraphs')
        self.parser.add_argument('--batch_size', type=int, default=4, help='Number of graphs in a batch.')
        self.parser.add_argument('--device', type=str, default="cpu", help='The device to run on models (cuda or cpu) cpu in default.')
        self.parser.add_argument('--model', type=str, default="gcn", help="Model to be used intrinsically.")
        self.parser.add_argument('--num_layers', type=int, default=5, help="Number of layers in the neural network.")
        self.parser.add_argument('--hidden_dim', type=int, default=32, help="Hidden dimension in GIN.")
        self.parser.add_argument('--test_step', type=int, default=10, help="The interval between mini evaluation along the training process.")
        self.parser.add_argument('--pooling_type', type=str, default="sagpool", help="Graph pooling type.")
        self.parser.add_argument('--readout_type', type=str, default="max", help="Readout type.")
        self.parser.add_argument('--splitted', type=bool, default=False, help="Indicating whether the target path has been splitted.")
        self.parser.add_argument('--ratio', type=float, default=0.7, help="Dataset splitting ratio")
        self.parser.add_argument('--poolratio', type=float, default=0.8, help="Ratio for graph pooling.")

        self.parser.add_argument('--pkl_path', type=str, default='./hardware_cache.pkl', help="Path to hardware graphs for parsing.")
        self.parser.add_argument('--raw_dataset_path', type=str, default='../data/TJ-datasets/data_graphs/data_ready_FIXED/', help="Path to raw dataset for parsing if no pkl.")
        self.parser.add_argument('--embed_dim', type=int, default=2, help="The dimension of graph embeddings.")

        args_parsed = self.parser.parse_args(args)
        for arg_name in vars(args_parsed):
            self.__dict__[arg_name] = getattr(args_parsed, arg_name)
        
        self.input_base_dir = Path(self.input_path).resolve()
        self.raw_dataset_path = Path(self.raw_dataset_path).resolve()
        self.pkl_path = Path(self.pkl_path).resolve()

from collections import Counter
from collections import defaultdict

def parse_attn_weights(node_attns, batches):

    original_batch = node_attns['original_batch']
    pool_perm = node_attns['pool_perm']
    pool_batch = node_attns['pool_batch']
    pool_score = node_attns['pool_score']
    batch_counter = Counter(original_batch)
    batch_deduct = {0: 0}
    
    node_attns_list = []
    for idx in range(1, len(batches.idx)):
        batch_deduct[idx] = batch_deduct[idx-1]+batch_counter[idx-1]
    
    node_index = {}
    node_dict= {}
    for idx, (p, b, s) in enumerate(zip(pool_perm, pool_batch, pool_score)):
        try:
            node_index[idx] = p - batch_deduct[b]
            if b not in node_dict:
                node_dict[b] = []
            node_dict[b].append("%s:%f"%(batches.idx[b][node_index[idx]], s))
        except Exception as e:
            import pdb; pdb.set_trace()
    node_attns_list.append(node_dict)

    return node_attns_list

if __name__ == "__main__": 
    cfg = Config(sys.argv[1:])
    if cfg.pkl_path.exists() is False:
        parser = GraphParser_TJ(cfg.raw_dataset_path)
        if cfg.splitted:
            # assuming the dataset has been properly splited. and is structured as follows:
            # 1) we will read all the labels from the nodes in parser.root_path and build the dictionary of node labels.
            # 2) we will read hardware designs and assign labels for each of them.
            #   [root_path]/train contains both TjFree ([root_path]/train/TjFree) and TjIn ([root_path]/train/TjIn) hardware designs for training.
            #   [root_path]/test contains both TjFree ([root_path]/test/TjFree) and TjIn ([root_path]/test/TjIn) hardware designs for testing.
            # 3) No split is needed as it has been manually splited.

            parser.read_node_labels("")
            parser.read_hardware_designs("Train/TjFree", 0, store_type="train")
            parser.read_hardware_designs("Train/TjIn", 1, store_type="train")
            parser.read_hardware_designs("Test/TjFree", 0, store_type="test")
            parser.read_hardware_designs("Test/TjIn", 1, store_type="test")

        else:
            # assuming the dataset hasn't been properly splited. 
            # 1) we will read all the labels from the nodes in parser.root_path and build the dictionary of node labels.
            # 2) we will read hardware designs and assign labels for each of them.
            #   [root_path]/TjFree contains all hardware designs w/o a trojan.
            #   [root_path]/TjIn  contains all hardware designs w/ a trojan.
            # 3) we will perform a stratified split over the parser.data

            parser.read_node_labels("")
            parser.read_hardware_designs("TjFree", 0, store_type="all")
            parser.read_hardware_designs("TjIn", 1, store_type="all")

        with open(cfg.pkl_path, 'wb') as f:
            pkl.dump(parser, f)

    trainer = GraphTrainer(cfg)
    trainer.build()
    trainer.train()
    trainer.evaluate(cfg.epochs)
    
    # train_loss, train_labels, _, train_preds, train_node_attns = trainer.inference(trainer.train_loader)
    # test_loss, test_labels, _, test_preds, test_node_attns = trainer.inference(trainer.test_loader)

    # # import pdb; pdb.set_trace()
    # node_attns_train_proc = []
    # for i, data in enumerate(trainer.train_loader):
    #     # for i, data in enumerate(dataset): # iterate through graphs
    #     node_attns_train_proc += parse_attn_weights(train_node_attns[i], data)
    # # import pdb; pdb.set_trace()
    # node_attns_test_proc = []
    # for i in tqdm(range(len(trainer.test_loader))):
    #     node_attns_test_proc += parse_attn_weights(test_node_attns[i], data)