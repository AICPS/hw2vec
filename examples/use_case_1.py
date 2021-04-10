import os, sys
sys.path.append(os.path.dirname(sys.path[0]))

from hw2vec.hw2graph import *

from optparse import OptionParser
import shutil 
from glob import glob
from pathlib import Path
from pprint import pprint
import networkx as nx
from torch_geometric.utils.convert import from_networkx


def code2graph(code_path, out_path, g_form="DFG"):
    g_form = "DFG" # toggle this to select different graph generator. 
    if g_form == "DFG":
        gen = DFGgenerator(code_path, out_path)
    elif g_form == "AST":
        gen = ASTgenerator(code_path, out_path)
    gen.process()
    g_json = gen.get_graph_json()
    pprint(g_json)
    gen.draw()
    

if __name__ == '__main__':
    ''' 
        An example on how to genreate the data flow graph for one Verilog harwdare design
        USAGE:  python use_case_1.py 
    '''
    verilog_path = '../tests/data/IP-dataset/Verilog/C880/c880-CY3880/topModule.v'
    output_path  = './' #TODO: eliminate the use of output_path
    
    code2graph(verilog_path, output_path, g_form="DFG")
    
     
   