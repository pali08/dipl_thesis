from Bio.File import as_handle
from Bio.PDB.MMCIF2Dict import MMCIF2Dict


def get_pdb_id(mmcif_dict):
    return mmcif_dict['_entry.id'][0]


def get_pdb_release_date(mmcif_dict):
    return mmcif_dict['_citation.year'][0]


def get_mmcif_resolution(mmcif_dict):
    """
    MMCIF is loaded as dictionary
    :param mmcif_dict
    :return: Highest resolution value if exists, nan otherwise.
    Highest resolution can be different item in different file. 2 of possibilities are covered for now
    """
    if '_refine.ls_d_res_high' in mmcif_dict:
        return mmcif_dict['_refine.ls_d_res_high'][0]
    return 'nan'


def get_mmcif_dictionary(filename):
    def get_mmcif_dictionary_local_function(fnm):
        return MMCIF2Dict(fnm)

    try:
        return get_mmcif_dictionary_local_function(filename)
    except UnicodeDecodeError:
        with as_handle(filename, 'r', encoding='utf-16') as f:
            return get_mmcif_dictionary_local_function(f)

# def get_data
