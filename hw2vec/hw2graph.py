from optparse import OptionParser

import pyverilog
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer as PyDataflowAnalyzer
from pyverilog.dataflow.optimizer import VerilogDataflowOptimizer as PyDataflowOptimizer
from pyverilog.dataflow.graphgen import VerilogGraphGenerator as PyGraphGenerator

from json import dumps

import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

import torch
import torch.nn.functional as F

import json
import networkx as nx

from sklearn.model_selection import train_test_split
from glob import glob

from hw2vec.graph2vec.trainers import *


class JsonGraphParser:
    def __init__(self, cfg):
        self.cfg = cfg
        self.root_path = self.cfg.raw_dataset_path.resolve()

        ''' self.graphs is a dict that stores all the hardware graphs that can be parsed from the raw datatset folder. 
            'all': means it is a collection of all graph datasets.
            'train' and 'test': store the collection of graph instances according to a prespliting result.
        '''
        self.graphs = {}

        self.node_labels = set()
        
        ''' for GNN4IP '''
        ''' self.graph_pairs/_train/_test stores the graph-pairing info. e.g. (0, 1, -1) means graph 0 and graph 1 is dissimilar. '''
        self.graph_pairs       = []
        self.graph_pairs_train = [] 
        self.graph_pairs_test  = []
        
        # self.trunk stores the hardware category information about each hardware design. e.g. in [0, 1, 1, 2, 3], hw #1 belongs to category 1.
        self.trunk = []

        # list to store names of graphs in each set
        self.training_graph_count = 0
        self.testing_graph_count = 0

    def append_training_graph_data(self, data):
        if 'train' not in self.graphs: 
            self.graphs['train'] = []
        self.graphs['train'].append(data)

    def append_testing_graph_data(self, data):
        if 'test' not in self.graphs: 
            self.graphs['test'] = []
        self.graphs['test'].append(data)
    
    def append_graph_data(self, data):
        if 'all' not in self.graphs: 
            self.graphs['all'] = []
        self.graphs['all'].append(data)

    def append_graph_pair(self, pair):
        self.graph_pairs.append(pair)

    def get_graphs(self):
        if 'train' in self.graphs and 'test' in self.graphs:
            return self.graphs['train'], self.graphs['test']
        elif 'all' in self.graphs:
            return self.split_dataset(ratio=self.cfg.ratio, seed=self.cfg.seed, dataset=self.graphs['all'])

    def get_pairs(self):
        graph_pairs = self.graph_pairs if self.cfg.debug else self.graph_pairs[:100]
        self.graph_pairs_train, self.graph_pairs_test = self.split_dataset(ratio=self.cfg.ratio, seed=self.cfg.seed, dataset=graph_pairs)
        return self.graph_pairs_train, self.graph_pairs_test

    def do_pickle_dataset(self):
        with open(self.cfg.pkl_path, 'wb') as f:
            if self.cfg.debug and len(self.graph_pairs) is 0:
                if 'train' in self.graphs and 'test' in self.graphs:
                    self.graphs['train'] = self.graphs['train'][:100]
                    self.graphs['test'] = self.graphs['test'][:100] 
                elif 'all' in self.graphs:
                    self.graphs['all'] = self.graphs['all'][:200]   
            pkl.dump(self, f)

    def read_node_labels(self, key):
        # read thru all the node labels in a dataset. 
        for json_path in glob("%s/**/**/topModule.json" % str(self.root_path/key), recursive=True):
            with open(str(json_path), 'r') as json_file:
                edge_list_dict = json.loads(json_file.read())
                for src in edge_list_dict:
                    node_name = src
                    if '_graphrename' in src:
                        node_name = src[:src.index('_graphrename')]
                    if '.' in node_name: 
                        type_of_node = node_name.split('.')[-1]
                    elif '_' in node_name:
                        type_of_node = node_name.split('_')[-1]
                    else:
                        type_of_node = node_name.lower()
                    self.node_labels.add(type_of_node)

        self.label2idx = {v:k for k, v in enumerate(list(self.node_labels))}
        self.idx2label = {v:k for k, v in self.label2idx.items()}

    def split_dataset(self, ratio, seed, dataset):
        train_size = int(len(dataset) * ratio)

        sim_diff_label = []

        for data in dataset:
            if data[2] == 1:
                sim_diff_label.append(1)
            else:
                sim_diff_label.append(-1)

        return train_test_split(dataset, train_size = train_size, shuffle = True, stratify=sim_diff_label, random_state=seed)

    def get_graph_from_json(self, json_path):
        json_file = open(str(json_path), 'r')
        hardware_graph = nx.DiGraph()
        edge_list_dict = json.loads(json_file.read())
        for src in edge_list_dict:
            node_name = src
            if '_graphrename' in src:
                node_name = src[:src.index('_graphrename')]
            if '.' in node_name: 
                type_of_node = node_name.split('.')[-1]
            elif '_' in node_name:
                type_of_node = node_name.split('_')[-1]
            else:
                type_of_node = node_name.lower()

            hardware_graph.add_node(src, x=self.label2idx[type_of_node], label=type_of_node) 
            for neighbor in edge_list_dict[src]:
                dst = neighbor[1]
                hardware_graph.add_edge(src, dst)

        return hardware_graph

    def get_node_embeddeings(self, graph):
        X=[]
        name2idx = {}
        idx2name = {}
        for idx, node in enumerate(graph.nodes(data=True)):
            node_name = node[0]
            node_label = node[1]['x']

            name2idx[node_name] = idx
            idx2name[idx] = node_name
            X.append(node_label)
        X = torch.LongTensor(X)
        return X, name2idx, idx2name

    def get_edge_idxs(self, graph, name2idx):
        edge_idx = []
        for src, dst in graph.edges():
            edge_idx.append((name2idx[src], name2idx[dst]))
        edge_idx = torch.transpose(torch.LongTensor(edge_idx), 0, 1).detach()
        return edge_idx


class VerilogParser:
    '''
        the only class that interfaces with pyverilog.
    ''' 
    #holds a graph_generator instance
    def __init__(self, verilog_file, output_directory, top_module, draw_graph=False):
        self.output_directory = output_directory
        self.signals_DFG  = self._generate_graph(verilog_file, top_module)
        self.signals_DFG = self.generate_signals_DFG(self.signals_DFG, draw_graph)
        self.graph_generator = self.merge_graphs(self.signals_DFG, draw_graph)
        
    #helper fcn to __init__
    def _generate_graph(self, verilog_file, top_module):
        # create dataflow analyzer
        dataflow_analyzer = PyDataflowAnalyzer(verilog_file, top_module)
        dataflow_analyzer.generate()
        binddict = dataflow_analyzer.getBinddict()
        terms = dataflow_analyzer.getTerms()
        
        # create dataflow optimizer
        dataflow_optimizer = PyDataflowOptimizer(terms, binddict)
        dataflow_optimizer.resolveConstant()
        resolved_terms = dataflow_optimizer.getResolvedTerms()
        resolved_binddict = dataflow_optimizer.getResolvedBinddict()
        constlist = dataflow_optimizer.getConstlist()

        return PyGraphGenerator(top_module, terms, binddict, resolved_terms, 
                            resolved_binddict, constlist, 
                            f'{self.output_directory}seperate_modules.pdf')
    
    # This function returns True, if the child is a child of checkParent
    def _isChild(self, graph, checkParent, child):
        # This function recursively returns a list of all the parents of a node up to the root
        def getAllParents(node):
            # if node has no parents
            if graph.in_degree(node) == 0:
                return []
            # if node has no grandparents
            elif sum([graph.in_degree(parent) for parent in graph.predecessors(node)]) == 0:
                return graph.predecessors(node)
            # recursive call, node has unknown generations of parents
            else:
                retlist = list()
                for parent in graph.predecessors(node):
                    x = getAllParents(parent)
                    x.append(parent)
                    retlist += x
                return retlist
        allParents = getAllParents(child)
        return checkParent in allParents

    #generate separate graph separate modules 
    def generate_signals_DFG(self, subgraph_gen, draw_graph=False):
        # binddict with string keys
        signals = [str(bind) for bind in subgraph_gen.binddict]

        print(f'{len(signals)} signals to generate signals data flow graphs...')
        for num, signal in enumerate(sorted(signals, key=str.casefold), start=1):
            subgraph_gen.generate(signal, walk=False)
            print(f'\rProgress : {num} / {len(signals)}', end='', flush=True)
        print('\nThe signals data flow graphs are generated.\n')

        if draw_graph:
            print(f'Saving signals data flow graphs with {len(subgraph_gen.graph.nodes())} nodes as a pdf...')
            subgraph_gen.draw()
            print('The subgraphs are saved.\n')
            
        return subgraph_gen

    def draw_signals_DFG(self):
        print(f'Drawing signals data flow graphs with {len(self.signals_DFG.graph.nodes())} nodes as a pdf...')
        self.signals_DFG.draw()
        print('The pdf is saved.\n')
        
    def draw_DFG(self):
        print(f'Drawing data flow graph with {len(self.graph_generator.graph.nodes())} nodes as a pdf...')
        self.graph_generator.draw()
        print('The pdf is saved.\n')
        
    #merge the graphs
    def merge_graphs(self, graph_gen, draw_graph=False):
        label_to_node = dict()
        for node in graph_gen.graph.nodes():
            if graph_gen.graph.in_degree(node) == 0:
                label = node.attr['label'] if node.attr['label'] != '\\N' else str(node)
                label_to_node[label] = node
        
        deleted = 0
        print('Merging subgraphs... ')
        for num, node in enumerate(graph_gen.graph.nodes(), start=1):
            label = node.attr['label'] if node.attr['label'] != '\\N' else str(node)
            if '_' in label and label.replace('_', '.') in label_to_node:
                parents = graph_gen.graph.predecessors(node)
                graph_gen.graph.delete_node(node)
                deleted += 1
                for parent in parents:
                    if not self._isChild(graph_gen.graph, label_to_node[label.replace('_', '.')], parent):
                        graph_gen.graph.add_edge(parent, label_to_node[label.replace('_', '.')])
            print(f'\rProgress : {num - deleted} / {len(graph_gen.graph.nodes())}', end='', flush=True)
        print('\nThe signals subgraphs are merged.\n')

        if draw_graph:
            print(f'Saving merged graph with {len(graph_gen.graph.nodes())} nodes as a pdf...')
            graph_gen.draw(f'{self.output_directory}merged_graph.pdf')
            print('The graphs are saved.\n')
            
        return graph_gen

    #export the graphs
    def export_graphs(self, output_dir, output='graph'):
        output_dir = str(output_dir)
        if (output=='roots'):
            root_nodes = [node for node in self.graph_generator.graph.nodes() if self.graph_generator.graph.in_degree(node) == 0]
            print(f'Saving {len(root_nodes)} root nodes as a json...')
            with open(f'{output_dir}root_nodes.json', 'w') as f:
                f.write(dumps(root_nodes, indent=4))
            print('List of root nodes saved in root_nodes.json.\n')
            f.close()
            return root_nodes
        elif (output=='nodes'):
            all_nodes = (self.graph_generator.graph.nodes())
            print(f'Saving all {len(all_nodes)} nodes as a json...')
            with open(f'{output_dir}all_nodes.json', 'w') as f:
                f.write(dumps(all_nodes, indent=4))
            print('List of nodes saved in all_nodes.json.\n')
            f.close()
            return all_nodes
            
        elif (output=='edges'):
            all_edges = list()
            for edge in self.graph_generator.graph.edges():
                all_edges.append((edge[0], edge[1], edge.attr['label']))
            print(f'Saving all {len(all_edges)} edges as a json...')
            with open(f'{output_dir}all_edges.json', 'w') as f:
                f.write(dumps(all_edges, indent=4))
            print('List of edges is saved in all_edges.json.\n')
            f.close()
            return all_edges
            
        elif (output=='graph'):
            jsondict = {}
            for node in self.graph_generator.graph.nodes():
                jsondict[str(node)] = list()
                for child in self.graph_generator.graph.successors(node):
                    edgeLabel = self.graph_generator.graph.get_edge(node, child).attr['label']
                    jsondict[str(node)].append((edgeLabel, str(child)))
            print(f'Saving graph dictionary as a json...')
            f = open(f'{output_dir}/topModule.json', 'w')
            jsonstr = dumps(jsondict, indent=4)
            f.write(jsonstr)
            f.close()
            print('The graph is saved as topModule.json.\n')
            return jsondict

class RTLASTGenerator:
    def __init__(self):
        pass

class RTLDFGGenerator:
    '''
        This generator generates DFG from RTL (Register Transfer Level) Verilog code.
    '''
    def __init__(self, code_language='verilog', top_module='top', draw_graph=False):
        self.code_language = code_language
        self.top_module = top_module
        self.draw_graph = draw_graph

        # if code_language == "verilog":
        # self.generate_DFG(verilog_file, output_path, top_module, draw_graph)

    def process(self, verilog_path, output_path):
        '''
            parse the hw code to graph object
        '''
        if not verilog_path.exists():
            raise IOError("file not found: " + verilog_path)
        print("Reading ", verilog_path)

        if self.code_language == "verilog":
            # self.DFG_gen = VerilogParser(verilog_path, self.output_path, self.top_module, self.draw_graph)
            # step 1: parse the verilog with language parser provided by Pyverilog.
            # step 2: convert the parsed results to singal graph using the convertor by Pyverilog. 
            # step 3: perform our post-processing. 
            # step 4: export the generated graph.
            return VerilogParser(verilog_path, output_path, self.top_module, self.draw_graph)
    
    def process_batch(self, verilog_dir, output_path, file_name):
        ''' This function processs graphs in batch '''
        #TODO: please change this to call self.process().
        graphs = []
        for verilog_path in glob("%s/**/%s" % (verilog_dir, file_name), recursive=True):
            graphs.append(VerilogParser(verilog_path, output_path, self.top_module, self.draw_graph))
        return graphs

    def export_json(self, graph_json, output_dir): # TODO: need to support a graph batch
        '''
            export the graph/graphs in self.DFG_gen to json
        '''
        
        print(f'Outputting to : {output_dir}\n')
        if not output_dir.exists():
            raise IOError("Error: The output path doesn't exist.") # TODO: should create a new dir
        print(f'Saving graph dictionary as a json...')
        f = open(f'{output_dir}/topModule.json', 'w')
        jsonstr = json.dumps(graph_json, indent=4)
        f.write(jsonstr)
        f.close()
        print('The graph is saved as topModule.json.\n')
    

    def get_graph_json(self, graph_generator):
        graph = graph_generator.graph
        graph_json = {"edge_index":{}}
        for node in graph.nodes():
            graph_json["edge_index"][str(node)] = list()
            for child in graph.successors(node):
                edgeLabel = graph.get_edge(node, child).attr['label']
                graph_json["edge_index"][str(node)].append((edgeLabel, str(child)))
        root_nodes = [node for node in graph.nodes() if graph.in_degree(node) == 0]
        all_nodes = (graph.nodes())
        all_edges = list()
        for edge in graph.edges():
            all_edges.append((edge[0], edge[1], edge.attr['label']))
        graph_json["nodes"] = all_nodes
        graph_json["edges"] = all_edges
        graph_json["root_nodes"] = root_nodes
        return graph_json

    def draw(self, graph_generator):
        output_path = "?" # TODO: fix 
        graph_generator.draw()
        print('The pdf is saved in %s.' % output_path)

    def export_nodes(self):
        return self.DFG_gen.export_graphs(output='nodes')
    
    def export_edges(self):
        return self.DFG_gen.export_graphs(output='edges')
    
    def export_root_nodes(self):
        return self.DFG_gen.export_graphs(output='roots')
        
        

class GLNDFGGenerator:
    '''
        This generator generates DFG from GLN (Gate-Level Netlist) Verilog code.
    '''
    def __init__(self, verilog_file, output_path, code_language='verilog', top_module='top', draw_graph=False):
        if code_language == "verilog":
            if not os.path.exists(verilog_file):
                raise IOError("file not found: " + verilog_file)
    
            print("Reading ", verilog_file)
            print(f'Outputting to : {output_path}\n')
            if not os.path.exists(f'{output_path}'):
                    print("Error: The output path doesn't exist.") 
            self.generate_DFG(verilog_file, output_path, top_module, draw_graph)
            
   
    def generate_DFG(self, verilog_file, output_path, top_module='top', draw_graph=False):
        self.DFG_gen = VerilogParser(verilog_file, output_path, top_module, draw_graph)
        self.DFG_gen.export_graphs(output='graph')
    
    def draw_DFG(self):
        pass
    
    def draw_signals_DFG(self):
        pass
    
    def export_nodes(self):
        return self.DFG_gen.export_graphs(output='nodes')
    
    def export_edges(self):
        return self.DFG_gen.export_graphs(output='edges')
    
    def export_root_nodes(self):
        return self.DFG_gen.export_graphs(output='roots')


class RTLCFGGenerator:
    '''
        This generator generates the Control Flow Graph (CFG) from RTL (Register Transfer Level) verilog code.
    '''
    def __init__(self, code_language="verilog"):
        if code_language == "verilog":
            self.parser = VerilogParser()

    def generate(self):
        pass


class GLNCFGGenerator:
    '''
        This generator generates CFG from GLN (Gate-Level Netlist) Verilog code.
    '''
    def __init__(self, code_language="verilog"):
        if code_language == "verilog":
            self.parser = VerilogParser()

    def generate(self):
        pass


class PreprocessVerilog:
    '''
        This class comprise the preprocessing functions for Verilog files in RTL (Register Transfer Level) and GLN (Gate-Level Netlist).
    '''
    def __init__(self, code_language="verilog"):
        if code_language == "verilog":
            pass

    def remove_underscores(self, input_file):
        f = open(input_file, 'r')
        s = f.read().replace('_', '')
        f.close()
        f = open(filename, 'w')
        f.write(s)
        f.close()

    def flatten(self, input_path, output_path, top_module):
        output_path = os.path.dirname(os.path.abspath(__file__))
        with open(output_path+"/topModule.v", "wt") as outfile:
            for verilog_file in glob(fr'{input_path}/*.v'):
                with open(verilog_file, "rt") as infile:
                    outfile.write(infile.read().replace(top_module, 'top'))