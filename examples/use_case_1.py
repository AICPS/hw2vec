import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

from hw2vec.hw2graph import *
from hw2vec.config import Config

def use_case_1(cfg):
    hw2graph = HW2GRAPH(cfg)

    hw_design_dir_path = cfg.raw_dataset_path
    hw_design_path = hw2graph.preprocess(hw_design_dir_path)
    hardware_nxgraph = hw2graph.process(hw_design_path)

    data_proc = DataProcessor(cfg)
    data_proc.process(hardware_nxgraph)
    all_graphs = data_proc.graph_data
    vis_loader   = DataLoader(all_graphs, batch_size=1)
    
    model = GRAPH2VEC(cfg)
    if cfg.model_path != "":
        model_path = Path(cfg.model_path)
        if model_path.exists():
            model.load_model(str(model_path/"model.cfg"), str(model_path/"model.pth"))
    else:
        from torch_geometric.nn import GCNConv
        from torch_geometric.nn import SAGPooling
        from torch_geometric.nn import global_max_pool
        convs = [
            GCNConv(data_proc.num_node_labels, cfg.hidden),
            GCNConv(cfg.hidden, cfg.hidden)
        ]
        model.set_graph_conv(convs)

        pool = SAGPooling(cfg.hidden, ratio=cfg.poolratio)
        model.set_graph_pool(pool)

        readout = global_max_pool
        model.set_graph_readout(readout)

        output = nn.Linear(cfg.hidden, cfg.embed_dim)
        model.set_output_layer(output)

    model.to(cfg.device)
    evaluator = Evaluator(cfg, "TJ")
    evaluator.build(model)
    return evaluator.get_embeddings(vis_loader)

if __name__ == '__main__': 
    
    graph_emb, hw_name = use_case_1(Config(sys.argv[1:]))
    
    print(graph_emb, hw_name)
    # NOTE: Embedding is a vector of features, do any inspection on embedding for your own usage.