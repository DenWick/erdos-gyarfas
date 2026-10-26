import itertools
import random

import pytest

from erdos_gyarfas import Graph, cycle_spectrum, find_cycle_of_length, power_of_two_cycles
from erdos_gyarfas.named_graphs import complete, cube, heawood, markstrom, odd_cycle, petersen


# --- Markström graph: the facts the project relies on -------------------------

def test_markstrom_is_cubic_with_24_vertices_and_36_edges():
    g = markstrom()
    assert (g.n, g.m) == (24, 36)
    assert all(g.degree(v) == 3 for v in range(g.n))


def test_markstrom_has_no_c4_or_c8_but_has_c16():
    res = power_of_two_cycles(markstrom())
    assert res[4] is None
    assert res[8] is None
    assert res[16] is not None and markstrom().is_cycle(res[16])


def test_markstrom_cycle_spectrum_matches_literature():
    # MathWorld: cycles of lengths 3, 5, 6, 7 and 9 through 24.
    assert cycle_spectrum(markstrom()) == {3, 5, 6, 7} | set(range(9, 25))


def test_markstrom_is_planar():
    nx = pytest.importorskip("networkx")
    G = nx.Graph(markstrom().edges())
    assert nx.check_planarity(G)[0]


# --- Classic graphs with known cycle spectra -----------------------------------

@pytest.mark.parametrize(
    "graph, spectrum",
    [
        (complete(4), {3, 4}),
        (complete(5), {3, 4, 5}),
        (petersen(), {5, 6, 8, 9}),
        (heawood(), {6, 8, 10, 12, 14}),
        (cube(3), {4, 6, 8}),
        (odd_cycle(7), {7}),
    ],
)
def test_known_spectra(graph, spectrum):
    assert cycle_spectrum(graph) == spectrum


def test_witnesses_are_real_cycles():
    for g in (markstrom(), petersen(), heawood(), complete(6)):
        for k, cyc in power_of_two_cycles(g).items():
            if cyc is not None:
                assert len(cyc) == k and g.is_cycle(cyc)


# --- Cross-check against brute force on random small graphs --------------------

def brute_force_spectrum(g: Graph) -> set[int]:
    found = set()
    for k in range(3, g.n + 1):
        for subset in itertools.combinations(range(g.n), k):
            first, rest = subset[0], subset[1:]
            if any(g.is_cycle([first, *perm]) for perm in itertools.permutations(rest)):
                found.add(k)
                break
    return found


@pytest.mark.parametrize("seed", range(40))
def test_matches_brute_force(seed):
    rng = random.Random(seed)
    n = rng.randint(3, 7)
    g = Graph(n, [e for e in itertools.combinations(range(n), 2) if rng.random() < 0.5])
    assert cycle_spectrum(g) == brute_force_spectrum(g)


def test_out_of_range_lengths():
    g = complete(4)
    assert find_cycle_of_length(g, 2) is None
    assert find_cycle_of_length(g, 5) is None
