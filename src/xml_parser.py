import math
import os
import xml.etree.ElementTree as eTree

from src.global_constants_and_functions import NAN_VALUE
from src.parser import Parser


def get_value_none_handle(function, parameter):
    """
    if parameter in xml tree does not exist (e.g. tree.getroot()[0].get('somenonexistingparam')),
    get function returns None instead of throwing exception
    :param function: applied function
    :param parameter: wanted parameter
    :return: 'nan' if parameter does not exist. Parameter's value otherwise
    """
    return_value = function(parameter)
    return NAN_VALUE if return_value is None else return_value


class XmlParser(Parser):
    def __init__(self, filename):
        super().__init__(filename)
        self.tree = eTree.parse(self.filename)
        self.result_dict = {'clashscore': NAN_VALUE}

    def get_data(self):
        """
        xml file is loaded in eTree format
        :param filename:
        :return: clashscore gotten from eTree
        """
        clashscore = get_value_none_handle(self.tree.getroot()[0].get, 'clashscore')
        if math.isnan(float(clashscore)):
            clashscore = get_value_none_handle(self.tree.getroot()[0].get, 'clashscore-full-length')
        if clashscore < 0:
            return NAN_VALUE
        rama_outliers = get_value_none_handle(self.tree.getroot()[0].get, 'percent-rama-outliers')
