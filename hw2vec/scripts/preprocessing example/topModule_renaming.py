# -*- coding: utf-8 -*-
"""
@author: Rozhin
"""


from optparse import OptionParser
import os


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
    
            
if __name__ == '__main__':
    optparser = OptionParser()
    (options, args) = optparser.parse_args()
    remove_comments('test.v', 'noComment.v')
    rename_topModule('noComment.v','final.v')
  
    
  