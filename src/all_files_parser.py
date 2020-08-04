import os

from src.pdb_parser import PdbParser
from src.pdb_vdb_computer import PdbVdbComputer
from src.vdb_parser import VdbParser


class AllFilesParser:

    def __init__(self, molecule, *filepaths):
        self.filepaths = filepaths
        self.molecule = molecule
        self.pdb_dict = PdbParser(self.get_pdb_filepath())
        self.vdb_dict = VdbParser(self.get_vdb_filepath())
        self.pdb_vdb_dict = PdbVdbComputer(self.pdb_dict, self.vdb_dict)
        self.result_dict = {**self.pdb_dict, **self.vdb_dict, **self.pdb_vdb_dict}

    def get_pdb_filepath(self):
        return os.path.join(self.filepaths[0], self.molecule + '_updated.mmcif')

    def get_vdb_filepath(self):
        return os.path.join(self.filepaths[1], self.molecule, 'result.json')

    def get_xml_filepath(self):
        pass
        # TODO return os.path.join(self.filepaths[2], self.molecule + '_validation.xml')

    def get_rest_filepath(self, subfolder):
        pass
        # TODO return os.path.join(self.filepaths[3], subfolder, self.molecule + '.json')
