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

columns = ['pdbid', 'resolution', 'year', 'structureWeight', 'polymerWeight', 'nonPolymerWeightWithWater',
           'nonPolymerWeight', 'waterWeight',
           'atomCount', 'hetatmCount', 'allAtomCount', 'allAtomCountLn',
           'aaCount', 'ligandCount', 'aaLigandCount',
           'aaLigandCountNowater', 'ligandRatio', 'hetatmCountNowater', 'ligandCountNowater', 'ligandRatioNowater',
           'hetatmCount_metal', 'ligandCount_metal', 'ligandRatio_metal', 'hetatmCountNometal', 'ligandCountNometal',
           'ligandRatioNometal', 'hetatmCountNowaterNometal', 'ligandCountNowaterNometal',
           'ligandRatioNowaterNometal']


def to_float(val):
    try:
        return float(val)
    except ValueError:
        return 'nan'


def to_int(val):
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
