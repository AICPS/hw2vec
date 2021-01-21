# Hardware Trojan Detection in RTL/Gate-Level Netlist using Graph Learning  


General Pipeline Architecture is shown as below:

![](https://github.com/louisccc/hard_hard_graph/blob/master/figures/pipeline.png?raw=true)

It mainly includes two steps:
- verilog2graph: Generate the data-flow graph of RTL/gate-level netlist. We leverage [Pyverilog](https://github.com/PyHDI/Pyverilog) from PyHDI as part of our graph extraction pipeline. It has capabilities to extract the data-flow and control-flow graphs from verilog code.
- rtl2vec: Graph learning. 



# Working Environment
To run [Pyverilog](https://github.com/PyHDI/Pyverilog), we use anaconda3 as primary working environment.
```sh
$ conda create --name [your working environment name] python=3.6
$ conda activate [your working environment name]
```

## Requirement for verilog2graph
The verilog2graph is the set of codes for generating the data-flow graph of the RTL code written in verilog. In order to run the verilog2graph codes, following packages should be installed:
```sh
$ conda install -c conda-forge iverilog
$ conda install graphviz
$ conda install -c alubbock pygraphviz
$ pip install pyverilog
$ pip install pyunpack
$ pip install patool
```

## Requirements for rtl2vec
The rtl2vec is the set of codes for building graph neural networks which classifies the RTL codes to Trojan free and with Trojan based on the graph representation of RTll. In order to run rtl2vec codes, the follow the steps below :
- install CUDA 10.2

- Install pytorch 1.5
```sh
$ conda install pytorch torchvision cudatoolkit=10.2 -c pytorch
```

- Ensure the version of pytorch and CUDA 
```sh
$ python -c "import torch; print(torch.__version__)"
>>> 1.5.0

$ python -c "import torch; print(torch.version.cuda)"
>>> 10.2
```

- Install pytorch-geometric (more info [here](https://pytorch-geometric.readthedocs.io/en/latest/notes/installation.html))
```sh
$ pip install torch-scatter==latest+cu102 -f https://pytorch-geometric.com/whl/torch-1.5.0.html
$ pip install torch-sparse==latest+cu102 -f https://pytorch-geometric.com/whl/torch-1.5.0.html
$ pip install torch-cluster==latest+cu102 -f https://pytorch-geometric.com/whl/torch-1.5.0.html
$ pip install torch-spline-conv==latest+cu102 -f https://pytorch-geometric.com/whl/torch-1.5.0.html
$ pip install torch-geometric
```

# verilog2graph
## Dataset
We obtain the dataset from a famous trojan [benchmark](http://www.trust-hub.org/benchmarks/trojan). We manually downloaded all the avaialable dataset in RTL level into [./input](https://github.com/louisccc/hard_hard_graph/tree/master/input) folder. 
Running the command
```python
python combine_dataset.py
```
will extract all data instances in the folder and store them into one combined dataset folder.

## Generate the graphs
The generateGraph.py reads verilog codes as input and generate the corresponding data-flow graphs. It draws the graphs in pdf format and save nodes, edges, root nodes and graph strusture in seprate JSON files.
Running the command below, it reads the FILENAME and save the graphs in teh current directory.
```sh
$ python generateGraph.py FILENAME
```
If the input fiel is not specified like running the command below, in a loop it reads all the data in the "../data/data_ready_FIXED/" and save the graphs in the "../graphs/data_ready_FIXED/".
```sh
$ python generateGraph.py
```


## Graph and JSON dictionary structure
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

# rtl2vec
Set the parametrs.
```sh
$ python trojan_classificatio.py -h 
>>>
usage: trojan_classification.py [-h] [--input_path INPUT_PATH]
                                [--learning_rate LEARNING_RATE] [--seed SEED]
                                [--epochs EPOCHS]
                                [--weight_decay WEIGHT_DECAY]
                                [--hidden HIDDEN] [--dropout DROPOUT]
                                [--nclass NCLASS] [--recursive RECURSIVE]
                                [--batch_size BATCH_SIZE] [--device DEVICE]
                                [--model MODEL] [--num_layers NUM_LAYERS]
                                [--hidden_dim HIDDEN_DIM]
                                [--pooling_type POOLING_TYPE]
                                [--readout_type READOUT_TYPE] [--nocache]

The parameters for training the scene graph using GCN.

optional arguments:
  -h, --help            show this help message and exit
  --input_path INPUT_PATH
                        Path to code directory.
  --learning_rate LEARNING_RATE
                        The initial learning rate for GCN.
  --seed SEED           Random seed.
  --epochs EPOCHS       Number of epochs to train.
  --weight_decay WEIGHT_DECAY
                        Weight decay (L2 loss on parameters).
  --hidden HIDDEN       Number of hidden units.
  --dropout DROPOUT     Dropout rate (1 - keep probability).
  --nclass NCLASS       The number of classes for node.
  --recursive RECURSIVE
                        Recursive loading scenegraphs
  --batch_size BATCH_SIZE
                        Number of graphs in a batch.
  --device DEVICE       The device to run on models (cuda or cpu) cpu in
                        default.
  --model MODEL         Model to be used intrinsically.
  --num_layers NUM_LAYERS
                        Number of layers in the neural network.
  --hidden_dim HIDDEN_DIM
                        Hidden dimension in GIN.
  --pooling_type POOLING_TYPE
                        Graph pooling type.
  --readout_type READOUT_TYPE
                        Readout type.
  --nocache             Don't use cached version of dataset.
```

Run the code:
```sh
$ python trojan_classification.py --input_path [the root path for the ready fixed folder]
```

# Directories structure
./ > README, and Requirements : how to install requirement, how to run the code and the functionality of each code.

./src > the verilog2graph which compromises the graph conversion codes + the code used for changing Verilog files such as flatten.py, and removeunderscore.py

./rtl2vec > the rtl2vec code.

./data_raw > all Verilog datasets.

./data_raw/trusthub > original trusthub benchmarks.

./data_raw/data_ready_FIXED > the processed verilog files that are ready to be used by graph converting code.

./data_graphs > all graphs and JSON files (The same naming and directories as the dataset are used. for example ./graphs/AES_ready/ )
