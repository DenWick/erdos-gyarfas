"""Cycle search: find simple cycles of given lengths, with a witness for each.

The search is exact. For each candidate length k it runs a depth-limited
backtracking DFS that only builds cycles whose smallest vertex is the start
vertex, so each cycle is explored from one start only. Whole paths are
tracked (not just a visited set), which is what makes the search correct:
a single global "visited" set would only explore one DFS tree and miss
most cycles.

The problem is NP-hard in general (k = n is the Hamiltonian cycle problem),
so the worst case is exponential. In practice it is instant for graphs with
a few dozen vertices, which covers every graph discussed in this project.
"""

from __future__ import annotations

from .graph import Graph


def find_cycle_of_length(graph: Graph, k: int) -> list[int] | None:
    """Return one simple cycle with exactly k vertices, or None if none exists."""
    if k < 3 or k > graph.n:
        return None

    adj = [sorted(nbrs) for nbrs in graph.adj]

    for start in range(graph.n):
        # Only use vertices >= start, so `start` is the minimum of the cycle.
        if len(adj[start]) < 2:
            continue
        path = [start]
        on_path = [False] * graph.n
        on_path[start] = True
        # Explicit stack of neighbour iterators avoids Python's recursion limit.
        iters = [iter(adj[start])]
        while iters:
            advanced = False
            for w in iters[-1]:
                if w < start:
                    continue
                if w == start:
                    if len(path) == k:
                        return list(path)
                    continue
                if on_path[w] or len(path) == k:
                    continue
                path.append(w)
                on_path[w] = True
                iters.append(iter(adj[w]))
                advanced = True
                break
            if not advanced:
                iters.pop()
                on_path[path.pop()] = False
    return None


def cycle_spectrum(graph: Graph) -> set[int]:
    """Return the set of all cycle lengths in the graph (exhaustive)."""
    return {k for k in range(3, graph.n + 1) if find_cycle_of_length(graph, k)}


def powers_of_two_up_to(limit: int) -> list[int]:
    """Powers of two that are valid cycle lengths: 4, 8, 16, ... <= limit."""
    out, k = [], 4
    while k <= limit:
        out.append(k)
        k <<= 1
    return out


def is_power_of_two(k: int) -> bool:
    return k >= 4 and k & (k - 1) == 0


def power_of_two_cycles(graph: Graph) -> dict[int, list[int] | None]:
    """Map each power-of-two length 4, 8, ... <= n to a witness cycle (or None)."""
    return {k: find_cycle_of_length(graph, k) for k in powers_of_two_up_to(graph.n)}
