# -*- coding: utf-8 -*-
"""
@author: Rozhin
"""


from optparse import OptionParser
import os


  
    
def rename_topModule(input_path, target_path):
    # read the file into a list of lines
    with open(input_path,'r') as f1:
        lines = f1.read().split("\n")

    modules_dic={}
    # iterate over lines, and list the module names.
    for i,line in enumerate(lines):
        words = line.split()
        for j,word in enumerate(words):
            if word == 'module':
                module_name = words[j+1]
                if '(' in module_name:
                    module_name = module_name[:-1]
                modules_dic[module_name]= 1
                
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
    f2 = open(target_path, 'w')
    for line in lines:
        f2.write(line.replace(top_module, 'top')+'\n')
    f1.close()
    f2.close()

            
            
def flatten(input_path, target_path):
    with open(target_path+"/topModule.v", "wt") as outfile:
        print(input_path, glob(fr'{input_path}/*.v'))
        for verilog_file in glob(fr'{input_path}/*.v'):
            with open(verilog_file, "rt") as infile:
                outfile.write(infile.read())    
    
            
if __name__ == '__main__':
    optparser = OptionParser()
    (options, args) = optparser.parse_args()
    rename_topModule('test.v','topModule.v')
  
    
  