import io
import os
import shutil
import unittest
import sys
from shutil import copy2

sys.path.append('..')
from src.global_constants_and_functions import ADDED, LATEST_SUFFIX, METADATA_FILES_PATH, MODIFIED, OBSOLETE, \
    remove_custom, DirOrFileNotFoundError
from src.exe_update_files import get_lists_of_changed_molecules, get_filepaths_from_list, remove_files

INPUT_DATA_PATH = os.path.join('.', 'input_data')
INPUT_DATA_PATH_BCK = os.path.join('.', 'input_data_backup')
pdb_filepath = os.path.join('.', 'input_data', 'pdb')
vdb_filepath = os.path.join('.', 'input_data', 'vdb')
xml_filepath = os.path.join('.', 'input_data', 'valid_xml')
rest_filepath = os.path.join('.', 'input_data', 'rest')
non_existing_files = 'File or directory ' + os.path.join('.', 'input_data', 'pdb',
                                                         '1omg_updated.cif') + ' not exists so not removed.' + \
                     os.linesep + \
                     'File or directory ' + os.path.join('.', 'input_data', 'vdb',
                                                         '1omg') + ' not exists so not removed.' + \
                     os.linesep + \
                     'File or directory ' + os.path.join('.', 'input_data', 'valid_xml',
                                                         '1omg_validation.xml') + ' not exists so not removed.' + \
                     os.linesep + \
                     'File or directory ' + os.path.join('.', 'input_data', 'rest', 'assembly',
                                                         '1omg.json') + ' not exists so not removed.' + \
                     os.linesep + \
                     'File or directory ' + os.path.join('.', 'input_data', 'rest', 'molecules',
                                                         '1omg.json') + ' not exists so not removed.' + \
                     os.linesep + \
                     'File or directory ' + os.path.join('.', 'input_data', 'rest', 'summary',
                                                         '1omg.json') + ' not exists so not removed.' + \
                     os.linesep + \
                     'File or directory ' + os.path.join('.', 'input_data', 'pdb',
                                                         '1img_updated.cif') + ' not exists so not removed.' + \
                     os.linesep + \
                     'File or directory ' + os.path.join('.', 'input_data', 'vdb',
                                                         '1img') + ' not exists so not removed.' + \
                     os.linesep + \
                     'File or directory ' + os.path.join('.', 'input_data', 'valid_xml',
                                                         '1img_validation.xml') + ' not exists so not removed.' + \
                     os.linesep + \
                     'File or directory ' + os.path.join('.', 'input_data', 'rest', 'assembly',
                                                         '1img.json') + ' not exists so not removed.' + \
                     os.linesep + \
                     'File or directory ' + os.path.join('.', 'input_data', 'rest', 'molecules',
                                                         '1img.json') + ' not exists so not removed.' + \
                     os.linesep + \
                     'File or directory ' + os.path.join('.', 'input_data', 'rest', 'summary',
                                                         '1img.json') + ' not exists so not removed.' \
                     + os.linesep


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        backup files before
        :return:
        """
        shutil.copytree(INPUT_DATA_PATH, INPUT_DATA_PATH_BCK)

    @classmethod
    def tearDownClass(cls):
        """
        restore files after test
        :return:
        """
        if os.path.exists(os.path.join(INPUT_DATA_PATH_BCK)):
            remove_custom(os.path.join(INPUT_DATA_PATH))
            os.rename(INPUT_DATA_PATH_BCK, INPUT_DATA_PATH)
        else:
            print('input_data does not exist, input_data will not be removed')

    def test_get_filepaths_from_lists(self):
        for i in [os.path.join(INPUT_DATA_PATH, ADDED + LATEST_SUFFIX),
                  os.path.join(INPUT_DATA_PATH, MODIFIED + LATEST_SUFFIX),
                  os.path.join(INPUT_DATA_PATH, OBSOLETE + LATEST_SUFFIX)]:
            copy2(i, METADATA_FILES_PATH)
        a, m, o = get_lists_of_changed_molecules()
        a_fp = get_filepaths_from_list(a, pdb_filepath, vdb_filepath, xml_filepath, rest_filepath)
        m_fp = get_filepaths_from_list(m, pdb_filepath, vdb_filepath, xml_filepath, rest_filepath)
        o_fp = get_filepaths_from_list(o, pdb_filepath, vdb_filepath, xml_filepath, rest_filepath)
        result_a = a_fp == [('./input_data/pdb/6hpj_updated.cif', './input_data/vdb/6hpj/result.json',
                             './input_data/valid_xml/6hpj_validation.xml', './input_data/rest/assembly/6hpj.json',
                             './input_data/rest/molecules/6hpj.json', './input_data/rest/summary/6hpj.json'), (
                                './input_data/pdb/6kml_updated.cif', './input_data/vdb/6kml/result.json',
                                './input_data/valid_xml/6kml_validation.xml',
                                './input_data/rest/assembly/6kml.json',
                                './input_data/rest/molecules/6kml.json', './input_data/rest/summary/6kml.json'), (
                                './input_data/pdb/6kmq_updated.cif', './input_data/vdb/6kmq/result.json',
                                './input_data/valid_xml/6kmq_validation.xml',
                                './input_data/rest/assembly/6kmq.json',
                                './input_data/rest/molecules/6kmq.json', './input_data/rest/summary/6kmq.json'), (
                                './input_data/pdb/6l9k_updated.cif', './input_data/vdb/6l9k/result.json',
                                './input_data/valid_xml/6l9k_validation.xml',
                                './input_data/rest/assembly/6l9k.json',
                                './input_data/rest/molecules/6l9k.json', './input_data/rest/summary/6l9k.json'), (
                                './input_data/pdb/6l9l_updated.cif', './input_data/vdb/6l9l/result.json',
                                './input_data/valid_xml/6l9l_validation.xml',
                                './input_data/rest/assembly/6l9l.json',
                                './input_data/rest/molecules/6l9l.json', './input_data/rest/summary/6l9l.json')]
        result_m = m_fp == [('./input_data/pdb/1h3j_updated.cif', './input_data/vdb/1h3j/result.json',
                             './input_data/valid_xml/1h3j_validation.xml',
                             './input_data/rest/assembly/1h3j.json',
                             './input_data/rest/molecules/1h3j.json', './input_data/rest/summary/1h3j.json'),
                            ('./input_data/pdb/1o7a_updated.cif', './input_data/vdb/1o7a/result.json',
                             './input_data/valid_xml/1o7a_validation.xml',
                             './input_data/rest/assembly/1o7a.json',
                             './input_data/rest/molecules/1o7a.json', './input_data/rest/summary/1o7a.json'),
                            ('./input_data/pdb/1w5r_updated.cif', './input_data/vdb/1w5r/result.json',
                             './input_data/valid_xml/1w5r_validation.xml',
                             './input_data/rest/assembly/1w5r.json',
                             './input_data/rest/molecules/1w5r.json', './input_data/rest/summary/1w5r.json'),
                            ('./input_data/pdb/2bgy_updated.cif', './input_data/vdb/2bgy/result.json',
                             './input_data/valid_xml/2bgy_validation.xml',
                             './input_data/rest/assembly/2bgy.json',
                             './input_data/rest/molecules/2bgy.json', './input_data/rest/summary/2bgy.json'),
                            ('./input_data/pdb/2bwf_updated.cif', './input_data/vdb/2bwf/result.json',
                             './input_data/valid_xml/2bwf_validation.xml',
                             './input_data/rest/assembly/2bwf.json',
                             './input_data/rest/molecules/2bwf.json', './input_data/rest/summary/2bwf.json'),
                            ('./input_data/pdb/2vev_updated.cif', './input_data/vdb/2vev/result.json',
                             './input_data/valid_xml/2vev_validation.xml',
                             './input_data/rest/assembly/2vev.json',
                             './input_data/rest/molecules/2vev.json', './input_data/rest/summary/2vev.json'),
                            ('./input_data/pdb/2vew_updated.cif', './input_data/vdb/2vew/result.json',
                             './input_data/valid_xml/2vew_validation.xml',
                             './input_data/rest/assembly/2vew.json',
                             './input_data/rest/molecules/2vew.json', './input_data/rest/summary/2vew.json')]
        result_o = o_fp == [('./input_data/pdb/6vnn_updated.cif', './input_data/vdb/6vnn/result.json',
                             './input_data/valid_xml/6vnn_validation.xml',
                             './input_data/rest/assembly/6vnn.json',
                             './input_data/rest/molecules/6vnn.json', './input_data/rest/summary/6vnn.json')]
        self.addCleanup(os.remove, os.path.join(METADATA_FILES_PATH, ADDED + LATEST_SUFFIX))
        self.addCleanup(os.remove, os.path.join(METADATA_FILES_PATH, MODIFIED + LATEST_SUFFIX))
        self.addCleanup(os.remove, os.path.join(METADATA_FILES_PATH, OBSOLETE + LATEST_SUFFIX))
        self.assertEqual(result_a and result_m and result_o, True)

    def test_remove_a_non_existing_file(self):
        molecules_to_remove = ['1omg', '1img']
        filepaths = get_filepaths_from_list(molecules_to_remove, pdb_filepath, vdb_filepath, xml_filepath,
                                            rest_filepath)
        orig_stdout = sys.stdout
        captured_output = io.StringIO()  # Create StringIO object
        sys.stdout = captured_output  # and redirect stdout.
        remove_files(filepaths)
        sys.stdout = orig_stdout  # Reset redirect.
        print(captured_output.getvalue())
        self.assertEqual(captured_output.getvalue(), non_existing_files)

    def test_remove_b(self):
        """
        tests are executed in alphabetical order - a must be executed first as b removes existing files
        :return:
        """
        molecules_to_remove = ['1cam', '1kvp', '1iob']
        filepaths = get_filepaths_from_list(molecules_to_remove, pdb_filepath, vdb_filepath, xml_filepath,
                                            rest_filepath)
        # print(filepaths)
        for i in filepaths:
            for j in i:
                if not os.path.exists(j):
                    raise DirOrFileNotFoundError('Directory or file' + str(j) + 'not exists before removing files')
        remove_files(filepaths)
        filepaths_not_exist_after = True
        for i in filepaths:
            for j in i:
                if os.path.exists(j):
                    filepaths_not_exist_after = False
                    break
        self.assertEqual(filepaths_not_exist_after, True)


if __name__ == '__main__':
    unittest.main()
