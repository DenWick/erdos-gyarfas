"""Command-line interface: python -m erdos_gyarfas [graph ...]"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .cycles import cycle_spectrum, power_of_two_cycles
from .graph import Graph
from .named_graphs import NAMED

WIDTH = 60


def load(spec: str) -> tuple[str, Graph]:
    if spec in NAMED:
        return spec, NAMED[spec]()
    path = Path(spec)
    if path.is_file():
        return path.name, Graph.from_edge_list_file(path)
    raise SystemExit(f"unknown graph {spec!r}: use one of {', '.join(NAMED)} or an edge-list file")


def report(name: str, g: Graph, show_spectrum: bool) -> bool:
    """Print a report. Returns False only if g is a counterexample."""
    print("=" * WIDTH)
    print(f"  {name}")
    print("=" * WIDTH)
    print(f"  vertices: {g.n}   edges: {g.m}   min degree: {g.min_degree()}")

    results = power_of_two_cycles(g)
    for k, cyc in results.items():
        if cyc:
            print(f"  C{k:<4} found   {' -> '.join(map(str, cyc + cyc[:1]))}")
        else:
            print(f"  C{k:<4} none")
    if show_spectrum:
        print(f"  cycle lengths: {sorted(cycle_spectrum(g))}")

    has_one = any(results.values())
    if g.min_degree() < 3:
        verdict = "conjecture does not apply (min degree < 3)"
    elif has_one:
        verdict = "conjecture holds for this graph"
    else:
        verdict = "NO power-of-two cycle: COUNTEREXAMPLE (please double-check and publish!)"
    print(f"\n  -> {verdict}\n")
    return g.min_degree() < 3 or has_one


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="python -m erdos_gyarfas",
        description="Check graphs for cycles whose length is a power of two.",
    )
    p.add_argument(
        "graphs",
        nargs="*",
        default=["markstrom", "petersen", "k4", "c7"],
        help=f"named graph ({', '.join(NAMED)}) or path to an edge-list file",
    )
    p.add_argument("--spectrum", action="store_true", help="also print every cycle length")
    args = p.parse_args(argv)

    ok = all([report(*load(s), args.spectrum) for s in args.graphs])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
