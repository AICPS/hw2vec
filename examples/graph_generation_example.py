import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

from hw2vec.hw2graph import *

from optparse import OptionParser
import shutil 
from glob import glob
from pathlib import Path
from pprint import pprint
import networkx as nx


def parse_single_verilog_code(verilog_path, output_path, graph_format="DFG"):
    ''' 
        handling a single verilog code to a DFG. 
    '''
    if graph_format == "DFG":
        graph_generator = RTLDFGGenerator()
    elif graph_format == "CFG":
        graph_generator = RTLCFGGenerator()
    elif graph_format == "AST":
        graph_generator = RTLASTGenerator()
    
    graph = graph_generator.process(verilog_path, output_path) 
    graph_json = graph_generator.get_graph_json(graph.graph_generator)
    pprint(graph_json['nodes'])
    pprint(graph_json['edges'])
    pprint(graph_json['edge_index'])
    pprint(graph_json['root_nodes'])
    graph_generator.export_json(graph_json, output_path)
    graph_generator.draw(graph.graph_generator)

    # TODO: visualize X and A?
    node_labels = set()
    for src in graph_json['edge_index']:
        node_labels.add((src.split(".")[-1].split("_")[0]).lower())

    label2idx = {v:k for k, v in enumerate(list(node_labels))}
    idx2label = {v:k for k, v in label2idx.items()}
    


    hardware_graph = nx.DiGraph()
    for src in graph_json['edge_index']:
        hardware_graph.add_node(src, label=src.split(".")[-1].split("_")[0].lower())
        for neighbor in graph_json['edge_index'][src]:
            dst = neighbor[1]
            hardware_graph.add_edge(src, dst)
    
    X=[]
    name2idx = {}
    idx2name = {}
    for idx, node in enumerate(hardware_graph.nodes(data=True)):
        node_name = node[0]
        node_label = node[1]['label']

        name2idx[node_name] = idx
        idx2name[idx] = node_name
        X.append(label2idx[node_label])
    
    X = F.one_hot(torch.LongTensor(X), num_classes=len(label2idx)).float()

    edge_idx = []
    for src, dst in hardware_graph.edges():
        edge_idx.append((name2idx[src], name2idx[dst]))
    edge_idx = torch.transpose(torch.LongTensor(edge_idx), 0, 1).detach()


def parse_multiple_verilog_code(verilog_path, output_path, graph_format="DFG"):
    # handling verilog code in batch to DFGs.
    # graphs = hw2graph_dfg.process_batch(dataset_directory, "topModule.v")
    # dfg_generator = HW2Graph(graph_format="DFG", code_language="verilog", top_module='top')
    # json_graphs = dfg_generator.process_batch(dataset_directory)
    # dfg_generator.export_jsons(json_graphs, output_dir=dataset_output_dir_path)
    
    # for verilog_path in glob("%s/**/topModule.v" % str(dataset_directory), recursive=True):
    #     print(verilog_path)
    #     # import pdb;pdb.set_trace()
    #     try:
    #         graph_generator = RTLDFGGenerator(verilog_path, "./", code_language='verilog', top_module='top', draw_graph=False)
    #         # Export the list of nodes 
    #         print('export the graph as a JSON dictionary: ')
    #         graph_generator.export_nodes()
    #         # Export the list of root nodes
    #         graph_generator.export_root_nodes()
    #         # Export the list of edges
    #         graph_generator.export_edges()
    #         # Draw Data Flow Graph
    #         graph_generator.draw_DFG()
    #         # Draw the subgraphs ( data flow graph of signals)
    #         graph_generator.draw_signals_DFG()
    #     except:
    #         print('Error in', verilog_path)
    pass


if __name__ == '__main__':
    ''' 
        An example on how to genreate the data flow graph for a dataset of Verilog harwdare designs
        USAGE:  python graph_generation_example.py 
    '''    
    verilog_path = Path('../tests/data/IP-dataset/Verilog/C432/c432/topModule.v')
    dataset_directory = Path('../tests/data/IP-dataset/Verilog/C432').resolve()
    dataset_output_dir_path = Path('./').resolve()
    
    # example 1: parse a single verilog code and visualize.
    parse_single_verilog_code(verilog_path, dataset_output_dir_path, graph_format="DFG")
    
    # example 2: parse a batch of verilog code and package.
    parse_multiple_verilog_code(verilog_path, dataset_output_dir_path, graph_format="DFG")