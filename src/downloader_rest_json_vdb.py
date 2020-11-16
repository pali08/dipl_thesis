import json

import requests

from src.downloader import FileDownloader
from src.downloader_rest_json import RestJsonDownloader


class RestJsonDownloaderVdb(RestJsonDownloader):
    def __init__(self, molecule, save_filepath):
        """
        :param molecule: 4 letters code
        :param save_filepath:
        """
        self.molecule = molecule
        self.set_url()
        super().__init__(self.url, save_filepath)

    def set_url(self):
        self.url = 'http://webchem.ncbr.muni.cz/Platform/ValidatorDb/Data/' + self.molecule.upper() + '?source' \
                                                                                                      '=ByStructure'
