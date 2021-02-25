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
Before using hw2vec, we recommend users to set up the environment by following the steps below:

To setup an anaconda working environment: 
```sh
$ conda create --name [your working environment name] python=3.6
$ conda activate [your working environment name]
```
To install PyTorch and PyTorch Geometric (cuda version is 10.2):
```sh
$ conda install pytorch==1.6.0 torchvision==0.7.0 cudatoolkit=10.2 -c pytorch
$ pip install --no-index torch-scatter -f https://pytorch-geometric.com/whl/torch-1.6.0+cu102.html
$ pip install --no-index torch-sparse -f https://pytorch-geometric.com/whl/torch-1.6.0+cu102.html
$ pip install --no-index torch-cluster -f https://pytorch-geometric.com/whl/torch-1.6.0+cu102.html
$ pip install --no-index torch-spline-conv -f https://pytorch-geometric.com/whl/torch-1.6.0+cu102.html
$ pip install torch-geometric
```
If you are using a different version, please refer to the instructions [here](https://pytorch-geometric.readthedocs.io/en/latest/notes/installation.html).

To use [Pyverilog](https://github.com/PyHDI/Pyverilog), we need to install the package and its supporting packages.
```sh
$ conda install -c conda-forge iverilog
$ conda install graphviz
$ conda install -c alubbock pygraphviz
$ pip install pyverilog
$ pip install pyunpack
$ pip install patool
```
Also some libraries used in our code needed to be installed:
```sh
$ pip install -r requirements.txt
```


# Example Use Cases (only contains training part for now)
## GNN4IP: IP piracy detection (clone detection) in hardware design
### Problem Formulation
(missing in gnn4tj.md)

### Dataset
We obtain the dataset from a famous trojan [benchmark](https://www.trust-hub.org/benchmarks/trojan). <br>
(maybe still need description)

### Training
After generating graphs from hardware code, we can train our graph model. The example script is in "hw2vec/examples" folder.
```sh
$ cd examples
```
To train a model on a dataset in folder "hw2vec/data/TJ-dataset" with default configurations defined in "hw2vec/hw2vec/graph2vec/config.py", specify the configuration file path and run the script by running the following command:
```sh
$ python gnn4tj.py --config_path ./example_config.yaml
```

## GNN4IP: IP piracy detection (clone detection) in hardware design
### Problem Formulation
In this work, we want to develop a model to detect IP piracy in hardware design. In other word, we want to develop a model to check similarity between two Verilog code and determine if they are for the same hardware design or not. In order to do that, we need to create two batch of samples; clone pair, and non-clone pair. The clone pair is two Verilog code that are similar and represent the same hardware design while the non-clone pair are a pair of two code that are for entirely different designs. We have gathered a dataset of veriog assignments and all samples in a assignments are clone pair while two codes from different assignment are considered as a non-clone pair.

### Dataset
(description of dataset)

### Training
After generating graphs from hardware code, we can train our graph model. The example script is in "hw2vec/examples" folder.
```sh
$ cd examples
```
To train a model on a dataset in folder "hw2vec/data/IP-dataset" with default configurations defined in "hw2vec/hw2vec/graph2vec/config.py", please first modify the "hw2vec/examples/example_config.yaml" file. Change arguments "raw_dataset_path" to "../data/IP-dataset" and "pkl_path" to "ip.pkl". Then specify the configuration file path and run the script by running the following command:
```sh
$ python gnn4ip.py --config_path ./example_config.yaml
```
