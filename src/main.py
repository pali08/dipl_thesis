# /usr/bin/env python3
import argparse
import csv
import os
import sys
import time
from datetime import datetime
from itertools import repeat
from multiprocessing import Pool

from src.all_files_parser import AllFilesParser
from src.global_constants_and_functions import columns
from src.pdb_parser import PdbParser
from src.pdb_vdb_computer import PdbVdbComputer
from src.vdb_parser import VdbParser


def get_molecule_name_from_filepath(filepath):
    filename = os.path.split(filepath)[1]
    if filename == 'result.json':
        return os.path.split(os.path.split(filepath)[0])[1]
    else:
        return filename.split('.')[0].split("_")[0]


def filename_with_path_generator(path):
    """
    Generates filenames with their absolute or relative path depending on input
    :param path:
    :return: yields paths in alphabetical order
    """
    for root, dirs, files in os.walk(path):
        dirs.sort()
        files.sort()
        for file in files:
            # useful for vim users, otherwise program ends
            # with decode error if file is opened during execution
            if not file.lower().endswith('.swp'):
                yield os.path.join(root, file)


def get_all_molecules(*filepaths):
    molecules = set()
    for i in filepaths:
        filenames = filename_with_path_generator(i)
        while True:
            try:
                molecules.add(next(filenames))
            except StopIteration:
                return molecules


def get_dicts(cpu_cores_count, molecules, *filepaths):
    # try what is faster for using one core - multiprocessing or for cycle
    if cpu_cores_count == 1:
        result_list = []
        for i in molecules:
            result_list.append(AllFilesParser(i, *filepaths).result_dict)
        return result_list

    # start_time = time.time()
    # pool = Pool(cpu_cores_count)
    # result_tuple = pool.starmap_async(AllFilesParser, zip(molecules, repeat(filepaths))).get()
    # pool.close()
    # pool.join()
    # print("Finished in {0:.3f} seconds.".format(time.time() - start_time))
    # return result_tuple


def csv_name():
    """
    :return: generated csv filename (output_<datetimestamp>.csv)
    """
    return 'output_' + datetime.now().strftime('%Y%m%d%H%M%S%f') + '.csv'


def write_csv_file(csv_file, list_of_dicts):
    with open(csv_file, mode='w', encoding='utf-8') as o:
        writer = csv.DictWriter(o, fieldnames=list(list_of_dicts[0].keys()), delimiter=';', lineterminator='\n')
        writer.writeheader()
        for i in list_of_dicts:
            # TODO formatting of floats
            writer.writerow(i)
            # writer.writerow(['{:.3f}'.format(i) if isinstance(i, float) else i for i in
            #                  [item for sublist in [j[i] for j in dicts] for item in sublist]])


def verify_cpu_core_count(required_cores):
    if os.cpu_count() > required_cores:
        sys.exit("Number of cpu cores is bigger than available on computer.")


def main():
    """
    main - argparsing and executing read_and_write
    4 folders are compulsory as user argument, output csv filename is generated automatically
    """
    parser = argparse.ArgumentParser(description='Intro task - parse different types of the data.')
    parser.add_argument('xml_files', help='Folder with xml files', type=str)
    parser.add_argument('mmcif_files', help='Folder with mmcif files files', type=str)
    parser.add_argument('vdb_files', help='Folder with original json files', type=str)
    parser.add_argument('rest_files', help='Folder with results of validation.'
                                           'Files can be stored in subfolder', type=str)
    parser.add_argument('--cpu_count', '-c', nargs='?', const=1, default=1, help='Folder with original json files',
                        type=int)
    args = parser.parse_args()
    csvname = csv_name()
    molecules = get_all_molecules(args.xml_files, args.mmcif_files, args.vdb_files, args.rest_files)
    dicts = get_dicts(args.cpu_count, molecules, args.mmcif_files, args.vdb_files, args.xml_files, args.rest_files)
    print(os.linesep + "Data were successfully written to " + csvname + ".")


if __name__ == '__main__':
    main()
