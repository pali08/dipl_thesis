import argparse
import csv
import ftplib
import itertools
import os
import sys
import time

sys.path.append('..')
from src.downloader_ftp_difference_files import DifferenceFilesDownloader
from src.downloader_pdb import PdbDownloader
from src.downloader_ftp_xml_validation import XmlValidationDownloader
from src.downloader_rest_json_rest import RestJsonDownloaderRest
from src.downloader_rest_json_vdb import RestJsonDownloaderVdb
from src.exe_compute_data_all import get_dicts, write_csv_file
from src.generate_filepaths import FilepathGenerator
from src.global_constants_and_functions import OBSOLETE, MODIFIED, ADDED, LATEST_SUFFIX, METADATA_FILES_PATH, \
    VDB_JSON_UNIVERSAL_NAME, remove_custom, DirOrFileNotFoundError, SUMMARY_FOLDER, MOLECULES_FOLDER, ASSEMBLY_FOLDER, \
    A_M_O_FILENAME


def download_metadata():
    try:
        for i in [ADDED, MODIFIED, OBSOLETE]:
            DifferenceFilesDownloader(i).get_file()
        print('Metadata downloaded.')
    except Exception:
        for i in [ADDED, MODIFIED, OBSOLETE]:
            if os.path.exists(os.path.join(METADATA_FILES_PATH, i + LATEST_SUFFIX)):
                os.remove(os.path.join(METADATA_FILES_PATH, i + LATEST_SUFFIX))
        if os.path.exists(os.path.join(METADATA_FILES_PATH, A_M_O_FILENAME)):
            os.remove(os.path.join(METADATA_FILES_PATH, A_M_O_FILENAME))
        sys.exit('Unable to download metadata (added.latest, modified.latest, obsolete.latest). Please try again later')


def get_lists_of_changed_molecules():
    lists_of_changed_molecules = []
    for i in [ADDED, MODIFIED, OBSOLETE]:
        with open(os.path.join(METADATA_FILES_PATH, i + LATEST_SUFFIX), mode='r', encoding='utf-8') as changelist:
            molecules = [i.strip() for i in changelist.readlines()]
            lists_of_changed_molecules.append(molecules)
    return lists_of_changed_molecules


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
    # print('list of files to remove' + str(list_of_files_to_remove))
    # flatten list:
    list_of_files_to_remove = list(itertools.chain(*list_of_files_to_remove))
    for path_to_remove in list_of_files_to_remove:
        if os.path.basename(path_to_remove).lower() == VDB_JSON_UNIVERSAL_NAME:
            path_to_remove = os.path.dirname(path_to_remove)
        try:
            remove_custom(path_to_remove)
        except DirOrFileNotFoundError:
            print('File or directory {} not exists so not removed.'.format(path_to_remove))


def download_with_retry(downloader, downloader_inputs):
    i = 0
    while True:
        if i >= 3:
            print('Unable to download data for {}'.format(downloader_inputs[0]))
            return False
        try:
            downloader(*downloader_inputs).get_file()
            if i > 0:
                print('Download succeeded on attempt {}'.format(i + 1))
            return True
        except Exception:
            print('Failed to Download {}. Waiting 1 minute and attempting again'.format(downloader_inputs[-1]))
            time.sleep(60)
            i += 1
            continue


def download_files(molecules, list_of_files_to_download):
    # print('molecules + list of files to download')
    # print(molecules)
    # print(list_of_files_to_download)
    for molecule, filepath in zip(molecules, list_of_files_to_download):
        # print('Downloading: {}'.format(molecule))
        pdb_bool = download_with_retry(PdbDownloader, [molecule, filepath[0]])
        # PdbDownloader(molecule, filepath[0]).get_file()
        vdb_bool = download_with_retry(RestJsonDownloaderVdb, [molecule, filepath[1]])
        # RestJsonDownloaderVdb(molecule, filepath[1]).get_file()
        xml_bool = download_with_retry(XmlValidationDownloader, [molecule, filepath[2]])
        # XmlValidationDownloader(molecule, filepath[2]).get_file()
        rest_a_bool = download_with_retry(RestJsonDownloaderRest, [molecule, ASSEMBLY_FOLDER, filepath[3]])
        rest_m_bool = download_with_retry(RestJsonDownloaderRest, [molecule, MOLECULES_FOLDER, filepath[4]])
        rest_s_bool = download_with_retry(RestJsonDownloaderRest, [molecule, SUMMARY_FOLDER, filepath[5]])
        # RestJsonDownloaderRest(molecule, ASSEMBLY_FOLDER, filepath[3]).get_file()
        # RestJsonDownloaderRest(molecule, MOLECULES_FOLDER, filepath[4]).get_file()
        # RestJsonDownloaderRest(molecule, SUMMARY_FOLDER, filepath[5]).get_file()
        if not (pdb_bool and vdb_bool and xml_bool and rest_a_bool and rest_m_bool and rest_s_bool):
            for i in filepath:
                if os.path.exists(i):
                    os.remove(i)
            print('Unable to download data for {}. Please download and update manually')


def update_input_files(molecules_added, molecules_modified, files_added, files_modified,
                       files_obsolete):
    # print('files modified and obsolete are...:')
    # print(files_modified)
    # print(files_obsolete)
    remove_files(files_modified + files_obsolete)
    download_files(molecules_added + molecules_modified, files_added + files_modified)


def update_csv(path_to_csv, molecule_records_update, molecules_added, molecules_modified, molecules_obsolete):
    """
    :param path_to_csv:
    :param molecules_added: set of added lists with ordered items (result of AllFilesParser.get_data_ordered())
    :param molecules_modified: set of modified...
    :param molecules_obsolete: set of obsolete
    :param molecule_records_update: added and modified files
    :return:
    """
    with open(path_to_csv, mode='r', encoding='utf-8') as f:
        molecule_records = list(csv.reader(f, delimiter=';', lineterminator='\n'))
        molecules_added_modified = set.union(set(molecules_added), set(molecules_modified))
        # TODO: check if this is necessary - in molecule_records_update, there should be only added+modified molecules
        molecule_records_added_modified = [i for i in molecule_records_update if
                                           i[0].strip().lower() in molecules_added_modified]
        # remove obsolete and modified
        molecule_records = [i for i in molecule_records if
                            # keep files that are either not in updated files at all - unchanged:
                            (i[0].strip().lower() not in set.union(set(molecules_added), set(molecules_modified),
                                                                   set(molecules_obsolete))) or
                            # or in added molecules
                            i[0].strip().lower() in molecules_added]
        # add added and modified
        molecule_records.extend(molecule_records_added_modified)
    remove_custom(path_to_csv)
    write_csv_file(path_to_csv, molecule_records)


def update():
    parser = argparse.ArgumentParser(description='Script for weekly updates of dataset and data.csv.')
    parser.add_argument('mmcif_files', help='Folder with mmcif files files', type=str)
    parser.add_argument('vdb_files', help='Folder with original json files', type=str)
    parser.add_argument('xml_files', help='Folder with xml files', type=str)
    parser.add_argument('rest_files', help='Folder with results of validation.'
                                           'Files can be stored in subfolder', type=str)
    parser.add_argument('ligand_stats_csv', help='CSV file with ligand statistics (heavy atoms size and flexibility)',
                        type=str)
    parser.add_argument('data_csv', help='Data.csv - csv file to update', type=str)
    parser.add_argument('--cpu_count', '-c', nargs='?', const=1, default=1, help='Folder with original json files',
                        type=int)
    args = parser.parse_args()
    # for testing purposes, downloading of metadata is commented out
    download_metadata()
    added_molecules, modified_molecules, obsolete_molecules = get_lists_of_changed_molecules()
    added_files = get_filepaths_from_list(added_molecules, args.mmcif_files, args.vdb_files, args.xml_files,
                                          args.rest_files)
    modified_files = get_filepaths_from_list(modified_molecules, args.mmcif_files, args.vdb_files, args.xml_files,
                                             args.rest_files)
    obsolete_files = get_filepaths_from_list(obsolete_molecules, args.mmcif_files, args.vdb_files, args.xml_files,
                                             args.rest_files)
    print('Updating input files...')
    update_input_files(added_molecules, modified_molecules, added_files, modified_files, obsolete_files)
    print('Update input files finished')
    print('Computing data for data.csv...')
    start = time.time()
    list_of_rec_lists = get_dicts(args.cpu_count, added_molecules + modified_molecules, args.ligand_stats_csv,
                                  args.mmcif_files, args.vdb_files,
                                  args.xml_files, args.rest_files)
    end = time.time()
    print('Computing data for data.csv lasted {:.3f} seconds'.format(end - start))
    print('Updating data.csv file...')
    update_csv(args.data_csv, list_of_rec_lists, added_molecules, modified_molecules, obsolete_molecules)
    print('Updating data.csv finished. \n Program finished')


if __name__ == '__main__':
    update()
