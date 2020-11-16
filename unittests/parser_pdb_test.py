import unittest

from src.global_constants_and_functions import NAN_VALUE
from src.parser_pdb import PdbParser


class PdbParserTest(unittest.TestCase):
    def test_result_dict_not_empty(self):
        parser = PdbParser('/home/pali/diplomka_python/rawpdbe/2fl0_updated.cif')
        print(parser.result_dict)
        self.assertNotEqual(parser.result_dict, {})

    def test_result_dict_not_nan(self):
        parser = PdbParser('/home/pali/diplomka_python/rawpdbe/2fl0_updated.cif')
        values = parser.result_dict.values()
        nan_values = [NAN_VALUE for i in range(0, len(values))]
        self.assertNotEqual(values, nan_values)


if __name__ == '__main__':
    unittest.main()
