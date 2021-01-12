import os
import sys
import unittest

sys.path.append('..')
from src.exe_get_json_precomputed_charts import get_pairs_of_factors_from_autoplot_csv, get_data_from_boundaries_csv, \
    combine_pairs_of_factors, split_into_intervals
from unittests.exe_get_json_precomputed_charts_test_verification_data import pairs_test, boundaries_test, \
    release_date_plus_clashscore

AUTOPLOT_FILEPATH = os.path.join('.', 'input_data_5', 'autoplot.csv')
BOUNDARIES_FILEPATH = os.path.join('.', 'input_data_5', 'boundaries.csv')
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

    def test_get_data_from_boundaries_csv(self):
        self.assertEqual(get_data_from_boundaries_csv(BOUNDARIES_FILEPATH), boundaries_test)

    def test_combine_pairs_of_factors(self):
        combined_pairs_of_factors = combine_pairs_of_factors(get_pairs_of_factors_from_autoplot_csv(AUTOPLOT_FILEPATH),
                                                             get_data_from_boundaries_csv(BOUNDARIES_FILEPATH))
        self.assertEqual(combined_pairs_of_factors['releaseDate+clashscore'], release_date_plus_clashscore)

    def test_split_into_intervals_1(self):
        print(split_into_intervals('test+split', test_split_into_intervals_input))

    def test_split_into_intervals_2(self):
        pass


if __name__ == '__main__':
    unittest.main()
