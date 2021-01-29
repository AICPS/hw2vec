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

from hw2vec.core.models import *


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
    
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.config.learning_rate, weight_decay=self.config.weight_decay)    

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


class PairwiseGraphTrainer(BaseTrainer):
    ''' trainer for graph classification ''' 
    def __init__(self, cfg):
        super().__init__(cfg)
        self.min_test_loss = 1

        with open(str(cfg.pkl_path), 'rb') as f:
            parser = pkl.load(f)
      
        if cfg.splitted == False:
            parser.graph_pairs_train, parser.graph_pairs_test = parser.split_dataset(ratio=cfg.ratio, seed=cfg.seed, dataset=parser.graph_pairs)   
        
        parser.print_data_statistics()

        self.train_pairs = []
        self.test_pairs = []
        self.data = parser.graphs
        self.training_graph_count = parser.training_graph_count
        self.testing_graph_count = parser.testing_graph_count

        train_list = parser.graph_pairs_train if not self.config.debug else parser.graph_pairs_train[:1000]
        test_list = parser.graph_pairs_test if not self.config.debug else parser.graph_pairs_test[:1000]
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

        self.cos_sim = torch.nn.CosineSimilarity(dim=-1, eps=1e-08).to(self.config.device)
        self.cos_loss = torch.nn.CosineEmbeddingLoss(margin=0.5).to(self.config.device)
   
    def train(self):

        tqdm_bar = tqdm(range(self.config.epochs))
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
        for data in dataset:
            graph1, graph2, labels_batch = data[0].to(self.config.device), data[1].to(self.config.device), data[2].to(self.config.device)
                
            self.model.eval()

            X1 = F.one_hot(graph1.x, num_classes=self.config.num_feature_dim).float().detach()
            X2 = F.one_hot(graph2.x, num_classes=self.config.num_feature_dim).float().detach()

            start = time()
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

    # def print_data_statistics(self):
    #     avg_num_nodes = sum([item[0].shape[0] for item in self.graphs]) / len(self.graphs)
    #     avg_num_edges = sum([item[1].shape[1] for item in self.graphs]) / len(self.graphs)
    #     similar_pairs_count = sum([item[2] == 1 for item in self.graph_pairs])
    #     dissimilar_pairs_count = sum([item[2] == -1 for item in self.graph_pairs])
    #     print("avg. # of nodes per graph: %f" % (avg_num_nodes) )
    #     print("avg. # of edges per graph: %f" % (avg_num_edges) )
    #     print("total graphs for training: %d" % (self.training_graph_count))
    #     print("total graphs for testing: %d" % (self.testing_graph_count))
    #     print("total pairs for training: %d" % (len(self.graph_pairs_train)))
    #     print("total pairs for testing: %d" % (len(self.graph_pairs_test)))
    #     print("# of different hardware categories: %d" % (max(self.trunk)))
    #     print("proportion of similar/disimilar in training set: %d/%d" %(similar_pairs_count, dissimilar_pairs_count))        

class GraphTrainer(BaseTrainer):
    ''' trainer for graph classification ''' 
    def __init__(self, cfg):
        super().__init__(cfg)
        self.min_test_loss = 100
        self.train_time = 0
        self.test_time = 0

        with open(str(cfg.pkl_path), 'rb') as f:
            parser = pkl.load(f)
        
        if cfg.splitted == False:
            self.train_graphs, self.test_graphs = parser.split_dataset(ratio=cfg.ratio, seed=cfg.seed, dataset=parser.graphs)
        else:
            self.train_graphs = parser.train_data
            self.test_graphs = parser.test_data

        self.training_labels = [data[2] for data in self.train_graphs]
        self.testing_labels = [data[2] for data in self.test_graphs]
        self.class_weights = torch.from_numpy(compute_class_weight('balanced', np.unique(self.training_labels), self.training_labels))

        print("Train on %d graphs, Test on %d graphs." % (len(self.train_graphs), len(self.test_graphs)))
        print("Class weights (Tj-free/Tj-in)", self.class_weights.detach().tolist())

        train_data_list = [Data(x=x, edge_index=edge_idx, y=torch.LongTensor([y]), idx=name2idx) for x, edge_idx, y, folder_name, name2idx in self.train_graphs]
        self.train_loader = DataLoader(train_data_list, shuffle=True, batch_size=self.config.batch_size)
        test_data_list = [Data(x=x, edge_index=edge_idx, y=torch.LongTensor([y]), idx=name2idx) for x, edge_idx, y, folder_name, name2idx in self.test_graphs]
        self.test_loader = DataLoader(test_data_list, shuffle=True, batch_size=1)

        self.config.num_feature_dim = self.train_graphs[0][0].shape[1]
        if self.class_weights.shape[0] < 2:
            self.loss_func = nn.CrossEntropyLoss()
        else:    
           self.loss_func = nn.CrossEntropyLoss(weight=self.class_weights.float().to(self.config.device))

    def train(self):
        tqdm_bar = tqdm(range(self.config.epochs))

        for epoch_idx in tqdm_bar: # iterate through epoch
            start_time = time()
            acc_loss_train = 0
            
            for data in self.train_loader: # iterate through scenegraphs
                
                data.to(self.config.device)

                self.model.train()
                self.optimizer.zero_grad()
                               
                output, _ = self.model.forward(data.x, data.edge_index, data.batch)
                output = F.log_softmax(output, dim=1)

                loss_train = self.loss_func(output, data.y)
                    
                loss_train.backward()

                self.optimizer.step()

                acc_loss_train += loss_train.detach().cpu().numpy()

            self.train_time += (time() - start_time)
            tqdm_bar.set_description('Epoch: {:04d}, loss_train: {:.4f}'.format(epoch_idx, acc_loss_train))

            if epoch_idx % self.config.test_step == 0:
                self.evaluate(epoch_idx)
                
    def inference(self, dataset):
        labels = []
        outputs = []
        node_attns = []
        total_loss = 0
        
        for i, data in enumerate(dataset): # iterate through graphs
            data.to(self.config.device)
            self.model.eval()
            output, attn = self.model.forward(data.x, data.edge_index, data.batch)
            output = F.log_softmax(output, dim=1)

            loss = self.loss_func(output, data.y)
            total_loss += loss.detach().cpu().numpy()

            outputs.append(output.cpu())
            
            if 'pool_score' in attn:
                node_attn = {}
                node_attn["original_batch"] = data.batch.detach().cpu().numpy().tolist()
                node_attn["pool_perm"] = attn['pool_perm'].detach().cpu().numpy().tolist()
                node_attn["pool_batch"] = attn['batch'].detach().cpu().numpy().tolist()
                node_attn["pool_score"] = attn['pool_score'].detach().cpu().numpy().tolist()
                node_attns.append(node_attn)

            labels += np.split(data.y.cpu().numpy(), len(data.y.cpu().numpy()))

        outputs = torch.cat(outputs).reshape(-1,2).detach()
        avg_loss = total_loss / (len(dataset))

        labels_tensor = torch.LongTensor(labels).detach()
        outputs_tensor = torch.FloatTensor(outputs).detach()
        preds = outputs_tensor.max(1)[1].type_as(labels_tensor).detach()

        return avg_loss, labels_tensor, outputs_tensor, preds, node_attns

    def evaluate(self, epoch_idx):
        start_time = time()
        train_loss, train_labels, _, train_preds, train_node_attns = self.inference(self.train_loader)
        test_loss, test_labels, _, test_preds, test_node_attns = self.inference(self.test_loader)
        self.test_time += (time() - start_time)
        train_tn, train_fp, train_fn, train_tp = confusion_matrix(train_labels, train_preds).ravel()
        test_tn, test_fp, test_fn, test_tp = confusion_matrix(test_labels, test_preds).ravel()

        print("")
        print("Mini Test for Epochs %d:"%epoch_idx)

        self.metric_calc(train_loss, train_labels, train_preds, train_tn, train_fp, train_fn, header="train")
        self.metric_calc(test_loss,  test_labels,  test_preds,  test_tn,  test_fp,  test_fn,  header="test ")

        # on final evaluate call, after training is 100% complete
        if(epoch_idx==self.config.epochs):
            self.metric_print(self.min_test_loss, **self.metrics, header="best ")

            total_graphs = len(self.train_graphs)+len(self.test_graphs)
            total_train_batches = len(self.train_graphs)/self.config.batch_size
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

    # def print_data_statistics():
    #     avg_num_nodes = sum([item[0].shape[0] for item in self.graphs]) / len(self.graphs)
    #     avg_num_edges = sum([item[1].shape[1] for item in self.graphs]) / len(self.graphs)
    #     similar_pairs_count = sum([item[2] == 1 for item in self.graph_pairs])
    #     dissimilar_pairs_count = sum([item[2] == -1 for item in self.graph_pairs])
    #     print("avg. # of nodes per graph: %f" % (avg_num_nodes) )
    #     print("avg. # of edges per graph: %f" % (avg_num_edges) )
    #     print("total graphs for training: %d" % (self.training_graph_count))
    #     print("total graphs for testing: %d" % (self.testing_graph_count))
    #     print("total pairs for training: %d" % (len(self.graph_pairs_train)))
    #     print("total pairs for testing: %d" % (len(self.graph_pairs_test)))
    #     print("# of different hardware categories: %d" % (max(self.trunk)))
    #     print("proportion of similar/disimilar in training set: %d/%d" %(similar_pairs_count, dissimilar_pairs_count))                