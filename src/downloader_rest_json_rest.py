import json
import os
import sys

import requests

sys.path.append('..')
from src.downloader import FileDownloader
from src.downloader_rest_json import RestJsonDownloader


class RestJsonDownloaderRest(RestJsonDownloader):
    def __init__(self, molecule, a_m_s, save_filepath):
        """
        :param molecule: 4 letters code
        :param a_m_s: assembly, molecules or summary
        :param save_filepath:
        """
        self.molecule = molecule
        self.a_m_s = a_m_s
        self.set_url()
        print('filepath is' + save_filepath)
        # self.save_filepath = os.path.join(os.path.dirname(save_filepath), a_m_s)
        super().__init__(self.url, save_filepath)

    def set_url(self):
        self.url = FileDownloader.HTTP_SERVER + FileDownloader.HTTP_PATH_TO_REST_FILES + self.a_m_s + '/' + self.molecule
