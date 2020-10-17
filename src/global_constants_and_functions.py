import csv
import inspect

METALS = {'li', 'na', 'k', 'rb', 'cs', 'fr',
          'be', 'mg', 'ca', 'sr', 'ba', 'ra',
          'lu', 'la', 'ce', 'pr', 'nd', 'pm', 'sm', 'eu', 'gd', 'tb', 'dy', 'ho', 'er', 'tm', 'yb',
          'lr', 'ac', 'th', 'pa', 'u', 'np', 'pu', 'am', 'cm', 'bk', 'cf', 'es', 'fm', 'md', 'no',
          'sc', 'ti', 'v', 'cr', 'mn', 'fe', 'co', 'ni', 'cu', 'zn',
          'y', 'zr', 'nb', 'mo', 'tc', 'ru', 'rh', 'pd', 'ag', 'cd',
          'hf', 'ta', 'w', 're', 'os', 'ir', 'pt', 'au', 'hg',
          'rf', 'db', 'sg', 'bh', 'hs', 'cn',
          'al', 'ga', 'in', 'sn', 'tl', 'pb', 'bi', 'po', 'fl'}
WATER_MOLECULE = 'HOH'
WATER_MOL_WEIGHT = 18.015
NAN_VALUE = 'nan'

COLUMNS = ['pdbid', 'resolution', 'year', 'structureWeight', 'polymerWeight', 'nonPolymerWeightWithWater',
           'nonPolymerWeight', 'waterWeight',
           'atomCount', 'hetatmCount', 'allAtomCount', 'allAtomCountLn',
           'aaCount', 'ligandCount', 'aaLigandCount',
           'aaLigandCountNowater', 'ligandRatio', 'hetatmCountNowater', 'ligandCountNowater', 'ligandRatioNowater',
           'hetatmCount_metal', 'ligandCount_metal', 'ligandRatio_metal', 'hetatmCountNometal', 'ligandCountNometal',
           'ligandRatioNometal', 'hetatmCountNowaterNometal', 'ligandCountNowaterNometal',
           'ligandRatioNowaterNometal']

BIOPOLYMERS = ['polypeptide(L)', 'polypeptide(D)', 'polyribonucleotide', 'polydeoxyribonucleotide', 'polysaccharide(D)',
               'polysaccharide(L)', 'polydeoxyribonucleotide/polyribonucleotide hybrid', 'cyclic-pseudo-peptide',
               'peptide nucleic acid']
CORRELATION_COEF_THRESHOLD_RSCC = 0.8


def to_float(val):
    """
    :param val: value
    :return: int value if it can be intigerized, nan otherwise (e.g. in case when val is 'nan'
    or other text that cannot be integerized)
    """
    try:
        return float(val)
    except ValueError:
        return 'nan'


def to_int(val):
    """
    :param val: value
    :return: int value if it can be floatized, nan otherwise (e.g. in case when val is 'nan'
    or other text that cannot be floatized)
    """
    try:
        return int(val)
    except ValueError:
        return 'nan'


def division_zero_div_handling(numerator, denominator):
    """
    :param numerator: numerator
    :param denominator: denomitator
    :return: result of division if denominator is no zero, nan otherwise
    """
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return 'nan'
    except TypeError:
        return 'nan'


def addition_nan_handling(*values):
    """
    addition of multiple numbers- omit strings
    :param values: string, floats and int
    :return: sum of values, omitting strings (nans)
    """
    if list(values) == [NAN_VALUE for i in range(0, len(values))]:
        return NAN_VALUE

    # TODO not string is probably not enough, fix it
    return sum([float(i) for i in values if is_float(i)])


def subtraction_nan_handling(minuend, subtrahend):
    if minuend == NAN_VALUE:
        return NAN_VALUE
    elif subtrahend == NAN_VALUE:
        return minuend
    else:
        return minuend - subtrahend


def underscores_to_camel(input_str):
    """
    :param input_str: e.g. non_camel_to_camel_case
    :return: base on input: nonCamelToCamelCase
    """
    return ''.join([i[0].upper() + i[1:] for i in input_str.split('_')])


def key_error_output(pdbid, note=''):
    caller = inspect.stack()[1].function
    return 'Key Error at function: ' + caller + ' pdbid: ' + pdbid + ' NOTE: ' + note


def is_float(val):
    try:
        float(val)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def multiplying_question_mark_handling(multiplier1, multiplier2):
    """
    in case of weights, there are sometimes question marks instead of weights.
    This can cause problems in getting weights
    :param multiplier1:
    :param multiplier2:
    :return:
    """
    if is_float(multiplier1) and is_float(multiplier2):
        return float(multiplier1) * float(multiplier2)
    return 0


def nan_if_list_empty(input_iterable):
    """
    :param input_iterable: list, tuple, set or dictionary
    :return: 'nan' if list is empty (bool value of list is false in that case),
    otherwise return list
    """
    if type(input_iterable) in (list, tuple, set, dict):
        return input_iterable if input_iterable else NAN_VALUE
    else:
        raise ValueError(
            'list_emptiness function: input argument must be list, tuple, dict or set, not' + str(type(input_iterable)))


def value_for_result_dictionary(input_dictionary, key):
    """
    :param input_dictionary:
    :param key:
    :return: If key is in input dictionary get its value which will be added to result dictionary.
    NAN value otherwise
    """
    if key in input_dictionary:
        return input_dictionary[key]
    return NAN_VALUE


def check_dictionary_contains_only_nan_values(dictionary):
    """
    true if all values in dictionary are NAN - probably parsed file from which dictionary was created does not exist
    :param dictionary: input dixctionary
    :return: see above
    """
    return set(dictionary.values()) == {NAN_VALUE}
