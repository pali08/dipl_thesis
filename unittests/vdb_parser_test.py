import unittest

from src.global_constants_and_functions import NAN_VALUE
from src.pdb_parser import PdbParser
from src.vdb_parser import VdbParser


class VdbParserTest(unittest.TestCase):
    def test_result_dict_not_empty(self):
        parser = VdbParser('/home/pali/diplomka_python/rawvdb/132d/result.json')
        self.assertNotEqual(parser.result_dict, {})

    def test_result_dict_not_nan(self):
        parser = VdbParser('/home/pali/diplomka_python/rawvdb/132d/result.json')
        values = parser.result_dict.values()
        nan_values = [NAN_VALUE for i in range(0, len(values))]
        self.assertNotEqual(values, nan_values)


if __name__ == '__main__':
    unittest.main()
