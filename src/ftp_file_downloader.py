from src.file_downloader import FileDownloader
import shutil
import urllib.request as request
from contextlib import closing


class FtpFileDownloader(FileDownloader):

    def __init__(self, url, save_filepath):
        super().__init__(url, save_filepath)

    def get_file(self):
        with closing(request.urlopen(self.url, )) as r:
            with open(self.save_filepath, 'wb') as f:
                shutil.copyfileobj(r, f)
