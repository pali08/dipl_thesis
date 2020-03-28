# /usr/bin/env python3
import argparse
import os
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
        print(os.path.split(filepath)[0].split('/')[-1])
        return os.path.split(filepath)[0].split('/')[-1]
    else:
        print(filename.split('.')[0].split("_")[0])
        return filename.split('.')[0].split("_")[0]


def load_json(filename):
    '''
    :param filename: .json file as string
    :return: dictionary with json data
    '''
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
        try:
            return MMCIF2Dict(fnm)['_reflns.d_resolution_high'][0]
        except KeyError:
            try:
                return MMCIF2Dict(fnm)['em_3d_reconstruction.resolution'][0]
            except KeyError:
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
            return "{0:.3f}".format(WATER_MOL_WEIGHT * i['number_of_copies'])
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
        return 'nan'


def filepath_generator(path):
    """
    Generates filenames with their absolute or relative path depending on input
    :param path:
    :return: yields paths in alphabetical order
    """
    for root, dirs, files in os.walk(path):
        dirs.sort()
        files.sort()
        print(fileset_xml)
        for file in files:
            filepath = os.path.join(root, file)
            if file.split(".")[1].lower() == 'xml':
                yield filepath
            elif get_molecule_name_from_filepath(filepath) in fileset_xml:
                print(filepath)
                yield filepath


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
        #if sum(1 for line in open(file)) != len(column_list):
            #return 'List length not equal to lengt of lines in file.'
        for index, line in enumerate(fileinput.input(file, inplace=True)):
            print(line.rstrip() + ';' + str(column_list[index]))
    except FileNotFoundError:
        with open(file, mode='w', encoding='utf-8') as f:
            for i in column_list:
                f.write(i + '\n')
    return


def read_file_get_list(path, column_name, required_data_function):
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
    column_list = [column_name]
    filename_generator = filepath_generator(path)
    while True:
        try:
            column_list.append(required_data_function(next(filename_generator)))
        except StopIteration:
            break
    print(column_list)
    return column_list


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
    write_csv_column(read_file_get_list(datafolders[0], 'pdb_id', get_pdbid_from_xml), csv_file)
    for i in range(0, len(datafolders)):

        write_csv_column(read_file_get_list(datafolders[i], columns[i], data_functions[i]), csv_file)


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
