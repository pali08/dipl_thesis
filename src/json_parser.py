import json
import os

from src.load_all_files import WATER_MOL_WEIGHT


def load_json(filename):
    """
    :param filename: .json file as string
    :return: dictionary with json data
    """
    with open(filename) as js:
        return json.load(js)



def get_orig_json_water_weight(filename):
    """
    json file is loaded as a dictionary
    :param filename:
    :return: total water weight (number of molecules * WATER_MOL_WEIGHT) if water is in molecule
    0 otherwise
    """
    dict_index = os.path.split(filename)[-1].rsplit('.', 1)[0]
    js = load_json(filename)
    for i in js[dict_index]:
        if i['molecule_name'] == ['water']:
            return ["{0:.2f}".format(WATER_MOL_WEIGHT * i['number_of_copies'])]
    return [0]


def get_validated_json_model_count_filtered(filename):
    """
    :param filename:
    :return: Number of models in validated json file
    if "Models" key exists in loaded json as dictionary, nan otherwise
    """
    try:
        return [len(load_json(filename)['Models'][0]['ModelNames'])]
    except IndexError:
        return ['0']
