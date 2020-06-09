import os
import xml.etree.ElementTree as etree

from src.load_all_files import fileset_xml


def get_clashscore_from_xml(filename):
    """
    xml file is loaded in etree format
    :param filename:
    :return: clashscore gotten from etree
    """
    tree = etree.parse(filename).getroot()[0]
    clashscore = tree.get('clashscore')
    if clashscore is None or float(clashscore) <= 0.0:
        clashscore = 'nan'
    clashscore_full_length = tree.get('clashscore-full-length')
    if clashscore_full_length is None or float(clashscore_full_length) <= 0.0:
        clashscore_full_length = 'nan'
    return clashscore, clashscore_full_length


def get_pdbid_from_xml(filename):
    """
    xml file is loaded in etree format
    :param filename:
    :return: pdbid gotten from etree
    probably if this function is run inside pool, global variables cannot be modified ?
    """
    fileset_xml.add(os.path.split(filename)[1].split('_')[0].strip())
    return [etree.parse(filename).getroot()[0].get('pdbid')]
