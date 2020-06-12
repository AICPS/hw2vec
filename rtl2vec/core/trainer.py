import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

import random
import torch
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import scipy.sparse as sp
import pandas as pd


from argparse import ArgumentParser
from pathlib import Path
from tqdm import tqdm

from torch_geometric.data import Data, DataLoader
from sklearn.utils.class_weight import compute_class_weight

from core.gcn import *
from core.gin import *
from abc import ABC, abstractmethod


class BaseTrainer(ABC):

	@abstractmethod
	def __init__(self, args):
		pass
	
	@abstractmethod
	def build(self):
		pass
		
	@abstractmethod
	def train(self):
		pass
	
	@abstractmethod
	def evaluate(self):
		pass


def accuracy(output, labels):
    preds = output.max(1)[1].type_as(labels)
    correct = preds.eq(labels).double()
    correct = correct.sum()
    return correct / len(labels)


class Config:
    '''Argument Parser for script to train scenegraphs.'''
    def __init__(self, args):
        self.parser = ArgumentParser(description='The parameters for training the scene graph using GCN.')
        self.parser.add_argument('--input_path', type=str, default="../input/synthesis_data/lane-change/", help="Path to code directory.")
        self.parser.add_argument('--learning_rate', default=0.0001, type=float, help='The initial learning rate for GCN.')
        self.parser.add_argument('--seed', type=int, default=random.randint(0,2**32), help='Random seed.')
        self.parser.add_argument('--epochs', type=int, default=200, help='Number of epochs to train.')
        self.parser.add_argument('--weight_decay', type=float, default=5e-4, help='Weight decay (L2 loss on parameters).')
        self.parser.add_argument('--hidden', type=int, default=200, help='Number of hidden units.')
        self.parser.add_argument('--dropout', type=float, default=0.5, help='Dropout rate (1 - keep probability).')
        self.parser.add_argument('--nclass', type=int, default=8, help="The number of classes for node.")
        self.parser.add_argument('--recursive', type=lambda x: (str(x).lower() == 'true'), default=True, help='Recursive loading scenegraphs')
        self.parser.add_argument('--batch_size', type=int, default=32, help='Number of graphs in a batch.')
        self.parser.add_argument('--device', type=str, default="cpu", help='The device to run on models (cuda or cpu) cpu in default.')
        self.parser.add_argument('--model', type=str, default="gcn", help="Model to be used intrinsically.")
        self.parser.add_argument('--num_layers', type=int, default=5, help="Number of layers in the neural network.")
        self.parser.add_argument('--hidden_dim', type=int, default=32, help="Hidden dimension in GIN.")
        self.parser.add_argument('--pooling_type', type=str, default="sagpool", help="Graph pooling type.")
        self.parser.add_argument('--readout_type', type=str, default="max", help="Readout type.")
        self.parser.add_argument('--nocache', action='store_true', default=False, dest="nocache", help="Don't use cached version of dataset.")

        args_parsed = self.parser.parse_args(args)
        
        for arg_name in vars(args_parsed):
            self.__dict__[arg_name] = getattr(args_parsed, arg_name)

        self.input_base_dir = Path(self.input_path).resolve()


class GraphTrainer(BaseTrainer):

    def __init__(self, args, hardware_graphs):
        self.config = Config(args)
        np.random.seed(self.config.seed)
        torch.manual_seed(self.config.seed)
        self.hardware_graphs = hardware_graphs
        self.num_feature_dim = hardware_graphs[0][0].shape[1]
        
        train_data_list = [Data(x=x, edge_index=edge_idx, y=torch.LongTensor([y])) for x, edge_idx, y in self.hardware_graphs]
        self.train_loader = DataLoader(train_data_list, batch_size=self.config.batch_size)
        test_data_list = [Data(x=x, edge_index=edge_idx, y=torch.LongTensor([y])) for x, edge_idx, y in self.hardware_graphs]
        self.test_loader = DataLoader(test_data_list, batch_size=1)


    def build(self):
        if self.config.model == "gcn":
            self.model = GCN(self.num_feature_dim, self.config.hidden, 2, self.config.dropout, self.config.pooling_type, self.config.readout_type).to(self.config.device)
        
        elif self.config.model == "gin":
            self.model = GIN(None, self.num_feature_dim, 2,  self.config.num_layers, self.config.hidden_dim, self.config.pooling_type, self.config.readout_type).to(self.config.device)

        self.optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate, weight_decay=self.config.weight_decay)

    def train(self):

        for epoch_idx in tqdm(range(self.config.epochs)): # iterate through epoch
            acc_loss_train = 0
            
            for data in self.train_loader: # iterate through scenegraphs
                
                data.to(self.config.device)

                self.model.train()
                self.optimizer.zero_grad()
                               
                output = self.model.forward(data.x, data.edge_index, data.batch)
                    
                loss_train = nn.CrossEntropyLoss()(output, data.y)
                    
                loss_train.backward()

                self.optimizer.step()

                acc_loss_train += loss_train.detach().cpu().numpy()

            print('')
            print('Epoch: {:04d},'.format(epoch_idx), 'loss_train: {:.4f}'.format(acc_loss_train))
            print('')

    def evaluate(self):
        labels = []
        outputs = []
        
        for i, data in enumerate(self.test_loader): # iterate through scenegraphs
            data.to(self.config.device)
            self.model.eval()
            output = self.model.forward(data.x, data.edge_index, data.batch)
            acc_test = accuracy(output, data.y)

            print('SceneGraph: {:04d}'.format(i), 'acc_test: {:.4f}'.format(acc_test.item()))

            outputs.append(output.cpu())
            labels.append(data.y.cpu().numpy())
            
        outputs = torch.cat(outputs).reshape(-1,2).detach()
        return outputs, np.array(labels).flatten()