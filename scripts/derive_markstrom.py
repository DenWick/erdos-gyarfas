"""Re-derive the Markström graph from a structural description.

Construction (Heckman & Krakovski / Markström): start from K4, replace three
of its vertices by a 7-vertex gadget H7 and the fourth by a triangle K3.
H7 has four vertices of degree 3 and three "ports" of degree 2, pairwise at
distance >= 2, with one pair of ports at distance 3.

This script enumerates every H7 that fits that description and has no
4- or 8-cycle, tries every way of wiring the ports to K4's edges, and keeps
the results that are cubic, planar and free of C4 and C8. It finds exactly
one graph up to isomorphism, and its cycle spectrum matches the published
one, which is how the edge list in named_graphs.py was obtained.

Requires networkx:  pip install networkx
"""

import itertools
import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from erdos_gyarfas import Graph, cycle_spectrum, markstrom  # noqa: E402


def spectrum(G: nx.Graph) -> set[int]:
    H = nx.convert_node_labels_to_integers(G)
    return cycle_spectrum(Graph(H.number_of_nodes(), H.edges()))


def h7_candidates() -> list[nx.Graph]:
    found: list[nx.Graph] = []
    for edges in itertools.combinations(itertools.combinations(range(7), 2), 9):
        H = nx.Graph(edges)
        if H.number_of_nodes() != 7 or not nx.is_connected(H):
            continue
        if sorted(d for _, d in H.degree()) != [2, 2, 2, 3, 3, 3, 3]:
            continue
        ports = [v for v, d in H.degree() if d == 2]
        dist = [nx.shortest_path_length(H, a, b) for a, b in itertools.combinations(ports, 2)]
        if min(dist) < 2 or 3 not in dist:
            continue
        if spectrum(H) & {4, 8}:
            continue
        if not any(nx.is_isomorphic(H, F) for F in found):
            found.append(H)
    return found


def main() -> None:
    gadgets = h7_candidates()
    print(f"H7 gadgets satisfying the description: {len(gadgets)}")

    results: list[nx.Graph] = []
    k4_edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    for H in gadgets:
        ports = [v for v, d in H.degree() if d == 2]
        for orders in itertools.product(itertools.permutations(ports), repeat=3):
            G = nx.Graph()
            for c in range(3):
                G.add_edges_from(((c, a), (c, b)) for a, b in H.edges())
            G.add_edges_from([((3, 0), (3, 1)), ((3, 1), (3, 2)), ((3, 2), (3, 0))])
            free = {0: list(orders[0]), 1: list(orders[1]), 2: list(orders[2]), 3: [0, 1, 2]}
            for x, y in k4_edges:
                G.add_edge((x, free[x].pop(0)), (y, free[y].pop(0)))
            if {d for _, d in G.degree()} != {3} or not nx.check_planarity(G)[0]:
                continue
            if spectrum(G) & {4, 8}:
                continue
            if not any(nx.is_isomorphic(G, R) for R in results):
                results.append(G)

    print(f"Cubic planar graphs with no C4/C8 from this construction: {len(results)}")
    ref = nx.Graph(markstrom().edges())
    for G in results:
        print(f"  n={G.number_of_nodes()} m={G.number_of_edges()} spectrum={sorted(spectrum(G))}")
        print(f"  isomorphic to the edge list in named_graphs.py: {nx.is_isomorphic(G, ref)}")


if __name__ == "__main__":
    main()
