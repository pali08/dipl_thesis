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


graph_test = (
    ('a', 'b'), ('a', 'c'), ('a', 'e'), ('b', 'c'), ('c', 'e'), ('b', 'g'), ('e', 'g'), ('i', 'h'), ('i', 'j'),
    ('j', 'h'))
find_all_cycles(graph_test)
