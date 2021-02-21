import yaml
import io
import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
import random

from pathlib import Path
class YamlConfig:
    def __init__(self, file):
        with open(file, 'r') as f:
            data = yaml.safe_load(f)

        self.learning_rate = data['learning_rate'] if ('learning_rate' in data and data['learning_rate']!=None ) else 0.001
        self.seed = data['seed'] if ('seed' in data and data['seed']!=None ) else random.randint(0,2**32)
        self.epochs = data['epochs'] if ('epochs' in data and data['epochs']!=None ) else 200
        self.weight_decay = data['weight_decay'] if ('weight_decay' in data and data['weight_decay']!=None ) else 5e-4
        self.hidden = data['hidden'] if ('hidden' in data and data['hidden']!=None ) else 200
        self.dropout = data['dropout'] if ('dropout' in data and data['dropout']!=None ) else 0.5
        self.nclass = data['nclass'] if ('nclass' in data and data['nclass']!=None ) else 8
        self.recursive = data['recursive'] if ('recursive' in data and data['recursive']!=None ) else True
        self.batch_size = data['batch_size'] if ('batch_size' in data and data['batch_size']!=None ) else 4
        self.device = data['device'] if ('device' in data and data['device']!=None ) else "cpu"
        self.model = data['model'] if ('model' in data and data['model']!=None ) else "gcn"
        self.num_layer = data['num_layer'] if ('num_layer' in data and data['num_layer']!=None ) else 5
        self.hidden_dim = data['hidden_dim'] if ('hidden_dim' in data and data['hidden_dim']!=None ) else 32
        self.test_step = data['test_step'] if ('test_step' in data and data['test_step']!=None ) else 10
        self.pooling_type = data['pooling_type'] if ('pooling_type' in data and data['pooling_type']!=None ) else "sagpool"
        self.readout_type = data['readout_type'] if ('readout_type' in data and data['readout_type']!=None ) else "max"
        self.splitted = data['splitted'] if ('splitted' in data and data['splitted']!=None ) else False
        self.ratio = data['ratio'] if ('ratio' in data and data['ratio']!=None ) else 0.7
        self.poolratio = data['poolratio'] if ('poolratio' in data and data['poolratio']!=None ) else 0.8
        self.pkl_path = data['pkl_path'] if ('pkl_path' in data and data['pkl_path']!=None ) else "./hardware_cache.pkl"
        self.raw_dataset_path = data['raw_dataset_path'] if ('raw_dataset_path' in data and data['raw_dataset_path']!=None ) else "../data/TJ-datasets/data_graphs/data_ready_FIXED/"
        self.embed_dim = data['embed_dim'] if ('embed_dim' in data and data['embed_dim']!=None ) else 2
        self.debug = data['debug'] if ('debug' in data and data['debug']!=None ) else False
        #TODO: debug and recursive type, lambda?

        self.raw_dataset_path = Path(self.raw_dataset_path).resolve()
        self.pkl_path = Path(self.pkl_path).resolve()


    




