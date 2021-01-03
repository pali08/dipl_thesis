def find_all_cycles(graph_as_list_of_lists):
    cycles = []
    for edge in graph_as_list_of_lists:
        for node in edge:
            find_new_cycles([node], cycles, graph_as_list_of_lists)

    return set([item for sublist in [[((circle[0].upper()), circle[-1].upper())] + \
                                     [(circle[i].upper(), circle[i + 1].upper()) for i in range(0, len(circle) - 1)] for
                                     circle in
                                     cycles] for item in sublist])
    # for cy in cycles:
    #     path = [str(node) for node in cy]
    #     s = ",".join(path)
    #     print(s)


def find_new_cycles(path, cycles, graph):
    start_node = path[0]
    next_node = None
    sub = []

    # visit each edge and each node of each edge
    for edge in graph:
        node1, node2 = edge
        if start_node in edge:
            if node1 == start_node:
                next_node = node2
            else:
                next_node = node1
            if not visited(next_node, path):
                # neighbor node not on path yet
                sub = [next_node]
                sub.extend(path)
                # explore extended path
                find_new_cycles(sub, cycles, graph)
            elif len(path) > 2 and next_node == path[-1]:
                # cycle found
                p = rotate_to_smallest(path)
                inv = invert(p)
                if is_new(p, cycles) and is_new(inv, cycles):
                    cycles.append(p)


def invert(path):
    return rotate_to_smallest(path[::-1])


#  rotate cycle path such that it begins with the smallest node
def rotate_to_smallest(path):
    n = path.index(min(path))
    return path[n:] + path[:n]


def is_new(path, cycles):
    return not path in cycles


def visited(node, path):
    return node in path

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
