"""Draw the Markström graph as a crossing-free SVG, with a 16-cycle highlighted.

Layout: Tutte's barycentric embedding. The graph is 3-connected and planar,
so fixing one face as a convex outer polygon and placing every other vertex
at the average of its neighbours gives a planar drawing with convex faces.

Writes figures/markstrom-light.svg and figures/markstrom-dark.svg.
Requires networkx and numpy.
"""

import math
import sys
from pathlib import Path

import networkx as nx
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from erdos_gyarfas import find_cycle_of_length, markstrom  # noqa: E402

OUTER_FACE = {1, 2, 11, 8, 9, 18, 15, 16, 4}

THEMES = {
    "light": dict(bg="#ffffff", edge="#c4c9d4", node="#ffffff", stroke="#4b5563",
                  text="#1f2937", hi="#e4572e", hi_node="#e4572e", hi_text="#ffffff"),
    "dark": dict(bg="#0d1117", edge="#3d444d", node="#161b22", stroke="#8b949e",
                 text="#e6edf3", hi="#ff7b54", hi_node="#ff7b54", hi_text="#0d1117"),
}


def faces(G: nx.Graph) -> list[list[int]]:
    ok, emb = nx.check_planarity(G)
    assert ok
    seen, out = set(), []
    for u, v in emb.edges():
        if (u, v) not in seen:
            out.append(emb.traverse_face(u, v, mark_half_edges=seen))
    return out


def tutte_layout(G: nx.Graph, outer: list[int]) -> dict[int, np.ndarray]:
    pos = {}
    k = len(outer)
    for i, v in enumerate(outer):
        a = math.pi / 2 + 2 * math.pi * i / k
        pos[v] = np.array([math.cos(a), -math.sin(a)])
    inner = [v for v in G if v not in pos]
    idx = {v: i for i, v in enumerate(inner)}
    A = np.zeros((len(inner), len(inner)))
    b = np.zeros((len(inner), 2))
    for v in inner:
        i = idx[v]
        A[i, i] = G.degree(v)
        for w in G[v]:
            if w in idx:
                A[i, idx[w]] -= 1
            else:
                b[i] += pos[w]
    sol = np.linalg.solve(A, b)
    for v in inner:
        pos[v] = sol[idx[v]]
    return pos


def svg(G, pos, cycle, theme, size=640, pad=46, r=15):
    t = THEMES[theme]
    xs = np.array([p[0] for p in pos.values()])
    ys = np.array([p[1] for p in pos.values()])
    s = (size - 2 * pad) / max(np.ptp(xs), np.ptp(ys))
    cx, cy = (xs.max() + xs.min()) / 2, (ys.max() + ys.min()) / 2

    def P(v):
        return (size / 2 + (pos[v][0] - cx) * s, size / 2 + (pos[v][1] - cy) * s)

    cyc_edges = {frozenset((cycle[i], cycle[(i + 1) % len(cycle)])) for i in range(len(cycle))}
    on = set(cycle)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
           f'width="{size}" height="{size}" font-family="Inter, Segoe UI, Helvetica, Arial, sans-serif">',
           f'<title>Markström graph with a 16-cycle highlighted</title>',
           f'<rect width="100%" height="100%" rx="18" fill="{t["bg"]}"/>']
    for u, v in G.edges():
        (x1, y1), (x2, y2) = P(u), P(v)
        if frozenset((u, v)) in cyc_edges:
            continue
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                   f'stroke="{t["edge"]}" stroke-width="2.2"/>')
    pts = " ".join(f"{P(v)[0]:.1f},{P(v)[1]:.1f}" for v in cycle)
    out.append(f'<polygon points="{pts}" fill="none" stroke="{t["hi"]}" stroke-width="4.5" '
               f'stroke-linejoin="round"/>')
    for v in G:
        x, y = P(v)
        hot = v in on
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" '
                   f'fill="{t["hi_node"] if hot else t["node"]}" '
                   f'stroke="{t["hi"] if hot else t["stroke"]}" stroke-width="2"/>')
        out.append(f'<text x="{x:.1f}" y="{y + 4.5:.1f}" text-anchor="middle" font-size="12.5" '
                   f'font-weight="600" fill="{t["hi_text"] if hot else t["text"]}">{v}</text>')
    out.append("</svg>")
    return "\n".join(out)


def main():
    g = markstrom()
    G = nx.Graph(g.edges())
    # Of the 14 faces, this 9-face touches all three H7 gadgets equally,
    # so using it as the outer face gives a drawing with 3-fold symmetry.
    outer = next(f for f in faces(G) if set(f) == OUTER_FACE)
    pos = tutte_layout(G, outer)
    cycle = find_cycle_of_length(g, 16)
    figs = ROOT / "figures"
    figs.mkdir(exist_ok=True)
    for theme in THEMES:
        (figs / f"markstrom-{theme}.svg").write_text(svg(G, pos, cycle, theme))
    print("outer face:", outer)
    print("highlighted C16:", cycle)


if __name__ == "__main__":
    main()
