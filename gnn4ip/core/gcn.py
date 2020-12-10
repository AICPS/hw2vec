import torch
import torch.nn as nn
import torch.nn.functional as F

from torch_geometric.nn import GCNConv, SAGPooling, TopKPooling, ASAPooling
from torch_geometric.nn import global_add_pool, global_mean_pool, global_max_pool, global_sort_pool

class GCN(nn.Module):
    def __init__(self, nfeat, nhid, nclass, dropout, pooling_type=None, readout_type=None):
        super(GCN, self).__init__()

        self.pooling_type = pooling_type
        # switch between average/max/mean/sort.
        self.readout_type = readout_type

        self.gc1 = GCNConv(nfeat, nhid)
        self.gc2 = GCNConv(nhid, nhid)
        self.dropout = dropout

        self.pooling_type = pooling_type
        self.readout_type = readout_type

        if self.pooling_type == "sagpool":
            self.pool1 = SAGPooling(nhid, ratio=0.8)
        elif self.pooling_type == "topk":
            self.pool1 = TopKPooling(nhid, ratio=0.8)
        elif self.pooling_type == "asa":
            self.pool1 = ASAPooling(nhid, ratio=0.8)

        self.fc = nn.Linear(nhid, nclass)

    def forward(self, x, edge_index, batch=None):
        ''' graphs_in_batch is a list of graph instances; '''
        attn_weights = dict()

        x = F.relu(self.gc1(x, edge_index))
        x = F.dropout(x, self.dropout, training=self.training)
        x = self.gc2(x, edge_index)

        if self.pooling_type == "sagpool":
            x, edge_index, _, batch, attn_weights['pool_perm'], attn_weights['pool_score'] = self.pool1(x, edge_index, batch=batch)
        elif self.pooling_type == "topk":
            x, edge_index, _, batch, attn_weights['pool_perm'], attn_weights['pool_score'] = self.pool1(x, edge_index, batch=batch)
        elif self.pooling_type == "asa":
            x, edge_index, _, batch, attn_weights['pool_perm'] = self.pool1(x, edge_index, batch=batch)

        if self.readout_type == "add":
            x = global_add_pool(x, batch)
        elif self.readout_type == "mean":
            x = global_mean_pool(x, batch)
        elif self.readout_type == "max":
            x = global_max_pool(x, batch)
        elif self.readout_type == "sort":
            x = global_sort_pool(x, batch, k=100)
        else:
            pass
       
        x = self.fc(x)

        return F.log_softmax(x, dim=1)
