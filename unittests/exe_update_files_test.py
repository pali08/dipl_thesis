import os
import unittest
import sys
from shutil import copy2

from src.global_constants_and_functions import ADDED, LATEST_SUFFIX, METADATA_FILES_PATH, MODIFIED, OBSOLETE

sys.path.append('..')
from src.exe_update_files import get_lists_of_changed_molecules, get_filepaths_from_list

INPUT_DATA_PATH = os.path.join('.', 'input_data')
pdb_filepath = './input_data/pdb'
vdb_filepath = './input_data/vdb'
xml_filepath = './input_data/valid_xml'
rest_filepath = './input_data/rest'


class MyTestCase(unittest.TestCase):
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

    def test_remove(self):
        pass

    def test_remove_non_existing_file(self):
        pass


if __name__ == '__main__':
    unittest.main()
