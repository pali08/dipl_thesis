import os
import time
import unittest

from src.downloader_ftp_pdb import PdbDownloader
from src.parser_pdb import PdbParser


class TestFtpPdbDownloader(unittest.TestCase):
    def test_file_downloading(self):
        PdbDownloader('1flv', os.path.join('.', '1flv_updated.cif')).get_file()
        pdb_id = PdbParser(os.path.join('.', '1flv_updated.cif')).result_dict['PDB ID']
        self.assertEqual(pdb_id.lower() == '1flv', True)
        self.addCleanup(os.remove, '1flv_updated.cif')


if __name__ == '__main__':
    unittest.main()
