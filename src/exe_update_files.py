import csv
import itertools
import os

from src.downloader_ftp_difference_files import DifferenceFilesDownloader
from src.downloader_ftp_pdb import PdbDownloader
from src.downloader_ftp_xml_validation import XmlValidationDownloader
from src.downloader_rest_json_rest import RestJsonDownloaderRest
from src.downloader_rest_json_vdb import RestJsonDownloaderVdb
from src.generate_filepaths import FilepathGenerator
from src.global_constants_and_functions import OBSOLETE, MODIFIED, ADDED, LATEST_SUFFIX, METADATA_FILES_PATH, \
    VDB_JSON_UNIVERSAL_NAME, remove_custom, DirOrFileNotFoundError, SUMMARY_FOLDER, MOLECULES_FOLDER, ASSEMBLY_FOLDER


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
    removes path_to_remove if path_to_remove is mmcif, xml, or one of rest json files
    in case of result.json (vdb file), function removed folder (with name of molecule code) and file
    :param list_of_files_to_remove: FLAT list of files
    :return
    """
    # flatten list:
    list_of_files_to_remove = list(itertools.chain(*list_of_files_to_remove))
    for path_to_remove in list_of_files_to_remove:
        if os.path.basename(path_to_remove).lower() == VDB_JSON_UNIVERSAL_NAME:
            path_to_remove = os.path.dirname(path_to_remove)
        try:
            remove_custom(path_to_remove)
        except DirOrFileNotFoundError:
            print('File or directory {} not exists so not removed.'.format(path_to_remove))


def download_files(molecules, list_of_files_to_download):
    for molecule, filepath in zip(molecules, list_of_files_to_download):
        PdbDownloader(molecule, filepath[0]).get_file()
        RestJsonDownloaderVdb(molecule, filepath[1]).get_file()
        XmlValidationDownloader(molecule, filepath[2]).get_file()
        RestJsonDownloaderRest(molecule, ASSEMBLY_FOLDER, filepath[3]).get_file()
        RestJsonDownloaderRest(molecule, MOLECULES_FOLDER, filepath[3]).get_file()
        RestJsonDownloaderRest(molecule, SUMMARY_FOLDER, filepath[3]).get_file()


def update_input_files(molecules_added, molecules_modified, files_added, files_modified,
                       files_obsolete):
    remove_files(files_modified + files_obsolete)
    download_files(molecules_added + molecules_modified, files_added + files_modified)


def update_csv(path_to_csv, list_added, list_modified, list_obsolete):
    """
    :param path_to_csv:
    :param list_added: list of added lists with ordered items (result of AllFilesParser.get_data_ordered())
    :param list_modified: list of modified...
    :param list_obsolete:  list of obsolete
    :return:
    """
    with open(path_to_csv, mode='r', encoding='utf-8') as f:
        molecule_records = list(csv.reader(f, delimiter=';', lineterminator='\n'))
        obsolete_molecules = set([i[0].strip().lower() for i in list_obsolete])
        modified_molecules = set([i[0].strip().lower() for i in list_modified])
        # remove obsolete and modified
        molecule_records = [i for i in molecule_records if
                            not i[0].strip().lower() in set.union(obsolete_molecules, modified_molecules)]
        # add added and updated modified
        molecule_records.append(list_added + list_modified)


def update():
    pass


if __name__ == '__main__':
    update()
