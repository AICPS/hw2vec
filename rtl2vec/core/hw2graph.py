class VerilogParser:
    '''
        the only class that interfaces with pyverilog.
    ''' 
    def __init__(self):
        pass

    def parse(self, rtlcode):
        pass
        
    def visualize(self):
        pass

    def export(self):
        pass
    
    

class RTLDFGGenerator:
    '''
        This generator generates DFG from RTL code.
    '''
    def __init__(self):
        if code_language == "verilog":
            self.parser = VerilogParser()

    def parse(self, rtlcode):
        self.graph_merged()
        self.graph_gen()
        self.graph_dependecy()
        
    '''
        non-interface functions for the parser
    '''

    def graph_merged(self):
        pass
    def graph_gen(self):
        pass
    def graph_dependecy(self):
        pass

class NetlistDFGGenerator:
    '''
        This generator generates DFG from Netlist code.
    '''
    def __init__(self, code_language="verilog"):
        if code_language == "verilog":
            self.parser = VerilogParser()

    def generate(self):
        pass


class RTLCFGGenerator:
    '''
        This generator generates the Control Flow Graph (CFG) from RTL verilog code.
    '''
    def __init__(self, code_language="verilog"):
        if code_language == "verilog":
            self.parser = VerilogParser()

    def generate(self):
        pass


class NetlistCFGGenerator:
    '''
        This generator generates CFG from Netlist code.
    '''
    def __init__(self, code_language="verilog"):
        if code_language == "verilog":
            self.parser = VerilogParser()

    def generate(self):
        pass

#TODO: check FSM?

def preprocess_verilog():
    # its going to example script: parse_verilog_2_graph.py
    # use case 1: 
    import hw2graph.RTLDFGGenerator
    parser = RTLDFGGenerator()
    parser.parse('''one or multiple RTLs''')
    parser.export("some file name", type="json")

if __name__ == "__main__":
    # This part will eventually goes to example script or test cases.

    preprocess_verilog()