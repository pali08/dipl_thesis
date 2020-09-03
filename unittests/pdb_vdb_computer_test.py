import unittest

from src.global_constants_and_functions import NAN_VALUE
from src.pdb_parser import PdbParser
from src.vdb_parser import VdbParser
from src.combined_data_computer import CombinedDataComputer


class PdbVdbComputerTest(unittest.TestCase):

    def test_result_is_computed_from_two_dicts(self):
        pdb_dict = {'PDBID': '2FL0', 'releaseDate': 2006, 'structureWeight': 154.74752, 'polymerWeight': 143.988592,
                    'nonPolymerWeight': 10758.928, 'nonPolymerWeightNowater': 3787.1229999999996,
                    'waterWeight': 6971.805,
                    'atomCount': 10096, 'hetatmCount': 590, 'allAtomCount': 10686, 'allAtomCountLn': 9.276689752517717,
                    'aaCount': 155,
                    'ligandCount': 160, 'aaLigandCount': 315, 'aaLigandCountNowater': 190, 'ligandRatio': 3.6875,
                    'hetatmCountNowater': 203, 'ligandCountNowater': 35, 'ligandRatioNowater': 5.8,
                    'hetatmCountMetal': 203,
                    'ligandCountMetal': 35, 'ligandRatioMetal': 5.8, 'hetatmCountNometal': 387,
                    'ligandCountNometal': 125,
                    'ligandRatioNometal': 3.096, 'hetatmCountNowaterNometal': 0, 'ligandCountNowaterNometal': 0,
                    'ligandRatioNowaterNometal': 'nan', 'resolution': 2.7}
        vdb_dict = {'hetatmCountFiltered': 43, 'ligandCarbonChiralAtomCountFiltered': 0, 'ligandCountFiltered': 4.0,
                    'ligandRatioFiltered': 10.75, 'ligandRatioFilteredMetal': 10.75,
                    'ligandRatioFilteredNometal': 'nan', 'missing_atom_count': 0, 'hetatmCountFilteredMetal': 43,
                    'hetatmCountFilteredNometal': 'nan', 'ligandCountFilteredNometal': 0.0, 'wrong_chiral_count': 0,
                    'ligandCountFilteredMetal': 4, 'total_bond_count': 50, 'sigma_bond_count': 35,
                    'ligandBondRotationFreedom': 0.7}
        computer = CombinedDataComputer(pdb_dict, vdb_dict)
        self.assertAlmostEqual(computer.result_dict['aaLigandCountFiltered'], 159)


if __name__ == '__main__':
    unittest.main()
