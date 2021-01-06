import io
import os
import shutil
import unittest
import sys
from shutil import copy2

sys.path.append('..')
from src.global_constants_and_functions import ADDED, LATEST_SUFFIX, METADATA_FILES_PATH, MODIFIED, OBSOLETE, \
    remove_custom, DirOrFileNotFoundError
from src.exe_update_files import get_lists_of_changed_molecules, get_filepaths_from_list, remove_files

INPUT_DATA_PATH = os.path.join('.', 'input_data_2')
INPUT_DATA_PATH_BCK = os.path.join('.', 'input_data_2_backup')
INPUT_DATA_PATH_EXECUTED_UPDATE_FILES_PY = os.path.join('..', 'unittests', 'input_data_2')
pdb_filepath = os.path.join(INPUT_DATA_PATH_EXECUTED_UPDATE_FILES_PY, 'pdb')
vdb_filepath = os.path.join(INPUT_DATA_PATH_EXECUTED_UPDATE_FILES_PY, 'vdb')
xml_filepath = os.path.join(INPUT_DATA_PATH_EXECUTED_UPDATE_FILES_PY, 'valid_xml')
rest_filepath = os.path.join(INPUT_DATA_PATH_EXECUTED_UPDATE_FILES_PY, 'rest')
ligandstats_filepath = os.path.join(INPUT_DATA_PATH_EXECUTED_UPDATE_FILES_PY, 'ligandStats.csv')
datacsv_filepath = os.path.join(INPUT_DATA_PATH_EXECUTED_UPDATE_FILES_PY, 'data.csv')
update_files_exe_py = os.path.join('..', 'src', 'exe_update_files.py')


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


def copy_metadata():
    shutil.copyfile(os.path.join(INPUT_DATA_PATH, ADDED + LATEST_SUFFIX),
                    os.path.join('..', 'metadata_files', ADDED + LATEST_SUFFIX))
    shutil.copyfile(os.path.join(INPUT_DATA_PATH, MODIFIED + LATEST_SUFFIX),
                    os.path.join('..', 'metadata_files', MODIFIED + LATEST_SUFFIX))
    shutil.copyfile(os.path.join(INPUT_DATA_PATH, OBSOLETE + LATEST_SUFFIX),
                    os.path.join('..', 'metadata_files', OBSOLETE + LATEST_SUFFIX))


def delete_metadata():
    remove_custom(os.path.join('..', 'metadata_files', ADDED + LATEST_SUFFIX))
    remove_custom(os.path.join('..', 'metadata_files', MODIFIED + LATEST_SUFFIX))
    remove_custom(os.path.join('..', 'metadata_files', OBSOLETE + LATEST_SUFFIX))


# if sys.argv[1] == 'backup':
#     backup()
# elif sys.argv[1] == 'restore':
#     restore()
# else:
#     print('Argument must be \'backup\' or \'restore\'.')

if __name__ == '__main__':
    # os.chdir(src)
    exe_path = os.path.join('..', 'src', 'exe_update_files.py')
    backup()
    copy_metadata()
    print(rest_filepath)
    os.system(
        '{} {} {} {} {} {} {} {} {}'.format('python', exe_path, pdb_filepath, vdb_filepath, xml_filepath,
                                            rest_filepath, ligandstats_filepath, datacsv_filepath,
                                            '--cpu_count 2'))
    # restore()
    delete_metadata()
