import csv
import unittest


class FinalDictResultRandomTest(unittest.TestCase):

    def get_original_data_csv_file(self, filename):
        """
        :param filename:
        :return:
        """
        with open(filename, mode='r', encoding='utf-8') as data:
            reader = csv.reader(data, delimiter=';')
            header = next(reader)
            import random
            sample_length = 10
            reader_list = list(reader)
            random_molecules_samples = random.sample(reader_list, sample_length)
            self.random_data_csv_dict = [
                dict((zip([header for j in range(0, sample_length)][i], random_molecules_samples[i]))) for i in
                range(0, sample_length)]

    def get_data_from_data_csv_dict(self):
        self.molecules = [self.random_data_csv_dict[i]['PDB ID'] for i in range(0, len(self.random_data_csv_dict))]

    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
