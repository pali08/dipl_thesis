import json

import requests

from src.downloader import FileDownloader


class RestJsonDownloader(FileDownloader):
    def __init__(self, molecule, rest_type, save_filepath):
        """
        :param molecule: 4 letters code
        :param rest_type: assembly, molecules or summary
        :param save_filepath:
        """
        self.molecule = molecule
        self.rest_type = rest_type
        self.url = self.get_url()
        super().__init__(self.url, save_filepath)

    def get_url(self):
        return 'https://www.ebi.ac.uk/pdbe/api/pdb/entry/' + self.rest_type + '/' + self.molecule

    def get_file(self):
        json_dict = requests.get(self.url).json()
        with open(self.save_filepath, 'w+') as file:
            json.dump(json_dict, self.save_filepath, indent=4)
