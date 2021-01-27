import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

from core.trainers import *

'''
    Usages:

    Use different precache paths before running different commands

    For training/testing on complete_dataset
    python trojan_classification.py --raw_dataset_path ../../data_graphs/complete_dataset/ --precache_path xxx --device cuda

    For training/testing on GCF-test1
    python trojan_classification.py --raw_dataset_path ../../data_graphs/GCF-test1/ --precache_path xxx --device cuda --splitted True

    For training/testing on GCF-test2
    python trojan_classification.py --raw_dataset_path ../../data_graphs/GCF-test2/ --precache_path xxx --device cuda --splitted True

    For training/testing on HTD-test1
    python trojan_classification.py --raw_dataset_path ../../data_graphs/HTD-test1/ --precache_path xxx --device cuda --splitted True
'''

'''
    new usages:
    use gcn model: python 1_gnn4tj_train.py 
    use gin model: python 1_gnn4tj_train.py --model gin
'''


class Config:
    '''Configuration and Argument Parser for script to train the trojan classification.'''
    def __init__(self, args):
        self.parser = ArgumentParser(description='The parameters for training the scene graph using GCN.')
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
        self.parser.add_argument('--poolratio', type=float, default=0.8, help="Ratio for graph pooling.")

        self.parser.add_argument('--precache_path', type=str, default='./hardware_cache.pkl', help="Path to hardware graphs for parsing.")
        self.parser.add_argument('--raw_dataset_path', type=str, default='../../data/TJ-datasets/data_graphs/data_ready_FIXED/', help="Path to raw dataset for parsing if no precache.")

        self.parser.add_argument('--embed_dim', type=int, default=2, help="The dimension of graph embeddings.")

        args_parsed = self.parser.parse_args(args)
        
        for arg_name in vars(args_parsed):
            self.__dict__[arg_name] = getattr(args_parsed, arg_name)

        self.input_base_dir = Path(self.input_path).resolve()
        self.precache_path = Path(self.precache_path).resolve()
        self.raw_dataset_path = Path(self.raw_dataset_path).resolve()

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

    # start training.
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

