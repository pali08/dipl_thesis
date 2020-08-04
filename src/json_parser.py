import json
import os

from src.global_constants_and_functions import WATER_MOL_WEIGHT
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
        self.json_dict = load_json(filename)

