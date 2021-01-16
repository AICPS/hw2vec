# GNN4IP: IP piracy detection (clone detection) in hardware design
 


# Problem Formulation
In this work, we want to develop a model to detect IP piracy in hardware design. In other word, we want to develop a model to check similarity between two Verilog code and determine if they are for the same hardware design or not. In order to do that, we need to create two batch of samples; clone pair, and non-clone pair. The clone pair is two Verilog code that are similar and represent the same hardware design while the non-clone pair are a pair of two code that are for entirely different designs. We have gathered a dataset of veriog assignments and all samples in a assignments are clone pair while two codes from different assignment are considered as a non-clone pair.

## Directories Structure
ALL data samples are stored in 3 main directories as follow:

GNN4IP/data_raw --> The base Verilog codes that are gathered from variety of sources.

GNN4IP/data_HW  --> The final Verilog codes that are preprocessed and ready to be used by graph generation python code. Preprocessing includes merging the seprate verilog file to one file and resolve all the syntax and parse error.

GNN4IP/data_DFG --> The generated data flow graphs for verilog codes in data_HW directory.

In each of these three main directories, the data samples, which represent the same hardware design, are stored in a directory named after the circuit name. Therefore, the data samples which are in the same dircotry are clone-pair and data samples from seprate directories are non-clone pair.

## Data Processing Pipeline
For each data sample in data_raw,

1. Merge the modules in teh seprate files and creat one .v file for teh sample.

2. Resolve the incompatibility, complexity, and syntax errors and make sure the final verilog could can be used with graph_generation.py without any error. Save this processed verilog codes in data_HW.

3. Use graph_generation.py to generate the data flow graph for teh verilog code in data_HW and save the generated graph in the coresponding directory in data_DFG.

4. Repaet it for all samples for each hardware design and then go for the next circuit.

## Data Flow Graph and JSON dictionary structure
The structure of the JSON is a dictionary with keys corresponding to every node in the graph. The value associated with each key is a list of edges that are originated from the key nofe. Each edge in the list is represented by a tuple in which the first element is the label of edge and the second item is the destination node. Note that some edges may not have any label. The following dictionary represents the corresponding graph.

```python
{
    "top.led": [
        [
            "",
            "PartSelect"
        ]
    ],
    "PartSelect": [
        [
            "VAR",
            "top_count"
        ],
        [
            "MSB",
            "'d23"
        ],
        [
            "LSB",
            "'d16"
        ]
    ],
    "top_count": [],
    "'d23": [],
    "'d16": []
}
```
![](https://github.com/RozhinYs/RTL2VEC/blob/master/graph_example.png)


# Working Environment
We tested the code under Linux only. To run [Pyverilog](https://github.com/PyHDI/Pyverilog), we use anaconda3 as primary working environment.
```sh
$ conda create --name [your working environment name] python=3.6
$ conda activate [your working environment name]
```

## Requirement for graph generation
The verilog2graph is the set of codes for generating the data-flow graph of the RTL code written in verilog. In order to run the verilog2graph codes, following packages should be installed:
```sh
$ conda install -c conda-forge iverilog
$ conda install graphviz
$ conda install -c alubbock pygraphviz
$ pip install --user pyverilog
$ pip install --user pyunpack
$ pip install --user patool
```

## Requirements for graph neural network model
The rtl2vec is the set of codes for building graph neural networks which classifies the RTL codes to Trojan free and with Trojan based on the graph representation of RTll. In order to run rtl2vec codes, the follow the steps below :
- install CUDA 10.1

- Install pytorch 1.6.0
```sh
conda install pytorch==1.6.0 torchvision==0.7.0 cudatoolkit=10.1 -c pytorch
```

- Ensure the version of pytorch and CUDA 
```sh
$ python -c "import torch; print(torch.__version__)"
>>> 1.6.0

$ python -c "import torch; print(torch.version.cuda)"
>>> 10.1
```

- Install pytorch-geometric (more info [here](https://pytorch-geometric.readthedocs.io/en/latest/notes/installation.html))
```sh
$ python -m pip install torch-scatter==latest+cu101 -f https://pytorch-geometric.com/whl/torch-1.6.0.html
$ python -m pip install torch-sparse==latest+cu101 -f https://pytorch-geometric.com/whl/torch-1.6.0.html
$ python -m pip install torch-cluster==latest+cu101 -f https://pytorch-geometric.com/whl/torch-1.6.0.html
$ python -m pip install torch-spline-conv==latest+cu101 -f https://pytorch-geometric.com/whl/torch-1.6.0.html
$ python -m pip install torch-geometric
```

# Graph Gnereation Phase
## Dataset
We gather varity of verilog code in RTL and generate the netlist of them. We use this collection as our base HW design data base.

## Generate the data flow garph
The generateGraph.py reads verilog codes as input and generate the corresponding data-flow graphs. It draws the graphs in pdf format and save nodes, edges, root nodes and graph strusture in seprate JSON files.
Running the command below, it reads the FILENAME and save the graphs in the current directory.
```sh
$ python generateGraph.py FILENAME
```
If the input file is not specified like running the command below, in a loop it reads all the data in the "../data_hw/" and save the graphs in the "../data_DFG/".
```sh
$ python generateGraph.py
```

## Transform data flow graph from Json to PKL
The 0_run_json2graph.py reads data-flow graphs stored as separate JSON files generated in the previous step, gather information needed, and store all information required in learning steps as one single PKL file.
Running the command below, it reads all graphs in the designated directory, and graphs in the same sub-directory will be considered as similar graphs.
```sh
$ python 0_run_json2graph.py --raw_dataset_path PATH_TO_DIR
```
If the input file is not spceified, it will read data from "../data/data_DFG/RTL/"
```sh
$ python 0_run_json2graph.py
```
