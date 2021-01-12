import csv


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
        result_dict[key] = list(zip(x_factor, y_factor))
    return result_dict


def split_into_intervals(key, combined_pair_of_factors, number_of_intervals=None):
    x_vals = [i[0] for i in combined_pair_of_factors]
    y_vals = [i[1] for i in combined_pair_of_factors]
    max_x = max(x_vals)
    min_x = min(x_vals)

    if number_of_intervals is None:
        number_of_intervals = int(max(x_vals)+1) - int(min(x_vals))
    print(number_of_intervals)
    factors_splitted_into_bins = [[] for i in range(0, number_of_intervals)]
    size_of_interval = (max_x - min_x) / number_of_intervals

    for i in combined_pair_of_factors:
        print(i[0])
        try:
            factors_splitted_into_bins[int((i[0] - min_x) / size_of_interval)].append(i)
        except IndexError:
            factors_splitted_into_bins[int(((i[0] - min_x) / size_of_interval) - 0.000001)].append(i)
    return key, factors_splitted_into_bins, min_x, max_x, min(y_vals), max(y_vals), size_of_interval
