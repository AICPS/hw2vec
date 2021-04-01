import cProfile
import pstats
import io
from use_case_1 import *
import os
import sys
#TODO: elinimate this file.
verilog_path = Path('../tests/data/IP-dataset/Verilog/C432/c432/topModule.v')
dataset_output_dir_path = Path('./').resolve()

''' 
    without printing: 53.77s
    with printing: 54.27s
'''

# f_null = open(os.devnull, 'w')
# sys.stdout = f_null

pr = cProfile.Profile()
pr.enable()

parse_single_verilog_code(verilog_path, dataset_output_dir_path, graph_format="DFG")

pr.disable()
s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
ps.print_stats()

with open('stats.txt', 'w+') as f:
    f.write(s.getvalue())