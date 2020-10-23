import math
import os
import xml.etree.ElementTree as eTree

import numpy as np

from src.global_constants_and_functions import NAN_VALUE, division_zero_div_handling, nan_if_list_empty, is_float, \
    CORRELATION_COEF_THRESHOLD_RSCC, addition_nan_handling
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
    def __init__(self, filename, ligand_stats):
        super().__init__(filename)
        self.ligand_stats = ligand_stats
        self.tree = eTree.parse(self.filename)
        self.result_dict = {'clashscore': NAN_VALUE, 'RamaOutliers': NAN_VALUE, 'SidechainOutliers': NAN_VALUE,
                            'ClashscorePercentile': NAN_VALUE, 'RamaOutliersPercentile': NAN_VALUE,
                            'SidechainOutliersPercentile': NAN_VALUE, 'combinedGeometryQuality': NAN_VALUE,
                            'DCC_R': NAN_VALUE, 'DCC_Rfree': NAN_VALUE, 'absolute-percentile-DCC_Rfree': NAN_VALUE,
                            'AngleRMSZstructure': NAN_VALUE, 'BondRMSZstructure': NAN_VALUE, 'RSRZoutliers': NAN_VALUE,
                            'RSRZoutliersPercentile': NAN_VALUE, 'combinedXrayQualityMetric': NAN_VALUE,
                            'highestChainBondsRMSZ': NAN_VALUE, 'highestChainAnglesRMSZ': NAN_VALUE,
                            'averageResidueRSR': NAN_VALUE, 'averageLigandRSR': NAN_VALUE,
                            'averageLigandAngleRMSZ': NAN_VALUE, 'averageLigandBondRMSZ': NAN_VALUE,
                            'averageLigandRSCC': NAN_VALUE, 'ligandRSCCoutlierRatio': NAN_VALUE,
                            'averageResidueRSCC': NAN_VALUE, 'averageLigandRSCCsmallLigs': NAN_VALUE,
                            'averageLigandRSCClargeLigs': NAN_VALUE, 'absolute-percentile-RNAsuiteness': NAN_VALUE
                            }

        self.create_result_dict()

    def get_data(self):
        """
        xml file is loaded in eTree format
        :param filename:
        :return: clashscore gotten from eTree
        """
        root = self.tree.getroot()
        root_zero_get = root[0].get
        clashscore = float(get_value_none_handle(root_zero_get, 'clashscore'))
        if clashscore == NAN_VALUE:
            clashscore = get_value_none_handle(root_zero_get, 'clashscore-full-length')
        if clashscore < 0:
            clashscore = NAN_VALUE
        rama_outliers = get_value_none_handle(root_zero_get, 'percent-rama-outliers')
        sidechain_outliers = get_value_none_handle(root_zero_get, 'percent-rota-outliers')
        clashscore_percentil = get_value_none_handle(root_zero_get, 'absolute-percentile-clashscore')
        rama_outliers_percentil = get_value_none_handle(root_zero_get, 'absolute-percentile-percent-rama-outliers')
        sidechain_outliers_percentil = get_value_none_handle(root_zero_get, 'absolute-percentile-percent-rota-outliers')
        rna_percentil = get_value_none_handle(root_zero_get, "absolute-percentile-RNAsuiteness")
        if clashscore_percentil != NAN_VALUE and \
                rama_outliers_percentil != NAN_VALUE and \
                sidechain_outliers_percentil != NAN_VALUE:
            summation_percentiles_1 = sum(
                [1 / i for i in
                 [float(clashscore_percentil), float(rama_outliers_percentil), float(sidechain_outliers_percentil)] if
                 is_float(i) and not np.isclose(i, 0)])
            # print(summation_percentiles_1)
            # print(type(summation_percentiles_1))
            if rna_percentil == NAN_VALUE:
                combined_quality_geometry = division_zero_div_handling(1, (
                    division_zero_div_handling(summation_percentiles_1, 3)))
            else:
                # print(summation_percentiles_1)
                # print(type(summation_percentiles_1))
                # print(rna_percentil)
                # print(type(rna_percentil))
                summation_percentiles_1 += division_zero_div_handling(1, float(rna_percentil)) if is_float(
                    division_zero_div_handling(1, float(rna_percentil))) else summation_percentiles_1
                combined_quality_geometry = division_zero_div_handling(1, (
                    division_zero_div_handling(summation_percentiles_1, 4)))
        else:
            combined_quality_geometry = NAN_VALUE
        dcc_r = get_value_none_handle(root_zero_get, 'DCC_R')
        dcc_r_free = get_value_none_handle(root_zero_get, 'DCC_Rfree')
        if not is_float(dcc_r_free):
            dcc_r_free = NAN_VALUE
        dcc_r_free_percentil = get_value_none_handle(root_zero_get, 'absolute-percentile-DCC_Rfree')
        angles_rmsz_structure = get_value_none_handle(root_zero_get, 'angles_rmsz')
        bonds_rmsz_structure = get_value_none_handle(root_zero_get, 'bonds_rmsz')
        percent_rsrz_outliers = get_value_none_handle(root_zero_get, 'percent-RSRZ-outliers')
        rsrz_outliers_percentil = get_value_none_handle(root_zero_get, 'absolute-percentile-percent-RSRZ-outliers')
        if not (dcc_r_free_percentil == NAN_VALUE or rsrz_outliers_percentil == NAN_VALUE):
            # print('DCC rfree percentil: ' + str(dcc_r_free_percentil))
            # print('rsrz_outlier_percentil: ' + str(rsrz_outliers_percentil))
            summation_percentiles_2 = addition_nan_handling(
                *[division_zero_div_handling(1, i) for i in
                  [float(dcc_r_free_percentil), float(rsrz_outliers_percentil)] if
                  is_float(division_zero_div_handling(1, i))])
            combined_xray_quality_metric = division_zero_div_handling(1, (
                division_zero_div_handling(summation_percentiles_2, 2)))
        else:
            combined_xray_quality_metric = NAN_VALUE
        try:
            highest_chain_bonds_rmsz = max(
                [float(root[i].get('bonds_rmsz')) for i in range(0, len(root)) if
                 root[i].get('bonds_rmsz') is not None])
            # highest_chain_bonds_rmsz = float(bonds_rmsz_structure) if float(bonds_rmsz_structure) > 0.0 else 0.0
        except TypeError:
            highest_chain_bonds_rmsz = 0.0
        except ValueError:
            highest_chain_bonds_rmsz = NAN_VALUE
        try:
            highest_chain_angles_rmsz = max(
                [float(root[i].get('angles_rmsz')) for i in range(0, len(root)) if
                 root[i].get('angles_rmsz') is not None])
            # highest_chain_angles_rmsz = angles_rmsz_structure if angles_rmsz_structure > 0.0 else 0.0
        except TypeError:
            highest_chain_angles_rmsz = 0.0
        except ValueError:
            highest_chain_angles_rmsz = NAN_VALUE
        residue_count = len(list(filter(lambda x: x.tag == 'ModelledSubgroup' and 'mogul_bonds_rmsz' not in x.attrib,
                                        list(self.tree.getroot()))))
        try:
            residue_rsr_num = sum([float(i.attrib['rsr']) for i in
                                   list(filter(
                                       lambda x: x.tag == 'ModelledSubgroup' and 'mogul_bonds_rmsz' not in x.attrib and
                                                 'rsr' in x.attrib,
                                       list(self.tree.getroot())))])
        except KeyError:
            residue_rsr_num = NAN_VALUE
        average_residue_rsr = division_zero_div_handling(residue_rsr_num, residue_count)
        if is_float(average_residue_rsr):
            if np.isclose(average_residue_rsr, 0.000):
                average_residue_rsr = NAN_VALUE
        ligand_count = len(list(filter(lambda x: 'mogul_bonds_rmsz' in x.attrib,
                                       list(self.tree.getroot()))))
        ligand_rsr_list = nan_if_list_empty([float(i.get('rsr')) for i in
                                             list(filter(
                                                 lambda x: x.tag == 'ModelledSubgroup'
                                                           and x.get('rsr') is not None
                                                           and x.get('mogul_bonds_rmsz') is not None,
                                                 list(self.tree.getroot())))])
        try:
            ligand_rsr_sum = sum(ligand_rsr_list)
        except TypeError:
            ligand_rsr_sum = ligand_rsr_list  # NAN
        average_ligand_rsr = division_zero_div_handling(ligand_rsr_sum, ligand_count)
        rmsz_angles_list = nan_if_list_empty([float(i.get('mogul_angles_rmsz')) for i in list(
            filter(
                lambda x: x.tag == 'ModelledSubgroup' and 'mogul_angles_rmsz' in x.attrib
                # and x.get('rsr') is not None
                ,
                list(self.tree.getroot())))])
        try:
            ligand_rmsz_sum_angles = sum(rmsz_angles_list)
        except TypeError:
            ligand_rmsz_sum_angles = rmsz_angles_list  # NAN
        average_ligand_angle_rmsz = division_zero_div_handling(ligand_rmsz_sum_angles, ligand_count)
        rmsz_bonds_list = nan_if_list_empty([float(i.get('mogul_bonds_rmsz')) for i in list(
            filter(
                lambda x: x.tag == 'ModelledSubgroup' and 'mogul_bonds_rmsz' in x.attrib  # and x.get('rsr') is not None
                ,
                list(self.tree.getroot())))])
        try:
            ligand_rmsz_sum_bonds = sum(rmsz_bonds_list)
        except TypeError:
            ligand_rmsz_sum_bonds = rmsz_bonds_list  # NAN
        average_ligand_bonds_rmsz = division_zero_div_handling(ligand_rmsz_sum_bonds, ligand_count)
        ligand_rscc_list = nan_if_list_empty([float(i.get('rscc')) for i in
                                              list(filter(
                                                  lambda x: x.tag == 'ModelledSubgroup'
                                                            and x.get('rscc') is not None
                                                            and x.get('mogul_bonds_rmsz') is not None,
                                                  list(self.tree.getroot())))])
        ligand_rscc_list_tuples_with_resid = nan_if_list_empty([(float(i.get('rscc')), i.get('resname')) for i in
                                                                list(filter(
                                                                    lambda x: x.tag == 'ModelledSubgroup'
                                                                              and x.get('rscc') is not None
                                                                              and x.get('mogul_bonds_rmsz') is not None,
                                                                    list(self.tree.getroot())))])
        try:
            ligand_rscc_sum = sum(ligand_rscc_list)
        except TypeError:
            ligand_rscc_sum = ligand_rscc_list  # NAN
        average_ligand_rscc = division_zero_div_handling(ligand_rscc_sum, ligand_count)
        if ligand_rscc_list != NAN_VALUE:
            ligand_rscc_outlier_count = len(
                list(filter(lambda x: is_float(x) and float(x) < CORRELATION_COEF_THRESHOLD_RSCC, ligand_rscc_list)))
            ligand_rscc_outlier_ratio = division_zero_div_handling(ligand_rscc_outlier_count, ligand_count)
        else:
            ligand_rscc_outlier_ratio = NAN_VALUE

        residue_rscc_list = nan_if_list_empty([float(i.get('rscc')) for i in
                                               list(filter(
                                                   lambda x: x.tag == 'ModelledSubgroup'
                                                             and x.get('rscc') is not None
                                                             and x.get('mogul_bonds_rmsz') is None,
                                                   list(self.tree.getroot())))])
        try:
            residue_rscc_sum = sum(residue_rscc_list)
        except TypeError:
            residue_rscc_sum = residue_rscc_list  # NAN_VALUE
        average_residue_rscc = division_zero_div_handling(residue_rscc_sum, residue_count)
        residue_rscc_outlier_count = len(
            list(filter(lambda x: is_float(x) and float(x) < CORRELATION_COEF_THRESHOLD_RSCC, residue_rscc_list)))
        if residue_rscc_list != NAN_VALUE:
            residue_rscc_outlier_ratio = division_zero_div_handling(residue_rscc_outlier_count, residue_count)
        else:
            residue_rscc_outlier_ratio = NAN_VALUE
        ligand_rscc_list_10_and_below = NAN_VALUE
        ligand_rscc_list_11_and_above = NAN_VALUE
        average_ligand_rscc_small_ligs = NAN_VALUE
        average_ligand_rscc_large_ligs = NAN_VALUE
        if ligand_rscc_list_tuples_with_resid != NAN_VALUE:
            ligand_rscc_list_10_and_below = [ligand_rscc_list_tuples_with_resid[i][0] for i in
                                             range(0, len(ligand_rscc_list_tuples_with_resid)) if
                                             ligand_rscc_list_tuples_with_resid[i][
                                                 1].upper() in self.ligand_stats and float(
                                                 self.ligand_stats[ligand_rscc_list_tuples_with_resid[i][1]][0]) <= 10]
            ligand_rscc_list_11_and_above = [ligand_rscc_list_tuples_with_resid[i][0] for i in
                                             range(0, len(ligand_rscc_list_tuples_with_resid)) if
                                             ligand_rscc_list_tuples_with_resid[i][
                                                 1].upper() in self.ligand_stats and float(
                                                 self.ligand_stats[ligand_rscc_list_tuples_with_resid[i][1]][0]) > 10]
            average_ligand_rscc_small_ligs = division_zero_div_handling(sum(ligand_rscc_list_10_and_below),
                                                                        len(ligand_rscc_list_10_and_below))

            average_ligand_rscc_large_ligs = division_zero_div_handling(sum(ligand_rscc_list_11_and_above),
                                                                        len(ligand_rscc_list_11_and_above))

        self.result_dict.update(
            {'clashscore': clashscore, 'RamaOutliers': rama_outliers, 'SidechainOutliers': sidechain_outliers,
             'ClashscorePercentile': clashscore_percentil, 'RamaOutliersPercentile': rama_outliers_percentil,
             'SidechainOutliersPercentile': sidechain_outliers_percentil,
             'combinedGeometryQuality': combined_quality_geometry,
             'DCC_R': dcc_r, 'DCC_Rfree': dcc_r_free, 'absolute-percentile-DCC_Rfree': dcc_r_free_percentil,
             'AngleRMSZstructure': angles_rmsz_structure, 'BondRMSZstructure': bonds_rmsz_structure,
             'RSRZoutliers': percent_rsrz_outliers,
             'RSRZoutliersPercentile': rsrz_outliers_percentil,
             'combinedXrayQualityMetric': combined_xray_quality_metric,
             'highestChainBondsRMSZ': highest_chain_bonds_rmsz, 'highestChainAnglesRMSZ': highest_chain_angles_rmsz,
             'averageResidueRSR': average_residue_rsr, 'averageLigandRSR': average_ligand_rsr,
             'averageLigandAngleRMSZ': average_ligand_angle_rmsz, 'averageLigandBondRMSZ': average_ligand_bonds_rmsz,
             'averageLigandRSCC': average_ligand_rscc, 'ligandRSCCoutlierRatio': ligand_rscc_outlier_ratio,
             'averageResidueRSCC': average_residue_rscc, 'residueRSCCoutlierRatio': residue_rscc_outlier_ratio,
             'averageLigandRSCCsmallLigs': average_ligand_rscc_small_ligs,
             'averageLigandRSCClargeLigs': average_ligand_rscc_large_ligs,
             'absolute-percentile-RNAsuiteness': rna_percentil})

    def create_result_dict(self):
        if super().file_exists():
            self.get_data()
