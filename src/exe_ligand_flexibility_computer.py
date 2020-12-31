import io
import os
import re

import networkx as nx
from Bio.File import as_handle
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

from src.parser_pdb import get_mmcif_dictionary

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


def get_graph(mmcif_dict):
    bonds = zip(mmcif_dict['_chem_comp_bond.atom_id_1'],
                mmcif_dict['_chem_comp_bond.atom_id_2'],
                [i.lower() for i in mmcif_dict['_chem_comp_bond.value_order']],
                [bond_grades[i.lower()] for i in mmcif_dict['_chem_comp_bond.value_order']])
    bonds_atom_ids_only = [i[:2] for i in bonds]
    atoms = set([item for sublist in bonds_atom_ids_only for item in sublist])
    g = nx.Graph()
    g.add_nodes_from(atoms)
    g.add_edges_from(bonds_atom_ids_only)
    return g


def find_all_cycles(G, source=None, cycle_length_limit=None):
    """forked from networkx dfs_edges function. Assumes nodes are integers, or at least
    types which work with min() and > ."""
    if source is None:
        # produce edges for all components
        nodes = [list(i)[0] for i in nx.connected_components(G)]
    else:
        # produce edges for components with source
        nodes = [source]
    # extra variables for cycle detection:
    cycle_stack = []
    output_cycles = set()

    def get_hashable_cycle(cycle):
        """cycle as a tuple in a deterministic order."""
        m = min(cycle)
        mi = cycle.index(m)
        mi_plus_1 = mi + 1 if mi < len(cycle) - 1 else 0
        if cycle[mi - 1] > cycle[mi_plus_1]:
            result = cycle[mi:] + cycle[:mi]
        else:
            result = list(reversed(cycle[:mi_plus_1])) + list(reversed(cycle[mi_plus_1:]))
        return tuple(result)

    for start in nodes:
        if start in cycle_stack:
            continue
        cycle_stack.append(start)

        stack = [(start, iter(G[start]))]
        while stack:
            parent, children = stack[-1]
            try:
                child = next(children)

                if child not in cycle_stack:
                    cycle_stack.append(child)
                    stack.append((child, iter(G[child])))
                else:
                    i = cycle_stack.index(child)
                    if i < len(cycle_stack) - 2:
                        output_cycles.add(get_hashable_cycle(cycle_stack[i:]))

            except StopIteration:
                stack.pop()
                cycle_stack.pop()

    list_of_circles = [list(i) for i in output_cycles]
    return set([item for sublist in [[((circle[0].upper()), circle[-1].upper())] + \
                                     [(circle[i].upper(), circle[i + 1].upper()) for i in range(0, len(circle) - 1)] for
                                     circle in
                                     list_of_circles] for item in sublist])
