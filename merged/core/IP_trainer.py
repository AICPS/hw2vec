'''
    copy from tnn4ip
'''
import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

import torch
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import pickle as pkl
import warnings
warnings.filterwarnings('ignore')

from argparse import ArgumentParser
from pathlib import Path
from tqdm import tqdm

from torch_geometric.data import Data, DataLoader
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, precision_score, recall_score, roc_auc_score, roc_curve

from core.models import *
from utils.json2graph import *

from time import time


def read_dataset_from_pkl(cfg):
    '''
        use cfg.splitted to differentiate the handling of splited dataset or unsplited dataset.
        ex. splited dataset: GCF-test1
        ex. unsplited dataset: complete_dataset
    '''
    if cfg.dataset_path.exists():
        with open(str(cfg.dataset_path),'rb') as data_f:
            parser = pkl.load(data_f)
        parser.split_dataset(ratio=cfg.ratio, seed=cfg.seed)
    else:
        raise Exception("pkl file does not exist")
    
    return parser # parser.train_pair_list and parser.test_pair_list are ready to be used. 

class GraphTrainer:
    ''' trainer for graph classification ''' 
    def __init__(self, cfg):
        self.config = cfg
        self.min_test_loss = 1
        self.metrics = {}

        np.random.seed(self.config.seed)
        torch.manual_seed(self.config.seed)

        parser = read_dataset_from_pkl(cfg)
        parser.print_data_statistics()

        self.train_pairs = []
        self.test_pairs = []
        self.data = parser.data
        self.training_graph_count = parser.training_graph_count
        self.testing_graph_count = parser.testing_graph_count

        train_list = parser.train_pair_list if not self.config.debug else parser.train_pair_list[:1000]
        test_list = parser.test_pair_list if not self.config.debug else parser.test_pair_list[:1000]
        for pairs in train_list:
            self.train_pairs.append((self.data[pairs[0]], self.data[pairs[1]], pairs[2]))
        for pairs in test_list:
            self.test_pairs.append((self.data[pairs[0]], self.data[pairs[1]], pairs[2]))
        
        train_data_list = [] 
        for graph_1, graph_2, label in self.train_pairs:
            g1 = Data(x=graph_1[0], edge_index=graph_1[1])
            g2 = Data(x=graph_2[0], edge_index=graph_2[1])
            train_data_list.append((g1, g2, label))

        test_data_list = [] 
        for graph_1, graph_2, label in self.test_pairs:
            g1 = Data(x=graph_1[0], edge_index=graph_1[1])
            g2 = Data(x=graph_2[0], edge_index=graph_2[1])
            test_data_list.append((g1, g2, label))
                
        self.train_loader = DataLoader(train_data_list, batch_size=self.config.batch_size)
        self.test_loader  = DataLoader(test_data_list, batch_size=self.config.batch_size)

        self.config.num_feature_dim = len(parser.node_labels)

    def build(self):
        if self.config.model == "gcn":
            self.model = GCN(self.config).to(self.config.device)
        # reserved from expanding other models.
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate, weight_decay=self.config.weight_decay)

        self.cos_sim = torch.nn.CosineSimilarity(dim=-1, eps=1e-08).to(self.config.device)
        self.cos_loss = torch.nn.CosineEmbeddingLoss(margin=0.5).to(self.config.device)

    def train(self):

        tqdm_bar = tqdm(range(self.config.epochs))
        import pdb; pdb.set_trace()
        for epoch_idx in tqdm_bar: # iterate through epoch
            acc_loss_train = 0
            acc_time = []
            for data in self.train_loader:
                graph1, graph2, labels = data[0].to(self.config.device), data[1].to(self.config.device), data[2].to(self.config.device)
                self.model.train()
                self.optimizer.zero_grad()
                
                X1 = F.one_hot(graph1.x, num_classes=self.config.num_feature_dim).float()
                X2 = F.one_hot(graph2.x, num_classes=self.config.num_feature_dim).float()

                start = time()
                # g_emb_1, g_emb_2 = self.model(X1, graph1.edge_index, X2, graph2.edge_index, batch=graph1.batch, batch2=graph2.batch)
                g_emb_1, _ = self.model(X1, graph1.edge_index, batch=graph1.batch)
                g_emb_2, _ = self.model(X2, graph2.edge_index, batch=graph2.batch)

                loss_train = self.cos_loss(g_emb_1, g_emb_2, labels)
                end = time()
                acc_time.append(end-start)

                loss_train.backward()
                self.optimizer.step()

                acc_loss_train += loss_train.detach().cpu().numpy()

            tqdm_bar.set_description('Epoch: {:04d}, loss_train: {:.4f}'.format(epoch_idx, acc_loss_train))
            print(sum(acc_time) / len(acc_time))
            if epoch_idx % self.config.test_step == 0:
                self.evaluate(epoch_idx)
                
    def inference(self, dataset):
        labels = []
        outputs = []
        total_loss = 0
        acc_time = []
        for data in self.test_loader:
            graph1, graph2, labels_batch = data[0].to(self.config.device), data[1].to(self.config.device), data[2].to(self.config.device)
                
            self.model.eval()

            X1 = F.one_hot(graph1.x, num_classes=self.config.num_feature_dim).float().detach()
            X2 = F.one_hot(graph2.x, num_classes=self.config.num_feature_dim).float().detach()

            start = time()
            # g_emb_1, g_emb_2 = self.model(X1, graph1.edge_index, X2, graph2.edge_index, batch=graph1.batch, batch2=graph2.batch)
            g_emb_1, _ = self.model(X1, graph1.edge_index, batch=graph1.batch)
            g_emb_2, _ = self.model(X2, graph2.edge_index, batch=graph2.batch)

            similarity = self.cos_sim(g_emb_1, g_emb_2)
            end = time()
            acc_time.append(end-start)

            loss = self.cos_loss(g_emb_1, g_emb_2, labels_batch)

            total_loss += loss.detach().cpu().numpy()

            outputs.append(similarity.detach().cpu())
            
            labels += np.split(labels_batch.detach().cpu().numpy(), len(labels_batch.detach().cpu().numpy()))
        print(sum(acc_time) / len(acc_time))
        outputs = torch.cat(outputs).detach()
        avg_loss = total_loss / (len(dataset))

        labels_tensor = (torch.LongTensor(labels)> 0).detach() 
        outputs_tensor = torch.FloatTensor(outputs).detach()
        preds = (outputs > 0.5).detach()

        return avg_loss, labels_tensor, outputs_tensor, preds

    def evaluate(self, epoch_idx):
        train_loss, train_labels, _, train_preds = self.inference(self.train_loader)
        test_loss, test_labels, _, test_preds = self.inference(self.test_loader)

        print("")
        print("Mini Test for Epochs %d:"%epoch_idx)
        print("train loss: %4f" % train_loss +
            ", train accuracy: %.4f" % accuracy_score(train_labels, train_preds) +
            ", train f1 score: %.4f" % f1_score(train_labels, train_preds, average="micro")+
            ", train confusion_matrix: %s" % str(confusion_matrix(train_labels, train_preds)).replace('\n', ',')+
            ", train precision: %.4f" % precision_score(train_labels, train_preds, average="micro")+
            ", train recall: %.4f" % recall_score(train_labels, train_preds, average="micro"))

        print("test  loss: %4f" % test_loss +
            ", test  accuracy: %.4f" % accuracy_score(test_labels, test_preds) +
            ", test  f1 score: %.4f" % f1_score(test_labels, test_preds, average="micro")+
            ", test  confusion_matrix: %s" % str(confusion_matrix(test_labels, test_preds)).replace('\n', ',')+
            ", test  precision: %.4f" % precision_score(test_labels, test_preds, average="micro")+
            ", test  recall: %.4f" % recall_score(test_labels, test_preds, average="micro"))

        if(self.min_test_loss >= test_loss): 
            self.min_test_loss = test_loss
            self.metrics["acc"] = accuracy_score(test_labels, test_preds)
            self.metrics["f1"] = f1_score(test_labels, test_preds, average="micro")
            self.metrics["conf_mtx"] = str(confusion_matrix(test_labels, test_preds)).replace('\n', ',')
            self.metrics["prec"] = precision_score(test_labels, test_preds, average="micro")
            self.metrics["rec"] = recall_score(test_labels, test_preds, average="micro")
            self.save_model()

        if(epoch_idx==self.config.epochs):
            print("best  loss: %4f" % self.min_test_loss+
                ", best  accuracy: %.4f" % self.metrics["acc"]+
                ", best  f1 score: %.4f" % self.metrics["f1"]+
                ", best  confusion_matrix: %s" % self.metrics["conf_mtx"]+
                ", best  precision: %.4f" % self.metrics["prec"]+
                ", best  recall: %.4f" % self.metrics["rec"])

    def visualize_embeddings(self, path=None):
        save_path = self.config.dataset_path.parent / "visualize_embeddings" if path is None else Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        self.model.eval()
        with open(str(save_path / "vectors.tsv"), "w") as vectors_file:
            with open(str(save_path / "metadata.tsv"), "w") as metadata_file:
                metadata_file.write("Type\tInstance\n")
                for graphs in self.data:
                    
                    X = F.one_hot(graphs[0].to(self.config.device), num_classes=self.config.num_feature_dim).float().detach()
                    embed_x, _ = self.model.embed_graph(X, graphs[1].to(self.config.device))
                    vectors_file.write("\t".join([str(x) for x in embed_x.detach().cpu().numpy()[0]]) + "\n")
                    metadata_file.write(str(graphs[2]).replace('/', '\t')+'\n')


    def load_saved_model(self, path=None):
        model_path = Path("./best_result/ippiracy") if path is None else Path(path)
        if model_path.exists():
            self.model.load_state_dict(torch.load(str(model_path)))
            self.model.to(self.config.device)
        else:
            raise ValueError("Model load path not exist %s" % model_path)

    def save_model(self, path=None):
        saved_path = self.config.dataset_path.parent / "ALU_excluded_result" if path is None else Path(path)
        saved_path.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), str(saved_path / "ippiracy"))
        save_path_config = saved_path / "ippiracy.txt"
        save_path_file = open(save_path_config, "w") 
        save_path_file.write(" ".join(sys.argv))
        save_path_file.close()

    def get_graph_embedding(self, g_key):
        embed = None
        self.model.eval()

        for data in self.data:
            if data[2] == g_key:
                X = data[0].to(self.config.device)
                A = data[1].to(self.config.device)
                X = F.one_hot(X, num_classes=self.config.num_feature_dim).float().detach()
                embed, _ = self.model.embed_graph(X, A)
        
        if embed == None:
            raise ValueError ("Graph %s not found!" % g_key)
        return embed

    def get_similarity(self, g1_key, g2_key):
        self.model.eval()
        
        similarity = self.cos_sim(self.get_graph_embedding(g1_key), \
                                  self.get_graph_embedding(g2_key))

        print("similarity between %s, %s is %f" %(g1_key, g2_key, similarity.detach().item()))
        return similarity.detach().cpu().item()

    def get_similarity_groups(self, g1_keys, g2_keys):
        self.model.eval()

        return [((g1_key, g2_key), self.get_similarity(g1_key, g2_key)) for g1_key, g2_key in itertools.product(g1_keys, g2_keys)]