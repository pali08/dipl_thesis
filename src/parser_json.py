import json
import os
import sys

from src.global_constants_and_functions import WATER_MOL_WEIGHT
sys.path.append('..')
from src.parser import Parser


def load_json(filename):
    """
    :param filename: .json file as string
    :return: dictionary with json data
    """
    with open(filename) as js:
        return json.load(js)


class JsonParser(Parser):
    def __init__(self, filename):
        super().__init__(filename)
        if super().file_exists():
            self.json_dict = load_json(filename)
