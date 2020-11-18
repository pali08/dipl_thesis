import os

from src.downloader_ftp_difference_files import DifferenceFilesDownloader
from src.generate_filepaths import FilepathGenerator
from src.global_constants_and_functions import OBSOLETE, MODIFIED, ADDED, LATEST_SUFFIX, METADATA_FILES_PATH, \
    VDB_JSON_UNIVERSAL_NAME, remove_custom


def download_metadata():
    for i in [ADDED, MODIFIED, OBSOLETE]:
        DifferenceFilesDownloader(i).get_file()


def get_lists_of_changed_molecules():
    lists_of_changed_molecules = []
    for i in [ADDED, MODIFIED, OBSOLETE]:
        with open(os.path.join(METADATA_FILES_PATH, i, LATEST_SUFFIX), mode='r', encoding='utf-8') as changelist:
            files = [i.strip() for i in changelist.readlines()]
            lists_of_changed_molecules.append(files)


def get_filepaths_from_list(molecules_list, *filepaths):
    """
    :param molecules_list: list of strings - 4 number code of molecules
    :param filepaths: general paths to pdb, vdb, xml validation and rest file - rest file must have 3 subfolders -
    assembly, molecules and summary
    :return:
    """
    filepaths_individual_molecules = []
    for molecule in molecules_list:
        filepaths_individual_molecules.append(FilepathGenerator(molecule, *filepaths).get_all_paths())
    return filepaths_individual_molecules


def remove_files(list_of_files_to_remove):
    """
    removes file if file is mmcif, xml, or one of rest json files
    in case of result.json (vdb file), function removed folder (with name of molecule code) and file
    :param list_of_files_to_remove: FLAT list of files
    TODO: check if flat list is better than list of lists with individual molecules.
    TODO: Handle if file does not exists
    :return
    """
    for file in list_of_files_to_remove:
        if os.path.basename(file).lower() == VDB_JSON_UNIVERSAL_NAME:
            remove_custom(os.path.dirname(file))
        else:
            os.remove(file)


def download_files():
    pass


def update_added():
    pass


def update_modified():
    pass


def update_obsolete():
    pass


def update_csv():
    pass


def update():
    pass


if __name__ == '__main__':
    update()
