import os, sys
sys.path.append(os.path.dirname(sys.path[0]))
import warnings
warnings.filterwarnings('ignore')

from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from hw2vec.graph2vec.trainers import *
from hw2vec.hw2graph import *
import itertools
from hw2vec.graph2vec.config import *


class ConfigHelper:
    '''Configuration and Argument Parser for script to train the IP piracy detection.'''
    def __init__(self, args_parsed):
        for arg_name in vars(args_parsed):
            self.__dict__[arg_name] = getattr(args_parsed, arg_name)
        # self.raw_dataset_path = Path(self.raw_dataset_path).resolve()
        # self.pkl_path = Path(self.pkl_path).resolve()
        self.config_path = Path(self.config_path).resolve()


# # test cases for netlist
# def test_c432(trainer):
#     '''
#     comparing c432 with obfuscated c432 variants one by one.
#     '''
#     c432_group  = ["C432/c432-BE280","C432/c432-CS320","C432/c432-CS640","C432/c432-CS1280","C432/c432-CY290","C432/c432-CY530",\
#                     "C432/c432-CY1020","C432/c432-CY2000","C432/c432-NC1400","C432/c432-NC1720","C432/c432-NC2360","C432/c432-NR1400",
#                     "C432/c432-NR1720","C432/c432-NR2360","C432/c432-NS1400","C432/c432-NS1720","C432/c432-NS2360","C432/c432-RN320",
#                     "C432/c432-RN640", "C432/c432-RN1280", "C432/c432-SL320", "C432/c432-SL640", "C432/c432-SL1280"]
#     pprint.pprint(trainer.get_similarity_groups(["C432/c432"], c432_group))


# def test_c499(trainer):
#     '''
#     comparing c499 with obfuscated c499 variants one by one.
#     '''
#     c499_group  = ["C499/c499-CS320","C499/c499-CS640","C499/c499-CS1280","C499/c499-CY270","C499/c499-CY520",\
#                    "C499/c499-CY1040","C499/c499-CY2060","C499/c499-NC1550","C499/c499-NC1870","C499/c499-NC2510","C499/c499-NR1550",
#                    "C499/c499-NR1870","C499/c499-NR2510","C499/c499-NS1550","C499/c499-NS1870","C499/c499-NS2510","C499/c499-RN320",
#                    "C499/c499-RN640", "C499/c499-RN1280", "C499/c499-SL320", "C499/c499-SL640", "C499/c499-SL1280"]
#     pprint.pprint(trainer.get_similarity_groups(["C499/c499"], c499_group))


# def test_c880(trainer):
#     '''
#     comparing c880 with obfuscated c880 variants one by one.
#     '''
#     c880_group  = ["C880/c880-CS320","C880/c880-CS640","C880/c880-CS1280","C880/c880-CS2560", "C880/c880-CY310","C880/c880-CY590",\
#                    "C880/c880-CY1070","C880/c880-CY2030","C880/c880-NC2120","C880/c880-NC2440","C880/c880-NC3080","C880/c880-NC4360",\
#                    "C880/c880-NR2120", "C880/c880-NR2440","C880/c880-NR3080", "C880/c880-NR4360","C880/c880-NS2120","C880/c880-NS2440","C880/c880-NS3080","C880/c880-NS4360",\
#                    "C880/c880-RN320", "C880/c880-RN640", "C880/c880-RN1280", "C880/c880-RN2560", "C880/c880-SL320", "C880/c880-SL640", "C880/c880-SL1280", "C880/c880-SL2560"]
#     pprint.pprint(trainer.get_similarity_groups(["C880/c880"], c880_group))


# def test_c1355(trainer):
#     '''
#     comparing c1355 with obfuscated c1355 variants one by one.
#     '''
#     c1355_group = ["c1355/c1355-CS1280","c1355/c1355-NC1550","c1355/c1355-NC1870","c1355/c1355-NC2510","c1355/c1355-NR1550","c1355/c1355-NR1870",\
#                     "c1355/c1355-NR2510","c1355/c1355-NS1550","c1355/c1355-NS1870","c1355/c1355-NS2510","c1355/c1355-RN1280","c1355/c1355-RN2560",
#                     "c1355/c1355-RN320","c1355/c1355-RN640","c1355/c1355-SL1280","c1355/c1355-SL2560","c1355/c1355-SL320","c1355/c1355-SL640"]
#     pprint.pprint(trainer.get_similarity_groups(["C1355/c1355"], c1355_group))


# def test_c1908(trainer):
#     '''
#     comparing c1908 with obfuscated c1908 variants one by one.
#     '''
#     c1908_group = ["C1908/c1908-CS320","C1908/c1908-CS640","C1908/c1908-CS1280","C1908/c1908-CY270","C1908/c1908-CY480",\
#                    "C1908/c1908-CY990","C1908/c1908-NC1310","C1908/c1908-NC1630","C1908/c1908-NC2270",\
#                    "C1908/c1908-NR1310", "C1908/c1908-NR1630","C1908/c1908-NR2270", "C1908/c1908-NS1310","C1908/c1908-NS1630","C1908/c1908-NS2270",\
#                    "C1908/c1908-RN320", "C1908/c1908-RN640", "C1908/c1908-RN1280", "C1908/c1908-SL320", "C1908/c1908-SL640", "C1908/c1908-SL1280"]
#     pprint.pprint(trainer.get_similarity_groups(["C1908/c1908"], c1908_group))


# def test_c6288(trainer):
#     '''
#     comparing c6288 with obfuscated c6288 variants one by one.
#     '''
#     c6288_group = ["C6288/c6288-CS320","C6288/c6288-CS640","C6288/c6288-CS1280","C6288/c6288-CS2560",\
#                    "C6288/c6288-NC1280","C6288/c6288-NC1600","C6288/c6288-NC2240", "C6288/c6288-NC3520",\
#                    "C6288/c6288-NR1280", "C6288/c6288-NR1600","C6288/c6288-NR2240", "C6288/c6288-NR3520",\
#                    "C6288/c6288-NS1280","C6288/c6288-NS1600","C6288/c6288-NS2240","C6288/c6288-NS3520",\
#                    "C6288/c6288-RN320", "C6288/c6288-RN640", "C6288/c6288-RN1280", "C6288/c6288-RN2560",\
#                    "C6288/c6288-SL320", "C6288/c6288-SL640", "C6288/c6288-SL1280","C6288/c6288-SL2560"]
#     pprint.pprint(trainer.get_similarity_groups(["C6288/c6288"], c6288_group))


# def test_self_comparisons(trainer):
#     pprint.pprint(trainer.get_similarity("C432/c432", "C432/c432"))
#     pprint.pprint(trainer.get_similarity("C499/c499", "C499/c499"))
#     pprint.pprint(trainer.get_similarity("C880/c880", "C880/c880"))
#     pprint.pprint(trainer.get_similarity("C1355/c1355", "C1355/c1355"))
#     pprint.pprint(trainer.get_similarity("C1908/c1908", "C1908/c1908"))
#     pprint.pprint(trainer.get_similarity("C6288/c6288", "C6288/c6288"))

# def test_diff_comparisons(trainer):
#     module_list = ["C432/c432", "C499/c499", "C880/c880", "C1355/c1355", "C1908/c1908", "C6288/c6288"]
#     comp_list = list(itertools.combinations(module_list, 2))
#     for pairs in comp_list:
#         pprint.pprint(trainer.get_similarity(pairs[0], pairs[1]))


# # test cases for alu
# def test_mips_alu(trainer):
#     mips_str = "mips_pipeline/mips_pipeline ("
#     alu_str = "ALU/ALU_"
#     mips_list = []
#     alu_list = []
#     for data in trainer.data:
#         if mips_str in data[2]:
#             mips_list.append(data[2])
#         elif alu_str in data[2]:
#             alu_list.append(data[2])
#     for mips in mips_list:
#         for alu in alu_list:
#             pprint.pprint(trainer.get_similarity(mips, alu))

# def test_diff_rtl(traner):
#     pass

# def test_same_rtl_sum(input_list):
#     similarity = 0
#     comp_list = list(itertools.combinations(input_list, 2))
#     for pairs in comp_list:
#         similarity += trainer.get_similarity(pairs[0], pairs[1])
#     # calculate average
#     similarity = similarity / len(comp_list)
#     print(similarity)
#     return similarity

# def test_same_rtl(trainer):
#     mips_pipe_list = []
#     mips_single_list = []
#     mips_multi_list = []
#     fp_adder_list = []
#     graycode_list = []
#     adder4bit_list = []
#     counter_list = []
#     for data in trainer.data:
#         if "mips_pipeline (" in data[2]:
#             mips_pipe_list.append(data[2])
#         elif "mips_single_cycle" in data[2]:
#             mips_single_list.append(data[2])
#         elif "mips_multi_cycle" in data[2]:
#             mips_multi_list.append(data[2])
#         elif "fp_adder" in data[2]:
#             fp_adder_list.append(data[2])
#         elif "graycode" in data[2]:
#             graycode_list.append(data[2])
#         elif "adder4bit" in data[2]:
#             adder4bit_list.append(data[2])
#         elif "counter_" in data[2]:
#             counter_list.append(data[2])

#     test_same_rtl_sum(mips_pipe_list)
#     test_same_rtl_sum(mips_single_list)
#     test_same_rtl_sum(mips_multi_list)
#     test_same_rtl_sum(fp_adder_list)
#     test_same_rtl_sum(graycode_list)
#     test_same_rtl_sum(adder4bit_list)
#     test_same_rtl_sum(counter_list)




if __name__ == "__main__":
    parser = ArgumentParser(description="scripts for generating datasets", formatter_class=RawTextHelpFormatter)
    parser.add_argument('--config_path', default='./configs/config_ip.yaml', help='path to the config file.')
    # parser.add_argument('--input_path', type=str, default="../input/synthesis_data/lane-change/", help="Path to code directory.")
    # parser.add_argument('--learning_rate', default=0.001, type=float, help='The initial learning rate for GCN.')
    # parser.add_argument('--seed', type=int, default=random.randint(0,2**32), help='Random seed.')
    # parser.add_argument('--epochs', type=int, default=200, help='Number of epochs to train.')
    # parser.add_argument('--weight_decay', type=float, default=5e-4, help='Weight decay (L2 loss on parameters).')
    # parser.add_argument('--hidden', type=int, default=200, help='Number of hidden units.')
    # parser.add_argument('--dropout', type=float, default=0.5, help='Dropout rate (1 - keep probability).')
    # parser.add_argument('--embed_dim', type=int, default=32, help="The dimension of graph embeddings.")
    # parser.add_argument('--batch_size', type=int, default=4, help='Number of graphs in a batch.')
    # parser.add_argument('--device', type=str, default="cpu", help='The device to run on models (cuda or cpu) cpu in default.')
    # parser.add_argument('--model', type=str, default="gcn", help="Model to be used intrinsically.")
    # parser.add_argument('--num_layers', type=int, default=5, help="Number of layers in the neural network.")
    # parser.add_argument('--test_step', type=int, default=10, help="The interval between mini evaluation along the training process.")
    # parser.add_argument('--pooling_type', type=str, default="sagpool", help="Graph pooling type.")
    # parser.add_argument('--readout_type', type=str, default="max", help="Readout type.")
    # parser.add_argument('--splitted', type=bool, default=False, help="Indicating whether the target path has been splitted.")
    # parser.add_argument('--ratio', type=float, default=0.8, help="Dataset splitting ratio")
    # parser.add_argument('--poolratio', type=float, default=0.75, help="Ratio for graph pooling.")
    # parser.add_argument('--debug', type=bool, default=False, help="Train on all pairs in debug mode.")
    # parser.add_argument('--raw_dataset_path', type=str, default='../data/IP-datasets/data_DFG/', help="Path to raw dataset for parsing if no precache.")
    # parser.add_argument('--pkl_path', type=str, default='./dataset_rtl.pkl', help="Path to hardware graphs for parsing.")
    # parser.add_argument('--dataset_name', type=str, default='RTL', help="name of hardware design languages." )
    # parser.add_argument('--debug', type=lambda x: (str(x).lower() == 'true'), default=True, help='debug mode.')

    # args_parsed = parser.parse_args(sys.argv[1:])
    # cfg = Config(args_parsed)
    args_parsed = parser.parse_args(sys.argv[1:])
    cfg_helper = ConfigHelper(args_parsed)

    cfg = Config(cfg_helper.config_path)

    '''
        Commands for running the experiments:
            Exp 1: python .\gnn4ip_RTL.py --device cuda --raw_dataset_path ..\data\IP-datasets\data_DFG --pkl_path gnn4ipnetlist.pkl

    '''

    SIMILAR = 1
    DISSIMILAR = -1
    
    if cfg.pkl_path.exists() is False:
        dataset = JsonGraphParser(cfg)
        dataset.read_node_labels("DFG")
            
        trunk = []
        # import pdb; pdb.set_trace()
        for hw_cat_idx, hardware_root_path in enumerate(glob("%s/**" % str(cfg.raw_dataset_path/"DFG"), recursive=False)):
            # print("parsing %s" %str(hardware_root_path))
            
            for hardware_folder_path in glob("%s/**/topModule.json" % hardware_root_path, recursive=True):
                folder_name = "%s/%s" % (Path(hardware_folder_path).parent.parent.name, Path(hardware_folder_path).parent.name)

                G = dataset.get_graph_from_json(hardware_folder_path)
                X, name2idx, idx2name = dataset.get_node_embeddeings(G)
                edge_idx = dataset.get_edge_idxs(G, name2idx)          
                
                trunk.append(hw_cat_idx)
                dataset.training_graph_count += 1

                dataset.append_graph_data((X, edge_idx, folder_name))

        for idx_graph_a, idx_graph_b in itertools.combinations(range(len(trunk)), 2):
            if trunk[idx_graph_a] == trunk[idx_graph_b]:
                dataset.append_graph_pair((idx_graph_a, idx_graph_b, SIMILAR))
            else:
                dataset.append_graph_pair((idx_graph_a, idx_graph_b, DISSIMILAR))

        dataset.do_pickle_dataset()

    trainer = PairwiseGraphTrainer(cfg)
    trainer.build()
    trainer.train()
    trainer.evaluate(cfg.epochs)    


    # trainer.load_saved_model(path = "./rtl_result/ippiracy")

    # # task 1: check obfuscated cases.
    # test_c432(trainer)
    # test_c499(trainer)
    # test_c880(trainer)
    # test_c1355(trainer)
    # test_c1908(trainer)
    # test_c6288(trainer)
    # test_self_comparisons(trainer)
    # test_diff_comparisons(trainer)

    # # task 2: check RTL cases.
    # test_mips_alu(trainer)
    # test_same_rtl(trainer)
    
    # subgraph_group = ["ALU/ALU_2", "ALU/ALU_3", "ALU/ALU_4", "ALU/ALU_5", "ALU/ALU_6", "ALU/ALU_7", ]
    # mips_pipeline_group = ["mips_pipeline/mips_pipeline (1)", "mips_pipeline/mips_pipeline (100)", "mips_pipeline/mips_pipeline (101)", "mips_pipeline/mips_pipeline (102)", "mips_pipeline/mips_pipeline (103)",
    #         "mips_pipeline/mips_pipeline (104)", "mips_pipeline/mips_pipeline (105)", "mips_pipeline/mips_pipeline (106)", "mips_pipeline/mips_pipeline (107)", "mips_pipeline/mips_pipeline (108)", "mips_pipeline/mips_pipeline (109)"]
    
    # # pprint.pprint(trainer.get_similarity("c1355/c1355", "C1355/c1355-CS1280"))
    # # pprint.pprint(trainer.get_similarity_groups(["c1355/c1355"], comp_group))
    # # pprint.pprint(trainer.get_similarity_groups(mips_pipeline_group, subgraph_group))
    # # trainer.visualize_embeddings("./vis_embedding_rtl")
                
    