import argparse
import csv
import json
import os

import numpy as np

from src.global_constants_and_functions import is_float


def get_pairs_of_factors_from_autoplot_csv(filename):
    with open(filename, mode='r', encoding='utf-8') as f:
        csv_reader = csv.reader(f, delimiter=';')
        pairs_of_factor = [i[:2] for i in csv_reader][1:]
    return pairs_of_factor


def get_data_from_boundaries_csv(filename):
    with open(filename, mode='r', encoding='utf-8') as f:
        csv_reader = list(csv.reader(f, delimiter=';'))
    # print(csv_reader)
    # print({i[0]: i[1:] for i in zip(*csv_reader)})
    return {i[0]: i[1:] for i in zip(*csv_reader)}


def combine_pairs_of_factors(data_from_autoplot, data_from_boundaries):
    """
    :param data_from_autoplot: result of  get_pairs_of_factors_from_autoplot_csv
    :param data_from_boundaries: result of  get_data_from_boundaries_csv
    :return: {'factor1+factor2':[(valuex1,valuey1),(valuex2, valuey2)...]}
    """
    result_dict = {}
    for i in data_from_autoplot:
        key = '{}+{}'.format(i[0], i[1])
        x_factor = data_from_boundaries[i[0]]
        y_factor = data_from_boundaries[i[1]]
        # remove na and nans:
        result_dict[key] = [i for i in list(zip(x_factor, y_factor)) if is_float(i[0]) and is_float(i[1])]
    return result_dict


def split_into_intervals(combined_pair_of_factors, number_of_intervals=None):
    x_vals = [i[0] for i in combined_pair_of_factors]
    y_vals = [i[1] for i in combined_pair_of_factors]
    max_x = max(x_vals)
    min_x = min(x_vals)

    if number_of_intervals is None:
        number_of_intervals = int(max_x + 1) - int(min_x)
    print(number_of_intervals)
    factors_splitted_into_bins = [[] for i in range(0, number_of_intervals)]
    size_of_interval = (max_x - min_x) / number_of_intervals
    borders = np.array([min_x + (i * size_of_interval) for i in range(0, number_of_intervals)])
    x_vals_np_array = np.array(x_vals)
    indices = np.digitize(x_vals_np_array, borders, right=False)
    for i in range(0, len(indices)):
        factors_splitted_into_bins[indices[i] - 1].append(x_vals_np_array[i])
    return factors_splitted_into_bins, size_of_interval, min_x, max_x, min(y_vals), max(y_vals), len(x_vals)


def compute_data_for_interval(pairs_of_values_in_interval, minimum, interval_size, bucket_ordinal_number_in_for_cycle):
    x_factor = [i[0] for i in pairs_of_values_in_interval]
    y_factor = [i[1] for i in pairs_of_values_in_interval]
    bucket = {
        "BucketOrdinalNumber": bucket_ordinal_number_in_for_cycle + 1,
        "StructureCountInBucket": len(pairs_of_values_in_interval),
        "XfactorFrom": {
            "XfactorFromIsInfinity": False,
            "XfactorFromOpenInterval": False,
            "XfactorFromValue": minimum + (interval_size * bucket_ordinal_number_in_for_cycle)
        },
        "XfactorTo": {
            "XfactorToIsInfinity": False,
            "XfactorToOpenInterval": True,
            "XfactorToValue": minimum + (interval_size * (bucket_ordinal_number_in_for_cycle + 1))
        },
        "YfactorAverage": np.average(y_factor),
        "YfactorHighQuartile": np.quantile(y_factor, 0.75),
        "YfactorLowQuartile": np.quantile(y_factor, 0.75),
        "YfactorMaximum": max(y_factor),
        "YfactorMedian": np.median(y_factor),
        "YfactorMinimum": min(y_factor)
    }
    return bucket


def create_json(filename, folder, dictionary_to_output):
    with open(os.path.join(folder, filename), mode='w+', encoding='utf-8') as json_file:
        json.dump(dictionary_to_output, json_file, indent=4)


def get_results(filename_autoplots, filename_boundaries, result_folder):
    pairs_of_factors = get_pairs_of_factors_from_autoplot_csv(filename_autoplots)
    data_from_boundaries = get_data_from_boundaries_csv(filename_boundaries)
    combiner_pairs_of_factors_with_key = combine_pairs_of_factors(pairs_of_factors, data_from_boundaries)
    for key, value in combiner_pairs_of_factors_with_key.items():
        factors_splitted_into_bins, size_of_interval, min_x, max_x, min_y, max_y, length = \
            split_into_intervals(value)
        result_dict = {'GraphBuckets': [],
                       'StructureCount': length,
                       'XfactorGlobalMaximum': max_x,
                       'XfactorGlobalMinimum': min_x,
                       'XfactorName': key.split('+')[0],
                       'YfactorGlobalMaximum': max_y,
                       'YfactorGlobalMinimum': min_y,
                       'YfactorName': key.split('+')[1]
                       }
        j = 0
        for i in factors_splitted_into_bins:
            result_dict['GraphBuckets'].append(compute_data_for_interval(i, min_x, size_of_interval, j))
            j += 1
        create_json(key + '.json', result_folder, result_dict)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script for generating .json file for charts')
    parser.add_argument('filename_autoplots', help='ususally autoplot.csv file', type=str)
    parser.add_argument('filename_boundaries', help='usually boundaries.csv file', type=str)
    parser.add_argument('result_folder',
                        help='Folder for result. Keep in mind, that existing files will be overwritten', type=str)
    args = parser.parse_args()
    get_results(args.filename_autoplots, args.filename_boundaries, args.result_folder)
