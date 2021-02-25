# HW2Vec: A Python-based Hardware Designs Embedding Tool for Hardware Security
[![Build Status](https://travis-ci.com/louisccc/hw2vec.svg?branch=master)](https://travis-ci.com/github/louisccc/hw2vec) [![GitHub license](https://img.shields.io/github/license/Sujit-O/pykg2vec.svg)](https://github.com/Sujit-O/pykg2vec/blob/master/LICENSE)

HW2vec contains the tools and source code we used for our previous research projects. In this repo, we collect our previous codebases and standardize the pipeline and use-cases and hope that this tool can be helpful in researchers in hardware security field and drive the research progress in this field. The two previous research projects are 1) Hardware Trojan Detection in RTL/Gate-Level Netlist using Graph Learning (GNN4TJ), 2) IP Piracy Detection in hardware design using graph learning (GNN4IP), published in DATE2021 and DAC2021, respectively. In this repo, we leverage [Pyverilog](https://github.com/PyHDI/Pyverilog) from PyHDI as part of our graph extraction pipeline.

The architecture of hw2vec is as follows:
- **hw2vec/hw2graph.py**: code for generating graph objects from hardware design.
- **hw2vec/graph2vec**: code of graph training trainers and models.
- Use case examples are stored in examples folder:<br>
  - **examples/gnn4ip_netlist.py**: gnn4ip script running on netlist dataset.
  - **examples/gnn4ip_RTL.py**: gnn4ip script running on RTL dataset.
  - **examples/gnn4tj.py**: gnn4tj script running on dataset which has not been splitted into training and testing dataset.
  - **examples/gnn4tj_presplit.py**: gnn4tj script running on dataset which has been splitted into training and testing dataset.

General Pipeline Architecture is shown as below:
![](https://github.com/louisccc/hw2vec/blob/master/figures/pipeline.png?raw=true)

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
## GNN4TJ: Hardware Trojan Detection in RTL/Gate-Level Netlist using Graph Learning
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
