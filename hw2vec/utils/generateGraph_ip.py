from optparse import OptionParser
import os
import sys
import shutil 
from glob import glob
import pyverilog
from pyverilog.dataflow.dataflow_analyzer import VerilogDataflowAnalyzer as DataflowAnalyzer
from pyverilog.dataflow.optimizer import VerilogDataflowOptimizer as DataflowOptimizer
from pyverilog.dataflow.graphgen import VerilogGraphGenerator as GraphGenerator

from json import dumps



# This function returns True, if the child is a child of checkParent
def isChild(graph, checkParent, child):
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
    

def generate_graph(verilog_file, output_directory):
    # create dataflow analyzer
    dataflow_analyzer = DataflowAnalyzer(verilog_file, 'top')
    dataflow_analyzer.generate()
    binddict = dataflow_analyzer.getBinddict()
    terms = dataflow_analyzer.getTerms()
    
    # create dataflow optimizer
    dataflow_optimizer = DataflowOptimizer(terms, binddict)
    dataflow_optimizer.resolveConstant()
    resolved_terms = dataflow_optimizer.getResolvedTerms()
    resolved_binddict = dataflow_optimizer.getResolvedBinddict()
    constlist = dataflow_optimizer.getConstlist()

    # create graph generator
    return GraphGenerator('top', terms, binddict, resolved_terms, 
                          resolved_binddict, constlist, 
                          f'{output_directory}seperate_modules.pdf')


def graph_seperate_modules(graph_generator, draw_graph=False):
    # binddict with string keys
    signals = [str(bind) for bind in graph_generator.binddict]

    print(f'{len(signals)} signals to generate seprate subgraphs...')
    for num, signal in enumerate(sorted(signals, key=str.casefold), start=1):
        graph_generator.generate(signal, walk=False)
        print(f'\rProgress : {num} / {len(signals)}', end='', flush=True)
    print('\nThe subgraphs are generated.\n')
    
    if draw_graph:
        print(f'Saving subgraphs with {len(graph_generator.graph.nodes())} nodes as a pdf...')
        graph_generator.draw()
        print('The subgraphs are saved.\n')
    
    return graph_generator
    

def graph_merged(graph_generator, draw_graph=False):

    label_to_node = dict()
    for node in graph_generator.graph.nodes():
        if graph_generator.graph.in_degree(node) == 0:
            label = node.attr['label'] if node.attr['label'] != '\\N' else str(node)
            label_to_node[label] = node
    
    deleted = 0
    print('Merging subgraphs... ')
    for num, node in enumerate(graph_generator.graph.nodes(), start=1):
        label = node.attr['label'] if node.attr['label'] != '\\N' else str(node)
        if '_' in label:
            if label.replace('_', '.') in label_to_node:
                parents = graph_generator.graph.predecessors(node)
                graph_generator.graph.delete_node(node)
                deleted += 1
                for parent in parents:
                    if not isChild(graph_generator.graph, label_to_node[label.replace('_', '.')], parent):
                        graph_generator.graph.add_edge(parent, label_to_node[label.replace('_', '.')])
        print(f'\rProgress : {num - deleted} / {len(graph_generator.graph.nodes())}', end='', flush=True)
    print('\nThe subgraphs are merged.\n')

    if draw_graph:
        print(f'Saving merged graph with {len(graph_generator.graph.nodes())} nodes as a pdf...')
        graph_generator.draw(f'{output_directory}merged.pdf')
        print('The graphs are saved.\n')
    
    return graph_generator


def graph_input_dependencies(graph_generator, draw_graph=False):
    
    labeltoNames = dict()
    for node in graph_generator.graph.nodes():
        label = node.attr['label'] if node.attr['label'] != '\\N' else str(node)
        if label not in labeltoNames: 
            labeltoNames[label] = list()
        labeltoNames[label].append(str(node))

    inputs = [graph_generator.graph.get_node(*labeltoNames[str(term).replace('.', '_')]) for x, term in zip(graph_generator.terms, graph_generator.terms.values()) if len(x.get_module_list()) == 1 and 'Input' in term.termtype]

    print('Locating nodes not connected to inputs...')
    to_delete = list()
    for num, node in enumerate(graph_generator.graph.nodes(), start=1):
        label = node.attr['label'] if node.attr['label'] != '\\N' else str(node)
        if label not in inputs:
            x = True
            for input_ in inputs:
                if isChild(graph_generator.graph, node, input_):
                    x = False
            if x == True:
                to_delete.append(node)
        print(f'\rProgress : {num} / {len(graph_generator.graph.nodes())}', end='', flush=True)
    print('\nRemoving nodes not connected to inputs...')
    for num, node in enumerate(to_delete, start=1):
        graph_generator.graph.delete_node(node)
        print(f'\rProgress : {num} / {len(to_delete)}', end='', flush=True)
    print('\nRemoval is complete.\n')
    
    if draw_graph:   
        print(f'Saving graph with {len(graph_generator.graph.nodes())} nodes as a pdf...')
        graph_generator.draw(f'{output_directory}input_dependencies.pdf')
        print('Graph saved.\n')
    
    
def export_basic_jsons(graph_generator, output_directory):
    
    root_nodes = [node for node in graph_generator.graph.nodes() if graph_generator.graph.in_degree(node) == 0]
    print(f'Saving {len(root_nodes)} root nodes as a json...')
    with open(f'{output_directory}root_nodes.json', 'w') as f:
        f.write(dumps(root_nodes, indent=4))
    print('List of root nodes saved in root_nodes.json.\n')
    f.close()
    
    all_nodes = (graph_generator.graph.nodes())
    print(f'Saving all {len(all_nodes)} nodes as a json...')
    with open(f'{output_directory}all_nodes.json', 'w') as f:
        f.write(dumps(all_nodes, indent=4))
    print('List of nodes saved in all_nodes.json.\n')
    f.close()
    
    all_edges = list()
    for edge in graph_generator.graph.edges():
        all_edges.append((edge[0], edge[1], edge.attr['label']))
    print(f'Saving all {len(all_edges)} edges as a json...')
    with open(f'{output_directory}all_edges.json', 'w') as f:
        f.write(dumps(all_edges, indent=4))
    print('List of edges is saved in all_edges.json.\n')
    f.close()
    
    jsondict = {}
    for node in graph_generator.graph.nodes():
        jsondict[str(node)] = list()
        for child in graph_generator.graph.successors(node):
            edgeLabel = graph_generator.graph.get_edge(node, child).attr['label']
            jsondict[str(node)].append((edgeLabel, str(child)))
    print(f'Saving graph dictionary as a json...')
    f = open(f'{output_directory}topModule.json', 'w')
    jsonstr = dumps(jsondict, indent=4)
    f.write(jsonstr)
    f.close()
    print('The Graph is saved as topModule.json.\n')


if __name__ == '__main__':
    optparser = OptionParser()
    (options, args) = optparser.parse_args()
    
    p = os.path.dirname(os.path.abspath(__file__)) 
    sys.path.insert(0, os.path.dirname(p))
    
    
    if len(args) != 1:
        dataset_name = "subgraph" 
        log_file = open(f'./log/log_alu.txt', 'w')
        os.chdir("../")
        current_directory = os.path.dirname(os.path.abspath(__file__))
        # Reading the circuits 
        dataset_directory = f'{current_directory}/data/data_HW/{dataset_name}/'
        print("Reading the circuits from", dataset_directory, "\n")
        circuit_list = [x[1] for x in os.walk(dataset_directory)]
        if not circuit_list:
            raise IOError("no circuit found in ", dataset_directory)
        for circuit_name in circuit_list[0]:    
            # Reading the data (instances of each circuit) 
            data_directory = f'{current_directory}/data/data_HW/{dataset_name}/{circuit_name}'
            print("Reading data from ", data_directory, "\n")
            data_list = [x[1] for x in os.walk(data_directory)]
            if not data_list:
                raise IOError("data not found in ", data_directory)
            for data_name in data_list[0]:
                input_directory = f"{current_directory}/data/data_HW/{dataset_name}/{circuit_name}/{data_name}/topModule.v"
                output_directory = f"{current_directory}/data/data_DFG/{dataset_name}/{circuit_name}/{data_name}/"
                print(f'Outputting to : {output_directory}\n')
                try:
                    if not os.path.exists(f'{output_directory}'):
                        os.makedirs(os.path.dirname(f'{output_directory}'))
                        graph_generator = generate_graph(input_directory, output_directory)
                        subgraphs = graph_seperate_modules(graph_generator)
                        mergedGraph = graph_merged(subgraphs)
                        export_basic_jsons(mergedGraph, output_directory)  
                except:
                    print('Error in', data_name)
                    log_file.write(str(data_name+'\n'))
        log_file.close()
                
    
      				
        print("------------------------------------------------------------------------")
        
    else:
        os.chdir("../")
        #if not os.path.exists(args[0]):
        #    raise IOError("file not found: " + args[0])
        current_directory = os.path.dirname(os.path.abspath(__file__))    
        #dataset_name = "RTL"
        #circuit_name = 'mips_pipeline'
        #input_directory = f"{current_directory}/data/data_HW/{dataset_name}/{circuit_name}/mips_pipeline (95)/topModule.v"
        #output_directory = f"{current_directory}/data/data_DFG/{dataset_name}/{circuit_name}/mips_pipeline (95)/"
        input_directory = args[0]
        print("Reading ", input_directory)
        output_directory = f"{current_directory}/graphs/"
        print(f'Outputting to : {output_directory}\n')
        if not os.path.exists(f'{output_directory}'):
            os.makedirs(os.path.dirname(f'{output_directory}'))
        graph_generator = generate_graph(input_directory, output_directory)
        subgraphs = graph_seperate_modules(graph_generator)
        mergedGraph = graph_merged(subgraphs)
        export_basic_jsons(mergedGraph, output_directory) 
        
