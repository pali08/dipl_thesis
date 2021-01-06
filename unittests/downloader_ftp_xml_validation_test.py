import os
import unittest

from src.downloader_ftp_xml_validation import XmlValidationDownloader
from src.global_constants_and_functions import is_float, XML_VALIDATION_SUFFIX
from src.parser_xml import XmlParser


class TestFtpXmlValidationDownloader(unittest.TestCase):
    def test_file_downloading(self):
        XmlValidationDownloader('1cjv', os.path.join('.', '1cjv' + XML_VALIDATION_SUFFIX)).get_file()
        clashscore = \
            XmlParser(os.path.join('.', '1cjv' + XML_VALIDATION_SUFFIX),
                      os.path.join('.', 'input_data_2', 'ligandStats.csv')).result_dict[
                'clashscore']
        self.assertEqual(is_float(clashscore), True)
        self.addCleanup(os.remove, '1cjv' + XML_VALIDATION_SUFFIX)

    def test_downloading_non_existing_file(self):
        pass


if __name__ == '__main__':
    unittest.main()
