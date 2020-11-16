import os
import shutil

from src.downloader_ftp import FtpFileDownloader
import gzip


class PdbDownloader(FtpFileDownloader):
    def __init__(self, molecule, save_filepath):
        self.molecule = molecule
        self.set_url()
        super().__init__(self.url, save_filepath)

    def set_url(self):
        self.url = 'ftp://ftp.ebi.ac.uk/pub/databases/pdb/data/structures/divided/mmCIF/' + self.molecule[
                                                                                            1:-1] + '/' + \
                   self.molecule + '.cif.gz'

    def get_file(self):
        """
        The file is packed in .gz, we need to unpack it
        """
        self.save_filepath = self.save_filepath + '.gz'
        super().get_file()
        with gzip.open(self.save_filepath, 'rb') as file_input:
            with open(self.save_filepath[:-3], 'wb') as file_output:
                # [:-3] - without gzip
                shutil.copyfileobj(file_input, file_output)
        os.remove(self.save_filepath)
