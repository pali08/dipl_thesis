import argparse
import csv
import json
import os
import sys

import numpy as np

from src.global_constants_and_functions import is_float, str_to_float_or_int


def get_pairs_of_factors_from_autoplot_csv(filename):
    with open(filename, mode='r', encoding='utf-8') as f:
        csv_reader = csv.reader(f, delimiter=';')
        pairs_of_factor = [i[:2] for i in csv_reader][1:]
    # print(pairs_of_factor)
    return pairs_of_factor


def get_data_from_csv(filename):
    with open(filename, mode='r', encoding='utf-8') as f:
        csv_reader = list(csv.reader(f, delimiter=';'))
    # print(csv_reader)
    # print({i[0]: i[1:] for i in zip(*csv_reader)})
    return {i[0]: tuple([j for j in i[1:]]) for i in zip(*csv_reader)}


def combine_pairs_of_factors(data_from_autoplot, data_from_data_csv):
    """
    :param data_from_autoplot: result of  get_pairs_of_factors_from_autoplot_csv
    :param data_from_data_csv: result of  get_data_from_boundaries_csv
    :return: {'factor1+factor2':[(valuex1,valuey1),(valuex2, valuey2)...]}
    """
    result_dict = {}
    for i in data_from_autoplot:
        key = '{}+{}'.format(i[0], i[1])
        x_factor = data_from_data_csv[i[0]]
        y_factor = data_from_data_csv[i[1]]
        # print(x_factor)
        # print(y_factor)
        # remove na and nans:
        # print(str_to_float_or_int(i[1]))
        result_dict[key] = [[(str_to_float_or_int(j[0])), str_to_float_or_int(j[1])] for j in
                            list(zip(x_factor, y_factor)) if
                            is_float(j[0]) and is_float(j[1])]
    # print(result_dict)
    return result_dict


def get_intervals_from_boundaries(data_from_boundaries_csv, wanted_factor_on_x_axis):
    numbers_of_buckets = data_from_boundaries_csv['']
    interval_borders = data_from_boundaries_csv[wanted_factor_on_x_axis]
    return [[int(i[0]), str_to_float_or_int(i[1])] for i in zip(numbers_of_buckets, interval_borders) if
            is_float(i[0]) and is_float(i[1])]


def split_into_intervals(combined_pair_of_factors, intervals, wanted_factor_pair):
    # print(combined_pair_of_factors[wanted_factor_pair])
    # print(intervals)
    x_vals = [i[0] for i in combined_pair_of_factors[wanted_factor_pair]]
    y_vals = [i[1] for i in combined_pair_of_factors[wanted_factor_pair]]
    max_x = max(x_vals)
    min_x = min(x_vals)

    factors_splitted_into_bins = [[] for i in range(0, len(intervals))]
    borders = [i[1] for i in intervals]
    borders_for_digitizing = np.array(borders)
    borders = [str_to_float_or_int(i[1]) for i in intervals]
    bucket_numbers = [i[0] for i in intervals]
    x_vals_np_array = np.array(x_vals)
    # print(x_vals_np_array)
    indices = np.digitize([i for i in x_vals_np_array], borders_for_digitizing, right=False)
    # print(combined_pair_of_factors)
    # print(x_vals_np_array)
    # print(borders)
    # print(intervals)
    # print(min(indices))
    # print(max(indices))
    len(factors_splitted_into_bins)
    # sys.exit()
    for i in range(0, len(indices)):
        factors_splitted_into_bins[indices[i] - 1].append(y_vals[i])
    return list(factors_splitted_into_bins), bucket_numbers, list(borders), min_x, max_x, min(y_vals), max(y_vals), len(
        x_vals)


def compute_data_for_interval(pairs_of_values_in_interval, bucket_number, is_highest_bucket=False):
    if pairs_of_values_in_interval:
        x_factor = [i[0] for i in pairs_of_values_in_interval]
        y_factor = [i[1] for i in pairs_of_values_in_interval]
        bucket = {
            "BucketOrdinalNumber": bucket_number,
            "StructureCountInBucket": len(pairs_of_values_in_interval),
            "XfactorFrom": {
                "XfactorFromIsInfinity": False,
                "XfactorFromOpenInterval": False,
                "XfactorFromValue": min(x_factor)
            },
            "XfactorTo": {
                "XfactorToIsInfinity": False,
                "XfactorToOpenInterval": is_highest_bucket,
                "XfactorToValue": max(x_factor)
            },
            "YfactorAverage": np.average(y_factor),
            "YfactorHighQuartile": np.quantile(y_factor, 0.75),
            "YfactorLowQuartile": np.quantile(y_factor, 0.25),
            "YfactorMaximum": max(y_factor),
            "YfactorMedian": np.median(y_factor),
            "YfactorMinimum": min(y_factor)
        }
    else:
        bucket = {
            "BucketOrdinalNumber": bucket_number,
            "StructureCountInBucket": len(pairs_of_values_in_interval),
            "XfactorFrom": {
                "XfactorFromIsInfinity": False,
                "XfactorFromOpenInterval": False,
                "XfactorFromValue": None
            },
            "XfactorTo": {
                "XfactorToIsInfinity": False,
                "XfactorToOpenInterval": is_highest_bucket,
                "XfactorToValue": None
            },
            "YfactorAverage": None,
            "YfactorHighQuartile": None,
            "YfactorLowQuartile": None,
            "YfactorMaximum": None,
            "YfactorMedian": None,
            "YfactorMinimum": None
        }

    return bucket


def create_json(filename, folder, dictionary_to_output):
    with open(os.path.join(folder, filename), mode='w+', encoding='utf-8') as json_file:
        json.dump(dictionary_to_output, json_file, indent=4)


def get_results(filename_autoplots, filename_boundaries, filename_data_csv, result_folder):
    pairs_of_factors = get_pairs_of_factors_from_autoplot_csv(filename_autoplots)
    data_from_boundaries = get_data_from_csv(filename_boundaries)
    data_from_data_csv = get_data_from_csv(filename_data_csv)
    # intervals = data_from_boundaries
    combined_pairs_of_factors_with_key = combine_pairs_of_factors(pairs_of_factors, data_from_data_csv)
    for key, value in combined_pairs_of_factors_with_key.items():
        # print(key.split('+')[0])
        # print(data_from_boundaries)
        intervals = get_intervals_from_boundaries(data_from_boundaries, key.split('+')[0])
        factors_splitted_into_bins, bucket_numbers, borders, min_x, max_x, min_y, max_y, length = split_into_intervals(
            value, intervals, key)
        result_dict = {'GraphBuckets': [],
                       'StructureCount': length,
                       'XfactorGlobalMaximum': max_x,
                       'XfactorGlobalMinimum': min_x,
                       'XfactorName': key.split('+')[0],
                       'YfactorGlobalMaximum': max_y,
                       'YfactorGlobalMinimum': min_y,
                       'YfactorName': key.split('+')[1]
                       }
        j = 1
        last_bucket = False
        for pair, number in zip(factors_splitted_into_bins, bucket_numbers):
            if j == len(factors_splitted_into_bins):
                last_bucket = True
            result_dict['GraphBuckets'].append(compute_data_for_interval(pair, number, last_bucket))
            j += 1
        create_json(key + '.json', result_folder, result_dict)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script for generating .json file for charts')
    parser.add_argument('filename_autoplots', help='ususally autoplot.csv file', type=str)
    parser.add_argument('filename_boundaries', help='usually boundaries.csv file', type=str)
    parser.add_argument('filename_data_csv', help='usually data.csv file', type=str)
    parser.add_argument('result_folder',
                        help='Folder for result. Keep in mind, that existing files will be overwritten', type=str)
    args = parser.parse_args()
    get_results(args.filename_autoplots, args.filename_boundaries, args.filename_data_csv, args.result_folder)
