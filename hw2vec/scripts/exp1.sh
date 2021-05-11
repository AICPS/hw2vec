# echo python graph_processer.py --yaml_path ../hw2vec/configs/AST-IP-NetList.yaml
# python graph_processer.py --yaml_path ../hw2vec/configs/AST-IP-NetList.yaml

# echo python graph_processer.py --yaml_path ../hw2vec/configs/AST-IP-RTL.yaml
# python graph_processer.py --yaml_path ../hw2vec/configs/AST-IP-RTL.yaml

# echo python graph_processer.py --yaml_path ../hw2vec/configs/AST-TJ-NetList.yaml
# python graph_processer.py --yaml_path ../hw2vec/configs/AST-TJ-NetList.yaml

echo python graph_processer.py --yaml_path ../hw2vec/configs/AST-TJ-RTL.yaml
python graph_processer.py --yaml_path ../hw2vec/configs/AST-TJ-RTL.yaml
mv process.txt AST-TJ-RTL-process.txt

# echo python graph_processer.py --yaml_path ../hw2vec/configs/DFG-IP-NetList.yaml
# python graph_processer.py --yaml_path ../hw2vec/configs/DFG-IP-NetList.yaml

# echo python graph_processer.py --yaml_path ../hw2vec/configs/DFG-IP-RTL.yaml
# python graph_processer.py --yaml_path ../hw2vec/configs/DFG-IP-RTL.yaml

# echo python graph_processer.py --yaml_path ../hw2vec/configs/DFG-TJ-NetList.yaml
# python graph_processer.py --yaml_path ../hw2vec/configs/DFG-TJ-NetList.yaml

echo python graph_processer.py --yaml_path ../hw2vec/configs/DFG-TJ-RTL.yaml
python graph_processer.py --yaml_path ../hw2vec/configs/DFG-TJ-RTL.yaml
mv process.txt DFG-TJ-RTL-process.txt