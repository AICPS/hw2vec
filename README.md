# HW2Vec: A Python-based Design Automation Library for Embedding Hardware Designs
[![Build Status](https://travis-ci.com/louisccc/hw2vec.svg?branch=master)](https://travis-ci.com/github/louisccc/hw2vec) [![GitHub license](https://img.shields.io/github/license/Sujit-O/pykg2vec.svg)](https://github.com/Sujit-O/pykg2vec/blob/master/LICENSE)

This repo is a collection of the following two projects:
1. Hardware Trojan Detection in RTL/Gate-Level Netlist using Graph Learning (GNN4TJ)
2. IP Piracy detection (clone detection) in hardware design using graph learning (GNN4IP)

We leverage [Pyverilog](https://github.com/PyHDI/Pyverilog) from PyHDI as part of our graph extraction pipeline. It has capabilities to extract the data-flow and control-flow graphs from verilog code.

General Pipeline Architecture is shown as below:
![](https://github.com/louisccc/hw2vec/blob/master/figures/pipeline.png?raw=true)

# Directories Structure
Directories structure (temporary) figure is shown below:
![](https://github.com/louisccc/hw2vec/blob/master/figures/folder%20structure.png?raw=true)
Library code are in hw2vec folder:<br>
hw2vec/hw2graph.py: code for generating graph objects from hardware design.<br>
hw2vec/graph2vec: code of graph training trainers and models.<br>
<br>
Use case examples are stored in examples folder:<br>
examples/gnn4ip_netlist.py: gnn4ip script running on netlist dataset.<br>
examples/gnn4ip_RTL.py: gnn4ip script running on RTL dataset.<br>
examples/gnn4tj.py:gnn4tj script running on dataset which has not been splitted into training and testing dataset. <br>
examples/gnn4tj_presplit.py: gnn4tj script running on dataset which has been splitted into training and testing dataset. <br>




# To Get Started
Before using hw2vec, we recommend users to have the following libraries installed: 
  * python >=3.6 (recommended)
  * pytorch>= 1.5
  * pyverilog 
  * PyTorch Geometric >= 1.5

To setup an Python env users can follow this: 
```sh
1. conda create --name [your working environment name] python=3.6
2. conda activate [your working environment name]
```

To install PyTorch 1.5.0 follow the instructions under "Quick Start Locally" [here](http://pytorch.org/).

Here is a quick guide for setting up an anaconda working environment:
```sh
$ conda activate [your working environment name]
$ pip install -r requirements.txt
```

To run [Pyverilog](https://github.com/PyHDI/Pyverilog), we use anaconda3 as primary working environment.
```sh
$ conda install -c conda-forge iverilog
$ conda install graphviz pygraphviz -c alubbock
$ pip install pyverilog
$ pip install pyunpack
$ pip install patool
```

To install PyTorch Geometric, simply follow the instructions [here](https://pytorch-geometric.readthedocs.io/en/latest/notes/installation.html).

# Directories Structure 
TO be finished. 

# Dataset
We obtain the dataset from a famous trojan [benchmark](http://www.trust-hub.org/benchmarks/trojan). We manually downloaded all the avaialable dataset in RTL level into [./input](https://github.com/louisccc/hard_hard_graph/tree/master/input) folder. 
Running the command"
```python
python combine_dataset.py
```
will extract all data instances in the folder and store them into one combined dataset folder.
