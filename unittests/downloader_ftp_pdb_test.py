import os
import time
import unittest

from src import global_constants_and_functions
from src.downloader_pdb import PdbDownloader
from src.global_constants_and_functions import MMCIF_UPDATED_SUFFIX
from src.parser_pdb import PdbParser


class TestFtpPdbDownloader(unittest.TestCase):
    def test_file_downloading(self):
        PdbDownloader('1flv', os.path.join('.', '1flv' + MMCIF_UPDATED_SUFFIX)).get_file()
        pdb_id = PdbParser(os.path.join('.', '1flv' + MMCIF_UPDATED_SUFFIX)).result_dict['PDB ID']
        self.assertEqual(pdb_id.lower() == '1flv', True)
        self.addCleanup(os.remove, '1flv' + MMCIF_UPDATED_SUFFIX)

    def test_downloading_non_existing_file(self):
        pass


if __name__ == '__main__':
    unittest.main()
