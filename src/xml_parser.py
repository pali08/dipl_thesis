import os
import xml.etree.ElementTree as etree

from src.main import fileset_xml


class XmlParser:
    def __init__(self, filename):
        self.tree = etree.parse(filename)

    def get_clashscore_from_xml(self):
        """
        xml file is loaded in etree format
        :param filename:
        :return: clashscore gotten from etree
        """
        clashscore = self.tree.getroot()[0].get('clashscore')
        if clashscore is None or float(clashscore) <= 0.0:
            clashscore = 'nan'
        clashscore_full_length = self.tree.getroot()[0].get('clashscore-full-length')
        if clashscore_full_length is None or float(clashscore_full_length) <= 0.0:
            clashscore_full_length = 'nan'
        return clashscore, clashscore_full_length
