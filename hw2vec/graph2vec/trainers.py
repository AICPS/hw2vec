#!/usr/bin/env python
#title           :trainers.py
#description     :This file includes the trainers of hw2vec.
#author          :Shih-Yuan Yu
#date            :2021/03/05
#version         :0.2
#notes           :
#python_version  :3.6
#==============================================================================
import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

import random
import torch
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import pickle as pkl

import warnings
warnings.filterwarnings('ignore')

from pathlib import Path
from tqdm import tqdm

from torch_geometric.data import Data, DataLoader
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, precision_score, recall_score, roc_auc_score, roc_curve

from hw2vec.graph2vec.models import *
from hw2vec.utilities import *

class BaseTrainer:
    def __init__(self, cfg):
        self.config = cfg
        self.min_test_loss = np.Inf
        self.task = None
        self.metrics = {}
        self.model = None
        np.random.seed(self.config.seed)
        torch.manual_seed(self.config.seed)

    def build(self):
        if self.config.model == "gcn":
            self.model = GCN(self.config).to(self.config.device)

        elif self.config.model == "gin":
            self.model = GIN(self.config).to(self.config.device)
    
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate)    

    def load_saved_model(self, path):
        model_path = Path(path)
        if model_path.exists():
            self.model.load_state_dict(torch.load(str(model_path)))
            self.model.to(self.config.device)
        else:
            raise ValueError("Model load path not exist %s" % model_path)

    def save_model(self, saved_path):
        saved_path.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), str(saved_path / "model"))
        save_path_config = saved_path / "model config.txt"
        save_path_file = open(save_path_config, "w") 
        save_path_file.write(" ".join(sys.argv))
        save_path_file.close()

    def visualize_embeddings(self, data_loader, path=None):
        save_path = "./visualize_embeddings/" if path is None else Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        with open(str(save_path / "vectors.tsv"), "w") as vectors_file, \
             open(str(save_path / "metadata.tsv"), "w") as metadata_file:

            with torch.no_grad():
                self.model.eval()

                for data in data_loader:
                    data.to(self.config.device)
                    embed_x, _ = self.model.forward(data.x, data.edge_index, data.batch)
                    hardware_name = data.folder_name[0].split("/")[-2]

                    if self.task == "TJ":
                        embed_x = F.log_softmax(embed_x, dim=1)

                    vectors_file.write("\t".join([str(x) for x in embed_x.detach().cpu().numpy()[0]]) + "\n")
                    metadata_file.write(hardware_name+"\n")

    #TODO; for use case 1, not completed. must adjust app.py
    def get_embedding(self, data_loader):
        with torch.no_grad():
            self.model.eval()

            data = next(iter(data_loader))
            data.to(self.config.device)
            embed_x, _ = self.model.forward(data.x, data.edge_index, data.batch)

            if self.task == "TJ":
                embed_x = F.log_softmax(embed_x, dim=1)

        return embed_x

    def metric_calc(self, loss, labels, preds, header):
        acc = accuracy_score(labels, preds)
        f1 = f1_score(labels, preds, average="binary")
        conf_mtx = str(confusion_matrix(labels, preds)).replace('\n', ',')
        precision = precision_score(labels, preds, average="binary")
        recall = recall_score(labels, preds, average="binary")

        self.metric_print(loss, acc, f1, conf_mtx, precision, recall, header)

        if header == "test " and (self.min_test_loss >= loss):
            self.min_test_loss = loss
            self.metrics["acc"] = acc
            self.metrics["f1"] = f1
            self.metrics["conf_mtx"] = conf_mtx
            self.metrics["precision"] = precision
            self.metrics["recall"] = recall

    def metric_print(self, loss, acc, f1, conf_mtx, precision, recall, header):
        print("%s loss: %4f" % (header, loss) +
            ", %s accuracy: %.4f" % (header, acc) +
            ", %s f1 score: %.4f" % (header, f1) +
            ", %s confusion_matrix: %s" % (header, conf_mtx) +
            ", %s precision: %.4f" % (header, precision) +
            ", %s recall: %.4f" % (header, recall))

class PairwiseGraphTrainer(BaseTrainer):
    ''' trainer for graph classification ''' 
    def __init__(self, cfg):
        super().__init__(cfg)
        self.task = "IP"
        self.cos_sim = torch.nn.CosineSimilarity(dim=-1, eps=1e-08).to(self.config.device)
        self.cos_loss = torch.nn.CosineEmbeddingLoss(margin=0.5).to(self.config.device)
    
    def train(self, train_loader, test_loader):
        tqdm_bar = tqdm(range(self.config.epochs))

        for epoch_idx in tqdm_bar:
            self.model.train()
            acc_loss_train = 0
            
            for data in tqdm(train_loader):
                self.optimizer.zero_grad()
                graph1, graph2, labels = data[0].to(self.config.device), data[1].to(self.config.device), data[2].to(self.config.device)

                loss_train = self.train_epoch_ip(graph1, graph2, labels)
                loss_train.backward()
                self.optimizer.step()

                acc_loss_train += loss_train.detach().cpu().numpy()

            tqdm_bar.set_description('Epoch: {:04d}, loss_train: {:.4f}'.format(epoch_idx, acc_loss_train))

            if epoch_idx % self.config.test_step == 0:
                self.evaluate(epoch_idx, train_loader, test_loader)
    
    @profileit
    def train_epoch_ip(self, graph1, graph2, labels):
        g_emb_1, _ = self.model.forward(graph1.x, graph1.edge_index, batch=graph1.batch)
        g_emb_2, _ = self.model.forward(graph2.x, graph2.edge_index, batch=graph2.batch)

        loss_train = self.cos_loss(g_emb_1, g_emb_2, labels)
        return loss_train

    @profileit
    def inference_epoch_ip(self, graph1, graph2):
        g_emb_1, _ = self.model(graph1.x, graph1.edge_index, batch=graph1.batch)
        g_emb_2, _ = self.model(graph2.x, graph2.edge_index, batch=graph2.batch)

        similarity = self.cos_sim(g_emb_1, g_emb_2)
        return g_emb_1, g_emb_2, similarity

    def inference(self, data_loader):
        labels = []
        outputs = []
        total_loss = 0
        with torch.no_grad():
            self.model.eval()
            
            for data in data_loader:
                graph1, graph2, labels_batch = data[0].to(self.config.device), data[1].to(self.config.device), data[2].to(self.config.device)
                    
                g_emb_1, g_emb_2, similarity = self.inference_epoch_ip(graph1, graph2)
                loss = self.cos_loss(g_emb_1, g_emb_2, labels_batch)

                total_loss += loss.detach().cpu().numpy()
                outputs.append(similarity.detach().cpu())
                labels += np.split(labels_batch.detach().cpu().numpy(), len(labels_batch.detach().cpu().numpy()))

            outputs = torch.cat(outputs).detach()
            avg_loss = total_loss / (len(data_loader))

            labels_tensor = (torch.LongTensor(labels)> 0).detach() 
            outputs_tensor = torch.FloatTensor(outputs).detach()
            preds = (outputs > 0.5).detach()

        return avg_loss, labels_tensor, outputs_tensor, preds
    
    def evaluate(self, epoch_idx, train_loader, test_loader):
        train_loss, train_labels, _, train_preds = self.inference(train_loader)
        test_loss, test_labels, _, test_preds = self.inference(test_loader)

        print("")
        print("Mini Test for Epochs %d:"%epoch_idx)

        self.metric_calc(train_loss, train_labels, train_preds, header="train")
        self.metric_calc(test_loss,  test_labels,  test_preds,  header="test ")

        if self.min_test_loss >= test_loss:
            self.save_model(self.config.model_path)

        # on final evaluate call
        if(epoch_idx==self.config.epochs):
            self.metric_print(self.min_test_loss, **self.metrics, header="best ")

class GraphTrainer(BaseTrainer):
    ''' trainer for graph classification ''' 
    def __init__(self, cfg, class_weights=None):
        super().__init__(cfg)
        self.task = "TJ"
        if class_weights.shape[0] < 2:
            self.loss_func = nn.CrossEntropyLoss()
        else:    
            self.loss_func = nn.CrossEntropyLoss(weight=class_weights.float().to(cfg.device))

    def train(self, data_loader, valid_data_loader):
        tqdm_bar = tqdm(range(self.config.epochs))

        for epoch_idx in tqdm_bar:
            self.model.train()
            acc_loss_train = 0

            for data in data_loader:
                self.optimizer.zero_grad()
                data.to(self.config.device)

                loss_train = self.train_epoch_tj(data)
                loss_train.backward()
                self.optimizer.step()
                acc_loss_train += loss_train.detach().cpu().numpy()

            tqdm_bar.set_description('Epoch: {:04d}, loss_train: {:.4f}'.format(epoch_idx, acc_loss_train))

            if epoch_idx % self.config.test_step == 0:
                self.evaluate(epoch_idx, data_loader, valid_data_loader)

    @profileit
    def train_epoch_tj(self, data):
        output, _ = self.model.forward(data.x, data.edge_index, data.batch)
        output = F.log_softmax(output, dim=1)

        loss_train = self.loss_func(output, data.label)
        return loss_train

    @profileit
    def inference_epoch_tj(self, data):
        output, attn = self.model.forward(data.x, data.edge_index, data.batch)
        output = F.log_softmax(output, dim=1)

        loss = self.loss_func(output, data.label)
        return loss, output, attn
                
    def inference(self, data_loader):
        labels = []
        outputs = []
        node_attns = []
        total_loss = 0
        folder_names = []
        
        with torch.no_grad():
            self.model.eval()
            for i, data in enumerate(data_loader):
                data.to(self.config.device)

                loss, output, attn = self.inference_epoch_tj(data)
                total_loss += loss.detach().cpu().numpy()

                outputs.append(output.cpu())
                
                if 'pool_score' in attn:
                    node_attn = {}
                    node_attn["original_batch"] = data.batch.detach().cpu().numpy().tolist()
                    node_attn["pool_perm"] = attn['pool_perm'].detach().cpu().numpy().tolist()
                    node_attn["pool_batch"] = attn['batch'].detach().cpu().numpy().tolist()
                    node_attn["pool_score"] = attn['pool_score'].detach().cpu().numpy().tolist()
                    node_attns.append(node_attn)

                labels += np.split(data.label.cpu().numpy(), len(data.label.cpu().numpy()))
                folder_names += data.folder_name

            outputs = torch.cat(outputs).reshape(-1,2).detach()
            avg_loss = total_loss / (len(data_loader))

            labels_tensor = torch.LongTensor(labels).detach()
            outputs_tensor = torch.FloatTensor(outputs).detach()
            preds = outputs_tensor.max(1)[1].type_as(labels_tensor).detach()

        return avg_loss, labels_tensor, outputs_tensor, preds, node_attns, folder_names

    def evaluate(self, epoch_idx, data_loader, valid_data_loader):
        train_loss, train_labels, _, train_preds, train_node_attns, _ = self.inference(data_loader)
        test_loss, test_labels, _, test_preds, test_node_attns, _ = self.inference(valid_data_loader)

        print("")
        print("Mini Test for Epochs %d:"%epoch_idx)

        self.metric_calc(train_loss, train_labels, train_preds, header="train")
        self.metric_calc(test_loss,  test_labels,  test_preds,  header="test ")

        if self.min_test_loss >= test_loss:
            self.save_model(self.config.model_path)
            #TODO: store the attn_weights right here. 

        # on final evaluate call
        if(epoch_idx==self.config.epochs):
            self.metric_print(self.min_test_loss, **self.metrics, header="best ")


class Evaluator(BaseTrainer):
    def __init__(self, cfg, task):
        super().__init__(cfg)
        self.task = task