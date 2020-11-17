import time
import unittest
import os

from src.downloader import FileDownloader
from src.downloader_ftp import FtpFileDownloader
from src.global_constants_and_functions import OBSOLETE, LATEST_SUFFIX, MODIFIED


class TestFtpDownloader(unittest.TestCase):
    def test_is_connection_working(self):
        """
        checks that is_connection_working returns true if connection with ftp server is working
        """
        ftp_downloader = FtpFileDownloader(
            FileDownloader.FTP_SERVER + FileDownloader.FTP_PATH_TO_A_M_O_FILES + OBSOLETE + LATEST_SUFFIX, '.')
        self.assertEqual(ftp_downloader.is_connection_working(), True)

    def test_get_file(self):
        ftp_downloader = FtpFileDownloader(
            FileDownloader.FTP_SERVER + FileDownloader.FTP_PATH_TO_A_M_O_FILES + MODIFIED + LATEST_SUFFIX,
            os.path.join('.', MODIFIED + LATEST_SUFFIX))
        ftp_downloader.get_file()
        print(os.path.join('.', MODIFIED + LATEST_SUFFIX))
        self.assertEqual(os.path.isfile(os.path.join('.', MODIFIED + LATEST_SUFFIX)), True)
        self.addCleanup(os.remove, MODIFIED + LATEST_SUFFIX)

    # TODO test situation where connection is working and file is not on FTP


if __name__ == '__main__':
    unittest.main()
