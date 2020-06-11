import os, pdb, sys
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
import json
import networkx as nx

from torch_geometric.data import Data, DataLoader
from sklearn.utils.class_weight import compute_class_weight

from core.gcn import *
from core.gin import *
from core.trainer import *
from abc import ABC, abstractmethod

from glob import glob
from utils.json2graph import *


if __name__ == "__main__":
    root = Path("../data/data_ready_FIXED/")
    root_healthy = root / "TjFree"
    root_trojan  = root / "TjIn"

    data = read_hardware_designs(root_healthy, 0) + read_hardware_designs(root_trojan, 1)
    
    trainer = GraphTrainer(sys.argv[1:], data)
    trainer.build()
    trainer.train()

            
    import pdb; pdb.set_trace() 
