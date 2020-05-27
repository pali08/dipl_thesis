import unittest

from pdb_parser import get_pdb_id, get_mmcif_dictionary, get_mmcif_resolution


class MyTestCase(unittest.TestCase):
    def test_get_pdb_id(self):
        try:
            get_mmcif_dictionary('/home/pali/diplomka_python/rawpdbe/2flp_updated.cif')
            self.assertEqual(True, True)
        except Exception:
            self.fail('Exception occured')

    def test_pdb_data(self):
        self.assertEqual(get_pdb_id(
            get_mmcif_dictionary('/home/pali/diplomka_python/rawpdbe/2flp_updated.cif')).lower(), '2flp')

    def test_resolution(self):
        self.assertAlmostEqual(float(get_mmcif_resolution(
            get_mmcif_dictionary('/home/pali/diplomka_python/rawpdbe/2fl6_updated.cif'))), 2.5)
        self.assertAlmostEqual(float(get_mmcif_resolution(
            get_mmcif_dictionary('/home/pali/diplomka_python/rawpdbe/2fll_updated.cif'))), 2.60)
        self.assertEqual(get_mmcif_resolution(
            get_mmcif_dictionary('/home/pali/diplomka_python/rawpdbe/2fly_updated.cif')), 'nan')


if __name__ == '__main__':
    unittest.main()
