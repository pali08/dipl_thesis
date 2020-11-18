import os
import sys

from src.global_constants_and_functions import MMCIF_UPDATED_SUFFIX, VDB_JSON_UNIVERSAL_NAME, XML_VALIDATION_SUFFIX, \
    ASSEMBLY_FOLDER, MOLECULES_FOLDER, SUMMARY_FOLDER, JSON_SUFFIX


class FilepathGenerator:

    def __init__(self, molecule, *filepaths):
        self.filepaths = filepaths
        self.molecule = molecule

    def get_pdb_filepath(self):
        return os.path.join(self.filepaths[0], self.molecule + MMCIF_UPDATED_SUFFIX)

    def get_vdb_filepath(self):
        return os.path.join(self.filepaths[1], self.molecule, VDB_JSON_UNIVERSAL_NAME)

    def get_xml_filepath(self):
        return os.path.join(self.filepaths[2], self.molecule + XML_VALIDATION_SUFFIX)

    def get_rest_filepath(self):
        assembly = os.path.join(self.filepaths[3], ASSEMBLY_FOLDER, self.molecule + JSON_SUFFIX)
        molecules = os.path.join(self.filepaths[3], MOLECULES_FOLDER, self.molecule + JSON_SUFFIX)
        summary = os.path.join(self.filepaths[3], SUMMARY_FOLDER, self.molecule + JSON_SUFFIX)
        return assembly, molecules, summary

    def get_all_paths(self):
        return self.get_pdb_filepath(), self.get_vdb_filepath(), self.get_xml_filepath(), *self.get_rest_filepath()
