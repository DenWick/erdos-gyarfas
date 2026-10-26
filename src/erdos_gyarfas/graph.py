"""A minimal undirected simple graph, with helpers to load and build graphs."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


class Graph:
    """Undirected simple graph on vertices 0..n-1, stored as adjacency sets."""

    def __init__(self, n: int, edges: Iterable[tuple[int, int]] = ()) -> None:
        if n < 0:
            raise ValueError("number of vertices must be non-negative")
        self.n = n
        self.adj: list[set[int]] = [set() for _ in range(n)]
        for u, v in edges:
            self.add_edge(u, v)

    def add_edge(self, u: int, v: int) -> None:
        if not (0 <= u < self.n and 0 <= v < self.n):
            raise ValueError(f"edge ({u}, {v}) has a vertex outside 0..{self.n - 1}")
        if u == v:
            raise ValueError(f"self-loop at vertex {u} is not allowed in a simple graph")
        self.adj[u].add(v)
        self.adj[v].add(u)

    @property
    def m(self) -> int:
        return sum(len(nbrs) for nbrs in self.adj) // 2

    def degree(self, v: int) -> int:
        return len(self.adj[v])

    def min_degree(self) -> int:
        return min((len(nbrs) for nbrs in self.adj), default=0)

    def edges(self) -> list[tuple[int, int]]:
        return [(u, v) for u in range(self.n) for v in sorted(self.adj[u]) if u < v]

    def is_cycle(self, cycle: list[int]) -> bool:
        """True if `cycle` lists distinct vertices forming a closed cycle in this graph."""
        k = len(cycle)
        if k < 3 or len(set(cycle)) != k:
            return False
        return all(cycle[(i + 1) % k] in self.adj[cycle[i]] for i in range(k))

    @classmethod
    def from_edge_list_file(cls, path: str | Path) -> "Graph":
        """Read a graph from a text file with one `u v` edge per line.

        Blank lines and lines starting with `#` are ignored. Vertices are
        integers; the number of vertices is inferred as max(vertex) + 1.
        """
        edges: list[tuple[int, int]] = []
        for lineno, raw in enumerate(Path(path).read_text().splitlines(), start=1):
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 2:
                raise ValueError(f"{path}:{lineno}: expected 'u v', got {raw!r}")
            edges.append((int(parts[0]), int(parts[1])))
        n = 1 + max((max(e) for e in edges), default=-1)
        return cls(n, edges)

    def __repr__(self) -> str:
        return f"Graph(n={self.n}, m={self.m})"
