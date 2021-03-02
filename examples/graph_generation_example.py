import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

from hw2vec.hw2graph import *

from optparse import OptionParser
import shutil 
from glob import glob
from pathlib import Path
from glob import glob

if __name__ == '__main__':
    ''' 
        An example on how to genreate the data flow graph for a dataset of Verilog harwdare designs
        USAGE:  python graph_generation_example.py 
    
    '''    
    verilog_path = Path('../tests/data/IP-dataset/Verilog/C432/c432/topModule.v')
    dataset_directory = Path('../tests/data/IP-dataset/Verilog/C432').resolve()
    dataset_output_dir_path = Path('./').resolve()

    # handling a single verilog code to a DFG.
    hw2graph_dfg = RTLDFGGenerator(dataset_output_dir_path, code_language="verilog", top_module='top') # graph_format="DFG" 
    graph = hw2graph_dfg.process(verilog_path) 
    hw2graph_dfg.export_json(graph, dataset_output_dir_path) 
    import pdb; pdb.set_trace()

    
    # hw2graph_dfg.export_json(json_graph, output_dir=dataset_output_dir_path)
    # we might want draw? visualize? print?

    # handling verilog code in batch to DFGs.
    graphs = hw2graph_dfg.process_batch(dataset_directory, "topModule.v")
    # dfg_generator = HW2Graph(graph_format="DFG", code_language="verilog", top_module='top')
    # json_graphs = dfg_generator.process_batch(dataset_directory)
    # dfg_generator.export_jsons(json_graphs, output_dir=dataset_output_dir_path)


    # # handling a single verilog code to a CFG.
    # hw2graph_cfg = HW2Graph(graph_format="CFG", code_language="verilog", top_module='top')
    # json_graph = hw2graph_cfg.process(verilog_path)
    # hw2graph_cfg.export_json(json_graph, output_dir=dataset_output_dir_path)
    # # we might want draw? visualize? print?
    # #TODO: rozhin finishes this part.

    # # handling a single verilog code to a AST.
    # hw2graph_ast = HW2Graph(graph_format="AST", code_language="verilog", top_module='top')
    # json_graph = hw2graph_ast.process(verilog_path)
    # hw2graph_ast.export_json(json_graph, output_dir=dataset_output_dir_path)
    # # we might want draw? visualize? print?
    # #TODO: rozhin finishes this part.

    
    for verilog_path in glob("%s/**/topModule.v" % str(dataset_directory), recursive=True):
        print(verilog_path)
        # import pdb;pdb.set_trace()
        try:
            graph_generator = RTLDFGGenerator(verilog_path, "./", code_language='verilog', top_module='top', draw_graph=False)
            # Export the list of nodes 
            print('export the graph as a JSON dictionary: ')
            graph_generator.export_nodes()
            # Export the list of root nodes
            graph_generator.export_root_nodes()
            # Export the list of edges
            graph_generator.export_edges()
            # Draw Data Flow Graph
            graph_generator.draw_DFG()
            # Draw the subgraphs ( data flow graph of signals)
            graph_generator.draw_signals_DFG()
        except:
            print('Error in', verilog_path)