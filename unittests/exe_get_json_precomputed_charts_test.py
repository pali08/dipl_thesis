import os
import sys
import unittest

sys.path.append('..')
from src.exe_get_json_precomputed_charts import get_pairs_of_factors_from_autoplot_csv, get_data_from_csv, \
    combine_pairs_of_factors, split_into_intervals, get_intervals_from_boundaries, compute_data_for_interval
from unittests.exe_get_json_precomputed_charts_test_verification_data import pairs_test, boundaries_test, \
    resolution_plus_release_date, buckets_year, test_split_into_intervals_result

AUTOPLOT_FILEPATH = os.path.join('.', 'input_data_5', 'autoplot.csv')
BOUNDARIES_FILEPATH = os.path.join('.', 'input_data_5', 'boundaries.csv')
DATA_CSV_FILEPATH = os.path.join('.', 'input_data_5', 'data.csv')
DATA_CSV_FILEPATH_2 = os.path.join('.', 'input_data_5', 'data_2.csv')
test_split_into_intervals_input = [(4.9184867074137975, 9.71912788178685),
                                   (0.3362218404068318, 0.303256099437611),
                                   (9.613, 1.3372324955180115),
                                   (3.8551927734774694, 6.032235236829006),
                                   (5.53198393114609, 3.234695062930909),
                                   (0.7671930508620439, 1.4264870821202735),
                                   (5.357129193947378, 2.359066926863298),
                                   (7.073765624234069, 0.04772856957861782),
                                   (5.094454173969133, 4.341933763142994),
                                   (3.0172448479687706, 3.018960638880971),
                                   (9.5, 1.2)]


class GetJsonPrecomputedChartsTest(unittest.TestCase):
    def test_get_autoplot_csv(self):
        pairs = get_pairs_of_factors_from_autoplot_csv(AUTOPLOT_FILEPATH)
        self.assertEqual(pairs, pairs_test)

    def test_combine_pairs_of_factors(self):
        combined_pairs_of_factors = combine_pairs_of_factors(get_pairs_of_factors_from_autoplot_csv(AUTOPLOT_FILEPATH),
                                                             get_data_from_csv(DATA_CSV_FILEPATH_2))
        # print(combined_pairs_of_factors)
        self.assertEqual(combined_pairs_of_factors['resolution+releaseDate'], resolution_plus_release_date)

    def test_get_intervals_from_boundaries(self):
        self.assertEqual(get_intervals_from_boundaries(get_data_from_csv(BOUNDARIES_FILEPATH), 'releaseDate'),
                         buckets_year)
        # print(split_into_intervals(test_split_into_intervals_input))

    # def test_split_into_intervals(self):
    #     combined_pair_of_factors = combine_pairs_of_factors(get_pairs_of_factors_from_autoplot_csv(AUTOPLOT_FILEPATH),
    #                                                         get_data_from_csv(DATA_CSV_FILEPATH_2))
    #     intervals = get_intervals_from_boundaries(get_data_from_csv(BOUNDARIES_FILEPATH), 'releaseDate')
    #     self.assertAlmostEqual(split_into_intervals(combined_pair_of_factors, intervals, 'releaseDate+clashscore'),
    #                            test_split_into_intervals_result)

    def test_result_for_interval(self):
        pairs_of_factors = get_pairs_of_factors_from_autoplot_csv(AUTOPLOT_FILEPATH)
        data_from_boundaries = get_data_from_csv(BOUNDARIES_FILEPATH)
        data_from_data_csv = get_data_from_csv(DATA_CSV_FILEPATH)
        combined_pairs_of_factors = combine_pairs_of_factors(pairs_of_factors, data_from_data_csv)
        key = 'resolution+clashscore'
        value = combined_pairs_of_factors[key]

        intervals = get_intervals_from_boundaries(data_from_boundaries, key.split('+')[0])
        # print(intervals)
        factors_splitted_into_bins, bucket_numbers, borders, min_x, max_x, min_y, max_y, length = split_into_intervals(
            value, intervals, key)
        # print(factors_splitted_into_bins)

        print(len(borders))
        print(len(bucket_numbers))
        print(len(factors_splitted_into_bins))
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
        k = 0
        first_bucket = True
        for pair, number in zip(factors_splitted_into_bins, bucket_numbers):
            if j == len(factors_splitted_into_bins):
                last_bucket = True
            if k > 0:
                first_bucket = False
            border_low = borders[k]
            try:
                border_high = borders[k + 1]
            except IndexError:
                border_high = 0  # does not matter
            result_dict['GraphBuckets'].append(
                compute_data_for_interval(pair, number, border_low, border_high, last_bucket, first_bucket))
            j += 1
            k += 1
        print(result_dict)

    def test_result_for_interval_2(self):
        pairs_of_factors = get_pairs_of_factors_from_autoplot_csv(AUTOPLOT_FILEPATH)
        data_from_boundaries = get_data_from_csv(BOUNDARIES_FILEPATH)
        data_from_data_csv = get_data_from_csv(DATA_CSV_FILEPATH)
        combined_pairs_of_factors = combine_pairs_of_factors(pairs_of_factors, data_from_data_csv)
        key = 'releaseDate+clashscore'
        value = combined_pairs_of_factors[key]

        intervals = get_intervals_from_boundaries(data_from_boundaries, key.split('+')[0])
        # print(intervals)
        factors_splitted_into_bins, bucket_numbers, borders, min_x, max_x, min_y, max_y, length = split_into_intervals(
            value, intervals, key)
        print(len(borders))
        print(len(bucket_numbers))
        print(len(factors_splitted_into_bins))

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
        k = 0
        first_bucket = True
        for pair, number in zip(factors_splitted_into_bins, bucket_numbers):
            if j == len(factors_splitted_into_bins):
                last_bucket = True
            if k > 0:
                first_bucket = False
            border_low = borders[k]
            try:
                border_high = borders[k + 1]
            except IndexError:
                border_high = 0  # does not matter
            result_dict['GraphBuckets'].append(
                compute_data_for_interval(pair, number, border_low, border_high, last_bucket, first_bucket))
            j += 1
            k += 1
        print(result_dict)


if __name__ == '__main__':
    unittest.main()
