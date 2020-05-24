# /usr/bin/env python3
import argparse
import csv
import os
import sys
import time
import xml.etree.ElementTree as etree
import json
from datetime import datetime
from itertools import repeat
from multiprocessing import Pool
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from Bio.File import as_handle

WATER_MOL_WEIGHT = 18.015
fileset_xml = set()


def get_molecule_name_from_filepath(filepath):
    filename = os.path.split(filepath)[1]
    if filename == 'result.json':
        return os.path.split(os.path.split(filepath)[0])[1]
    else:
        return filename.split('.')[0].split("_")[0]


def load_json(filename):
    """
    :param filename: .json file as string
    :return: dictionary with json data
    """
    with open(filename) as js:
        return json.load(js)


def get_clashscore_from_xml(filename):
    """
    xml file is loaded in etree format
    :param filename:
    :return: clashscore gotten from etree
    """
    tree = etree.parse(filename).getroot()[0]
    clashscore = tree.get('clashscore')
    clashscore_full_length = tree.get('clashscore-full-length')
    if clashscore_full_length is None:
        return clashscore, 'nan'
    return clashscore, clashscore_full_length


def get_pdbid_from_xml(filename):
    """
    xml file is loaded in etree format
    :param filename:
    :return: pdbid gotten from etree
    probably if this function is run inside pool, global variables cannot be modified ?
    """
    fileset_xml.add(os.path.split(filename)[1].split('_')[0].strip())
    return [etree.parse(filename).getroot()[0].get('pdbid')]


def get_mmcif_high_resolution(filename):
    """
    MMCIF is loaded as dictionary
    :param filename:
    :return: Highest resolution value if exists, nan otherwise.
    Highest resolution can be different item in different file. 2 of possibilities are covered for now
    """
    def get_resolution(fnm):
        mmcif_dict = MMCIF2Dict(fnm)
        if '_refine.ls_d_res_high' in mmcif_dict:
            return mmcif_dict['_refine.ls_d_res_high'][0]
        return ['nan']

    try:
        return [get_resolution(filename)]
    except UnicodeDecodeError:
        with as_handle(filename, 'r', encoding='utf-16') as f:
            return [get_resolution(f)]


def get_orig_json_water_weight(filename):
    """
    json file is loaded as a dictionary
    :param filename:
    :return: total water weight (number of molecules * WATER_MOL_WEIGHT) if water is in molecule
    0 otherwise
    """
    dict_index = os.path.split(filename)[-1].rsplit('.', 1)[0]
    js = load_json(filename)
    for i in js[dict_index]:
        if i['molecule_name'] == ['water']:
            return ["{0:.2f}".format(WATER_MOL_WEIGHT * i['number_of_copies'])]
    return [0]


def get_validated_json_model_count_filtered(filename):
    """
    :param filename:
    :return: Number of models in validated json file
    if "Models" key exists in loaded json as dictionary, nan otherwise
    """
    try:
        return [len(load_json(filename)['Models'][0]['ModelNames'])]
    except IndexError:
        return ['0']


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
                    j[i] = 'nan'
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
    if len(datafolders) != 4:
        print(
            'Incorrect number of datafolders in argument. Arguments must be: \
            xml_folder, mmcif_folder, json folder, json_validated_folder')
        return
    if len(columns) != 5:
        print('Incorrect number of items in column list')
    data_functions = [get_clashscore_from_xml,
                      get_mmcif_high_resolution,
                      get_orig_json_water_weight,
                      get_validated_json_model_count_filtered]
    dicts = [read_files_get_dict(datafolders[i], data_functions[i], cpu_cores_count) for i in
             range(0, len(data_functions))]
    molecules_for_output = check_dataset_completeness(*dicts)
    with open(csv_file, mode='w', encoding='utf-8') as o:
        writer = csv.writer(o, delimiter=';', lineterminator='\n')
        writer.writerow(columns)
        for i in molecules_for_output:
            writer.writerow([i] + [item for sublist in [j[i] for j in dicts] for item in sublist])


def verify_cpu_core_count(required_cores):
    if os.cpu_count() > required_cores:
        sys.exit("Number of cpu cores is bigger than available on computer.")


def main():
    """
    main - argparsing and executing read_and_write
    4 folders are compulsory as user argument, output csv filename is generated automatically
    """
    columns = ['filename', 'clashscore', 'clashscore_full_length', 'high_resolution', 'water_weight', 'model_count']
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
    read_and_write(csvname, columns, args.cpu_count, args.xml_files, args.mmcif_files, args.json_files,
                   args.json_files_validation)
    print(os.linesep + "Data were successfully written to " + csvname + ".")


if __name__ == '__main__':
    main()
