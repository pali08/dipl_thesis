import csv
import io
import os
import shutil
import unittest
import sys
from shutil import copy2

from src.generate_filepaths import FilepathGenerator

sys.path.append('..')
from src.global_constants_and_functions import ADDED, LATEST_SUFFIX, METADATA_FILES_PATH, MODIFIED, OBSOLETE, \
    remove_custom, DirOrFileNotFoundError, A_M_O_FILENAME
from src.exe_update_files import get_lists_of_changed_molecules, get_filepaths_from_list, remove_files, \
    download_metadata

INPUT_DATA_PATH = os.path.join('.', 'input_data_3')
INPUT_DATA_PATH_BCK = os.path.join('.', 'input_data_3_backup')
INPUT_DATA_PATH_BEFORE = os.path.join('.', 'input_data_3_before')
INPUT_DATA_PATH_EXECUTED_UPDATE_FILES_PY = os.path.join('..', 'unittests', 'input_data_3')
pdb_filepath = os.path.join(INPUT_DATA_PATH_EXECUTED_UPDATE_FILES_PY, 'pdb')
vdb_filepath = os.path.join(INPUT_DATA_PATH_EXECUTED_UPDATE_FILES_PY, 'vdb')
xml_filepath = os.path.join(INPUT_DATA_PATH_EXECUTED_UPDATE_FILES_PY, 'valid_xml')
rest_filepath = os.path.join(INPUT_DATA_PATH_EXECUTED_UPDATE_FILES_PY, 'rest')
ligandstats_filepath = os.path.join(INPUT_DATA_PATH_EXECUTED_UPDATE_FILES_PY, 'ligandStats.csv')
datacsv_filepath = os.path.join(INPUT_DATA_PATH_EXECUTED_UPDATE_FILES_PY, 'data.csv')
update_files_exe_py = os.path.join('..', 'src', 'exe_update_files.py')
metadata_file_path = os.path.join('..', 'metadata_files')


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
        print('input_data_3_bck does not exist, input_data_3 will not be removed')


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
    if os.path.exists(os.path.join(METADATA_FILES_PATH, A_M_O_FILENAME)):
        os.remove(os.path.join(METADATA_FILES_PATH, A_M_O_FILENAME))


def create_data_for_testing():
    try:
        amo_path = [os.path.join(metadata_file_path, ADDED + LATEST_SUFFIX),
                    os.path.join(metadata_file_path, MODIFIED + LATEST_SUFFIX),
                    os.path.join(metadata_file_path, OBSOLETE + LATEST_SUFFIX)]
        # download all
        with open(amo_path[0], 'r') as amo:
            molecules_added = [j.strip() for j in amo.readlines()]
        with open(amo_path[1], 'r') as amo:
            molecules_modified = [j.strip() for j in amo.readlines()]
        with open(amo_path[2], 'r') as amo:
            molecules_obsolete = [j.strip() for j in amo.readlines()]
        with open(datacsv_filepath, mode='r', encoding='utf-8') as csvfile:
            loaded_csv_list = list(csv.reader(csvfile, delimiter=';'))
        os.remove(datacsv_filepath)
        nans = ['nan' for i in range(0, 89)]
        modified_obsolete = [[i] + nans for i in molecules_modified + molecules_obsolete]
        with open(datacsv_filepath, mode='w', encoding='utf-8') as csv_file_write:
            csv_writer = csv.writer(csv_file_write, delimiter=';', lineterminator='\n')
            csv_writer.writerows(loaded_csv_list)
            csv_writer.writerows(modified_obsolete)
        filepaths = []
        for i in molecules_modified + molecules_obsolete:
            filepaths.extend(
                FilepathGenerator(i, pdb_filepath, vdb_filepath, xml_filepath, rest_filepath).get_all_paths())
        for i in filepaths:
            # print(i)
            from pathlib import Path
            Path(os.path.dirname(i)).mkdir(parents=True, exist_ok=True)
            with open(i, mode='w+', encoding='utf-8') as almost_empty_file:
                almost_empty_file.write('foobar')
    except Exception as e:
        delete_metadata()
        if os.path.exists(os.path.join(METADATA_FILES_PATH, A_M_O_FILENAME)):
            os.remove(os.path.join(METADATA_FILES_PATH, A_M_O_FILENAME))
        restore()
        print(str(type(e)))
        print(str(e))
        sys.exit('Unable to download metadata (added.latest, modified.latest, obsolete.latest). Please try again later')


# if sys.argv[1] == 'backup':
#     backup()
# elif sys.argv[1] == 'restore':
#     restore()
# else:
#     print('Argument must be \'backup\' or \'restore\'.')

# backup()
# download_metadata()
# create_data_for_testing()

if __name__ == '__main__':
    # os.chdir(src)
    exe_path = os.path.join('..', 'src', 'exe_update_files.py')
    backup()
    download_metadata()
    create_data_for_testing()
    delete_metadata()
    shutil.copytree(INPUT_DATA_PATH, INPUT_DATA_PATH_BEFORE)
    os.system(
        '{} {} {} {} {} {} {} {} {}'.format('python', exe_path, pdb_filepath, vdb_filepath, xml_filepath,
                                            rest_filepath, ligandstats_filepath, datacsv_filepath,
                                            '--cpu_count 2'))
    # restore()
    input(
        'Paused. Compare {} and {} and check that files were added/deleted/modified. '
        'Then continue with pressing any key'.format(INPUT_DATA_PATH, INPUT_DATA_PATH_BEFORE))
    delete_metadata()
    remove_custom(INPUT_DATA_PATH)
    remove_custom(INPUT_DATA_PATH_BEFORE)
    shutil.copytree(INPUT_DATA_PATH_BCK, INPUT_DATA_PATH)
    remove_custom(INPUT_DATA_PATH_BCK)
