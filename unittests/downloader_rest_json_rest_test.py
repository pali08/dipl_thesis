import os
import unittest

from src.downloader_rest_json_rest import RestJsonDownloaderRest
from src.global_constants_and_functions import MOLECULES_FOLDER, SUMMARY_FOLDER, ASSEMBLY_FOLDER, remove_custom
from src.parser_json_rest import RestParser


class TestRestJsonDownloaderRest(unittest.TestCase):

    def test_assembly_file_downloading(self):
        os.mkdir(ASSEMBLY_FOLDER)
        RestJsonDownloaderRest('3wgt', ASSEMBLY_FOLDER, os.path.join(ASSEMBLY_FOLDER, '3wgt.json')).get_file()
        try:
            tst = RestParser(os.path.join(ASSEMBLY_FOLDER, '3wgt.json'),
                             os.path.join('.', 'input_data_2', 'ligandStats.csv')).json_dict['3wgt']
            test_assembly = True
        except Exception as e:
            test_assembly = False
            print(str(e))
        self.assertEqual(test_assembly, True)
        self.addCleanup(remove_custom, os.path.join('.', ASSEMBLY_FOLDER))

    def test_molecules_file_downloading(self):
        os.mkdir(MOLECULES_FOLDER)
        RestJsonDownloaderRest('3wgt', MOLECULES_FOLDER,
                               os.path.join(MOLECULES_FOLDER, '3wgt.json')).get_file()
        try:
            tst = RestParser(os.path.join(MOLECULES_FOLDER, '3wgt.json'),
                             os.path.join('.', 'input_data_2', 'ligandStats.csv')).json_dict['3wgt']
            test_molecules = True
        except Exception as e:
            test_molecules = False
            print(str(e))
        self.assertEqual(test_molecules, True)
        self.addCleanup(remove_custom, os.path.join('.', MOLECULES_FOLDER))

    def test_summary_file_downloading(self):
        os.mkdir(SUMMARY_FOLDER)
        RestJsonDownloaderRest('3wgt', SUMMARY_FOLDER, os.path.join(SUMMARY_FOLDER, '3wgt.json')).get_file()
        try:
            tst = RestParser(os.path.join(SUMMARY_FOLDER, '3wgt.json'),
                             os.path.join('.', 'input_data_2', 'ligandStats.csv')).json_dict['3wgt']
            test_summary = True
        except Exception as e:
            test_summary = False
            print(str(e))
        self.assertEqual(test_summary, True)
        self.addCleanup(remove_custom, os.path.join('.', SUMMARY_FOLDER))

    def test_downloading_non_existing_file(self):
        pass


if __name__ == '__main__':
    unittest.main()
