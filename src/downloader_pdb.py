import sys
import time

import requests

sys.path.append('..')
from src.downloader import FileDownloader
from src.global_constants_and_functions import MMCIF_UPDATED_SUFFIX


class PdbDownloader(FileDownloader):
    def __init__(self, molecule, save_filepath):
        self.url = FileDownloader.HTTP_SERVER + FileDownloader.HTTP_PATH_TO_PDB_UPDATED + \
                   molecule + MMCIF_UPDATED_SUFFIX
        self.molecule = molecule
        super().__init__(self.url, save_filepath)

    def is_connection_working(self):
        try:
            requests.get(self.url)
            return True
        except requests.exceptions.ConnectionError as rec:
            return False

    def get_file(self):
        while not self.is_connection_working():
            print('Connection is not working. Sleeping 5 minutes and retrying')
            time.sleep(300)
        text_string = requests.get(self.url).text
        try:
            if not ('url not found' in text_string.lower()):
                with open(self.save_filepath, 'w+') as file:
                    file.write(text_string)
            else:
                print('WARNING: Requesting file got "URL not found" - probably file was deleted- skipping')
        except FileNotFoundError:
            print(self.save_filepath + ' problem - with open not working')
            print('WARNING: Connection is OK, but system was not able to get file. Skipping.')
