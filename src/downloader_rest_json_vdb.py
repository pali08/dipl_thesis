import json
import os
import sys

import requests

sys.path.append('..')
from src.global_constants_and_functions import VDB_JSON_UNIVERSAL_NAME
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
        self.save_filepath = os.path.join(os.path.dirname(save_filepath), VDB_JSON_UNIVERSAL_NAME)
        if not os.path.exists(os.path.dirname(self.save_filepath)):
            os.mkdir(os.path.join(os.path.dirname(self.save_filepath)))
        super().__init__(self.url, save_filepath)

    def set_url(self):
        self.url = FileDownloader.HTTP_SERVER_WEBCHEM + \
                   FileDownloader.HTTP_WEBCHEM_PATH_TO_VDB_FILES + \
                   self.molecule.upper() + FileDownloader.HTTP_WEBCHEM_SOURCE_BY_STRUCTURES
