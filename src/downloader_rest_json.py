import json
import sys
import time
import requests

sys.path.append('..')
from src.downloader import FileDownloader


class RestJsonDownloader(FileDownloader):
    def __init__(self, url, save_filepath):
        """
        :param save_filepath:
        """
        super().__init__(url, save_filepath)

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
        try:
            json_dict = requests.get(self.url).json()
            with open(self.save_filepath, 'w+') as file:
                json.dump(json_dict, file, indent=4)
        except json.decoder.JSONDecodeError:
            print('WARNING: Connection is OK, but system was not able to get file. Skipping.')
