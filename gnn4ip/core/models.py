import torch
import torch.nn as nn
import torch.nn.functional as F

from torch_geometric.nn import GCNConv, SAGPooling, TopKPooling, ASAPooling
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
       
        x = self.fc(x)
        return x, attn_weights

    def forward(self, x, edge_index, x2, edge_index2, batch=None, batch2=None):
        ''' graphs_in_batch is a list of graph instances; '''
        x, attn_weights = self.embed_graph(x, edge_index, batch=batch)
        x2,attn_weights2= self.embed_graph(x2, edge_index2, batch=batch2)

        return x, x2