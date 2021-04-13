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


from time import time # needs to be here.


class BaseTrainer:
    def __init__(self, cfg):
        self.config = cfg
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

    def save_model(self, path):
        saved_path = Path(path)
        saved_path.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), str(saved_path / "model"))
        save_path_config = saved_path / "model config.txt"
        save_path_file = open(save_path_config, "w") 
        save_path_file.write(" ".join(sys.argv))
        save_path_file.close()

    def visualize_embeddings(self, data_loader, path=None):
        save_path = self.config.data_loader_path.parent / "visualize_embeddings" if path is None else Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        self.model.eval()
        with open(str(save_path / "vectors.tsv"), "w") as vectors_file:
            with open(str(save_path / "metadata.tsv"), "w") as metadata_file:
                metadata_file.write("Type\tInstance\n")
             
                for data in data_loader:
                    
                    if type(data) == list:
                        graph1, graph2 = data[0].to(self.config.device), data[1].to(self.config.device)
                        embed_x_1, _ = self.model.forward(graph1.x, graph1.edge_index, batch=graph1.batch)
                        embed_x_2, _ = self.model.forward(graph2.x, graph2.edge_index, batch=graph2.batch)
                        vectors_file.write("\t".join([str(x) for x in embed_x_1.detach().cpu().numpy()[0]]) + "\n")
                        vectors_file.write("\t".join([str(x) for x in embed_x_2.detach().cpu().numpy()[0]]) + "\n")
                    else:
                        data.to(self.config.device)
                        embed_x, _ = self.model.forward(data.x, data.edge_index, data.batch)
                        embed_x = F.log_softmax(embed_x, dim=1)
                        vectors_file.write("\t".join([str(x) for x in embed_x.detach().cpu().numpy()[0]]) + "\n")
                    # metadata_file.write(str(graphs[2]).replace('/', '\t')+'\n') #TODO: what is this?   


class PairwiseGraphTrainer(BaseTrainer):
    ''' trainer for graph classification ''' 
    def __init__(self, cfg):
        super().__init__(cfg)
        self.min_test_loss = 1
        self.cos_sim = torch.nn.CosineSimilarity(dim=-1, eps=1e-08).to(self.config.device)
        self.cos_loss = torch.nn.CosineEmbeddingLoss(margin=0.5).to(self.config.device)
    
    def train(self, train_loader, test_loader):

        tqdm_bar = tqdm(range(self.config.epochs))
        for epoch_idx in tqdm_bar: # iterate through epoch
            acc_loss_train = 0
            acc_time = []
            for data in train_loader:
                graph1, graph2, labels = data[0].to(self.config.device), data[1].to(self.config.device), data[2].to(self.config.device)
                self.model.train()
                self.optimizer.zero_grad()

                start = time()
            
                loss_train = self.train_epoch(graph1, graph2, labels)

                end = time()
                acc_time.append(end-start)

                

                loss_train.backward()
                self.optimizer.step()

                acc_loss_train += loss_train.detach().cpu().numpy()

            tqdm_bar.set_description('Epoch: {:04d}, loss_train: {:.4f}'.format(epoch_idx, acc_loss_train))
            print(sum(acc_time) / len(acc_time))
            if epoch_idx % self.config.test_step == 0:
                self.evaluate(epoch_idx, train_loader, test_loader)
    
    @profileit
    def train_epoch(self, graph1, graph2, labels):
        g_emb_1, _ = self.model(graph1.x, graph1.edge_index, batch=graph1.batch)
        g_emb_2, _ = self.model(graph2.x, graph2.edge_index, batch=graph2.batch)

        loss_train = self.cos_loss(g_emb_1, g_emb_2, labels)
        return loss_train

    def inference(self, data_loader):
        labels = []
        outputs = []
        total_loss = 0
        acc_time = []
        for data in data_loader:
            graph1, graph2, labels_batch = data[0].to(self.config.device), data[1].to(self.config.device), data[2].to(self.config.device)
                
            self.model.eval()

            start = time()
            
            g_emb_1, g_emb_2, similarity = self.inference_epoch(graph1, graph2)

            end = time()
            acc_time.append(end-start)

            loss = self.cos_loss(g_emb_1, g_emb_2, labels_batch)

            total_loss += loss.detach().cpu().numpy()

            outputs.append(similarity.detach().cpu())
            
            labels += np.split(labels_batch.detach().cpu().numpy(), len(labels_batch.detach().cpu().numpy()))
        print(sum(acc_time) / len(acc_time))
        outputs = torch.cat(outputs).detach()
        avg_loss = total_loss / (len(data_loader))

        labels_tensor = (torch.LongTensor(labels)> 0).detach() 
        outputs_tensor = torch.FloatTensor(outputs).detach()
        preds = (outputs > 0.5).detach()

        return avg_loss, labels_tensor, outputs_tensor, preds
    
    @profileit
    def inference_epoch(self, graph1, graph2):
        g_emb_1, _ = self.model(graph1.x, graph1.edge_index, batch=graph1.batch)
        g_emb_2, _ = self.model(graph2.x, graph2.edge_index, batch=graph2.batch)

        similarity = self.cos_sim(g_emb_1, g_emb_2)
        return g_emb_1, g_emb_2, similarity

    def evaluate(self, epoch_idx, train_loader, test_loader):
        train_loss, train_labels, _, train_preds = self.inference(train_loader)
        test_loss, test_labels, _, test_preds = self.inference(test_loader)

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
            self.save_model("./ALU_excluded_result")

        if(epoch_idx==self.config.epochs):
            print("best  loss: %4f" % self.min_test_loss+
                ", best  accuracy: %.4f" % self.metrics["acc"]+
                ", best  f1 score: %.4f" % self.metrics["f1"]+
                ", best  confusion_matrix: %s" % self.metrics["conf_mtx"]+
                ", best  precision: %.4f" % self.metrics["prec"]+
                ", best  recall: %.4f" % self.metrics["rec"])


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


class GraphTrainer(BaseTrainer):
    ''' trainer for graph classification ''' 
    def __init__(self, cfg, class_weights=None):
        super().__init__(cfg)
        self.min_test_loss = 100
        self.train_time = 0
        self.test_time = 0

        if class_weights.shape[0] < 2:
            self.loss_func = nn.CrossEntropyLoss()
        else:    
            self.loss_func = nn.CrossEntropyLoss(weight=class_weights.float().to(cfg.device))

    def train(self, data_loader, valid_data_loader):
        tqdm_bar = tqdm(range(self.config.epochs))

        for epoch_idx in tqdm_bar: # iterate through epoch
            start_time = time()
            acc_loss_train = 0
            
            for data in data_loader: # iterate through scenegraphs
                
                data.to(self.config.device)

                self.model.train()
                self.optimizer.zero_grad()
                               
                output, _ = self.model.forward(data.x, data.edge_index, data.batch)
                output = F.log_softmax(output, dim=1)

                loss_train = self.loss_func(output, data.label)
                    
                loss_train.backward()

                self.optimizer.step()

                acc_loss_train += loss_train.detach().cpu().numpy()

            self.train_time += (time() - start_time)
            tqdm_bar.set_description('Epoch: {:04d}, loss_train: {:.4f}'.format(epoch_idx, acc_loss_train))

            if epoch_idx % self.config.test_step == 0:
                self.evaluate(epoch_idx, data_loader, valid_data_loader)
                
    def inference(self, data_loader):
        labels = []
        outputs = []
        node_attns = []
        total_loss = 0
        folder_names = []
        
        for i, data in enumerate(data_loader): # iterate through graphs
            data.to(self.config.device)
            self.model.eval()
            output, attn = self.model.forward(data.x, data.edge_index, data.batch)
            output = F.log_softmax(output, dim=1)

            loss = self.loss_func(output, data.label)
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
        start_time = time()
        train_loss, train_labels, _, train_preds, train_node_attns, _ = self.inference(data_loader)
        test_loss, test_labels, _, test_preds, test_node_attns, _ = self.inference(valid_data_loader)
        self.test_time += (time() - start_time)
        train_tn, train_fp, train_fn, train_tp = confusion_matrix(train_labels, train_preds, labels=self.config.labels).ravel()
        test_tn, test_fp, test_fn, test_tp = confusion_matrix(test_labels, test_preds, labels=self.config.labels).ravel()

        print("")
        print("Mini Test for Epochs %d:"%epoch_idx)

        self.metric_calc(train_loss, train_labels, train_preds, train_tn, train_fp, train_fn, header="train")
        self.metric_calc(test_loss,  test_labels,  test_preds,  test_tn,  test_fp,  test_fn,  header="test ")

        # on final evaluate call, after training is 100% complete
        if(epoch_idx==self.config.epochs):
            self.metric_print(self.min_test_loss, **self.metrics, header="best ")

            total_graphs = len(data_loader)+len(valid_data_loader)
            total_train_batches = len(data_loader)/self.config.batch_size
            total_evaluates = (self.config.epochs/self.config.test_step) + 1
            total_inferences = 2 * total_evaluates
            total_test_samples = total_evaluates * total_graphs

            avg_epoch_time = self.train_time/self.config.epochs
            avg_batch_time = avg_epoch_time/total_train_batches
            avg_inference_time = self.test_time / total_inferences
            avg_sample_test_time = self.test_time / total_test_samples

            print("total training time: %.4f seconds" % self.train_time)
            print("average epoch training time: %.4f seconds" % avg_epoch_time)
            print("average batch training time: %.4f seconds" % avg_batch_time)
            print("total testing time: %.4f seconds" % self.test_time)
            print("average inference time: %.4f seconds" % avg_inference_time)
            print("average sample testing time: %.4f seconds" % avg_sample_test_time)

    def metric_calc(self, loss, labels, preds, tn, fp, fn, header):
        acc = accuracy_score(labels, preds)
        f1 = f1_score(labels, preds, average="binary")
        conf_mtx = str(confusion_matrix(labels, preds)).replace('\n', ',')
        precision = precision_score(labels, preds, average="binary")
        recall = recall_score(labels, preds, average="binary")
        specificity = (tn/(tn + fp))
        npv = (tn/(tn + fn))
        
        self.metric_print(loss, acc, f1, conf_mtx, precision, recall, specificity, npv, header)

        if header == "test " and (self.min_test_loss >= loss):
            self.min_test_loss = loss
            self.metrics["acc"] = acc
            self.metrics["f1"] = f1
            self.metrics["conf_mtx"] = conf_mtx
            self.metrics["precision"] = precision
            self.metrics["recall"] = recall
            self.metrics["specificity"] = specificity
            self.metrics["npv"] = npv

            self.save_model("./TJ Best result")

            #TODO: store the attn_weights right here. 

    def metric_print(self, loss, acc, f1, conf_mtx, precision, recall, specificity, npv, header):
        print("%s loss: %4f" % (header, loss) +
            ", %s accuracy: %.4f" % (header, acc) +
            ", %s f1 score: %.4f" % (header, f1) +
            ", %s confusion_matrix: %s" % (header, conf_mtx) +
            ", %s precision: %.4f" % (header, precision) +
            ", %s recall: %.4f" % (header, recall) +
            ", %s specificity: %.4f" % (header, specificity) +
            ", %s NPV: %.4f" % (header, npv))