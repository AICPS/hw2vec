import os
import sys
sys.path.append(os.path.dirname(sys.path[0]))
from core.IP_trainer import *
from argparse import ArgumentParser, RawTextHelpFormatter

class Config:
    '''Configuration and Argument Parser for script to train the trojan classification.'''
    def __init__(self, args):
        self.parser = ArgumentParser(description='Script for training the scene graph using GCN:\n      python 1_train_gnn4ip.py --device cuda --batch_size 64 --hidden 16 --embed_dim 16', formatter_class=RawTextHelpFormatter)
        self.parser.add_argument('--input_path', type=str, default="../input/synthesis_data/lane-change/", help="Path to code directory.")
        self.parser.add_argument('--learning_rate', default=0.001, type=float, help='The initial learning rate for GCN.')
        self.parser.add_argument('--seed', type=int, default=random.randint(0,2**32), help='Random seed.')
        self.parser.add_argument('--epochs', type=int, default=200, help='Number of epochs to train.')
        self.parser.add_argument('--weight_decay', type=float, default=5e-4, help='Weight decay (L2 loss on parameters).')
        self.parser.add_argument('--hidden', type=int, default=200, help='Number of hidden units.')
        self.parser.add_argument('--dropout', type=float, default=0.5, help='Dropout rate (1 - keep probability).')
        self.parser.add_argument('--embed_dim', type=int, default=32, help="The dimension of graph embeddings.")
        self.parser.add_argument('--batch_size', type=int, default=4, help='Number of graphs in a batch.')
        self.parser.add_argument('--device', type=str, default="cpu", help='The device to run on models (cuda or cpu) cpu in default.')
        self.parser.add_argument('--model', type=str, default="gcn", help="Model to be used intrinsically.")
        self.parser.add_argument('--num_layers', type=int, default=5, help="Number of layers in the neural network.")
        self.parser.add_argument('--test_step', type=int, default=10, help="The interval between mini evaluation along the training process.")
        self.parser.add_argument('--pooling_type', type=str, default="sagpool", help="Graph pooling type.")
        self.parser.add_argument('--readout_type', type=str, default="max", help="Readout type.")
        self.parser.add_argument('--splitted', type=bool, default=False, help="Indicating whether the target path has been splitted.")

        self.parser.add_argument('--dataset_path', type=str, default='./dataset_rtl.pkl', help="Path to dataset.")
        self.parser.add_argument('--ratio', type=float, default=0.8, help="Dataset splitting ratio")
        self.parser.add_argument('--poolratio', type=float, default=0.75, help="Ratio for graph pooling.")
        self.parser.add_argument('--debug', type=bool, default=False, help="Train on all pairs in debug mode.")
        
        args_parsed = self.parser.parse_args(args)
        
        for arg_name in vars(args_parsed):
            self.__dict__[arg_name] = getattr(args_parsed, arg_name)

        self.input_base_dir = Path(self.input_path).resolve()
        self.dataset_path = Path(self.dataset_path).resolve()

if __name__ == "__main__":
    ''' sample command python 1_train_gnn4ip.py --device cuda --batch_size 64 --hidden 16 --embed_dim 16'''
    cfg = Config(sys.argv[1:])

    trainer = GraphTrainer(cfg)
    trainer.build()
    trainer.train()
    trainer.evaluate(cfg.epochs)    