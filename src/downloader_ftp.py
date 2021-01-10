import ftplib
import sys
import time
import urllib
import shutil
import urllib.request as request
from contextlib import closing
from urllib3 import HTTPSConnectionPool

sys.path.append('..')
from src.downloader import FileDownloader


class FtpFileDownloader(FileDownloader):

    def __init__(self, url, save_filepath):
        super().__init__(url, save_filepath)

    def get_file(self):
        """
        Check connection and download file trough ftp.
        !!! Overwrites existing file if not told otherwise
        """
        while not (self.is_connection_working()):
            print('Connection is not working. Reason should be printed above. Sleeping 5 minutes and retrying.')
            time.sleep(300)
        i = 0
        while True:
            if i >= 3:
                print('Looks like file {} is really not on FTP. Skipping.'.format(self.url))
                return
            if self.file_exists_on_ftp():
                with closing(request.urlopen(self.url, )) as r:
                    with open(self.save_filepath, 'wb') as f:
                        shutil.copyfileobj(r, f)
                        return
            else:
                print('According to requests.urlopen file {} "not exists" on FTP, but this might not be true. '
                      'Sleeping 1 minute and retrying download. Retry will be done {} more times'.format(self.url,
                                                                                                         3 - (i + 1)))
                time.sleep(60)
                i += 1
                continue
        # print('WARNING: Connection is OK, but system was not able to get file. Skipping.')

    def is_connection_working(self):
        try:
            ftplib.FTP(host=self.url.split('/')[2])
            return True
        except ftplib.socket.gaierror as sge:
            print(str(sge))
            print('socket.gaierror - probably internet connection is not working')
            return False
        except ftplib.error_temp as et:
            print(str(et))
            print('error_temp - this probably means, that too many users are connected to server.\n'
                  'Or we are downloading files too fast one after another')
            return False
        except ConnectionRefusedError as cre:
            print(
                'ConnectionRefusedError: connection to main page ftp.ebi.ac.uk does not working, \n'
                'but download of file to {} might be OK. Program will continue and tries to get file'.format(
                    str(self.save_filepath)))
            return True
        except TimeoutError:
            print(
                'TimeoutError: connection to main page ftp.ebi.ac.uk does not working, \n'
                'but download of file to {} might be OK. Program will continue and tries to get file'.format(
                    str(self.save_filepath)))
            return True
        except Exception as e:
            print(str(self.save_filepath) +
                  'Program encountered exception when testing connection:\n' + str(
                e) + '. This exception was not encountered during testing and program do not know how to handle it.\n' +
                  '\nPlease contact author (p.mikulaj@mail.muni.cz). Program will be exited. '
                  'Try execute it again in few minutes')
            sys.exit()

    def file_exists_on_ftp(self):
        while not self.is_connection_working():
            print(
                'I wanted to try if file is on server, but even connection is not working. Wait 5 minutes and try again')
            time.sleep(300)
        try:
            urllib.request.urlopen(self.url)
            print('True - file exists')
            return True
        except urllib.error.URLError:
            print('False - file not exists')
            return False
