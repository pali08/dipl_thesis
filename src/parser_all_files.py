import os
import sys

sys.path.append('..')
from src import global_constants_and_functions
from src.generate_filepaths import FilepathGenerator
from src.global_constants_and_functions import is_float, NAN_VALUE, MMCIF_UPDATED_SUFFIX, XML_VALIDATION_SUFFIX, \
    VDB_JSON_UNIVERSAL_NAME, ASSEMBLY_FOLDER, MOLECULES_FOLDER, SUMMARY_FOLDER, JSON_SUFFIX
from src.parser_pdb import PdbParser
from src.computer_combined_data import CombinedDataComputer
from src.parser_json_rest import RestParser
from src.parser_json_vdb import VdbParser
from src.parser_xml import XmlParser
import csv


def get_ligand_stats_csv(filename):
    """
    :param filename: ligand_stats.csv
    :return: ligand stats in format: [<key(ligand name)>: [<heavyAtomSize (index 0)>, <flexibility (index 1)>]]
    """
    with open(filename, encoding='utf-8', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        return {i[0].upper(): [i[1], i[2]] for i in list(reader)}


class AllFilesParser:
    ligand_stats = None

    def __init__(self, molecule, ligand_stats_csv, *filepaths):
        try:
            if AllFilesParser.ligand_stats is None:
                AllFilesParser.ligand_stats = get_ligand_stats_csv(ligand_stats_csv)
            self.filepaths = filepaths
            self.molecule = molecule
            self.filepath_generator = FilepathGenerator(molecule, *filepaths)
            self.pdb_result_dict = PdbParser(self.filepath_generator.get_pdb_filepath()).result_dict
            self.vdb_result_dict = VdbParser(self.filepath_generator.get_vdb_filepath()).result_dict
            self.xml_result_dict = XmlParser(self.filepath_generator.get_xml_filepath(), self.ligand_stats).result_dict
            self.rest_assembly_parser = RestParser(self.filepath_generator.get_rest_filepath()[0],
                                                   AllFilesParser.ligand_stats)
            self.rest_result_dict_assembly = self.rest_assembly_parser.result_dict
            self.rest_molecules_parser = RestParser(self.filepath_generator.get_rest_filepath()[1],
                                                    AllFilesParser.ligand_stats)
            self.rest_result_dict_molecules = self.rest_molecules_parser.result_dict
            self.rest_summary_parser = RestParser(self.filepath_generator.get_rest_filepath()[2],
                                                  AllFilesParser.ligand_stats)
            self.rest_result_dict_summary = RestParser(self.filepath_generator.get_rest_filepath()[2],
                                                       AllFilesParser.ligand_stats).result_dict

            self.combined_data_result_dict = CombinedDataComputer(self.pdb_result_dict, self.vdb_result_dict,
                                                                  self.xml_result_dict, self.rest_result_dict_assembly,
                                                                  self.rest_result_dict_molecules,
                                                                  self.rest_result_dict_summary,
                                                                  self.rest_assembly_parser,
                                                                  self.rest_molecules_parser,
                                                                  self.rest_summary_parser,
                                                                  self.ligand_stats).result_dict
            self.result_dict = {**self.pdb_result_dict, **self.vdb_result_dict,
                                **self.xml_result_dict, **self.rest_result_dict_assembly,
                                **self.rest_result_dict_molecules,
                                **self.rest_result_dict_summary,
                                **self.combined_data_result_dict}
        except Exception as e:
            print(str(molecule) + ': There was some problem with parsing this molecule. Stacktrace follows:')
            print(e)
            self.result_dict = {i: NAN_VALUE for i in self.order_list}

    order_list = ['PDB ID', 'resolution', 'releaseDate', 'StructureWeight', 'PolymerWeight',
                  'NonpolymerWeight',
                  'NonpolymerWeightNowater',
                  'WaterWeight', 'atomCount', 'hetatmCount', 'allAtomCount', 'allAtomCountLn', 'aaCount',
                  'ligandCount',
                  'ligandBondRotationFreedom', 'aaLigandCount', 'aaLigandCountNowater',
                  'aaLigandCountFiltered',
                  'ligandRatio', 'hetatmCountNowater', 'ligandCountNowater', 'ligandRatioNowater',
                  'hetatmCountFiltered', 'ligandCarbonChiraAtomCountFiltered', 'ligandCountFiltered',
                  'ligandRatioFiltered', 'hetatmCountMetal', 'ligandCountMetal', 'ligandRatioMetal',
                  'hetatmCountNometal', 'ligandCountNometal', 'ligandRatioNometal',
                  'hetatmCountNowaterNometal', 'ligandCountNowaterNometal', 'ligandRatioNowaterNometal',
                  'hetatmCountFilteredMetal', 'ligandCountFilteredMetal', 'ligandRatioFilteredMetal',
                  'hetatmCountFilteredNometal', 'ligandCountFilteredNometal', 'ligandRatioFilteredNometal',
                  'clashscore', 'RamaOutliers', 'SidechainOutliers', 'ClashscorePercentile', 'RamaOutliersPercentile',
                  'SidechainOutliersPercentile', 'combinedGeometryQuality', 'DCC_R', 'DCC_Rfree',
                  'absolute-percentile-DCC_Rfree', 'AngleRMSZstructure', 'BondRMSZstructure', 'RSRZoutliers',
                  'RSRZoutliersPercentile', 'combinedXrayQualityMetric', 'combinedOverallQualityMetric',
                  'highestChainBondsRMSZ', 'highestChainAnglesRMSZ', 'averageResidueRSR', 'ChiralProblemLigandRatio',
                  'GoodLigandRatio', 'TopologyProblemLigandRatio', 'LigandTopologyProblemsPrecise',
                  'LigandTopologyCarbonChiraProblemsPrecise', 'ChiraProblemsPrecise', 'GoodLigandRatioBinary',
                  'LigandTopologyProblemsPreciseBinary', 'LigandTopologyCarbonChiraProblemsPreciseBinary',
                  'ChiraProblemsPreciseBinary', 'averageLigandRSR', 'averageLigandAngleRMSZ', 'averageLigandBondRMSZ',
                  'averageLigandRSCC', 'ligandRSCCoutlierRatio', 'AssemblyTotalWeight', 'AssemblyBiopolymerCount',
                  'AssemblyUniqueBiopolymerCount', 'AssemblyLigandCount', 'AssemblyUniqueLigandCount',
                  'AssemblyWaterCount', 'AssemblyBiopolymerWeight', 'AssemblyLigandWeight', 'AssemblyWaterWeight',
                  'averageResidueRSCC', 'residueRSCCoutlierRatio', 'AssemblyLigandFlexibility',
                  'averageLigandRSCCsmallLigs', 'averageLigandRSCClargeLigs', 'absolute-percentile-RNAsuiteness']

    def get_data_ordered(self):
        """
        order result data in original data.csv format
        :return:
        """
        # print(str(self.molecule) + 'this molecule got key error')
        # print(self.result_dict)
        try:
            ordered_list = []
            for i in AllFilesParser.order_list:
                ordered_list.append(self.result_dict[i])
            return ordered_list
        except KeyError:
            print(str(self.molecule) + 'this molecule got key error')
            print(self.result_dict)
            sys.exit()

    def result_dict_final_edit(self):
        """
        format floating point numbers to 3 decimals
        :return:
        """
        for key, value in self.result_dict:
            if '.' in value:
                self.result_dict[key] = '{:.3f}'.format(float(value))
