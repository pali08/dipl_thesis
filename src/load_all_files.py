# /usr/bin/env python3
import argparse
import csv
import os
import sys
import time
from datetime import datetime
from itertools import repeat
from multiprocessing import Pool

from src.global_constants_and_functions import columns
from src.pdb_parser import PdbParser
from src.vdb_parser import VdbParser

fileset_xml = set()


def get_molecule_name_from_filepath(filepath):
    filename = os.path.split(filepath)[1]
    if filename == 'result.json':
        return os.path.split(os.path.split(filepath)[0])[1]
    else:
        return filename.split('.')[0].split("_")[0]


def get_mmcif_data(filename):
    """
    MMCIF is loaded as dictionary
    :param filename:
    :return: Highest resolution value if exists, nan otherwise.
    Highest resolution can be different item in different file. 2 of possibilities are covered for now
    """
    pdb_parser = PdbParser(filename)
    return pdb_parser.get_pdb_id(), pdb_parser.get_mmcif_resolution(), pdb_parser.get_pdb_release_date(), \
           *pdb_parser.get_structure_weights(), *pdb_parser.get_structure_counts()


def get_vdb_data(filename):
    vdb_parser = VdbParser(filename)
    return vdb_parser.get_counts()


def get_data_and_molecule_name(filename, function):
    return function(filename), get_molecule_name_from_filepath(filename)


def filepath_generator(path):
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


def two_funcs_to_one(filepath, required_data_function):
    """
    :param filepath:
    :param required_data_function required data function
    :return: tuple- molecule name as first argument, wanted value as second
    """
    return get_molecule_name_from_filepath(filepath).lower(), required_data_function(filepath)


def read_files_get_dict(path, required_data_function, cpu_cores_count):
    """
    Gets data of all files in given path and creates list from them. List is used by
    write_csv_column function
    :param path:
    :param required_data_function: function that loads data from individual file (parsing function). One of:
    get_validated_json_model_count_filtered, get_orig_json_water_weight,
    get_mmcif_high_resolution, get_pdbid_from_xml, get_clashscore_from_xml
    :return: column list - see description
    """
    print("Working with {} function on dataset.".format(required_data_function.__name__))
    start_time = time.time()
    filename_generator = filepath_generator(path)
    pool = Pool(cpu_cores_count)
    column_list = pool.starmap_async(two_funcs_to_one, zip(filename_generator, repeat(required_data_function))).get()
    pool.close()
    pool.join()
    print("Finished in {0:.3f} seconds.".format(time.time() - start_time))
    filename_value_dict = dict(column_list)
    if len(column_list) != len(filename_value_dict):
        print(
            "WARNING: Dataset included duplicated molecules - probably same name with different .suffix "
            "or different name after subscore (e.g. 1xyz_foo.pdb vs 1xyz_bar.pdb). Last found will be used. It is "
            "highly recommended to check your dataset.")
    return filename_value_dict


def check_dataset_completeness(*dicts):
    """
    :param dicts: dictionaries in format {molecule:value}
    :return: union of all molecules. Keep in mind that function also modifies dicts in given scope, if some file does
    not exist for given molecule, value dependent on this file is set to nan
    """
    intersection = set.intersection(*map(set, [i.keys() for i in dicts]))
    union = set.union(*map(set, [i.keys() for i in dicts]))
    union_minus_intersection = union - intersection
    if union_minus_intersection != {}:
        for i in union_minus_intersection:
            for j in dicts:
                if i not in j:
                    j[i] = ['nan' for i in range(0, len(j[list(j.keys())[0]]))]
    return union


def csv_name():
    """
    :return: generated csv filename (output_<datetimestamp>.csv)
    """
    return 'output_' + datetime.now().strftime('%Y%m%d%H%M%S%f') + '.csv'


def read_and_write(csv_file, columns, cpu_cores_count, *datafolders):
    """
    Putting it all together
    :param csv_file: Filename generated by csv_name function
    :param columns: List of columnlists generated by read_file_get_list
    :param datafolders: datafolders with different type of data
    :param cpu_cores_count count of cpu cores chosen by user
    """
    # if len(columns) != 5:
    #     print('Incorrect number of items in column list')
    data_functions = [get_mmcif_data]
    dicts = [read_files_get_dict(datafolders[i], data_functions[i], cpu_cores_count) for i in
             range(0, len(data_functions))]
    molecules_for_output = check_dataset_completeness(*dicts)
    print(molecules_for_output)
    with open(csv_file, mode='w', encoding='utf-8') as o:
        writer = csv.writer(o, delimiter=';', lineterminator='\n')
        writer.writerow(columns)
        for i in molecules_for_output:
            writer.writerow(['{:.3f}'.format(i) if isinstance(i, float) else i for i in
                             [item for sublist in [j[i] for j in dicts] for item in sublist]])


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
    parser.add_argument('json_files', help='Folder with original json files', type=str)
    parser.add_argument('json_files_validation', help='Folder with results of validation.'
                                                      'Files can be stored in subfolder', type=str)
    parser.add_argument('--cpu_count', '-c', nargs='?', const=1, default=1, help='Folder with original json files',
                        type=int)
    args = parser.parse_args()
    csvname = csv_name()
    read_and_write(csvname, columns, args.cpu_count,
                   # args.xml_files,
                   args.mmcif_files,
                   # args.json_files,
                   # args.json_files_validation
                   )
    print(os.linesep + "Data were successfully written to " + csvname + ".")


if __name__ == '__main__':
    main()
