import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

from hw2vec.hw2graph import *

from optparse import OptionParser
import shutil 
from glob import glob


if __name__ == '__main__':
    ''' 
        An example on how to genreate the data flow graph for a dataset of Verilog harwdare designs
        USAGE:  python graph_generation_example.py 
    
    '''    

    parser = OptionParser()
    parser.add_option('--dataset_name', type=str, dest="dataset_name", default="IP-dataset", help="Name of Verilog dataset")
    (options, args) = parser.parse_args()
    

    dataset_name = options.dataset_name
    log_file = open(f'./log.txt', 'w')
    os.chdir("../")
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Reading the circuits 
    dataset_directory = f'{current_directory}/data/{dataset_name}/Verilog/'
    print("Reading the circuits from", dataset_directory, "\n")
    circuit_list = [x[1] for x in os.walk(dataset_directory)]
    if not circuit_list:
        raise IOError("no circuit found in ", dataset_directory)
    for circuit_name in circuit_list[0]:    
        # Reading the data (instances of each circuit) 
        data_directory = f'{current_directory}/data/{dataset_name}/Verilog/{circuit_name}'
        data_list = [x[1] for x in os.walk(data_directory)]
        if not data_list:
            raise IOError("data not found in ", data_directory)
        for data_name in data_list[0]:
            input_directory = f"{current_directory}/data/{dataset_name}/Verilog/{circuit_name}/{data_name}/topModule.v"
            output_directory = f"{current_directory}/data/{dataset_name}/DFG/{circuit_name}/{data_name}/"
            try:
                if not os.path.exists(f'{output_directory}'):
                    os.makedirs(os.path.dirname(f'{output_directory}'))
                # Generate the Data Flow Graph (DFG)
                graph_generator = RTLDFGGenerator(input_directory, output_directory, code_language='verilog', top_module='top', draw_graph=False)
                # Export the list of nodes 
                print('export the graph as a JSON dictionary: ')
                graph_generator.export_nodes()
                # Export the list of root nodes
                graph_generator.export_root_nodes()
                # Export the list of edges
                graph_generator.export_edges()
                # Draw Data Flow Graph
                graph_generator.draw_DFG
                # Draw the subgraphs ( data flow graph of signals)
                graph_generator.draw_signals_DFG
                print("------------------------------------------------------------------------")
            except:
                print('Error in', data_name)
                log_file.write(str(data_name+'\n'))
    log_file.close()
            

  				
    

        
