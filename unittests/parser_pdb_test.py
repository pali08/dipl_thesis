import os
import unittest

from src import global_constants_and_functions
from src.global_constants_and_functions import NAN_VALUE, MMCIF_UPDATED_SUFFIX
from src.parser_pdb import PdbParser


class PdbParserTest(unittest.TestCase):
    def test_result_dict_not_empty(self):
        parser = PdbParser(
            os.path.join('.', 'input_data', 'pdb', '2fl0') + MMCIF_UPDATED_SUFFIX)
        print(parser.result_dict)
        self.assertNotEqual(parser.result_dict, {})

    def test_result_dict_not_nan(self):
        parser = PdbParser(
            os.path.join('.', 'input_data', 'pdb', '2fl0') + MMCIF_UPDATED_SUFFIX)
        values = parser.result_dict.values()
        nan_values = [NAN_VALUE for i in range(0, len(values))]
        self.assertNotEqual(values, nan_values)


if __name__ == '__main__':
    unittest.main()
