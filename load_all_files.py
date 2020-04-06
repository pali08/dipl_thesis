# /usr/bin/env python3
import argparse
import csv
import os
import time
import fileinput
import xml.etree.ElementTree as etree
import json
from datetime import datetime
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from Bio.File import as_handle

WATER_MOL_WEIGHT = 18.015
fileset_xml = set()


def get_molecule_name_from_filepath(filepath):
    filename = os.path.split(filepath)[1]
    if filename == 'result.json':
        return os.path.split(filepath)[0].split('/')[-1]
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
    fileset_xml.add(os.path.split(filename)[1].split('_')[0].strip())
    return etree.parse(filename).getroot()[0].get('clashscore')


def get_pdbid_from_xml(filename):
    """
    xml file is loaded in etree format
    :param filename:
    :return: pdbid gotten from etree
    """
    return etree.parse(filename).getroot()[0].get('pdbid')


def get_mmcif_high_resolution(filename):
    """
    MMCIF is loaded as dictionary
    :param filename:
    :return: Highest resolution value if exists, nan otherwise.
    Highest resolution can be different item in different file. 2 of possibilities are covered for now
    """

    def get_resolution(fnm):
        mmcif_dict = MMCIF2Dict(fnm)
        if '_reflns.d_resolution_high' in mmcif_dict:
            return mmcif_dict['_reflns.d_resolution_high'][0]
        elif '_em_3d_reconstruction.resolution' in mmcif_dict:
            return mmcif_dict['_em_3d_reconstruction.resolution'][0]
        else:
            return 'nan'

    try:
        return get_resolution(filename)
    except UnicodeDecodeError:
        with as_handle(filename, 'r', encoding='utf-16') as f:
            return get_resolution(f)


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
            return "{0:.2f}".format(WATER_MOL_WEIGHT * i['number_of_copies'])
    return 0


def get_validated_json_model_count_filtered(filename):
    """
    :param filename:
    :return: Number of models in validated json file
    if "Models" key exists in loaded json as dictionary, nan otherwise
    """
    try:
        return len(load_json(filename)['Models'][0]['ModelNames'])
    except IndexError:
        return '0'


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
            return os.path.join(root, file)


def write_csv_column(column_list, file):
    """
    Wrtites csv column
    For existing file, except block is executed (first column)
    For every next file, try block is executed. Writing is done.
    Fileinput.input(file, inplace=True) redirects output of print to file instead of
    stdout
    :param column_list: csv column list. The first item is column name
    :param file:
    :return:
    """
    try:
        for index, line in enumerate(fileinput.input(file, inplace=True)):
            print(line.rstrip() + ';' + str(column_list[index]))
    except FileNotFoundError:
        with open(file, mode='w', encoding='utf-8') as f:
            for i in column_list:
                f.write(i + os.linesep)
    return


def read_files_get_list(path, column_name, required_data_function):
    """
    Gets data of all files in given path and creates list from them. List is used by
    write_csv_column function
    :param path:
    :param column_name: first item in output list
    :param required_data_function: function that loads data from individual file (parsing function). One of:
    get_validated_json_model_count_filtered, get_orig_json_water_weight,
    get_mmcif_high_resolution, get_pdbid_from_xml, get_clashscore_from_xml
    :return: column list - see description
    """
    print("Working with {} function on dataset.".format(required_data_function.__name__))
    filename_value_dict = {}
    filename_generator = filepath_generator(path)
    while True:
        try:
            filepath = next(filename_generator)
            molecule_name = get_molecule_name_from_filepath(filepath)
            if molecule_name in filename_value_dict:
                print(
                    "WARNING: Filename {} is duplicated in given folder (e.g. slightly "
                    "changed name after subscore). Last found will be used".format(molecule_name))
            filename_value_dict[get_molecule_name_from_filepath(filepath)] = required_data_function(filepath)
        except StopIteration:
            break
    return filename_value_dict


def check_dataset_completeness(*dicts):
    intersection = set.intersection(*map(set, [i.keys() for i in dicts]))
    union_minus_intersection = set.union(*map(set, [i.keys() for i in dicts])) - intersection
    if union_minus_intersection != {}:
        print("Following molecules were omitted, because some of them did not exist in all datasets: {}".format(
            str(union_minus_intersection)))
    return intersection


def csv_name():
    """
    :return: generated csv filename (output_<datetimestamp>.csv)
    """
    return 'output_' + datetime.now().strftime('%Y%m%d%H%M%S%f') + '.csv'


def read_and_write(csv_file, columns, *datafolders):
    """
    Putting it all together
    :param csv_file: Filename generated by csv_name function
    :param columns: List of columnlists generated by read_file_get_list
    :param datafolders: datafolders with different type of data
    """
    if len(datafolders) != 4:
        print(
            'Incorrect number of datafolders in argument. Arguments must be: \
            xml_folder, mmcif_folder, json folder, json_validated_folder')
        return
    if len(columns) != 4:
        print('Incorrect number of items in column list')
    data_functions = [get_clashscore_from_xml, get_mmcif_high_resolution, get_orig_json_water_weight,
                      get_validated_json_model_count_filtered]
    #TODO:
    dicts = [data_functions[i](datafolders[i]) for i in range(0, len(data_functions))]
    molecules_for_output = check_dataset_completeness(*dicts)
    start_time = time.time()
    print("Finished in {0:.3f} seconds.".format(time.time() - start_time))
    with open(csv_file, mode='w', encoding='utf-8') as o:
        writer = csv.writer(o, delimiter=';')
        writer.writerow(columns)
        for i in molecules_for_output:
            writer.writerow([i] + [j[i] for j in dicts])


def main():
    """
    main - argparsing and executing read_and_write
    4 folders are compulsory as user argument, output csv filename is generated automatically
    """
    columns = ['clashscore', 'high_resolution', 'water_weight', 'model_count']
    parser = argparse.ArgumentParser(description='Intro task - parse different types of the data.')
    parser.add_argument('xml_files', help='Folder with xml files', type=str)
    parser.add_argument('mmcif_files', help='Folder with mmcif files files', type=str)
    parser.add_argument('json_files', help='Folder with original json files', type=str)
    parser.add_argument('json_files_validation', help='Folder with results of validation.'
                                                      'Files can be stored in subfolder', type=str)
    args = parser.parse_args()
    csvname = csv_name()
    read_and_write(csvname, columns, args.xml_files, args.mmcif_files, args.json_files, args.json_files_validation)
    print("Data were successfully written to " + csvname + ".")


if __name__ == '__main__':
    main()
