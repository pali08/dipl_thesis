import unittest

from src.global_constants_and_functions import NAN_VALUE, VDB_JSON_UNIVERSAL_NAME
from src.parser_pdb import PdbParser
from src.parser_json_vdb import VdbParser


class VdbParserTest(unittest.TestCase):
    def test_result_dict_not_empty(self):
        parser = VdbParser('/home/pali/diplomka_python/rawvdb/132d/' + VDB_JSON_UNIVERSAL_NAME)
        self.assertNotEqual(parser.result_dict, {})

    def test_result_dict_not_nan(self):
        parser = VdbParser('/home/pali/diplomka_python/rawvdb/2fl0/' + VDB_JSON_UNIVERSAL_NAME)
        print(parser.result_dict)
        values = parser.result_dict.values()
        nan_values = [NAN_VALUE for i in range(0, len(values))]
        self.assertNotEqual(values, nan_values)


if __name__ == '__main__':
    unittest.main()
