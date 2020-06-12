import os, sys
sys.path.append(os.path.dirname(sys.path[0]))


from core.trainer import *
from utils.json2graph import *
import pickle as pkl


if __name__ == "__main__":

    parser = None
    
    precache_path = Path('./hardware_cache.pkl')
    if precache_path.exists():
        with open(str(precache_path),'rb') as f:
            parser = pkl.load(f)
            
    else:
        parser = GraphParser(Path("../data/data_ready_FIXED/"))

        parser.read_node_labels("TjFree")
        parser.read_node_labels("TjIn")
        
        parser.read_hardware_designs("TjFree", 0)
        parser.read_hardware_designs("TjIn", 1)

        with open('hardware_cache.pkl', 'wb') as f:
            pkl.dump(parser, f)

    parser.split_dataset(0.7)
    trainer = GraphTrainer(sys.argv[1:], parser.train_data, parser.test_data)
    trainer.build()
    trainer.train()
    trainer.evaluate()