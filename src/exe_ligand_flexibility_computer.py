import argparse
import csv
import io
import os
import re
import sys

import networkx as nx
from Bio.File import as_handle
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

from src.parser_pdb import get_mmcif_dictionary
from src.find_cycles import *

bond_grades = {'sing': 1, 'delo': 2, 'doub': 2, 'trip': 3, 'quad': 4}


def split_file(filename):
    """
    MMCIF2Dict from biopython does not know how to parse this type of file, because it is like multiple
    mmcif files in one file. We need to split it
    :param filename:
    :return: list of mmcifdict ligands
    """
    try:
        with open(filename, mode='r', encoding='utf-8') as f:
            file_string = f.read()
            ligands = re.split('([\r\n?|\n]#[\r\n?|\n]data_.*?[\r\n?|\n]#)', file_string)
            ligands = [MMCIF2Dict(io.StringIO(x + y)) for x, y in zip(ligands[1:][0::2], ligands[1:][1::2])]
    except UnicodeDecodeError:
        with open(filename, mode='r', encoding='utf-16') as f:
            file_string = f.read()
            ligands = re.split('([\r\n?|\n]#[\r\n?|\n]data_.*?[\r\n?|\n]#)', file_string)
            ligands = [MMCIF2Dict(io.StringIO(x + y)) for x, y in zip(ligands[1:][0::2], ligands[1:][1::2])]
    return ligands


def get_bonds(mmcif_dict):
    try:
        return list(zip(mmcif_dict['_chem_comp_bond.atom_id_1'],
                        mmcif_dict['_chem_comp_bond.atom_id_2'],
                        [i.lower() for i in mmcif_dict['_chem_comp_bond.value_order']],
                        [bond_grades[i.lower()] for i in mmcif_dict['_chem_comp_bond.value_order']]))
    except KeyError:
        return []


def get_atoms(mmcif_dict):
    return list(zip(mmcif_dict['_chem_comp_atom.atom_id'], mmcif_dict['_chem_comp_atom.type_symbol']))


def get_hydrogen_atoms(atoms):
    return set([i[0] for i in atoms if i[1].upper() == 'H'])


def get_hydrogen_bonds(hydrogen_atoms, bonds):
    # print(bonds)
    return set([tuple(i) for i in bonds if (i[0] in hydrogen_atoms) or (i[1] in hydrogen_atoms)])


def get_non_single_bonds(bonds):
    return [j[:2] for j in [i for i in bonds if i[3] > 1]]


def get_graph(bonds):
    bonds_atom_ids_only = [i[:2] for i in bonds]
    atoms_from_bonds = set([item for sublist in bonds_atom_ids_only for item in sublist])
    g = nx.Graph()
    g.add_nodes_from(atoms_from_bonds)
    g.add_edges_from(bonds_atom_ids_only)
    return g


def get_bonds_in_cycles(bonds):
    # print(bonds)
    return find_all_cycles([i[:2] for i in bonds])


# def get_bonds_in_cycles(g, source=None):
#     """forked from networkx dfs_edges function. Assumes nodes are integers, or at least
#     types which work with min() and > ."""
#     if source is None:
#         # produce edges for all components
#         nodes = [list(i)[0] for i in nx.connected_components(g)]
#     else:
#         # produce edges for components with source
#         nodes = [source]
#     # extra variables for cycle detection:
#     cycle_stack = []
#     output_cycles = set()
#
#     def get_hashable_cycle(cycle):
#         """cycle as a tuple in a deterministic order."""
#         m = min(cycle)
#         mi = cycle.index(m)
#         mi_plus_1 = mi + 1 if mi < len(cycle) - 1 else 0
#         if cycle[mi - 1] > cycle[mi_plus_1]:
#             result = cycle[mi:] + cycle[:mi]
#         else:
#             result = list(reversed(cycle[:mi_plus_1])) + list(reversed(cycle[mi_plus_1:]))
#         return tuple(result)
#
#     for start in nodes:
#         if start in cycle_stack:
#             continue
#         cycle_stack.append(start)
#
#         stack = [(start, iter(g[start]))]
#         while stack:
#             parent, children = stack[-1]
#             try:
#                 child = next(children)
#
#                 if child not in cycle_stack:
#                     cycle_stack.append(child)
#                     stack.append((child, iter(g[child])))
#                 else:
#                     i = cycle_stack.index(child)
#                     if i < len(cycle_stack) - 2:
#                         output_cycles.add(get_hashable_cycle(cycle_stack[i:]))
#
#             except StopIteration:
#                 stack.pop()
#                 cycle_stack.pop()
#
#     list_of_circles = [list(i) for i in output_cycles]
#     return set([item for sublist in [[((circle[0].upper()), circle[-1].upper())] + \
#                                      [(circle[i].upper(), circle[i + 1].upper()) for i in range(0, len(circle) - 1)] for
#                                      circle in
#                                      list_of_circles] for item in sublist])


def get_terminal_atoms_bonds(g):
    terminal_atoms = set([i for i in g.nodes if len(g.edges(i)) <= 1])
    return set([tuple([j.upper() for j in i]) for i in g.edges if set(i).intersection(terminal_atoms)])


def get_flexibility_and_size(filename):
    ligands_mmcifs = split_file(filename)
    ligand_stats_list = []
    j = 0
    for mmcif_dict in ligands_mmcifs:
        ligand_name = mmcif_dict['_chem_comp.id'][0]
        print('{} file of {} - name {}'.format(j, len(ligands_mmcifs), ligand_name))
        if ligand_name.upper() == 'UNL':
            ligand_stats_list.append([ligand_name, '0', '1'])
        else:
            j += 1
            bonds = get_bonds(mmcif_dict)
            atoms = get_atoms(mmcif_dict)
            hydrogen_atoms = get_hydrogen_atoms(atoms)
            graph = get_graph(bonds)
            non_rotateable_bonds = set.union(get_hydrogen_bonds(hydrogen_atoms, bonds), get_non_single_bonds(bonds),
                                             get_bonds_in_cycles(bonds), get_terminal_atoms_bonds(graph))

            def get_flexibility():
                if len(bonds) != 0:
                    return len(non_rotateable_bonds) / len(list(bonds))
                else:
                    return 1
            # print('bonds: ' + str(bonds))
            ligand_stats_list.append([ligand_name,
                                      len(atoms) - len(hydrogen_atoms),
                                      round(get_flexibility(), 6)])
    return ligand_stats_list


def create_csv(filename, ligand_stats_list):
    with open(filename, 'w', newline='') as csvfile:
        ligand_stats_writer = csv.writer(csvfile, delimiter=';',
                                         quotechar='|', quoting=csv.QUOTE_MINIMAL)
        ligand_stats_writer.writerow(['LigandID', 'heavyAtomSize', 'flexibility'])
        for i in ligand_stats_list:
            ligand_stats_writer.writerow(i)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Intro task - parse different types of the data.')
    parser.add_argument('mmcif_file', help='mmcif file to compute ligand_stats file from', type=str)
    parser.add_argument('ligand_stats_csv',
                        help='Output CSV file with ligand statistics (heavy atoms size and flexibility)',
                        type=str)
    args = parser.parse_args()
    ligand_stats_lst = get_flexibility_and_size(args.mmcif_file)
    create_csv(args.ligand_stats_csv, ligand_stats_lst)
