import datetime
import json
import os
import filecmp
import time
import os
from ftplib import FTP

from src.downloader_ftp import FtpFileDownloader


class DifferenceFilesDownloader(FtpFileDownloader):
    def __init__(self, url, save_filepath, wait_time):
        super().__init__(url, save_filepath)
        self.wait_time = wait_time
        self.timestamp_file = '..' + os.sep + 'metadata_files' + os.sep + 'added_modified_obsolete_timestamps.json'

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
        self.sync_timestamp()
        return

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
                file.seek(0)
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
            timestamp = datetime.datetime.strptime(str(datetime.datetime.now().year) + ' ' + time_str, "%Y %b %d %H:%M")
        timestamp_dict = {self.url: str(timestamp)}
        return timestamp_dict

    def get_timestamp_local(self):
        with open(self.timestamp_file, "r+") as file:
            data = json.load(file)
        return data[self.url]

    def get_set_of_added_modified_or_obsolete_files(self):
        with open(self.save_filepath) as f:
            return [i.strip() for i in f.readlines()]
