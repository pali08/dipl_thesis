import datetime
import json
import os
import time
from ftplib import FTP

from src.downloader_ftp import FtpFileDownloader


class DifferenceFilesDownloader(FtpFileDownloader):
    """
    Class for getting added.latest, modified.latest and obsolete.latest files. Files are stored in
    ../metadata_files folder. The time of the latest update is stored in
    ../metadata_files/added_modified_obsolete_timestamps.json.
    get_file() method checks, if files added.latest, modified.latest and obsolete.latest in metadata_files has
    same timestamp as files on ftp server. If result is True, it means, that files have not been updated. In that case
    it waits 5 minutes and tries again. This is repeated until files are updated on ftp server.
    """
    timestamp_file = '..' + os.sep + 'metadata_files' + os.sep + 'added_modified_obsolete_timestamps.json'

    def __init__(self, a_m_o):
        """
        :param a_m_o: added, modified or obsolete
        """
        self.a_m_o = a_m_o
        self.set_url()
        self.set_savepath()
        super().__init__(self.url, self.save_filepath)

    def get_file(self):
        print('Downloading file: ' + str(self.save_filepath.rsplit(os.path.sep, 1)[1]))
        if not os.path.exists(self.save_filepath):
            super().get_file()
            print('New file was saved.')
            self.sync_timestamp()
            return
        while self.get_timestamp_local() == self.get_timestamp_dict_ftp()[self.url]:
            print('File not yet updated on FTP server. Sleeping 5 minutes and repeating')
            time.sleep(300)
        super().get_file()
        print('File was updated.')
        self.sync_timestamp()
        return

    def set_url(self):
        self.url = 'ftp://ftp.ebi.ac.uk/pub/databases/msd/status/' + self.a_m_o + '.latest'

    def set_savepath(self):
        self.save_filepath = os.path.join('..', 'metadata_files', self.a_m_o + '.latest')

    def sync_timestamp(self):
        """
        get last modified date of file on ftp server
        and put it to json file in format:
        {'path/to/file/on/ftp': timestamp}
        """
        timestamp_dict = self.get_timestamp_dict_ftp()
        json_object = json.dumps(timestamp_dict, indent=4)
        if not os.path.exists(self.timestamp_file):
            with open(self.timestamp_file, "w") as outfile:
                outfile.write(json_object)
        else:
            with open(self.timestamp_file, "r+") as file:
                data = json.load(file)
                data.update(timestamp_dict)
            os.remove(self.timestamp_file)
            with open(self.timestamp_file, 'w+') as file:
                json.dump(data, file, indent=4)

    def get_timestamp_dict_ftp(self):
        ftp_connection = FTP(self.url.split('/')[2])
        lines = []
        ftp_connection.sendcmd("USER anonymous")
        ftp_dir = '/' + '/'.join(self.url.split('/')[3:])
        ftp_connection.dir(ftp_dir, lines.append)
        for line in lines:
            tokens = line.split(maxsplit=9)
            time_str = tokens[5] + " " + tokens[6] + " " + tokens[7]
        timestamp_dict = {self.url: str(datetime.datetime.now().year) + ' ' + time_str}
        return timestamp_dict

    def get_timestamp_local(self):
        with open(self.timestamp_file, "r+") as file:
            data = json.load(file)
        return data[self.url]

