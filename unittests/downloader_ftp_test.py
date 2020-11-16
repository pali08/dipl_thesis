import time
import unittest
import os

from src.downloader_ftp import FtpFileDownloader


class TestFtpDownloader(unittest.TestCase):
    def test_is_connection_working(self):
        """
        checks that is_connection_working returns true if connection with ftp server is working
        """
        ftp_downloader = FtpFileDownloader('ftp://ftp.ebi.ac.uk/pub/databases/msd/status/obsolete.latest', '.')
        self.assertEqual(ftp_downloader.is_connection_working(), True)

    def test_get_file(self):
        ftp_downloader = FtpFileDownloader('ftp://ftp.ebi.ac.uk/pub/databases/msd/status/modified.latest',
                                           os.path.join('.', 'modified.latest'))
        ftp_downloader.get_file()
        print(os.path.join('.', 'modified.latest'))
        self.assertEqual(os.path.isfile(os.path.join('.', 'modified.latest')), True)
        self.addCleanup(os.remove, 'modified.latest')

    # TODO test situation where connection is working and file is not on FTP


if __name__ == '__main__':
    unittest.main()
