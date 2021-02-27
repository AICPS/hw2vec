# HW2Vec: A Python-based Hardware Designs Embedding Tool for Hardware Security
[![Build Status](https://travis-ci.com/louisccc/hw2vec.svg?branch=master)](https://travis-ci.com/github/louisccc/hw2vec) [![GitHub license](https://img.shields.io/github/license/Sujit-O/pykg2vec.svg)](https://github.com/Sujit-O/pykg2vec/blob/master/LICENSE)

HW2vec contains the tools and source code we used for our previous research projects. In this repo, we collect our previous codebases and standardize the pipeline and use-cases and hope that this tool can be helpful in researchers in hardware security field and drive the research progress in this field. The two previous research projects are 1) Hardware Trojan Detection in RTL/Gate-Level Netlist using Graph Learning (GNN4TJ), 2) IP Piracy Detection in hardware design using graph learning (GNN4IP), published in DATE2021 and DAC2021, respectively. In this repo, we leverage [Pyverilog](https://github.com/PyHDI/Pyverilog) from PyHDI as part of our graph extraction pipeline.

The architecture of hw2vec is as follows:
- **hw2vec/hw2graph.py**: code for generating graph objects from hardware design.
- **hw2vec/graph2vec**: code of graph training trainers and models.

General Pipeline Architecture is shown as below:
![](https://github.com/louisccc/hw2vec/blob/master/figures/pipeline_add%20visual.jpg?raw=true)

# To Get Started
We recommend our potential users to use [Anaconda](https://www.anaconda.com/) as the virtual environment. The requirments for hw2vec is as follows,
- python >= 3.6 
- torch == 1.6.0
- torch_teometric == 1.6.1
- pygraphviz
- [Pyverilog](https://github.com/PyHDI/Pyverilog)
- packages in requirements.txt

Our recommended command sequence is as follows, 
```sh
$ conda create --name hw2vec python=3.6
$ conda activate hw2vec
$ sudo add-apt-repository universe
$ sudo apt update
$ sudo apt install graphviz
$ python -m pip install pygraphviz
$ conda install pytorch==1.6.0 torchvision==0.7.0 cudatoolkit=10.1 -c pytorch
$ python -m pip install --no-index torch-scatter -f https://pytorch-geometric.com/whl/torch-1.6.0+cu101.html
$ python -m pip install --no-index torch-sparse -f https://pytorch-geometric.com/whl/torch-1.6.0+cu101.html
$ python -m pip install --no-index torch-cluster -f https://pytorch-geometric.com/whl/torch-1.6.0+cu101.html
$ python -m pip install --no-index torch-spline-conv -f https://pytorch-geometric.com/whl/torch-1.6.0+cu101.html
$ python -m pip install torch-geometric==1.6.1
$ pip install pyverilog
$ pip install pyunpack
$ pip install patool
$ python -m pip install -r requirements.txt
```
This set of commands assumes you to have cuda10.1 in your local and you are using linux. Please refer to the installation guides of [torch](https://pytorch.org/) and [pytorch_geometric](https://pytorch-geometric.readthedocs.io/en/latest/notes/installation.html) if you have different cuda settings. If installing pygraphviz in windows, please refer this [issue](https://github.com/pygraphviz/pygraphviz/issues/58) for more information.

# Example Use Cases (only contains training part for now)
- Use case examples are stored in examples folder:
  - **examples/gnn4ip_netlist.py**: gnn4ip script running on netlist dataset.
  - **examples/gnn4ip_RTL.py**: gnn4ip script running on RTL dataset.
  - **examples/gnn4tj.py**: gnn4tj script running on dataset which has not been splitted into training and testing dataset.

## Use Case 1: Create Your Own Graph Dataset From hardware code
To be filled. (DFG, CFG, AST)

## Use Case 2: Hardware Trojan Detection in RTL-level (Advanced Application)
The sample code for this use case is examples/gnn4tj.py. The related research paper is [Graph Neural Networks for Hardware Trojan Detection at Register Transfer Level](https://drive.google.com/file/d/1XFgWWO4v2oA-lmkwleG0h03znAvmJV5i/view). The dataset used in this paper is obtained from a famous trojan [benchmark](https://www.trust-hub.org/benchmarks/trojan). The converted hardware DFG dataset can be downloaded from [here](http://ieee-dataport.org/3640).

To run this use case, use the script examples/gnn4tj.py and the downloaded dataset (data/TJ-dataset). To train a model on a dataset, we provide the following command sequence.
```sh
$ cd examples
$ python gnn4tj.py --config_path ./example_config.yaml
```
You can try to adjust the configuration (example_config.yaml) to play with the model's hyperparameter.
```python
---
learning_rate: 0.001 # The initial learning rate for the model.
seed: 1 # Random seed.
epochs: 200 # Number of epochs to train.
weight_decay: 5e-4 # Weight decay (L2 loss on parameters).
hidden: 200 # Number of hidden units.
dropout: 0.5 # Dropout rate (1 - keep probability).
nclass: 8 # The number of classes for node.
recursive: True # Recursive loading scenegraphs.
batch_size: 4 # Number of graphs in a batch.
device: "cuda" # The device to run on models (cuda or cpu) cpu in default.
model: "gcn" # Model to be used.
num_layer: 5 # Number of layers in the neural network.
hidden_dim: 32 # Hidden dimension in GIN.
test_step: 10 # The interval between mini evaluation along the training process.
pooling_type: "sagpool" # Graph pooling type.
readout_type: "max" # Readout type.
rati0: 0.8 # Dataset splitting ratio
poolratio: 0.75 # Ratio for graph pooling.
raw_dataset_path: "../data/TJ-dataset" # Path to raw dataset for parsing if no precache.
pkl_path: "tj.pkl" # Path to hardware graphs for parsing.
embed_dim: 2 # The dimension of graph embeddings.
debug: False # Debug mode.
```

## Use Case 3: IP Piracy Detection in hardware design (Advanced Application)
The sample code for this use case is examples/gnn4ip.py and examples/gnn4ip_RTL.py. The related research paper is [GNN4IP: Graph Neural Network for HardwareIntellectual Property Piracy Detection]() (still under review). The dataset used in this paper is obtained from a famous trojan [benchmark](https://www.trust-hub.org/benchmarks/trojan). The converted hardware DFG dataset can be downloaded from [here](http://ieee-dataport.org/3640). In this use case, we demonstrate how to use hw2vec to develop a model that detects IP piracy in RTL and Netlist levels. In other word, we want to develop a model to check similarity between two Verilog code and determine if they are for the same hardware design or not. In order to do that, we need to create two batch of samples; clone pair, and non-clone pair. 

To run this use case, use the script examples/gnn4tj.py and the downloaded dataset (data/IP-dataset). To train a model on a dataset, we provide the following command sequence.
```sh
$ cd examples
$ python gnn4ip.py --config_path ./example_config.yaml
```
To train a model on a dataset in folder "hw2vec/data/IP-dataset" with default configurations defined in "hw2vec/hw2vec/graph2vec/config.py", please first modify the "hw2vec/examples/example_config.yaml" file. Change arguments "raw_dataset_path" to "../data/IP-dataset" and "pkl_path" to "ip.pkl". 

You can try to adjust the configuration (example_config.yaml) to play with the model's hyperparameter.
```python
---
learning_rate: 0.001 # The initial learning rate for the model.
seed: 1 # Random seed.
epochs: 200 # Number of epochs to train.
weight_decay: 5e-4 # Weight decay (L2 loss on parameters).
hidden: 200 # Number of hidden units.
dropout: 0.5 # Dropout rate (1 - keep probability).
nclass: 8 # The number of classes for node.
recursive: True # Recursive loading scenegraphs.
batch_size: 4 # Number of graphs in a batch.
device: "cuda" # The device to run on models (cuda or cpu) cpu in default.
model: "gcn" # Model to be used.
num_layer: 5 # Number of layers in the neural network.
hidden_dim: 32 # Hidden dimension in GIN.
test_step: 10 # The interval between mini evaluation along the training process.
pooling_type: "sagpool" # Graph pooling type.
readout_type: "max" # Readout type.
rati0: 0.8 # Dataset splitting ratio
poolratio: 0.75 # Ratio for graph pooling.
raw_dataset_path: "../data/TJ-dataset" # Path to raw dataset for parsing if no precache.
pkl_path: "tj.pkl" # Path to hardware graphs for parsing.
embed_dim: 2 # The dimension of graph embeddings.
debug: False # Debug mode.
```
