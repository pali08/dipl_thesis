import os
import unittest

from src.downloader_ftp_xml_validation import XmlValidationDownloader
from src.global_constants_and_functions import is_float
from src.parser_xml import XmlParser


class TestFtpXmlValidationDownloader(unittest.TestCase):
    def test_file_downloading(self):
        XmlValidationDownloader('1cjv', os.path.join('.', '1cjv_validation.xml')).get_file()
        clashscore = \
            XmlParser(os.path.join('.', '1cjv_validation.xml'),
                      '/home/pali/diplomka_python/ligandStats.csv').result_dict[
                'clashscore']
        self.assertEqual(is_float(clashscore), True)
        self.addCleanup(os.remove, '1cjv_validation.xml')


if __name__ == '__main__':
    unittest.main()
