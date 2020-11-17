import csv
import sys
import time
import unittest
from datetime import datetime
from itertools import repeat
from multiprocessing import Pool

import numpy
import random

sys.path.append('..')
from src.parser_all_files import AllFilesParser
from src.global_constants_and_functions import NAN_VALUE, is_float

"""
This is specific test that 
- takes random rows from csv and creates list of dicts ,
- gets mmcif/json/xml files corresponding to random csv rows from previous step
- compares values
Main purpose is to find if values matches with data from validator (e.g. 0 and nan)
"""


def get_data_csv_random_records_dicts(sample_length, data_csv):
    """
    :param sample_length: count of records we want to pick
    :param data_csv:
    :return: list of dicts in format [{'PDB
    ID':'<pdb id code>', 'resolution': <resolution>, 'releaseDate' : releaseDate , ...etc.}]
    """
    with open(data_csv, mode='r', encoding='utf-8') as data:
        reader = csv.reader(data, delimiter=';')
        header = next(reader)
        reader_list = list(reader)
        random_molecules_samples = random.sample(reader_list, sample_length)
        return [dict((zip([header for j in range(0, sample_length)][i], random_molecules_samples[i]))) for i in
                range(0, sample_length)]


def get_molecules(random_data_csv_dicts):
    return [random_data_csv_dicts[i]['PDB ID'] for i in range(0, len(random_data_csv_dicts))]


def get_result_dicts(molecules, ligand_stats_csv, cpu_count, *filepaths):
    pool = Pool(cpu_count)
    result_tuple = pool.starmap_async(AllFilesParser, zip(molecules, repeat(ligand_stats_csv),
                                                          repeat(filepaths[0]),
                                                          repeat(filepaths[1]),
                                                          repeat(filepaths[2]),
                                                          repeat(filepaths[3]))).get()
    pool.close()
    pool.join()
    return [i.result_dict for i in result_tuple]
    # list_of_result_dicts = []
    # for i in molecules:
    #     list_of_result_dicts.append(AllFilesParser(i, ligand_stats_csv, *filepaths).result_dict)
    # return list_of_result_dicts


def compare(random_data_csv_dicts, result_dicts):
    success_rate = {'Passed': 0, 'Failed': 0}
    for result_dict in result_dicts:
        errors = 0
        if 'PDB ID' not in result_dict:
            errors += 1
            print('Test failed: ' + str(result_dict) + ' does not have PDB ID')
        else:
            print('Testing ' + result_dict['PDB ID'])
            for random_data_csv_dict in random_data_csv_dicts:
                if random_data_csv_dict['PDB ID'].upper() == result_dict['PDB ID'].upper():
                    for key, value in result_dict.items():
                        if key not in random_data_csv_dict:
                            # TODO When we will parse all data, we also need to compare, that all data.csv column are
                            #  in result dict
                            print('Test failed: ' + key + ' not in data.csv')
                            errors += 1
                        else:
                            # following block is used for known issues with atom count.
                            # There are a lot of them and it makes test result messy
                            if key in ('atomCount', 'allAtomCount', 'allAtomCountLn') and value != NAN_VALUE and \
                                    random_data_csv_dict[key] != 'nan':
                                if key == 'allAtomCountLn':
                                    if float(random_data_csv_dict[key]) + 0.1 >= float(value) >= float(
                                            random_data_csv_dict[key]) - 0.1:
                                        continue
                                else:
                                    if float(random_data_csv_dict[key]) + 1 >= float(value) >= float(
                                            random_data_csv_dict[key]) - 1:
                                        continue
                            if str(value).lower() == str(random_data_csv_dict[key].lower()) \
                                    and not is_float(value) \
                                    and not is_float(random_data_csv_dict[key]):
                                pass
                                # pdbid names
                            elif is_float(value) and is_float(random_data_csv_dict[key]):
                                if numpy.isclose(float(value), float(random_data_csv_dict[key])):
                                    pass
                                    # two float nonnan values
                                elif numpy.isnan(float(value)) and numpy.isnan(float(random_data_csv_dict[key])):
                                    pass
                                    # nan vs nan
                                else:
                                    errors += 1
                                    print('First Test failed: ' + str(key) + ':' + 'Actual: ' + str(
                                        value) + ' Expected: ' +
                                          random_data_csv_dict[key])
                                    # either values are completely different (e.g. 1.0 vs 1000.0)
                                    # or one of values is nan and one is not
                                # print(random_data_csv_dicts)
                            elif (is_float(value) and not is_float(random_data_csv_dict[key])) \
                                    or (not is_float(value) and is_float(random_data_csv_dict[key])):
                                errors += 1
                                print(
                                    'Second Test failed: ' + str(key) + ':' + 'Actual: ' + str(value) + ' Expected: ' +
                                    random_data_csv_dict[key])
                                # not sure if this can happen - maybe question mark in pdb file ?
                            else:
                                print('compare function: This else branch should never happen')
        if errors == 0:
            success_rate['Passed'] += 1
        else:
            success_rate['Failed'] += 1
    print(str(success_rate))


def main():
    data_csv_dicts = get_data_csv_random_records_dicts(int(sys.argv[1]), sys.argv[2])
    molecules_globalvar = get_molecules(data_csv_dicts)
    start = time.time()
    result_dicts_globalvar = get_result_dicts(molecules_globalvar, sys.argv[3], int(sys.argv[4]), *sys.argv[5:])
    end = time.time()
    print("Loading files lasted {:.3f} seconds".format(end - start))
    compare(data_csv_dicts, result_dicts_globalvar)


if __name__ == '__main__':
    main()
