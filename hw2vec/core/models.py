'''
    copy from tnn4ip
'''
import torch
import torch.nn as nn
import torch.nn.functional as F

from torch.nn import Sequential, Linear, ReLU
from torch_geometric.nn import GCNConv, GINConv, SAGPooling, TopKPooling, ASAPooling
from torch_geometric.nn import global_add_pool, global_mean_pool, global_max_pool, global_sort_pool


class GCN(nn.Module):
    def __init__(self, config):
        super(GCN, self).__init__()

        self.config = config
        
        self.gc1 = GCNConv(self.config.num_feature_dim, self.config.hidden)
        self.gc2 = GCNConv(self.config.hidden, self.config.hidden)

        if self.config.pooling_type == "sagpool":
            self.pool1 = SAGPooling(self.config.hidden, ratio=self.config.poolratio)
        elif self.config.pooling_type == "topk":
            self.pool1 = TopKPooling(self.config.hidden, ratio=self.config.poolratio)
        elif self.config.pooling_type == "asa":
            self.pool1 = ASAPooling(self.config.hidden, ratio=self.config.poolratio)

        self.fc = nn.Linear(self.config.hidden, self.config.embed_dim)

    def embed_graph(self, x, edge_index, batch=None):
        attn_weights = dict()

        x = F.relu(self.gc1(x, edge_index))
        x = F.dropout(x, self.config.dropout, training=self.training)
        x = self.gc2(x, edge_index)

        if self.config.pooling_type == "sagpool":
            x, edge_index, _, batch, attn_weights['pool_perm'], attn_weights['pool_score'] = self.pool1(x, edge_index, batch=batch)
        elif self.config.pooling_type == "topk":
            x, edge_index, _, batch, attn_weights['pool_perm'], attn_weights['pool_score'] = self.pool1(x, edge_index, batch=batch)
        elif self.config.pooling_type == "asa":
            x, edge_index, _, batch, attn_weights['pool_perm'] = self.pool1(x, edge_index, batch=batch)

        if self.config.readout_type == "add":
            x = global_add_pool(x, batch)
        elif self.config.readout_type == "mean":
            x = global_mean_pool(x, batch)
        elif self.config.readout_type == "max":
            x = global_max_pool(x, batch)
        elif self.config.readout_type == "sort":
            x = global_sort_pool(x, batch, k=100)
        else:
            pass

        attn_weights['batch'] = batch
        x = self.fc(x)
        return x, attn_weights

    def forward(self, x, edge_index, batch=None):
        ''' graphs_in_batch is a list of graph instances; '''
        x, attn_weights = self.embed_graph(x, edge_index, batch=batch)
        # return F.log_softmax(x, dim=1), attn_weights (TJ)
        # TODO: put softmax in trainer instead. e.g model = nn.Sequential(GCN, softmax)
        return x, attn_weights # (IP)
'''
    copy from gin.py
'''
class GIN(nn.Module):
    
    def __init__(self, config):
        super(GIN, self).__init__()
        self.config = config

        self.gin_convs = torch.nn.ModuleList()
        self.batch_norms = torch.nn.ModuleList()

        for layer in range(self.config.num_layers-1):
            if layer == 0:
                nn = Sequential(Linear(self.config.num_feature_dim, self.config.hidden_dim), ReLU(), Linear(self.config.hidden_dim, self.config.hidden_dim))
            else:
                nn = Sequential(Linear(self.config.hidden_dim, self.config.hidden_dim), ReLU(), Linear(self.config.hidden_dim, self.config.hidden_dim))
            self.gin_convs.append(GINConv(nn))
            self.batch_norms.append(torch.nn.BatchNorm1d(self.config.hidden_dim))

        if self.config.pooling_type == "sagpool":
            self.pool1 = SAGPooling(self.config.hidden_dim, ratio=self.config.poolratio)
        elif self.config.pooling_type == "topk":
            self.pool1 = TopKPooling(self.config.hidden_dim, ratio=self.config.poolratio)
        elif self.config.pooling_type == "asa":
            self.pool1 = ASAPooling(self.config.hidden_dim, ratio=self.config.poolratio)

        self.fc1 = Linear(self.config.hidden_dim, self.config.hidden_dim)
        self.fc2 = Linear(self.config.hidden_dim, self.config.embed_dim)


    def forward(self, x, edge_index, batch=None):
        attn_weights = dict()

        for layer in range(self.config.num_layers-1):
            x = F.relu(self.gin_convs[layer](x, edge_index))
            x = self.batch_norms[layer](x)

        if self.config.pooling_type == "sagpool":
            x, edge_index, _, batch, attn_weights['pool_perm'], attn_weights['pool_score'] = self.pool1(x, edge_index, batch=batch)
        elif self.config.pooling_type == "topk":
            x, edge_index, _, batch, attn_weights['pool_perm'], attn_weights['pool_score'] = self.pool1(x, edge_index, batch=batch)
        elif self.config.pooling_type == "asa":
            x, edge_index, _, batch, attn_weights['pool_perm'] = self.pool1(x, edge_index, batch=batch)
        else: 
            pass

        if self.config.readout_type == "add":
            x = global_add_pool(x, batch)
        elif self.config.readout_type == "mean":
            x = global_mean_pool(x, batch)
        elif self.config.readout_type == "max":
            x = global_max_pool(x, batch)
        elif self.config.readout_type == "sort":
            x = global_sort_pool(x, batch, k=100)
        else:
            pass
        attn_weights['batch'] = batch    
        x = F.relu(self.fc1(x))
        x = F.dropout(x, p=0.5, training=self.training)
        x = self.fc2(x)

        return F.log_softmax(x, dim=-1), attn_weights
