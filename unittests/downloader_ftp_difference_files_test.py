import datetime
import glob
import json
import os
import time
import unittest

from src.downloader import FileDownloader
from src.downloader_ftp_difference_files import DifferenceFilesDownloader
from src.global_constants_and_functions import ADDED, LATEST_SUFFIX, MODIFIED, OBSOLETE, A_M_O_FILENAME, \
    METADATA_FILES_PATH


def is_timestamp(string):
    try:
        # datetime.datetime.strptime(string, "%Y %b %d %H:%M")
        datetime.datetime.strptime(string, "%Y%m%d%H%M%S")
        return True
    except ValueError:
        return False


class TestDifferenceFileDownloader(unittest.TestCase):
    """
    this case tests:
    getting new added/modified/obsolete files in case:
    - they don't exist yet (first run of update)
    - they exists and needs to be updated
    """
    timestamp_fake_dict = {
        FileDownloader.FTP_SERVER + FileDownloader.FTP_PATH_TO_A_M_O_FILES + MODIFIED + LATEST_SUFFIX: 'faketimestamp1',
        FileDownloader.FTP_SERVER + FileDownloader.FTP_PATH_TO_A_M_O_FILES + ADDED + LATEST_SUFFIX: 'faketimestamp2',
        FileDownloader.FTP_SERVER + FileDownloader.FTP_PATH_TO_A_M_O_FILES + OBSOLETE + LATEST_SUFFIX: 'faketimestamp3'
    }

    def step1(self):
        DifferenceFilesDownloader(MODIFIED).get_file()
        self.assertEqual(os.path.exists(os.path.join(METADATA_FILES_PATH, MODIFIED + LATEST_SUFFIX)), True)

        # self.assertEqual(False, True)

    def step2(self):
        DifferenceFilesDownloader(ADDED).get_file()
        self.assertEqual(os.path.exists(os.path.join(METADATA_FILES_PATH, ADDED + LATEST_SUFFIX)), True)

    def step3(self):
        DifferenceFilesDownloader(OBSOLETE).get_file()
        self.assertEqual(os.path.exists(os.path.join(METADATA_FILES_PATH, OBSOLETE + LATEST_SUFFIX)), True)

    def step4(self):
        with open(DifferenceFilesDownloader.timestamp_file, "r+") as file:
            data = json.load(file)
            data.update(self.timestamp_fake_dict)
        os.remove(DifferenceFilesDownloader.timestamp_file)
        with open(DifferenceFilesDownloader.timestamp_file, "w+") as file:
            json.dump(data, file, indent=4)

    def step5(self):
        DifferenceFilesDownloader(MODIFIED).get_file()
        first_condition = os.path.exists(os.path.join(METADATA_FILES_PATH, MODIFIED + LATEST_SUFFIX))
        print(str(first_condition))
        with open(METADATA_FILES_PATH + A_M_O_FILENAME, "r+") as file:
            data = json.load(file)
            second_condition = is_timestamp(
                data[FileDownloader.FTP_SERVER + FileDownloader.FTP_PATH_TO_A_M_O_FILES + MODIFIED + LATEST_SUFFIX])
        print(str(second_condition))
        self.assertEqual(first_condition and second_condition, True)

    def step6(self):
        DifferenceFilesDownloader(ADDED).get_file()
        first_condition = os.path.exists(os.path.join(METADATA_FILES_PATH, ADDED + LATEST_SUFFIX))
        with open(METADATA_FILES_PATH + A_M_O_FILENAME, "r+") as file:
            data = json.load(file)
            second_condition = is_timestamp(
                data[FileDownloader.FTP_SERVER + FileDownloader.FTP_PATH_TO_A_M_O_FILES + ADDED + LATEST_SUFFIX])
        self.assertEqual(first_condition and second_condition, True)

    def step7(self):
        DifferenceFilesDownloader(OBSOLETE).get_file()
        first_condition = os.path.exists(os.path.join(METADATA_FILES_PATH, OBSOLETE + LATEST_SUFFIX))
        with open(METADATA_FILES_PATH + A_M_O_FILENAME, "r+") as file:
            data = json.load(file)
            second_condition = is_timestamp(
                data[FileDownloader.FTP_SERVER + FileDownloader.FTP_PATH_TO_A_M_O_FILES + OBSOLETE + LATEST_SUFFIX])
        self.assertEqual(first_condition and second_condition, True)

    def step8(self):
        os.remove(DifferenceFilesDownloader.timestamp_file)
        os.remove(os.path.join(METADATA_FILES_PATH, ADDED + LATEST_SUFFIX))
        os.remove(os.path.join(METADATA_FILES_PATH, MODIFIED + LATEST_SUFFIX))
        os.remove(os.path.join(METADATA_FILES_PATH, OBSOLETE + LATEST_SUFFIX))

    def _steps(self):
        for name in dir(self):  # dir() result is implicitly sorted
            if name.startswith("step"):
                yield name, getattr(self, name)

    def test_steps(self):
        for name, step in self._steps():
            try:
                step()
                time.sleep(2)  # this should handle problem with too many connected users
            except Exception as e:
                self.fail("{} failed ({}: {})".format(step, type(e), e))


if __name__ == '__main__':
    unittest.main()
