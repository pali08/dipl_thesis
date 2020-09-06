import math
import os
import xml.etree.ElementTree as eTree

from src.global_constants_and_functions import NAN_VALUE, division_zero_div_handling
from src.parser import Parser


# not sure if we need this or convert all Nones to nan after we get all values
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
        self.result_dict = {'clashscore': NAN_VALUE, 'RamaOutliers': NAN_VALUE, 'SidechainOutliers': NAN_VALUE,
                            'ClashscorePercentile': NAN_VALUE, 'RamaOutliersPercentile': NAN_VALUE,
                            'SidechainOutliersPercentile': NAN_VALUE, 'combinedGeometryQuality': NAN_VALUE,
                            'DCC_R': NAN_VALUE, 'DCC_Rfree': NAN_VALUE, 'absolute-percentile-DCC_Rfree': NAN_VALUE,
                            'AngleRMSZstructure': NAN_VALUE, 'BondRMSZstructure': NAN_VALUE, 'RSRZoutliers': NAN_VALUE,
                            'RSRZoutliersPercentile': NAN_VALUE, 'combinedXrayQualityMetric': NAN_VALUE,
                            'highestChainBondsRMSZ': NAN_VALUE}

    def get_data(self):
        """
        xml file is loaded in eTree format
        :param filename:
        :return: clashscore gotten from eTree
        """
        root_zero_get = self.tree.getroot()[0].get
        clashscore = get_value_none_handle(root_zero_get, 'clashscore')
        if clashscore == NAN_VALUE:
            clashscore = get_value_none_handle(root_zero_get, 'clashscore-full-length')
        if clashscore < 0:
            clashscore = NAN_VALUE
        rama_outliers = get_value_none_handle(root_zero_get, 'percent-rama-outliers')
        sidechain_outliers = get_value_none_handle(root_zero_get, 'percent-rota-outliers')
        clashscore_percentil = get_value_none_handle(root_zero_get, 'absolute-perecentil-clashscore')
        rama_outliers_percentil = get_value_none_handle(root_zero_get, 'absolute-percentile-percent-rama-outliers')
        sidechain_outliers_percentil = get_value_none_handle(root_zero_get, 'absolute-percentile-percent-rota-outliers')
        rna_percentil = get_value_none_handle(root_zero_get, "absolute-percentile-RNAsuiteness")
        if clashscore_percentil != NAN_VALUE and \
                rama_outliers_percentil != NAN_VALUE and \
                sidechain_outliers_percentil != NAN_VALUE:
            summation_percentiles_1 = sum(
                [1 / i for i in [clashscore_percentil, rama_outliers_percentil, sidechain_outliers_percentil]])
            if rna_percentil == NAN_VALUE:
                combined_quality_geometry = 1 / (summation_percentiles_1 / 3)
            else:
                summation_percentiles_1 += 1 / rna_percentil
                combined_quality_geometry = 1 / (summation_percentiles_1 / 4)
        else:
            combined_quality_geometry = NAN_VALUE
        dcc_r = get_value_none_handle(root_zero_get, 'DCC_R')
        dcc_r_free = get_value_none_handle(root_zero_get, 'DCC_Rfree')
        dcc_r_free_percentil = get_value_none_handle(root_zero_get, 'absolute-percentile-DCC_Rfree')
        angles_rmsz_structure = get_value_none_handle(root_zero_get, 'angles_rmsz')
        bonds_rmsz_structure = get_value_none_handle(root_zero_get, 'bonds_rmsz')
        percent_rsrz_outliers = get_value_none_handle(root_zero_get, 'percent-RSRZ-outliers')
        rsrz_outliers_percentil = get_value_none_handle(root_zero_get, 'absolute-percentile-percent-RSRZ-outliers')
        if dcc_r_free_percentil != NAN_VALUE and rsrz_outliers_percentil != NAN_VALUE:
            summation_percentiles_2 = sum([1 / i for i in [dcc_r_free_percentil, rsrz_outliers_percentil]])
            combined_xray_quality_metric = 1 / (summation_percentiles_2 / 2)
        else:
            combined_xray_quality_metric = NAN_VALUE
        # guess this is not needed: if modelledentity instance is zero, then bonds rmsz is none
        # if self.tree.find('ModelledEntityInstance') is not None:
        #     if bonds_rmsz_structure > 0.0:
        #         highest_chain_bonds_rmsz = bonds_rmsz_structure
        #     else:
        #         highest_chain_bonds_rmsz = 0.0
        # else:
        #     highest_chain_bonds_rmsz = NAN_VALUE
        try:
            highest_chain_bonds_rmsz = bonds_rmsz_structure if bonds_rmsz_structure > 0.0 else 0.0
        # comparing text and
        except TypeError:
            highest_chain_bonds_rmsz = 0.0
        try:
            highest_chain_angles_rmsz = angles_rmsz_structure if angles_rmsz_structure > 0.0 else 0.0
        except TypeError:
            highest_chain_angles_rmsz = 0.0
        residue_count = len(list(filter(lambda x: x.tag == 'ModelledSubgroup' and 'mogul_bonds_rmsz' not in x.attrib,
                                        list(self.tree.getroot()))))
        residue_rsr_num = sum([float(i.attrib['rsr']) for i in
                               list(filter(lambda x: x.tag == 'ModelledSubgroup' and 'mogul_bonds_rmsz' not in x.attrib,
                                           list(self.tree.getroot())))])
        average_residue_rsr = division_zero_div_handling(residue_rsr_num, residue_count)
