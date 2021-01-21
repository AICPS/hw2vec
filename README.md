# hw2vec

This repo is a collection of the following two projects:
1. Hardware Trojan Detection in RTL/Gate-Level Netlist using Graph Learning (GNN4TJ)
2. IP Piracy detection (clone detection) in hardware design using graph learning (GNN4IP)

We leverage [Pyverilog](https://github.com/PyHDI/Pyverilog) from PyHDI as part of our graph extraction pipeline. It has capabilities to extract the data-flow and control-flow graphs from verilog code.

General Pipeline Architecture is shown as below:
![](https://github.com/louisccc/hw2vec/blob/master/figures/pipeline.png?raw=true)

# Directories Structure 
TO be finished. 

# Working Environment
To run [Pyverilog](https://github.com/PyHDI/Pyverilog), we use anaconda3 as primary working environment.
```sh
1. conda create --name [your working environment name] python=3.6
2. conda activate [your working environment name]
3. conda install -c conda-forge iverilog
4. conda install graphviz
5. conda install -c alubbock pygraphviz
6. pip install pyverilog
```

Also, these two packages are needed:
```sh 
pip install pyunpack
pip install patool
```

# Installation 

## Install PyTorch 1.5.0

To install PyTorch 1.5.0 follow the instructions under "Quick Start Locally" [here](http://pytorch.org/).

## Install Requirements

Run the following commands to install the requirements.

```sh
$ conda activate [your working environment name]
$ pip install -r requirements.txt
```

## Install PyTorch Geometric

To install PyTorch Geometric, simply follow the instructions [here](https://pytorch-geometric.readthedocs.io/en/latest/notes/installation.html).

# Dataset
We obtain the dataset from a famous trojan [benchmark](http://www.trust-hub.org/benchmarks/trojan). We manually downloaded all the avaialable dataset in RTL level into [./input](https://github.com/louisccc/hard_hard_graph/tree/master/input) folder. 
Running the command"
```python
python combine_dataset.py
```
will extract all data instances in the folder and store them into one combined dataset folder.
