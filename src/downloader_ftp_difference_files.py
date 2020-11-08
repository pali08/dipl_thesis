import os
import filecmp
import time
import os

from src.downloader_ftp import FtpFileDownloader


class DifferenceFilesDownloader(FtpFileDownloader):
    def __init__(self, url, save_filepath, wait_time):
        super().__init__(url, save_filepath)
        self.wait_time = wait_time

    def get_file(self):
        print('Downloading file: ' + str(self.save_filepath.rsplit(os.path.sep, 1)[1]))
        if not os.path.exists(self.save_filepath):
            super().get_file()
            print('New file was saved.')
            return
        else:
            self.save_filepath = self.save_filepath + '_temp'
            while True:
                super().get_file()
                if filecmp.cmp(self.save_filepath, self.save_filepath[:-5], shallow=False):
                    print('Files were not yet updated, waiting for' + str(self.wait_time) + 'seconds and try again')
                    time.sleep(int(self.wait_time))
                    continue
                else:
                    os.remove(self.save_filepath[:-5])
                    os.rename(self.save_filepath, self.save_filepath[:-5])
                    print('File was replaced with newer version.')
                    return

    def get_set_of_added_modified_or_obsolete_files(self):
        with open(self.save_filepath) as f:
            return [i.strip() for i in f.readlines()]


a = DifferenceFilesDownloader('ftp://ftp.ebi.ac.uk/pub/databases/msd/status/obsolete.late', './obsolete.latest', 10)
a.get_file()
