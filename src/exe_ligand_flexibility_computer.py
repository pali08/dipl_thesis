import argparse
import csv
import io
import re

import networkx as nx
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

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
        return list(zip([i.upper() for i in mmcif_dict['_chem_comp_bond.atom_id_1']],
                        [i.upper() for i in mmcif_dict['_chem_comp_bond.atom_id_2']],
                        [i.lower() for i in mmcif_dict['_chem_comp_bond.value_order']],
                        [bond_grades[i.lower()] for i in mmcif_dict['_chem_comp_bond.value_order']]))
    except KeyError:
        return []


def get_atoms(mmcif_dict):
    return list(zip([i.upper() for i in mmcif_dict['_chem_comp_atom.atom_id']],
                    [i.upper() for i in mmcif_dict['_chem_comp_atom.type_symbol']]))


def get_hydrogen_atoms(atoms):
    return set([i[0] for i in atoms if i[1].upper() == 'H'])


def get_hydrogen_bonds(hydrogen_atoms, bonds):
    # print(bonds)
    return set([tuple(i[:2]) for i in bonds if (i[0] in hydrogen_atoms) or (i[1] in hydrogen_atoms)])


def get_non_single_bonds(bonds):
    return [j[:2] for j in [i for i in bonds if i[3] > 1]]


def get_graph(bonds):
    bonds_atom_ids_only = [[j.upper() for j in i[:2]] for i in bonds]
    atoms_from_bonds = set([item.upper() for sublist in bonds_atom_ids_only for item in sublist])
    g = nx.Graph()
    g.add_nodes_from(atoms_from_bonds)
    g.add_edges_from(bonds_atom_ids_only)
    return g


def get_bonds_in_cycles(graph):
    edges_sets = [set(i) for i in graph.edges]
    cycles_sets = [set(i) for i in nx.cycle_basis(graph)]
    bonds_in_cycles = []
    for edge in edges_sets:
        for cycle in cycles_sets:
            if edge.issubset(cycle):
                bonds_in_cycles.append(tuple(edge))
    return bonds_in_cycles


def get_terminal_atoms_bonds(graph, hydrogen_atoms):
    terminal_atoms_with_one_bond = set([i for i in graph.nodes if len(graph.edges(i)) <= 1])

    def count_of_hydrogen_bonds(node):
        return len([i for i in graph.edges(node) if i[0] in hydrogen_atoms or i[1] in hydrogen_atoms])

    terminal_atoms_with_hydrogens_only = set(
        [i for i in graph.nodes if
         (len(list(graph.edges(i))) > 1 and len(list(graph.edges(i))) - count_of_hydrogen_bonds(i) == 1)])
    all_terminal_atoms = set.union(terminal_atoms_with_one_bond, terminal_atoms_with_hydrogens_only)
    return set([tuple([j.upper() for j in i]) for i in graph.edges if set(i).intersection(all_terminal_atoms)])


def remove_tuples_with_order_differences(non_rotateable_bonds):
    """
    looks like networkx removes does not keep order of added notes and 'duplicated'
    bonds are made like this ('A','B') -> ('B','A')
    we need to remove those
    :param non_rotateable_bonds:
    :return:
    """
    non_rotateable_bonds_revert_order_removed = set()
    for bond in non_rotateable_bonds:
        non_rotateable_bonds_revert_order_removed.add(tuple(sorted(bond)))
    return non_rotateable_bonds_revert_order_removed


def get_flexibility_and_size(filename):
    ligands_mmcifs = split_file(filename)
    ligand_stats_list = []
    j = 1
    for mmcif_dict in ligands_mmcifs:
        ligand_name = mmcif_dict['_chem_comp.id'][0]
        print('{} file of {} - name {}'.format(j, len(ligands_mmcifs), ligand_name))
        j += 1
        if ligand_name.upper() == 'UNL':
            ligand_stats_list.append([ligand_name, '0', '1'])
        else:
            bonds = get_bonds(mmcif_dict)
            atoms = get_atoms(mmcif_dict)
            hydrogen_atoms = get_hydrogen_atoms(atoms)
            graph = get_graph(bonds)
            non_rotateable_bonds = remove_tuples_with_order_differences(
                set.union(get_hydrogen_bonds(hydrogen_atoms, bonds), get_non_single_bonds(bonds),
                          get_bonds_in_cycles(graph), get_terminal_atoms_bonds(graph, hydrogen_atoms)))

            def get_flexibility():
                if len(bonds) != 0:
                    return (len(list(bonds)) - len(non_rotateable_bonds)) / len(list(bonds))
                else:
                    return 1

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
    parser = argparse.ArgumentParser(description='Script for computing ligand flexibility and heavy atoms count')
    parser.add_argument('mmcif_file', help='mmcif file to compute ligand_stats file from', type=str)
    parser.add_argument('ligand_stats_csv',
                        help='Output CSV file with ligand statistics (heavy atoms size and flexibility)',
                        type=str)
    args = parser.parse_args()
    ligand_stats_lst = get_flexibility_and_size(args.mmcif_file)
    print('Ligand flexibility has been computed.')
    create_csv(args.ligand_stats_csv, ligand_stats_lst)
    print('Data were written to {}'.format(args.ligand_stats_csv))
