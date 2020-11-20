import os
import shutil
import sys
import gzip

from src import global_constants_and_functions

sys.path.append('..')
from src.downloader import FileDownloader
from src.downloader_ftp import FtpFileDownloader
from src.global_constants_and_functions import XML_VALIDATION_SUFFIX, SUFFIX_GZIP


class XmlValidationDownloader(FtpFileDownloader):
    def __init__(self, molecule, save_filepath):
        self.molecule = molecule
        self.set_url()
        super().__init__(self.url, save_filepath)

    def set_url(self):
        self.url = FileDownloader.FTP_SERVER + FileDownloader.FTP_PATH_TO_VALIDATION_REPORT_FILES + \
                   self.molecule[1:-1] + '/' + self.molecule + '/' + self.molecule + \
                   XML_VALIDATION_SUFFIX + SUFFIX_GZIP

    def get_file(self):
        """
        The file is packed in .gz, we need to unpack it
        """
        self.save_filepath = self.save_filepath + SUFFIX_GZIP
        super().get_file()
        # ungzip if exists
        if os.path.exists(self.save_filepath):
            with gzip.open(self.save_filepath, 'rb') as file_input:
                with open(self.save_filepath[:-3], 'wb') as file_output:
                    # [:-3] - without gzip
                    shutil.copyfileobj(file_input, file_output)
            os.remove(self.save_filepath)
