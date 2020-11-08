import ftplib
import sys
import time
import urllib

from src.downloader import FileDownloader
import shutil
import urllib.request as request
from contextlib import closing


class FtpFileDownloader(FileDownloader):

    def __init__(self, url, save_filepath):
        super().__init__(url, save_filepath)

    def get_file(self):
        """
        Check connection and download file trough ftp.
        !!! Overwrites existing file if not told otherwise
        """
        while not (self.is_connection_working() and self.file_exists_on_ftp()):
            print('Connection is not working or file not exists on ftp. Sleep 5 minutes and retry')
            time.sleep(300)
        with closing(request.urlopen(self.url, )) as r:
            with open(self.save_filepath, 'wb') as f:
                shutil.copyfileobj(r, f)

    def is_connection_working(self):
        try:
            ftplib.FTP(host=self.url.split('/')[2])
            return True
        except ftplib.socket.gaierror as sge:
            print('Problem encountered when connecting trough FTP: ' + str(sge) + '. Is the Internet working ?')
            return False
        except Exception as e:
            print(
                'System encountered problem when getting FTP file although connection with server is working:\n' + str(
                    e) + '\nPlease contact author of this program.')
            sys.exit()

    def file_exists_on_ftp(self):
        while not self.is_connection_working():
            print(
                'I wanted to try if file is on server, but even connection is not working. Wait 5 minutes and try again')
            time.sleep(300)
        try:
            urllib.request.urlopen(self.url)
            return True
        except urllib.error.URLError:
            return False
