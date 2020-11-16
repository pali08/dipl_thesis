import datetime
import glob
import json
import os
import time
import unittest

from src.downloader_ftp_difference_files import DifferenceFilesDownloader


def is_timestamp(string):
    try:
        datetime.datetime.strptime(string, "%Y %b %d %H:%M")
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
        "ftp://ftp.ebi.ac.uk/pub/databases/msd/status/modified.latest": "faketimestamp1",
        "ftp://ftp.ebi.ac.uk/pub/databases/msd/status/added.latest": "faketimestamp2",
        "ftp://ftp.ebi.ac.uk/pub/databases/msd/status/obsolete.latest": "faketimestamp3"
    }

    def step1(self):
        DifferenceFilesDownloader('modified').get_file()
        self.assertEqual(os.path.exists('../metadata_files/modified.latest'), True)
        # self.assertEqual(False, True)

    def step2(self):
        DifferenceFilesDownloader('added').get_file()
        self.assertEqual(os.path.exists('../metadata_files/added.latest'), True)

    def step3(self):
        DifferenceFilesDownloader('obsolete').get_file()
        self.assertEqual(os.path.exists('../metadata_files/obsolete.latest'), True)

    def step4(self):
        with open(DifferenceFilesDownloader.timestamp_file, "r+") as file:
            data = json.load(file)
            data.update(self.timestamp_fake_dict)
        os.remove(DifferenceFilesDownloader.timestamp_file)
        with open(DifferenceFilesDownloader.timestamp_file, "w+") as file:
            json.dump(data, file, indent=4)

    def step5(self):
        DifferenceFilesDownloader('modified').get_file()
        first_condition = os.path.exists('../metadata_files/modified.latest')
        print(str(first_condition))
        with open('../metadata_files/added_modified_obsolete_timestamps.json', "r+") as file:
            data = json.load(file)
            second_condition = is_timestamp(data['ftp://ftp.ebi.ac.uk/pub/databases/msd/status/modified.latest'])
        print(str(second_condition))
        self.assertEqual(first_condition and second_condition, True)

    def step6(self):
        DifferenceFilesDownloader('added').get_file()
        first_condition = os.path.exists('../metadata_files/added.latest')
        with open('../metadata_files/added_modified_obsolete_timestamps.json', "r+") as file:
            data = json.load(file)
            second_condition = is_timestamp(data['ftp://ftp.ebi.ac.uk/pub/databases/msd/status/added.latest'])
        self.assertEqual(first_condition and second_condition, True)

    def step7(self):
        DifferenceFilesDownloader('obsolete').get_file()
        first_condition = os.path.exists('../metadata_files/obsolete.latest')
        with open('../metadata_files/added_modified_obsolete_timestamps.json', "r+") as file:
            data = json.load(file)
            second_condition = is_timestamp(data['ftp://ftp.ebi.ac.uk/pub/databases/msd/status/obsolete.latest'])
        self.assertEqual(first_condition and second_condition, True)

    def step8(self):
        os.remove(DifferenceFilesDownloader.timestamp_file)
        os.remove('../metadata_files/added.latest')
        os.remove('../metadata_files/modified.latest')
        os.remove('../metadata_files/obsolete.latest')

    def _steps(self):
        for name in dir(self):  # dir() result is implicitly sorted
            if name.startswith("step"):
                yield name, getattr(self, name)

    def test_steps(self):
        for name, step in self._steps():
            try:
                step()
            except Exception as e:
                self.fail("{} failed ({}: {})".format(step, type(e), e))


if __name__ == '__main__':
    unittest.main()
