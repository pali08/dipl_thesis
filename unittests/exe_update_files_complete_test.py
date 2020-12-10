import io
import os
import shutil
import unittest
import sys
from shutil import copy2

from src.global_constants_and_functions import ADDED, LATEST_SUFFIX, METADATA_FILES_PATH, MODIFIED, OBSOLETE, \
    remove_custom, DirOrFileNotFoundError

sys.path.append('..')
from src.exe_update_files import get_lists_of_changed_molecules, get_filepaths_from_list, remove_files

INPUT_DATA_PATH = os.path.join('.', 'input_data_2')
INPUT_DATA_PATH_BCK = os.path.join('.', 'input_data_2_backup')
pdb_filepath = os.path.join('.', 'input_data_2', 'pdb')
vdb_filepath = os.path.join('.', 'input_data_2', 'vdb')
xml_filepath = os.path.join('.', 'input_data_2', 'valid_xml')
rest_filepath = os.path.join('.', 'input_data_2', 'rest')
ligandstats_filepath = os.path.join('.', 'input_data_2', 'ligandStats.csv')
datacsv_filepath = os.path.join('.', 'input_data_2', 'data.csv')


def backup():
    """
    backup files before
    :return:
    """
    shutil.copytree(INPUT_DATA_PATH, INPUT_DATA_PATH_BCK)


def restore():
    """
    restore files after test
    :return:
    """
    if os.path.exists(os.path.join(INPUT_DATA_PATH_BCK)):
        remove_custom(os.path.join(INPUT_DATA_PATH))
        os.rename(INPUT_DATA_PATH_BCK, INPUT_DATA_PATH)
    else:
        print('input_data_2_bck does not exist, input_data_2 will not be removed')


if __name__ == '__main__':
    backup()
    os.system(
        '../src/exe_update_files.py ' + pdb_filepath + ' ' + vdb_filepath + ' ' + xml_filepath + ' ' + rest_filepath +
        ' ' + ligandstats_filepath + ' ' + datacsv_filepath + ' ' + '2')
    restore()