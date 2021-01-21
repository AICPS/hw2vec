from glob import glob
from pathlib import Path
import os
import sys

def flatten(input_path, target_path, topmodule_name):
    with open(target_path+"/topModule.v", "wt") as outfile:
        print(input_path, glob(fr'{input_path}/*.v'))
        for verilog_file in glob(fr'{input_path}/*.v'):
            with open(verilog_file, "rt") as infile:
                outfile.write(infile.read().replace(topmodule_name, 'top'))


if __name__ == "__main__":
    data_list = ['AES-T100', 'AES-T200', 'AES-T300', 'AES-T400', 'AES-T500', 'AES-T600', 'AES-T700', 'AES-T800', 'AES-T900', 'AES-T1000', \
                 'AES-T1100', 'AES-T1200', 'AES-T1300','AES-T1400', 'AES-T1500', 'AES-T1600', 'AES-T1700', 'AES-T1800', 'AES-T1900', 'AES-T2000']
    
    working_directory = Path(__file__).parent

    # retrieve all directories in the processed directory
    # data_list = glob(f'{working_directory}/Datasets/trusthub-processed/*')

    if len(sys.argv) > 2:
        print('\nERROR: This program takes one or no arguments (-t for trojan, none for trojan free).\n\n')

    if len(sys.argv) == 1:
        for data_name in data_list:
            #example path for Trojan free AES circuits
            input_path = fr'{working_directory}/Datasets/trusthub_processed/'+ data_name +'/src/TjFree'
            target_path = fr'{working_directory}/Datasets/data_ready/TjFree/'+ data_name
            os.mkdir(target_path)
            flatten(input_path, target_path, 'aes_128')
    elif sys.argv[1] == '-t':
        for data_name in data_list:
            # example path for Trojan inserted AES circuits
            input_path = fr'{working_directory}/Datasets/trusthub_processed/'+ data_name +'/src/TjIn'
            target_path = fr'{working_directory}/Datasets/data_ready/TjIn/'+ data_name
            os.mkdir(target_path)
            flatten(input_path, target_path, 'top')
    else:
        print('\nERROR: Invalid argument (-t for trojan, none for trojan free).\n\n')