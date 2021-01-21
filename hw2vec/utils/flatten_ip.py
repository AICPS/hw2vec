from optparse import OptionParser
import os
import sys
import shutil 
from glob import glob

def flatten(input_path, target_path, topmodule_name):
    with open(target_path+"topModule.v", "wt") as outfile:
        for verilog_file in glob(fr'{input_path}/*.v'):
            with open(verilog_file, "rt") as infile:
                outfile.write(infile.read().replace(topmodule_name, 'top'))
                outfile.write('\n\n')
                

if __name__ == '__main__':
    optparser = OptionParser()
    (options, args) = optparser.parse_args()
    
    p = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(p))
    
    if len(args) != 1: 
        dataset_name = "subgraph"
        circuit_name = "ALU"
        topmodule_name = 'ALU'
        os.chdir("../")
        current_directory = os.path.dirname(os.path.abspath(__file__))    
        data_directory = f'{current_directory}\data\data_raw\{dataset_name}\{circuit_name}'
        print("Reading all data from ", data_directory, "\n")
        data_list = [x[1] for x in os.walk(data_directory)]
        if not data_list:
            raise IOError("data not found in ", data_directory)
        for data_name in data_list[0]:
            raw_directory = f"{data_directory}/{data_name}"
            hw_directory = f"{current_directory}/data/data_HW/{dataset_name}/{circuit_name}/{data_name}/"
            if not os.path.exists(f'{hw_directory}'):
                os.makedirs(os.path.dirname(f'{hw_directory}')) 
            flatten(raw_directory, hw_directory, topmodule_name)
        print("All Verilog codes are flattened and saved.")			
        print("------------------------------------------------------------------------")
    else:
        topmodule_name = 'mips_32'
        current_directory = os.path.dirname(os.path.abspath(__file__))    
        raw_directory = args[0]
        print("Reading the data from ", raw_directory, "\n")
        hw_directory = f"{current_directory}/HW/"
        if not os.path.exists(f'{hw_directory}'):
            os.makedirs(os.path.dirname(f'{hw_directory}')) 
        flatten(raw_directory, hw_directory, topmodule_name)
        print("All Verilog codes are flattened and saved.")			
        print("------------------------------------------------------------------------")
