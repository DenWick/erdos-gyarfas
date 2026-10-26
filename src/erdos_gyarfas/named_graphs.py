"""Graphs that appear in the project, built explicitly so every claim is checkable."""

from __future__ import annotations

from .graph import Graph

# The Markström graph: the unique planar graph among the four smallest cubic
# graphs with no cycle of length 4 or 8 (Markström, 2004). 24 vertices,
# 36 edges. It has girth 3 and cycle spectrum {3, 5, 6, 7, 9, 10, ..., 24}.
#
# This labelling comes from the construction "take K4, replace three of its
# vertices by a 7-vertex gadget H7 and the fourth by a triangle". Vertices
# 21, 22, 23 are the triangle; 0-6, 7-13 and 14-20 are the three gadgets.
# scripts/derive_markstrom.py re-derives it from that description.
MARKSTROM_EDGES: list[tuple[int, int]] = [
    (0, 1), (0, 2), (0, 3), (1, 2), (1, 4), (2, 11), (3, 5), (3, 6), (4, 5),
    (4, 16), (5, 6), (6, 21), (7, 8), (7, 9), (7, 10), (8, 9), (8, 11),
    (9, 18), (10, 12), (10, 13), (11, 12), (12, 13), (13, 22), (14, 15),
    (14, 16), (14, 17), (15, 16), (15, 18), (17, 19), (17, 20), (18, 19),
    (19, 20), (20, 23), (21, 22), (21, 23), (22, 23),
]


def markstrom() -> Graph:
    return Graph(24, MARKSTROM_EDGES)


def complete(n: int) -> Graph:
    return Graph(n, [(u, v) for u in range(n) for v in range(u + 1, n)])


def petersen() -> Graph:
    g = Graph(10)
    for i in range(5):
        g.add_edge(i, (i + 1) % 5)          # outer pentagon
        g.add_edge(5 + i, 5 + (i + 2) % 5)  # inner pentagram
        g.add_edge(i, 5 + i)                # spokes
    return g


def heawood() -> Graph:
    """Heawood graph: cubic, 14 vertices, girth 6 (so no C4)."""
    g = Graph(14)
    for i in range(14):
        g.add_edge(i, (i + 1) % 14)
    for i in range(0, 14, 2):
        g.add_edge(i, (i + 5) % 14)
    return g


def cube(d: int = 3) -> Graph:
    n = 1 << d
    return Graph(n, [(v, v ^ (1 << b)) for v in range(n) for b in range(d) if v < v ^ (1 << b)])


def odd_cycle(k: int = 7) -> Graph:
    """C_k with k odd: minimum degree 2 and no power-of-two cycle (shows delta >= 3 is needed)."""
    return Graph(k, [(i, (i + 1) % k) for i in range(k)])


NAMED = {
    "markstrom": markstrom,
    "petersen": petersen,
    "heawood": heawood,
    "k4": lambda: complete(4),
    "cube": cube,
    "c7": odd_cycle,
}
