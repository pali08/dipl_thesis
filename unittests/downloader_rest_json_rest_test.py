import os
import shutil
import unittest

from src.downloader_rest_json_rest import RestJsonDownloaderRest
from src.global_constants_and_functions import MOLECULES_FOLDER, SUMMARY_FOLDER, ASSEMBLY_FOLDER
from src.parser_json_rest import RestParser


def remove(path):
    """ param <path> could either be relative or absolute. """
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains
    else:
        raise ValueError("file {} is not a file or dir.".format(path))


class TestRestJsonDownloaderRest(unittest.TestCase):

    def test_assembly_file_downloading(self):
        os.mkdir(ASSEMBLY_FOLDER)
        RestJsonDownloaderRest('3wgt', ASSEMBLY_FOLDER, os.path.join(ASSEMBLY_FOLDER, '3wgt.json')).get_file()
        try:
            tst = RestParser(os.path.join(ASSEMBLY_FOLDER, '3wgt.json'),
                             '/home/pali/diplomka_python/ligandStats.csv').json_dict['3wgt']
            test_assembly = True
        except Exception as e:
            test_assembly = False
            print(str(e))
        self.assertEqual(test_assembly, True)
        self.addCleanup(remove, os.path.join('.', ASSEMBLY_FOLDER))

    def test_molecules_file_downloading(self):
        os.mkdir(MOLECULES_FOLDER)
        RestJsonDownloaderRest('3wgt', MOLECULES_FOLDER,
                               os.path.join(MOLECULES_FOLDER, '3wgt.json')).get_file()
        try:
            tst = RestParser(os.path.join(MOLECULES_FOLDER, '3wgt.json'),
                             '/home/pali/diplomka_python/ligandStats.csv').json_dict['3wgt']
            test_molecules = True
        except Exception as e:
            test_molecules = False
            print(str(e))
        self.assertEqual(test_molecules, True)
        self.addCleanup(remove, os.path.join('.', MOLECULES_FOLDER))

    def test_summary_file_downloading(self):
        os.mkdir(SUMMARY_FOLDER)
        RestJsonDownloaderRest('3wgt', SUMMARY_FOLDER, os.path.join(SUMMARY_FOLDER, '3wgt.json')).get_file()
        try:
            tst = RestParser(os.path.join(SUMMARY_FOLDER, '3wgt.json'),
                             '/home/pali/diplomka_python/ligandStats.csv').json_dict['3wgt']
            test_summary = True
        except Exception as e:
            test_summary = False
            print(str(e))
        self.assertEqual(test_summary, True)
        self.addCleanup(remove, os.path.join('.', SUMMARY_FOLDER))


if __name__ == '__main__':
    unittest.main()
