import json
import sys

import requests

sys.path.append('..')
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
        self.url = FileDownloader.HTTP_SERVER_WEBCHEM + \
                   FileDownloader.HTTP_WEBCHEM_PATH_TO_VDB_FILES + \
                   self.molecule.upper() + FileDownloader.HTTP_WEBCHEM_SOURCE_BY_STRUCTURES
