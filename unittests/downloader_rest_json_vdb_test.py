import os
import unittest

from src.downloader_rest_json_vdb import RestJsonDownloaderVdb
from src.global_constants_and_functions import is_float
from src.parser_json_vdb import VdbParser


class TestRestJsonDownloaderVdb(unittest.TestCase):
    def test_file_downloading(self):
        RestJsonDownloaderVdb('3wgt', os.path.join('.', '3wgt.json')).get_file()
        hetatm_count_filtered = VdbParser(os.path.join('.', '3wgt.json')).result_dict['hetatmCountFiltered']
        self.assertEqual(is_float(hetatm_count_filtered), True)
        self.addCleanup(os.remove, '3wgt.json')

    def test_downloading_non_existing_file(self):
        pass


if __name__ == '__main__':
    unittest.main()
