# /usr/bin/env python3
import argparse
import os
import time
import fileinput
import xml.etree.ElementTree as etree
import json
from datetime import datetime
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from Bio.File import as_handle
import sys


def rough_readlines(filename):
    try:
        with open(filename) as f:
            while True:
                try:
                    line = next(f)
                    if '_em_3d_reconstruction.resolution' in line or '_reflns.d_resolution_high' in line:
                        print(line.split()[1])
                        break
                except StopIteration:
                    print('nan')
                    break
    except UnicodeDecodeError:
        with open(filename, encoding='utf-16-le') as f:
            while True:
                line = next(f)
                if '_em_3d_reconstruction.resolution' in line or '_reflns.d_resolution_high' in line:
                    print(line.split()[1])
                    break
                else:
                    print('nan')
                    break


def get_mmcif_high_resolution_biopython(filename):
    """
    MMCIF is loaded as dictionary
    :param filename:
    :return: Highest resolution value if exists, nan otherwise.
    Highest resolution can be different item in different file. 2 of possibilities are covered for now
    """

    def get_resolution(fnm):
        mmcif_dict = MMCIF2Dict(fnm)
        if '_reflns.d_resolution_high' in mmcif_dict:
            return mmcif_dict['_reflns.d_resolution_high'][0]
        elif '_em_3d_reconstruction.resolution' in mmcif_dict:
            return mmcif_dict['_em_3d_reconstruction.resolution'][0]
        else:
            return 'nan'

    try:
        print(get_resolution(filename))
    except UnicodeDecodeError:
        pass
        with as_handle(filename, 'r', encoding='utf-16', engine='python') as f:
            return (get_resolution(f))


def walk_over_files(path, function):
    start_time = time.time()
    for root, dirs, files in os.walk(path):
        files.sort()
        for file in files:
            function(os.path.join(root, file))
    print(function.__name__ + ':')
    print("Finished in {0:.3f} seconds.".format(time.time() - start_time))


walk_over_files(sys.argv[1], rough_readlines)
walk_over_files(sys.argv[1], get_mmcif_high_resolution_biopython)
