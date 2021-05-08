import cProfile
import pstats
import io
import os
import sys
from matplotlib import pylab
import matplotlib.pyplot as plt
import networkx as nx

from pyverilog.vparser.parser import VerilogCodeParser
from pyverilog.dataflow.modulevisitor import ModuleVisitor
from pyverilog.dataflow.signalvisitor import SignalVisitor
from pyverilog.dataflow.bindvisitor import BindVisitor

def profileit(func):
    def wrapper(*args, **kwargs):
        datafn = func.__name__ + ".txt" 
        last_time = 0
        count = 0
        if os.path.exists(datafn):
            with open(datafn, 'r') as f: 
                line = f.readline().split(" ")
                count = int(line[0])
                last_time = float(line[1])
        pr = cProfile.Profile()
        retval = pr.runcall(func, *args, **kwargs)
        st = io.StringIO()
        ps = pstats.Stats(pr, stream=st).sort_stats('tottime')
        ps.print_stats()

        with open(datafn, 'w+') as f:
            new_time = float(st.getvalue().split('\n')[0].split(' ')[-2]) + last_time
            f.write(str(count+1) + " " + str(new_time))
        return retval
    wrapper.unwrapped = func
    return wrapper

# profiler for graph extraction 
def profilegraph(func):
    def wrapper(*args, **kwargs):
        datafn = func.__name__ + ".txt" 
        #disable stdout
        f_null = open(os.devnull, 'w')
        sys.stdout = f_null
        
        pr = cProfile.Profile()
        pr.enable()

        result_graph = func(*args, **kwargs)

        pr.disable()
        # re-enable stdout
        sys.stdout = sys.__stdout__

        hardware_name = result_graph.name
        node_num = len(result_graph.nodes())
        edge_num = len(result_graph.edges())

        st = io.StringIO()
        ps = pstats.Stats(pr, stream=st).sort_stats('tottime')
        ps.print_stats()

        with open(datafn, 'a') as f:
            time = float(st.getvalue().split('\n')[0].split(' ')[-2])
            f.write(str(hardware_name) + " " + str(node_num) + " " + str(edge_num) + " " + str(time) + "\n")
        return result_graph
    wrapper.unwrapped = func
    return wrapper

#TODO; is this used anywhere?
# def save_graph(nxgraph, file_name):
#     plt.figure(num=None, figsize=(60, 60), dpi=80)
#     plt.axis('off')
#     fig = plt.figure(1)

#     pos = nx.nx_pydot.graphviz_layout(nxgraph, prog="dot")
#     nx.draw_networkx_nodes(nxgraph, pos, with_labels=False)
#     nx.draw_networkx_edges(nxgraph, pos)
#     labels = {}    
#     for node in nxgraph.nodes(data=True):
#         labels[node[0]] = node[1]['label']
#     nx.draw_networkx_labels(nxgraph, pos, labels)
#     plt.savefig(file_name, bbox_inches="tight")
#     pylab.close()
#     del fig

def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class VerilogDataflowAnalyzer(VerilogCodeParser):
    def __init__(self, filelist, topmodule='TOP', noreorder=False, nobind=False,
                 preprocess_include=None,
                 preprocess_define=None):
        self.topmodule = topmodule
        self.terms = {}
        self.binddict = {}
        self.frametable = None
        files = filelist if isinstance(filelist, tuple) or isinstance(
            filelist, list) else [filelist]
        VerilogCodeParser.__init__(self, files,
                                   preprocess_include=preprocess_include,
                                   preprocess_define=preprocess_define, debug=False)
        self.noreorder = noreorder
        self.nobind = nobind

    def generate(self):
        ast = self.parse()

        module_visitor = ModuleVisitor()
        module_visitor.visit(ast)
        modulenames = module_visitor.get_modulenames()
        moduleinfotable = module_visitor.get_moduleinfotable()

        signal_visitor = SignalVisitor(moduleinfotable, self.topmodule)
        signal_visitor.start_visit()
        frametable = signal_visitor.getFrameTable()

        if self.nobind:
            self.frametable = frametable
            return

        bind_visitor = BindVisitor(moduleinfotable, self.topmodule, frametable,
                                   noreorder=self.noreorder)

        bind_visitor.start_visit()
        dataflow = bind_visitor.getDataflows()

        self.frametable = bind_visitor.getFrameTable()
        self.terms = dataflow.getTerms()
        self.binddict = dataflow.getBinddict()

    def getFrameTable(self):
        return self.frametable

    # -------------------------------------------------------------------------
    def getInstances(self):
        if self.frametable is None:
            return ()
        return self.frametable.getAllInstances()

    def getSignals(self):
        if self.frametable is None:
            return ()
        return self.frametable.getAllSignals()

    def getConsts(self):
        if self.frametable is None:
            return ()
        return self.frametable.getAllConsts()

    def getTerms(self):
        return self.terms

    def getBinddict(self):
        return self.binddict