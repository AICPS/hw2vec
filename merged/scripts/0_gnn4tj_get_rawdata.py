'''
    copy from combine_dataset.py
'''

from typing import Any, Union

from pyunpack import Archive
from pathlib import Path
from glob import glob

def extract_zip(path, saved_path):
    print(glob(fr'{path}/*.zip'))
    for zip_file in glob(fr'{path}/*.zip'):
        print(zip_file)
        Archive(zip_file).extractall(saved_path)

def extract_rar(path, saved_path):
    for rar_file in glob(fr'{path}/*.rar'):
        print(rar_file)
        Archive(rar_file).extractall(saved_path)


if __name__ == "__main__": 
    # sample decompressing the zip and rar
    # Archive(r'./Datasets/trusthub/AES-T100.zip').extractall(r'./combine')
    # Archive(r'./trusthub/b19-T300.rar').extractall(r'./combine')

    working_directory = Path(__file__).parent
    
    # create final folder in the first place.
    target_folder: Union[Path, Any] = working_directory / Path(r'Datasets/trusthub_processed/')
    print(target_folder)
    target_folder.mkdir(exist_ok=True)

    # extract all data from trust-hub.org to one target folder.
    print(r'./Datasets/trusthub')
    extract_zip(working_directory / Path(r'Datasets/trusthub'), str(target_folder))
    extract_rar(working_directory / Path(r'Datasets/trusthub/'), str(target_folder))

    # usage for now: python combine_dataset.py
    # should be changing to argument based at some points.
    
    