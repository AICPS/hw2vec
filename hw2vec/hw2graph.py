#!/usr/bin/env python
#title           :hw2graph.py
#description     :This file includes the neccessary functions in hw2graph.
#author          :Rozhin
#date            :2021/03/05
#version         :0.2
#notes           :
#python_version  :3.6
#==============================================================================
from __future__ import absolute_import
from __future__ import print_function

import pyverilog.utils.util as util
import networkx as nx

import pyverilog, pydot, json, os, sys
sys.path.append(os.path.dirname(sys.path[0]))

from json import dumps
from collections import defaultdict
from pyverilog.dataflow.optimizer import VerilogDataflowOptimizer
from pyverilog.dataflow.graphgen import VerilogGraphGenerator
from pyverilog.controlflow.controlflow_analyzer import VerilogControlflowAnalyzer
from pyverilog.vparser.parser import parse
from sklearn.model_selection import train_test_split
from glob import glob
from hw2vec.graph2vec.trainers import *
from hw2vec.utilities import *


class DataProcessor:
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
        
        self.label2idx = None

        self.global_type2idx_AST_list = ['names','always','none','senslist','sens','identifier','nonblockingsubstitution',
                                         'lvalue','rvalue','intconst','pointer','ifstatement','pure numeric','assign','cond',
                                         'unot','plus','land','reg','partselect','eq','lessthan','greaterthan','decl','wire',
                                         'width','output','input','moduledef','portarg','instancelist','source','description',
                                         'port','portlist','ulnot','instance','or','and','lor','block','xor','ioport',
                                         'blockingsubstitution','minus','times','casestatement','case','parameter','sll','srl',
                                         'sra','divide','systemcall','singlestatement','stringconst','noteq','concat','repeat',
                                         'integer','xnor','dimensions','length','lconcat','uminus','greatereq','initial','uor',
                                         'casexstatement','forstatement','localparam','eventstatement','mod','delaystatement',
                                         'floatconst','task','paramarg', 'paramlist', 'inout']
        self.global_type2idx_AST = {v:k for k, v in enumerate(self.global_type2idx_AST_list)}

        self.global_type2idx_DFG_list = ['concat','input','unand','unor','uxor','signal','uand','ulnot','uxnor','numeric','partselect',
                                         'and','unot','branch','or','uor','output','plus','eq','minus','xor','lor','noteq','land',
                                         'greatereq','greaterthan','sll','lessthan','times','srl','pointer','mod','divide','sra','sla',
                                         'xnor']

        self.global_type2idx_DFG = {v:k for k, v in enumerate(self.global_type2idx_DFG_list)}

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
        graph_pairs = self.graph_pairs
        self.graph_pairs_train, self.graph_pairs_test = self.split_dataset(ratio=self.cfg.ratio, seed=self.cfg.seed, dataset=graph_pairs)
        return self.graph_pairs_train, self.graph_pairs_test

    def normalize(self, nx_graph, graph_format="DFG", normalize="keep_variable"):
        ''' 
            Normalization is a step to replace the label of a node to a value.
            We have two options in hw2vec: 
            1. keep the variable name/numeric value.
            2. replace all the variable name and numeric values with a high-level type.
        '''
        if normalize == "keep_variable":
            if self.label2idx == None:
                self.label2idx = {v:k for k, v in enumerate(list(self.node_labels))}
            for node in nx_graph.nodes(data=True):
                node[1]['x'] = self.label2idx[node[1]['label']]
            self.num_node_labels = len(self.label2idx)
        elif graph_format == 'DFG': # normalize for DFG
            in_degrees = [val for (node, val) in nx_graph.in_degree()]
            out_degrees = [val for (node, val) in nx_graph.out_degree()]
            for idx, node in enumerate(nx_graph.nodes(data=True)):
                node_name = node[0]
                if '_graphrename' in node_name:
                    node_name = node_name[:node_name.index('_graphrename')]
                if '\'d' in node_name or '\'b' in node_name or '\'o' in node_name or '\'h' in node_name:
                    type_of_node = "numeric"
                elif in_degrees[idx] == 0:
                    type_of_node = "output"
                elif out_degrees[idx] == 0:
                    type_of_node = "input"
                elif '.' in node_name or '_' in node_name:
                    type_of_node = "signal"
                else:
                    type_of_node = node_name.lower()

                if type_of_node not in self.global_type2idx_DFG:
                    print("----------"+type_of_node+"-------------")
                    raise Exception("The operation is not in the global_type2idx_DFG table, please report the error to " +   
                                "https://github.com/louisccc/hw2vec/issues")
                
                node[1]['x'] = self.global_type2idx_DFG[type_of_node]
            self.num_node_labels = len(self.global_type2idx_DFG)
        
        else: # normalize for AST
            out_degrees = [val for (node, val) in nx_graph.out_degree()]
            for idx, node in enumerate(nx_graph.nodes(data=True)):
                label = node[1]['label']
                if out_degrees[idx] == 0 and not isInt(label):
                    type_of_node = "names"
                elif isInt(label):
                    type_of_node = "pure numeric"
                else:
                    type_of_node = label.lower()
                
                if type_of_node not in self.global_type2idx_AST:
                    print("----------"+type_of_node+"-------------")
                    raise Exception("The operation is not in the global_type2idx_AST table, please report the error to " +   
                                "https://github.com/louisccc/hw2vec/issues")
                
                node[1]['x'] = self.global_type2idx_AST[type_of_node]
            self.num_node_labels = len(self.global_type2idx_AST)


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
            if type(data) == tuple:
                if data[2] == 1:
                    sim_diff_label.append(1)
                else:
                    sim_diff_label.append(-1)
            else:
                if data.label == 1:
                    sim_diff_label.append(1)
                else:
                    sim_diff_label.append(-1)

        return train_test_split(dataset, train_size = train_size, shuffle = True, stratify=sim_diff_label, random_state=seed)
    

class DFGGenerator:
    def __init__(self):
        pass

    def process(self, verilog_file):
        dataflow_analyzer = VerilogDataflowAnalyzer(verilog_file, "top")
        dataflow_analyzer.generate()
        binddict = dataflow_analyzer.getBinddict()
        terms = dataflow_analyzer.getTerms()
        
        dataflow_optimizer = VerilogDataflowOptimizer(terms, binddict)
        dataflow_optimizer.resolveConstant()
        resolved_terms = dataflow_optimizer.getResolvedTerms()
        resolved_binddict = dataflow_optimizer.getResolvedBinddict()
        constlist = dataflow_optimizer.getConstlist()
        dfg_graph_generator = VerilogGraphGenerator("top", terms, binddict, resolved_terms, 
                                                    resolved_binddict, constlist, './seperate_modules.pdf')

        # binddict with string keys
        signals = [str(bind) for bind in dfg_graph_generator.binddict]

        for num, signal in enumerate(sorted(signals, key=str.casefold), start=1):
            dfg_graph_generator.generate(signal, walk=False)
            # print(f'\rProgress : {num} / {len(signals)}', end='', flush=True)

        # import pdb; pdb.set_trace()
        label_to_node = dict()
        for node in dfg_graph_generator.graph.nodes():
            if dfg_graph_generator.graph.in_degree(node) == 0:
                label = node.attr['label'] if node.attr['label'] != '\\N' else str(node)
                label_to_node[label] = node
        
        # deleted = 0
        # print('\nMerging subgraphs... ')
        num_nodes = len(dfg_graph_generator.graph.nodes())
        for num, node in enumerate(dfg_graph_generator.graph.nodes(), start=1):
            label = node.attr['label'] if node.attr['label'] != '\\N' else str(node)
            if '_' in label and label.replace('_', '.') in label_to_node:
                parents = dfg_graph_generator.graph.predecessors(node)
                dfg_graph_generator.graph.delete_node(node)
                # deleted += 1
                for parent in parents:
                    # if not self._isChild(self.dfg_graph_generator.graph, label_to_node[label.replace('_', '.')], parent):
                    dfg_graph_generator.graph.add_edge(parent, label_to_node[label.replace('_', '.')])
            # print(f'\rProgress : {num} - {deleted} = {num - deleted} / {num_nodes}', end='', flush=True)
        # print('\nThe signals subgraphs are merged.')
        
        nx_graph = nx.DiGraph()
        
        for node in dfg_graph_generator.graph.nodes():
            node_name = node.name
            if '_graphrename' in node.name:
                node_name = node.name[:node.name.index('_graphrename')]
            if '.' in node_name: 
                type_of_node = node_name.split('.')[-1]
            elif '_' in node_name:
                type_of_node = node_name.split('_')[-1]
            else:
                type_of_node = node_name.lower()
            nx_graph.add_node(node.name, label=type_of_node) 
            for child in dfg_graph_generator.graph.successors(node):
                # edgeLabel = dfg_graph_generator.graph.get_edge(node, child).attr['label']
                nx_graph.add_edge(node.name, child.name)

        return nx_graph
    

class ASTGenerator:
    def __init__(self):
        self.DICTIONARY_GEN = \
            ["Source","Description","Ioport","Decl","Lvalue"]
        self.ARRAY_GEN = \
            ["ModuleDef","Paramlist","Portlist","Input","Width","Reg","Wire","Rvalue","ParseSelect",
             "Uplus","Uminus","Ulnot","Unot","Uand","Unand","Uor","Unor","Uxnor","Power","Times","Divide","Mod","Plus",
             "Minus","Sll","Srl","Sla","Sra","LessThan","GreaterThan","LessEq","GreaterEq","Eq","Eql","NotEq","Eql","NotEql",
             "And","Xor","Xnor","Or","Land","Lor","Cond","Assign","Always","AlwaysFF","AlwaysComb","AlwaysLatch",
             "SensList","Sens","Substitution","BlockingSubstitution","NonblockingSubstitution","IfStatement","Block",
             "Initial","Plus","Output","Partselect","Port","InstanceList","Instance","PortArg","Pointer","Concat", "Parameter", 
             "SystemCall", "CaseStatement", "Case", "Function", "CasezStatement", "FunctionCall", "Dimensions", "Length", 
             "LConcat", "Concat", "SingleStatement", "Repeat", "Integer", "CasexStatement", "ForStatement", "Localparam",
             "EventStatement", "DelayStatement", "Task", "ParamArg", "Inout"]
        self.CONST_DICTIONARY_GEN = \
            ["IntConst","FloatConst","StringConst","Identifier"]

    def process(self, verilog_file):
        #when generating AST, determines which substructure (dictionary/array) to generate
        #before converting the json-like structure into actual json
        
        self.ast, _ = parse([verilog_file], debug=False)
        ast_dict = self._generate_ast_dict(self.ast)
        return ast_dict

    #generates nested dictionary for conversion to json (AST helper)
    def _generate_ast_dict(self, ast_node):
        class_name = ast_node.__class__.__name__
        structure = {}
        #based on the token class_name, determine the value type of class_name
        if class_name in self.ARRAY_GEN:
            structure[class_name] = [getattr(ast_node, n) for n in ast_node.attr_names] if ast_node.attr_names else []
            for c in ast_node.children():
                structure[class_name].append(self._generate_ast_dict(c))
        elif class_name in self.DICTIONARY_GEN:
            structure[class_name] = self._generate_ast_dict(ast_node.children()[0])
        elif class_name in self.CONST_DICTIONARY_GEN:
            structure = {}
            structure[class_name] = getattr(ast_node,ast_node.attr_names[0])
            return structure
        else:
            raise Exception(f"Error. Token name {class_name} is invalid or has not yet been supported")
        return structure

class CFGGenerator:
    def __init__(self):
        pass

    def process(self, verilog_file): 
        fsm_vars = tuple(['fsm', 'state', 'count', 'cnt', 'step', 'mode'])
        dataflow_analyzer = PyDataflowAnalyzer(self.verilog_file, "top")
        dataflow_analyzer.generate()
        binddict = dataflow_analyzer.getBinddict()
        terms = dataflow_analyzer.getTerms()
        
        dataflow_optimizer = VerilogDataflowOptimizer(terms, binddict)
        dataflow_optimizer.resolveConstant()
        resolved_terms = dataflow_optimizer.getResolvedTerms()
        resolved_binddict = dataflow_optimizer.getResolvedBinddict()
        constlist = dataflow_optimizer.getConstlist()
        cfg_graph_generator = VerilogControlflowAnalyzer("top", terms, binddict, resolved_terms, resolved_binddict, constlist, fsm_vars)
        fsms = cfg_graph_generator.getFiniteStateMachines()

        print("VIEWING FSM's")
        print("LENGTH OF FSM: ", len(fsms))
        for signame, fsm in fsms.items():
            print('# SIGNAL NAME: %s' % signame)
            print('# DELAY CNT: %d' % fsm.delaycnt)
            fsm.view()
            fsm.tograph(filename=util.toFlatname(signame) + '.png', nolabel=False)

        graph = pydot.graph_from_dot_file("./file.dot")[0]

        nodes = [node.get_name() for node in graph.get_node_list()]
        root_nodes = [node.get_name() for node in graph.get_node_list() if node.obj_dict['parent_graph'] == None]
        edges = [[edge.get_source(),edge.get_destination(),edge.obj_dict['attributes']['label']] for edge in graph.get_edge_list()]
        topModule = defaultdict([]) 

        for edge in edges:
            if edge[2] == 'None':
                topModule[edge[0]].append("")
            else:
                topModule[edge[0]].append(edge[2])
        
        if (output=='roots'):
            print(f'Saving all {len(root_nodes)} nodes as json')
            with open('./root_nodes.json', 'w') as f:
                f.write(dumps(root_nodes, indent=4))
            print('List of root nodes saved in root_nodes.json.\n')
            f.close()
        
        elif (output=='nodes'):
            print(f'Saving all {len(nodes)} nodes as json')
            with open('./all_nodes.json', 'w') as f:
                f.write(dumps(nodes, indent=4))
            print('List of nodes saved in all_nodes.json.\n')
            f.close()
            
        elif (output=='edges'):
            print(f'Saving all {len(edges)} edges as json')
            with open('./all_edges.json', 'w') as f:
                f.write(dumps(edges, indent=4))
            print('List of edges saved in all_edges.json.\n')
            f.close()
            
        elif (output=='graph'):
            print(f'Saving cfg graph dictionary as a json')
            with open('./topModule.json', 'w') as f:
                f.write(dumps(topModule, indent=4))
            print('Saving cfg graph dictionary as a json.\n')
            f.close()
            print('The graph is saved as topModule.json.\n')
        return None


class HW2GRAPH:
    '''the main class of hw2graph.''' 
    def __init__(self, cfg):
        self.cfg = cfg
        self.count = 0

    @profilegraph
    def process(self, verilog_file):
        if self.cfg.graph_type == "CFG":
            generator = CFGGenerator()
            return_obj = generator.process(verilog_file)
            nx_graph = None
        
        elif self.cfg.graph_type == "AST":
            generator = ASTGenerator()
            ast_dict = generator.process(verilog_file)
            nx_graph = nx.DiGraph()
            for key in ast_dict.keys():
                self.add_node(nx_graph, 'None', key, ast_dict[key])

        elif self.cfg.graph_type == "DFG":
            generator = DFGGenerator()
            nx_graph = generator.process(verilog_file)
        
        else:
            pass
            
        for file in ['file.dot','parser.out','parsetab.py','top_state.png']:
            try:
                os.remove(file)
            except FileNotFoundError:
                pass

        if nx_graph != None:
            nx_graph.name = verilog_file.split("/")[-2]
        return nx_graph

    def add_node(self, graph, parent, child, cur_dict):
        index = self.count
        graph.add_nodes_from([(index, {"label": str(child)})])
        if parent != 'None':
            graph.add_edge(parent, index)
        self.count = self.count + 1
        if type(cur_dict) == dict:
            for key in cur_dict.keys():
                self.add_node(graph, index, key, cur_dict[key])
        elif type(cur_dict) == list:
            for ele in cur_dict:
                if type(ele) == dict:
                    self.add_node(graph, index, 'None', ele)
                elif ele is not None:
                    graph.add_nodes_from([(self.count, {"label": str(ele)})])
                    graph.add_edge(index, self.count)
                    self.count = self.count + 1
        else:
            graph.add_nodes_from([(self.count, {"label": str(cur_dict)})])
            graph.add_edge(index, self.count)
            self.count = self.count + 1


class PreprocessVerilog:
    '''This class comprise the preprocessing functions for Verilog files in RTL (Register Transfer Level) and GLN (Gate-Level Netlist).'''
    def __init__(self):
        pass

    def remove_comments(input_path, target_path):
        # read the file into a list of lines
        with open(input_path,'r') as file_in:
            lines = file_in.read().split("\n")
    
        file_out = open(target_path, 'w')
        modules_dic={}
        for i,line in enumerate(lines):
            idx = line.find('/')
            file_out.write(line[0:idx]+'\n')
                    
        file_in.close()
        file_out.close()
        
    def rename_topModule(input_path, target_path):
        # read the file into a list of lines
        with open(input_path,'r') as file_in:
            lines = file_in.read().split("\n")
    
        modules_dic={}
        # iterate over lines, and list the module names.
        for i,line in enumerate(lines):
            words = line.split()
            for j,word in enumerate(words):
                if word == 'module':
                    module_name = words[j+1]
                    if '(' in module_name:
                        idx = module_name.find('(')
                        module_name = module_name[:idx]
                        modules_dic[module_name]= 1
                    else:
                        modules_dic[module_name]= 0
                    
        # iterate over file and count the occurance of each module name.                       
        for i,line in enumerate(lines):
            words = line.split()
            for j,word in enumerate(words):
                for m in modules_dic:
                    if word == m:
                        modules_dic[m] = modules_dic[m] + 1
        print("a dictionary of module names and the number of their occurance: ", modules_dic)
        
        # find the name of top module
        for m in modules_dic:
            if modules_dic[m] == 1:
                top_module = m
                break   
        
        # rename the top module to 'top'
        file_out = open(target_path, 'w')
        for line in lines:
            file_out.write(line.replace(top_module, 'top')+'\n')
        file_in.close()
        file_out.close()
            
    def flatten(input_path, target_path):
        with open(target_path+"/topModule.v", "wt") as outfile:
            print(input_path, glob(fr'{input_path}/*.v'))
            for verilog_file in glob(fr'{input_path}/*.v'):
                with open(verilog_file, "rt") as infile:
                    outfile.write(infile.read())       
                    
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