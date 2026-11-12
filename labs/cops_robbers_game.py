"""
cops_robbers_game.py: play and simulate cops and robbers on networks.

Economic Networks Fundamentals (UAM, Master in Quantitative Economic Analysis)
Part 1.2: "Let's play a game: the cops and robbers example".

- play(...)      an interactive board: move with W A S D (or the arrow keys),
                 Space to stay. Choose the network, the number of cops and
                 robbers, and who you play.
- launcher()     the same with drop-down menus (ipywidgets).
- simulate(...)  computer against computer, many games, for experiments.
- solve(...)     exact optimal play for k cops against one robber
                 (backward induction, like a chess endgame table).

Networks include every example in Olsen (2023), "Cops and Robbers: A Game
of Pursuit on Graphs", Procedia Computer Science 221, 434-441, with her
vertex labels, so you can replay her move tables.

The board is drawn in your browser (HTML + JavaScript), so it responds
instantly and works in Google Colab, in Jupyter, and as a standalone .html
file. Python builds the network and computes the optimal strategies.
"""

from __future__ import annotations

import itertools
import json
import math
import random
from collections import Counter

import networkx as nx
import numpy as np

INF = 10 ** 6


# =========================================================================
# 1. The networks (with positions for drawing)
# =========================================================================
def _graph(edges: str, pos: dict) -> nx.Graph:
    G = nx.Graph([e.split("-") for e in edges.split()])
    nx.set_node_attributes(G, pos, "pos")
    return G


def _ring(labels, r=1.0, start=90, cx=0.0, cy=0.0):
    n = len(labels)
    return {l: (cx + r * math.cos(math.radians(start - 360 * i / n)),
                cy + r * math.sin(math.radians(start - 360 * i / n)))
            for i, l in enumerate(labels)}


def _cycle(labels: str) -> nx.Graph:
    edges = " ".join(f"{a}-{b}" for a, b in zip(labels, labels[1:] + labels[0]))
    return _graph(edges, _ring(list(labels)))


def _olsen_dodecahedron() -> nx.Graph:
    """Olsen's Figure 8, with her labels (outer pentagon A, E, H, L, O;
    inner pentagon R, S, T, U, V)."""
    edges = ("A-E E-H H-L L-O O-A A-B E-D H-G L-J O-N "
             "B-C C-D D-F F-G G-I I-J J-M M-N N-Q Q-B "
             "Q-R C-S F-T I-U M-V R-S S-T T-U U-V V-R")
    pos = {**_ring(list("AEHLO"), 1.0),                    # outer pentagon
           **_ring(list("BCDFGIJMNQ"), 0.66),              # middle ring of 10
           **_ring(list("STUVR"), 0.3, start=54)}          # inner pentagon, each next to its partner
    return _graph(edges, pos)


def _olsen_cube() -> nx.Graph:
    """Olsen's Figure 9(b): the cube drawn flat, outer square A B C D,
    inner square F G H E."""
    pos = {"A": (-1, 1), "B": (1, 1), "C": (1, -1), "D": (-1, -1),
           "F": (-.45, .45), "G": (.45, .45), "H": (.45, -.45), "E": (-.45, -.45)}
    return _graph("A-B B-C C-D D-A F-G G-H H-E E-F A-F B-G C-H D-E", pos)


def _grid(m: int) -> nx.Graph:
    G = nx.grid_2d_graph(m, m)
    G = nx.relabel_nodes(G, {(i, j): f"{chr(65 + j)}{m - i}" for i, j in G})
    pos = {f"{chr(65 + j)}{m - i}": (j, -i) for i in range(m) for j in range(m)}
    nx.set_node_attributes(G, pos, "pos")
    return G


def _letters(G: nx.Graph, seed: int) -> nx.Graph:
    """Relabel 0..n-1 as A, B, ..., Z, AA, AB ... and add a spring layout."""
    names = [chr(65 + i) if i < 26 else chr(64 + i // 26) + chr(65 + i % 26)
             for i in range(G.number_of_nodes())]
    G = nx.relabel_nodes(G, dict(zip(sorted(G), names)))
    nx.set_node_attributes(G, nx.kamada_kawai_layout(G), "pos")
    return G


def _connected(make, seed: int) -> nx.Graph:
    for s in range(seed, seed + 200):
        G = make(s)
        if nx.is_connected(G):
            return G
    raise RuntimeError("Could not draw a connected network; try more links.")


NETWORKS = {
    # --- the seminar's whiteboard examples ---
    "Square (Round 1)":                 lambda n, s: _graph("A-B B-C C-D D-A",
                                            {"A": (-1, 1), "B": (1, 1), "C": (1, -1), "D": (-1, -1)}),
    "Square + diagonal (Round 2)":      lambda n, s: _graph("A-B B-C C-D D-A B-D",
                                            {"A": (-1, 1), "B": (1, 1), "C": (1, -1), "D": (-1, -1)}),
    "House (Round 3)":                  lambda n, s: _graph("A-B B-C C-D D-A A-E B-E",
                                            {"A": (-1, .4), "B": (1, .4), "C": (1, -1.2), "D": (-1, -1.2), "E": (0, 1.4)}),
    # --- Olsen (2023), with her labels ---
    "Olsen Fig. 1: complete graph K4":  lambda n, s: _graph("A-B A-C A-D B-C B-D C-D",
                                            {"A": (-1, 1), "B": (1, 1), "C": (1, -1), "D": (-1, -1)}),
    "Olsen Fig. 2: hexagon":            lambda n, s: _cycle("ABCDEF"),
    "Olsen Fig. 3: tree":               lambda n, s: _graph("A-B B-C A-D D-E A-F F-G",
                                            {"A": (0, 1), "B": (-1, .3), "C": (-1.3, -.5), "D": (0, .2),
                                             "E": (0, -.6), "F": (1, .3), "G": (1.3, -.5)}),
    "Olsen Fig. 4: pitfall P":          lambda n, s: _graph("F-D F-G G-E D-E D-P E-P",
                                            {"F": (-1, 1), "D": (.4, 1), "G": (-1, -.2), "E": (.4, -.2), "P": (1.4, -.2)}),
    "Olsen Fig. 7: octagon":            lambda n, s: _cycle("ABCDEFGH"),
    "Olsen Fig. 8: dodecahedron":       lambda n, s: _olsen_dodecahedron(),
    "Olsen Fig. 9: cube":               lambda n, s: _olsen_cube(),
    # --- classic families ---
    "Grid 3x3":                         lambda n, s: _grid(3),
    "Grid 4x4":                         lambda n, s: _grid(4),
    "Grid 5x5":                         lambda n, s: _grid(5),
    "Petersen graph":                   lambda n, s: _letters(nx.petersen_graph(), s),
    # --- random networks (size n, seed s) ---
    "Random (Erdős–Rényi)":             lambda n, s: _letters(_connected(
                                            lambda t: nx.gnm_random_graph(n, int(1.6 * n), seed=t), s), s),
    "Hubs (Barabási–Albert)":           lambda n, s: _letters(nx.barabasi_albert_graph(n, 2, seed=s), s),
    "Small world (Watts–Strogatz)":     lambda n, s: _letters(_connected(
                                            lambda t: nx.watts_strogatz_graph(n, 4, 0.2, seed=t), s), s),
    "Random tree":                      lambda n, s: _letters(nx.random_labeled_tree(n, seed=s)
                                            if hasattr(nx, "random_labeled_tree") else nx.random_tree(n, seed=s), s),
}


def find_network(name: str) -> str:
    """Exact name, or the first network whose name contains `name`
    (ignoring case): 'dodeca' -> 'Olsen Fig. 8: dodecahedron'."""
    if name in NETWORKS:
        return name
    hits = [k for k in NETWORKS if name.lower() in k.lower()]
    if not hits:
        raise KeyError(f"Unknown network {name!r}. Choose from: {list(NETWORKS)}")
    return hits[0]


def network(name: str, n: int = 16, seed: int = 1) -> nx.Graph:
    """One of NETWORKS by name (or part of it); n and seed only matter for
    random networks."""
    return NETWORKS[find_network(name)](n, seed)


# =========================================================================
# 2. Theory: corners (Olsen's pitfalls), exact solver, cop number
# =========================================================================
def corners(G: nx.Graph) -> list[str]:
    """Olsen's pitfalls: P is a corner if some other K has N[P] ⊆ N[K]."""
    closed = {v: set(G[v]) | {v} for v in G}
    return sorted(p for p in G if any(k != p and closed[p] <= closed[k] for k in G[p]))


def dismantlable(G: nx.Graph) -> bool:
    """Cross out corners one by one; one node left = one cop always wins."""
    H = G.copy()
    while H.number_of_nodes() > 1:
        c = corners(H)
        if not c:
            return False
        H.remove_node(c[0])
    return True


def solve(G: nx.Graph, k: int, max_states: int = 120_000):
    """Exact optimal play for k cops against ONE robber (backward induction).

    Returns (states, Vc, Vr):
      states  list of cop positions (sorted tuples of node indices)
      Vc[s,r] cop moves until capture with optimal play, COPS to move
      Vr[s,r] the same with the ROBBER to move
    INF means the robber escapes forever. Returns None if the game is too big.
    """
    nodes = sorted(G)
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    states = list(itertools.combinations_with_replacement(range(n), k))
    if len(states) * n > max_states:
        return None
    sidx = {s: i for i, s in enumerate(states)}
    closed = [sorted({idx[u] for u in G[v]} | {idx[v]}) for v in nodes]
    nxt = [np.array(sorted({sidx[tuple(sorted(m))] for m in itertools.product(*(closed[c] for c in s))}))
           for s in states]
    caught = np.zeros((len(states), n), bool)
    for i, s in enumerate(states):
        caught[i, list(s)] = True
    Vc = np.where(caught, 0, INF)
    Vr = np.where(caught, 0, INF)
    for _ in range(4 * n * k + 10):
        # robber to move: picks the reply that delays capture longest
        # (staying put is in closed[r], so the robber never has to step onto a cop)
        newVr = np.stack([Vc[:, closed[r]].max(axis=1) for r in range(n)], axis=1)
        newVr = np.where(caught, 0, newVr)
        # cops to move: pick the joint move that captures soonest
        best = np.array([Vr[m].min(axis=0) for m in nxt])
        newVc = np.where(caught, 0, np.minimum(best + 1, INF))
        if np.array_equal(newVc, Vc) and np.array_equal(newVr, Vr):
            break
        Vc, Vr = newVc, newVr
    return states, Vc, Vr


def cops_always_win(G: nx.Graph, k: int):
    """True/False with k cops (cops place first, robber second, cops move
    first), or None if the game is too big to solve exactly."""
    sol = solve(G, k)
    if sol is None:
        return None
    states, Vc, _ = sol
    return bool(Vc.max(axis=1).min() < INF)   # best cop start vs worst robber start


def cop_number(G: nx.Graph, kmax: int = 3):
    """Smallest k <= kmax with cops_always_win; '>kmax' or '?' if unknown."""
    for k in range(1, kmax + 1):
        w = cops_always_win(G, k)
        if w is None:
            return "?"
        if w:
            return k
    return f">{kmax}"


# =========================================================================
# 3. The computer players (the same rules are used in the browser)
# =========================================================================
class Brain:
    """Strategies for computer-controlled cops and robbers.

    'smart': exact optimal play when there is one robber and the game is
             small enough to solve; otherwise the heuristics below.
    'greedy': cops step towards the nearest robber (spreading out to
             pincer); robbers keep away from cops, avoid squares a cop can
             reach next move, and prefer nodes with many exits.
    'random': uniform over the moves allowed.
    """

    def __init__(self, G: nx.Graph, k_cops: int, k_robbers: int, rng=None):
        self.nodes = sorted(G)
        self.idx = {v: i for i, v in enumerate(self.nodes)}
        n = len(self.nodes)
        self.closed = [sorted({self.idx[u] for u in G[v]} | {self.idx[v]}) for v in self.nodes]
        self.deg = [G.degree(v) for v in self.nodes]
        D = dict(nx.all_pairs_shortest_path_length(G))
        self.D = [[D[a][b] for b in self.nodes] for a in self.nodes]
        self.rng = rng or random.Random()
        self.table = solve(G, k_cops) if k_robbers == 1 else None
        if self.table:
            states, self.Vc, self.Vr = self.table
            self.sidx = {s: i for i, s in enumerate(states)}

    # --- cops ---------------------------------------------------------
    def cop_moves(self, cops, robbers, ai="smart"):
        live = [r for r in robbers if r is not None]
        if ai == "random":
            return [self.rng.choice(self.closed[c]) for c in cops]
        if ai == "smart" and self.table and len(live) == 1:
            r = live[0]
            options = list(itertools.product(*(self.closed[c] for c in cops)))
            score = lambda m: 0 if r in m else self.Vr[self.sidx[tuple(sorted(m))], r]
            best = min(score(m) for m in options)
            return list(self.rng.choice([m for m in options if score(m) == best]))
        new = []
        for c in cops:
            target = min(live, key=lambda r: (self.D[c][r], r))
            cand = self.closed[c]
            if target in cand:
                new.append(target)
                continue
            d = min(self.D[x][target] for x in cand)
            cand = [x for x in cand if self.D[x][target] == d]
            if new:
                far = max(min(self.D[x][y] for y in new) for x in cand)
                cand = [x for x in cand if min(self.D[x][y] for y in new) == far]
            new.append(self.rng.choice(cand))
        return new

    # --- robbers ------------------------------------------------------
    def robber_move(self, r, cops, ai="smart", taken=()):
        cand = [x for x in self.closed[r] if x not in cops] or [r]
        cand = [x for x in cand if x not in taken] or cand        # robbers spread out
        if ai == "random":
            return self.rng.choice(cand)
        if ai == "smart" and self.table:
            s = self.sidx[tuple(sorted(cops))]
            best = max(self.Vc[s, x] for x in cand)
            cand = [x for x in cand if self.Vc[s, x] == best]
        key = lambda x: (min(self.D[c][x] for c in cops) > 1, min(self.D[c][x] for c in cops), self.deg[x])
        top = max(key(x) for x in cand)
        return self.rng.choice([x for x in cand if key(x) == top])

    # --- starting positions ---------------------------------------------
    def cop_start(self, k, ai="smart"):
        n = len(self.nodes)
        if ai == "random":
            return [self.rng.randrange(n) for _ in range(k)]
        if ai == "smart" and self.table:
            states, Vc, _ = self.table
            worst = [max((Vc[i, r] for r in range(n) if r not in s), default=0) for i, s in enumerate(states)]
            best = min(worst)
            return list(self.rng.choice([s for s, w in zip(states, worst) if w == best]))
        ecc = [max(row) for row in self.D]
        start = [min(range(n), key=lambda v: (ecc[v], -self.deg[v]))]
        while len(start) < k:
            start.append(max(range(n), key=lambda v: (min(self.D[v][c] for c in start), self.deg[v])))
        return start

    def robber_start(self, cops, ai="smart", taken=()):
        free = ([v for v in range(len(self.nodes)) if v not in cops and v not in taken]
                or [v for v in range(len(self.nodes)) if v not in cops] or list(range(len(self.nodes))))
        if ai == "random":
            return self.rng.choice(free)
        if ai == "smart" and self.table:
            s = self.sidx[tuple(sorted(cops))]
            best = max(self.Vc[s, v] for v in free)
            free = [v for v in free if self.Vc[s, v] == best]
        key = lambda v: (min(self.D[c][v] for c in cops), self.deg[v])
        top = max(key(v) for v in free)
        return self.rng.choice([v for v in free if key(v) == top])


# =========================================================================
# 4. Computer against computer: simulations
# =========================================================================
def play_one(G, k_cops=1, k_robbers=1, cop_ai="smart", robber_ai="smart",
             max_rounds=None, brain=None, rng=None):
    """One game. Returns (cops_won, rounds, history)."""
    brain = brain or Brain(G, k_cops, k_robbers, rng)
    max_rounds = max_rounds or 2 * G.number_of_nodes()
    cops = brain.cop_start(k_cops, cop_ai)
    robbers = []
    for _ in range(k_robbers):
        robbers.append(brain.robber_start(cops, robber_ai, taken=robbers))
    history = [(list(cops), list(robbers))]
    for rnd in range(1, max_rounds + 1):
        cops = brain.cop_moves(cops, robbers, cop_ai)
        robbers = [None if (r is None or r in cops) else r for r in robbers]
        if all(r is None for r in robbers):
            history.append((list(cops), list(robbers)))
            return True, rnd, history
        moved = []
        for i, r in enumerate(robbers):
            if r is not None:
                robbers[i] = brain.robber_move(r, cops, robber_ai, taken=moved)
                moved.append(robbers[i])
        robbers = [None if (r is None or r in cops) else r for r in robbers]
        history.append((list(cops), list(robbers)))
        if all(r is None for r in robbers):
            return True, rnd, history
    return False, max_rounds, history


def simulate(name: str, cops=(1, 2, 3), robbers: int = 1, games: int = 100,
             cop_ai="smart", robber_ai="smart", n: int = 16, seed: int = 1):
    """Many computer-vs-computer games on one network. Returns a DataFrame:
    share of games the cops win and average rounds until capture."""
    import pandas as pd
    G = network(name, n, seed)
    rows = []
    for k in cops:
        rng = random.Random(seed)
        brain = Brain(G, k, robbers, rng)
        results = [play_one(G, k, robbers, cop_ai, robber_ai, brain=brain, rng=rng) for _ in range(games)]
        wins = [r for won, r, _ in results if won]
        rows.append({"network": name, "cops": k, "robbers": robbers,
                     "cops win (%)": round(100 * len(wins) / games),
                     "avg rounds to capture": round(sum(wins) / len(wins), 1) if wins else None,
                     "exact play?": bool(brain.table)})
    return pd.DataFrame(rows)


def olsen_blindfold(trials: int = 200_000, seed: int = 0):
    """Olsen section 5: on the cube, cop and robber walk at random, never
    revisiting a node and never staying. Estimate the chance they are both
    at F after one move, cop starting at A and robber at E (she gets 1/9),
    and with the robber starting at D (0: the cube is bipartite)."""
    G, rng = network("Olsen Fig. 9: cube"), random.Random(seed)
    def step(v):
        return rng.choice(sorted(G[v]))
    both_AE = sum(step("A") == "F" and step("E") == "F" for _ in range(trials)) / trials
    both_AD = sum(step("A") == "F" and step("D") == "F" for _ in range(trials)) / trials
    return {"cop A, robber E: both at F after 1 move": round(both_AE, 4), "Olsen": "1/9 = 0.1111",
            "cop A, robber D: both at F after 1 move": both_AD, "parity": "0: D-F has even length"}


# =========================================================================
# 5. The interactive board
# =========================================================================
MODES = {"robber": "You are the robber(s): the computer plays the cops",
         "cop": "You are the cop(s): the computer plays the robbers",
         "two players": "Two players: take turns on one keyboard",
         "watch": "Watch: computer against computer"}


def _layout(G: nx.Graph, width=620, height=440, pad=48):
    pos = nx.get_node_attributes(G, "pos") or nx.kamada_kawai_layout(G)
    xs, ys = zip(*pos.values())
    sx = (width - 2 * pad) / ((max(xs) - min(xs)) or 1)
    sy = (height - 2 * pad) / ((max(ys) - min(ys)) or 1)
    s = min(sx, sy)
    ox = (width - s * (max(xs) - min(xs))) / 2
    oy = (height - s * (max(ys) - min(ys))) / 2
    return {v: (round(ox + s * (x - min(xs)), 1), round(oy + s * (max(ys) - y), 1)) for v, (x, y) in pos.items()}


def board_html(name="Square (Round 1)", cops=1, robbers=1, mode="robber", ai="smart",
               n=16, seed=1, max_rounds=None, show_corners=False) -> str:
    """The game as a self-contained HTML page (string)."""
    name = find_network(name)
    G = network(name, n, seed)
    brain = Brain(G, cops, robbers, random.Random(seed))
    nodes = brain.nodes
    xy = _layout(G)
    theory = []
    if robbers == 1 and brain.table is not None:
        win = cops_always_win(G, cops)
        theory.append(f"With perfect play, {cops} cop{'s' if cops > 1 else ''} "
                      f"{'always win' if win else 'cannot always win'} on this network.")
    if cops == 1:
        theory.append("One cop always wins here: you can cross out corners until one node is left."
                      if dismantlable(G) else "No way to cross out every corner: one cop cannot always win.")
    data = {
        "name": name, "nodes": nodes, "xy": [xy[v] for v in nodes],
        "edges": [[brain.idx[a], brain.idx[b]] for a, b in G.edges()],
        "closed": brain.closed, "D": brain.D, "deg": brain.deg,
        "k_cops": cops, "k_robbers": robbers, "mode": mode, "ai": ai,
        "max_rounds": max_rounds or 2 * len(nodes),
        "corners": [brain.idx[v] for v in corners(G)], "show_corners": show_corners,
        "theory": " ".join(theory),
        "cop_start": brain.cop_start(cops, ai),
        "table": None,
    }
    if brain.table is not None:
        states, Vc, Vr = brain.table
        data["table"] = {"states": [",".join(map(str, s)) for s in states],
                         "Vc": np.where(Vc >= INF, -1, Vc).tolist(),
                         "Vr": np.where(Vr >= INF, -1, Vr).tolist()}
    return _TEMPLATE.replace("__DATA__", json.dumps(data))


def play(name="Square (Round 1)", cops=1, robbers=1, mode="robber", ai="smart",
         n=16, seed=1, max_rounds=None, show_corners=False, save=None):
    """Show the board in the notebook. Click it once, then use the keys.
    mode: 'robber', 'cop', 'two players' or 'watch'. ai: 'smart', 'greedy', 'random'.
    save='game.html' also writes a standalone page you can open in any browser."""
    from IPython.display import HTML, display
    html = board_html(name, cops, robbers, mode, ai, n, seed, max_rounds, show_corners)
    if save:
        with open(save, "w", encoding="utf-8") as f:
            f.write(html)
    import warnings
    warnings.filterwarnings("ignore", message="Consider using IPython.display.IFrame")
    srcdoc = html.replace("&", "&amp;").replace('"', "&quot;")
    display(HTML(f'<iframe srcdoc="{srcdoc}" style="width:100%;max-width:960px;height:540px;'
                 f'border:1px solid #ddd;border-radius:8px" allow="autoplay"></iframe>'))


def launcher():
    """Drop-down menus for play(): choose, then press Play."""
    import ipywidgets as w
    from IPython.display import display, clear_output
    net = w.Dropdown(options=list(NETWORKS), value="Square (Round 1)", description="Network",
                     layout=w.Layout(width="420px"))
    size = w.IntSlider(16, 8, 30, description="Size (random)", style={"description_width": "initial"})
    k_c = w.IntSlider(1, 1, 3, description="Cops")
    k_r = w.IntSlider(1, 1, 3, description="Robbers")
    mode = w.Dropdown(options=[(v, k) for k, v in MODES.items()], value="robber", description="Mode",
                      layout=w.Layout(width="420px"))
    ai = w.Dropdown(options=[("Smart (optimal when solvable)", "smart"), ("Greedy", "greedy"),
                             ("Random", "random")], value="smart", description="Computer")
    corner = w.Checkbox(False, description="Mark corners (Olsen's pitfalls)")
    seed = w.IntText(1, description="Seed", layout=w.Layout(width="160px"))
    go = w.Button(description="Play", button_style="success")
    out = w.Output()

    def run(_):
        with out:
            clear_output()
            print("Building the network and solving the game...")
            html_args = dict(name=net.value, cops=k_c.value, robbers=k_r.value, mode=mode.value,
                             ai=ai.value, n=size.value, seed=seed.value, show_corners=corner.value)
            clear_output()
            play(**html_args)
    go.on_click(run)
    display(w.VBox([net, w.HBox([k_c, k_r]), mode, ai, w.HBox([size, seed]), corner, go, out]))


_TEMPLATE = r"""<!doctype html>
<html><head><meta charset="utf-8"><title>Cops and robbers</title>
<style>
  body{font-family:Calibri,Carlito,'Segoe UI',Arial,sans-serif;margin:0;padding:10px;background:#fff;color:#111}
  #wrap{display:flex;gap:14px;flex-wrap:wrap;outline:none}
  #wrap:focus #board{box-shadow:0 0 0 3px #1E6B3A55}
  #board{border:1px solid #ddd;border-radius:8px;background:#fafafa;max-width:100%;height:auto}
  h1{font-size:19px;color:#1E6B3A;margin:0 0 6px}
  #side{width:290px;font-size:14px}
  #status{font-size:16px;font-weight:bold;margin:6px 0;min-height:44px}
  #theory{color:#555;font-size:13px;margin:6px 0}
  #log{height:160px;overflow:auto;white-space:pre-wrap;font-family:Consolas,monospace;font-size:12px;background:#f4f4f4;padding:6px;border-radius:6px}
  .keys{color:#555;font-size:13px;margin:6px 0}
  kbd{border:1px solid #bbb;border-bottom-width:2px;border-radius:4px;padding:0 5px;font-size:12px;background:#fff}
  button{font:inherit;padding:4px 10px;margin:4px 4px 0 0;border:1px solid #1E6B3A;background:#fff;color:#1E6B3A;border-radius:6px;cursor:pointer}
  .piece{transition:transform .35s ease}
  .edge{stroke:#999;stroke-width:2}
  .node{fill:#fff;stroke:#333;stroke-width:1.5;cursor:pointer}
  .node.target{stroke:#1E6B3A;stroke-width:3.5}
  .lab{font-size:13px;font-weight:bold;text-anchor:middle;pointer-events:none}
  .hint{font-size:12px;font-weight:bold;fill:#1E6B3A;text-anchor:middle;pointer-events:none}
</style></head><body>
<div id="wrap" tabindex="0">
  <svg id="board" width="620" height="440" viewBox="0 0 620 440"></svg>
  <div id="side">
    <h1 id="title"></h1>
    <div id="status"></div>
    <div class="keys"><b>Click the board first</b>, then: <kbd>W</kbd><kbd>A</kbd><kbd>S</kbd><kbd>D</kbd> or arrow keys to move along a link,
      <kbd>Space</kbd> to stay, or click a neighbouring node. <kbd>R</kbd> restarts. The green letters show where each key takes you.</div>
    <div id="theory"></div>
    <button id="restart">Restart (R)</button><button id="pause" style="display:none">Pause</button>
    <div style="margin-top:8px;font-weight:bold">Move log</div>
    <div id="log"></div>
  </div>
</div>
<script>
const G = __DATA__;
const n = G.nodes.length, NS = "http://www.w3.org/2000/svg";
const svg = document.getElementById("board"), wrap = document.getElementById("wrap");
const COP = "#1E6B3A", ROB = "#C0392B";
let S;                                   // game state
const idxOf = new Map();
if (G.table) G.table.states.forEach((k, i) => idxOf.set(k, i));
const keyOf = cops => [...cops].sort((a, b) => a - b).join(",");
const rand = arr => arr[Math.floor(Math.random() * arr.length)];
const humanTeam = () => G.mode === "robber" ? "robbers" : G.mode === "cop" ? "cops" : G.mode === "two players" ? S.turn : null;

// ---------- computer players (same rules as the Python Brain) ----------
function copMoves(cops, robbers) {
  const live = robbers.filter(r => r !== null);
  if (G.ai === "random") return cops.map(c => rand(G.closed[c]));
  if (G.ai === "smart" && G.table && live.length === 1) {
    const r = live[0]; let best = Infinity, opts = [];
    const prod = cops.reduce((acc, c) => acc.flatMap(p => G.closed[c].map(x => [...p, x])), [[]]);
    for (const m of prod) {
      let v = m.includes(r) ? 0 : G.table.Vr[idxOf.get(keyOf(m))][r];
      if (v < 0) v = 1e9;
      if (v < best) { best = v; opts = [m]; } else if (v === best) opts.push(m);
    }
    return rand(opts);
  }
  const out = [];
  for (const c of cops) {
    const target = live.reduce((a, b) => (G.D[c][b] < G.D[c][a] ? b : a));
    let cand = G.closed[c];
    if (cand.includes(target)) { out.push(target); continue; }
    const d = Math.min(...cand.map(x => G.D[x][target]));
    cand = cand.filter(x => G.D[x][target] === d);
    if (out.length) {
      const sep = x => Math.min(...out.map(y => G.D[x][y]));
      const far = Math.max(...cand.map(sep));
      cand = cand.filter(x => sep(x) === far);
    }
    out.push(rand(cand));
  }
  return out;
}
function robberMove(r, cops, taken = []) {
  let cand = G.closed[r].filter(x => !cops.includes(x));
  const spread = cand.filter(x => !taken.includes(x));
  if (spread.length) cand = spread;
  if (!cand.length) cand = [r];
  if (G.ai === "random") return rand(cand);
  if (G.ai === "smart" && G.table) {
    const s = idxOf.get(keyOf(cops)), val = x => { const v = G.table.Vc[s][x]; return v < 0 ? 1e9 : v; };
    const best = Math.max(...cand.map(val)); cand = cand.filter(x => val(x) === best);
  }
  const key = x => { const m = Math.min(...cops.map(c => G.D[c][x])); return [m > 1 ? 1 : 0, m, G.deg[x]]; };
  const cmp = (a, b) => a[0] - b[0] || a[1] - b[1] || a[2] - b[2];
  const top = cand.map(key).reduce((a, b) => (cmp(a, b) >= 0 ? a : b));
  return rand(cand.filter(x => cmp(key(x), top) === 0));
}
function robberStart(cops, taken = []) {
  let free = [...Array(n).keys()].filter(v => !cops.includes(v) && !taken.includes(v));
  if (!free.length) free = [...Array(n).keys()].filter(v => !cops.includes(v));
  if (G.ai === "random") return rand(free);
  if (G.ai === "smart" && G.table) {
    const s = idxOf.get(keyOf(cops)), val = x => { const v = G.table.Vc[s][x]; return v < 0 ? 1e9 : v; };
    const best = Math.max(...free.map(val)); free = free.filter(x => val(x) === best);
  }
  const key = v => Math.min(...cops.map(c => G.D[c][v])) * 100 + G.deg[v];
  const top = Math.max(...free.map(key));
  return rand(free.filter(v => key(v) === top));
}

// ---------- drawing ----------
function el(tag, attrs, parent) { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); (parent || svg).appendChild(e); return e; }
function draw() {
  svg.innerHTML = "";
  for (const [a, b] of G.edges) el("line", {x1: G.xy[a][0], y1: G.xy[a][1], x2: G.xy[b][0], y2: G.xy[b][1], class: "edge"});
  const hints = hintMap();
  for (let v = 0; v < n; v++) {
    const [x, y] = G.xy[v];
    const c = el("circle", {cx: x, cy: y, r: 17, class: "node" + (Object.values(hints).includes(v) ? " target" : "")});
    c.addEventListener("click", () => clickNode(v));
    if (G.show_corners && G.corners.includes(v)) el("path", {d: `M${x + 13} ${y - 22} l7 12 h-14 z`, fill: "#C9A227"});
    el("text", {x, y: y + 5, class: "lab"}).textContent = G.nodes[v];
  }
  for (const [k, v] of Object.entries(hints)) {
    if (v === undefined) continue;
    const [x, y] = G.xy[v]; el("text", {x: x, y: y - 22, class: "hint"}).textContent = k;
  }
  const count = {}, at = {};
  [...S.cops, ...S.robbers].forEach(v => { if (v !== null) count[v] = (count[v] || 0) + 1; });
  const put = (v, color, txt, active) => {
    const k = (at[v] = (at[v] || 0) + 1) - 1, m = count[v];
    const ang = 2 * Math.PI * k / m, rad = m > 1 ? 10 : 0, dx = rad * Math.cos(ang), dy = rad * Math.sin(ang);
    const g = el("g", {class: "piece", transform: `translate(${G.xy[v][0] + dx},${G.xy[v][1] + dy})`});
    el("circle", {r: active ? 13 : 11, fill: color, stroke: active ? "#000" : "#fff", "stroke-width": active ? 3 : 2}, g);
    const t = el("text", {y: 4, fill: "#fff", "font-size": 11, "font-weight": "bold", "text-anchor": "middle"}, g); t.textContent = txt;
  };
  S.cops.forEach((v, i) => v !== null && put(v, COP, "C" + (i + 1), S.turn === "cops" && S.active === i && S.phase === "play" && humanTeam() === "cops"));
  S.robbers.forEach((v, i) => v !== null && put(v, ROB, "R" + (i + 1), S.turn === "robbers" && S.active === i && S.phase === "play" && humanTeam() === "robbers"));
  document.getElementById("status").innerHTML = S.msg;
}
function hintMap() {
  if (S.phase !== "play" || humanTeam() !== S.turn) return {};
  const v = S.turn === "cops" ? S.cops[S.active] : S.robbers[S.active];
  if (v === null || v === undefined) return {};
  const out = {};
  for (const [k, dir] of Object.entries({W: [0, -1], A: [-1, 0], S: [0, 1], D: [1, 0]})) out[k] = neighbourInDir(v, dir);
  return out;
}
function neighbourInDir(v, [dx, dy]) {
  let best, bestCos = 0.35;
  for (const u of G.closed[v]) {
    if (u === v) continue;
    const ex = G.xy[u][0] - G.xy[v][0], ey = G.xy[u][1] - G.xy[v][1], len = Math.hypot(ex, ey) || 1;
    const cos = (ex * dx + ey * dy) / len;
    if (cos > bestCos) { bestCos = cos; best = u; }
  }
  return best;
}
function log(s) { const L = document.getElementById("log"); L.textContent += s + "\n"; L.scrollTop = 1e9; }
const name = v => G.nodes[v];

// ---------- game flow ----------
function reset() {
  S = {phase: "place", turn: "cops", active: 0, round: 0, cops: [], robbers: [], pending: [], msg: "", timer: null};
  document.getElementById("log").textContent = "";
  document.getElementById("title").textContent = G.name;
  document.getElementById("theory").textContent = G.theory;
  document.getElementById("pause").style.display = G.mode === "watch" ? "inline-block" : "none";
  placeNext();
}
function placeNext() {
  const copsHuman = G.mode === "cop" || G.mode === "two players";
  const robHuman = G.mode === "robber" || G.mode === "two players";
  if (S.cops.length < G.k_cops) {
    if (copsHuman) { S.msg = `Cops: click a node to place cop ${S.cops.length + 1}.`; return draw(); }
    S.cops = G.cop_start.slice(0, G.k_cops); log("Cops start at " + S.cops.map(name).join(", "));
  }
  if (S.robbers.length < G.k_robbers) {
    if (robHuman) { S.msg = `Robbers: click a node to place robber ${S.robbers.length + 1}.`; return draw(); }
    while (S.robbers.length < G.k_robbers) S.robbers.push(robberStart(S.cops, S.robbers));
    log("Robbers start at " + S.robbers.map(name).join(", "));
  }
  S.phase = "play"; S.turn = "cops"; S.round = 1; S.active = 0; nextTurn();
}
function clickNode(v) {
  wrap.focus();
  if (S.phase === "place") {
    const copsHuman = G.mode === "cop" || G.mode === "two players";
    if (S.cops.length < G.k_cops && copsHuman) { S.cops.push(v); log(`Cop ${S.cops.length} starts at ${name(v)}`); }
    else if (S.robbers.length < G.k_robbers) {
      if (S.cops.includes(v)) { S.msg = "A cop is there: pick another node."; return draw(); }
      S.robbers.push(v); log(`Robber ${S.robbers.length} starts at ${name(v)}`);
    }
    return placeNext();
  }
  if (S.phase !== "play" || humanTeam() !== S.turn) return;
  const cur = S.turn === "cops" ? S.cops[S.active] : S.robbers[S.active];
  if (G.closed[cur].includes(v)) humanMove(v);
}
function nextTurn() {
  if (S.phase !== "play") return;
  const team = S.turn === "cops" ? S.cops : S.robbers;
  while (S.active < team.length && team[S.active] === null) S.active++;
  if (S.active >= team.length) return endTeam();
  if (humanTeam() === S.turn) {
    const who = S.turn === "cops" ? `cop C${S.active + 1}` : `robber R${S.active + 1}`;
    S.msg = `Round ${S.round}: your move, ${who}.`; draw();
  } else {
    S.msg = `Round ${S.round}: the ${S.turn} are thinking…`; draw();
    S.timer = setTimeout(computerTeam, G.mode === "watch" ? 700 : 450);
  }
}
function computerTeam() {
  if (S.phase !== "play") return;
  if (S.turn === "cops") {
    const before = S.cops.slice(); S.cops = copMoves(S.cops, S.robbers);
    log(`R${S.round} cops: ` + before.map((v, i) => `${name(v)}→${name(S.cops[i])}`).join(", "));
  } else {
    const before = S.robbers.slice();
    const moved = [];
    S.robbers = S.robbers.map(r => { if (r === null) return null; const x = robberMove(r, S.cops, moved); moved.push(x); return x; });
    log(`R${S.round} robbers: ` + before.map((v, i) => (v === null ? "caught" : `${name(v)}→${name(S.robbers[i])}`)).join(", "));
  }
  S.active = 1e9; endTeam();
}
function humanMove(v) {
  if (S.turn === "cops") { log(`R${S.round} C${S.active + 1}: ${name(S.cops[S.active])}→${name(v)}`); S.cops[S.active] = v; }
  else { log(`R${S.round} R${S.active + 1}: ${name(S.robbers[S.active])}→${name(v)}`); S.robbers[S.active] = v; }
  S.active++; captures(); if (S.phase === "play") nextTurn();
}
function captures() {
  S.robbers = S.robbers.map((r, i) => { if (r !== null && S.cops.includes(r)) { log(`  R${i + 1} caught at ${name(r)}!`); return null; } return r; });
  if (S.robbers.every(r => r === null)) {
    S.phase = "over"; S.msg = `<span style="color:${COP}">Cops win in round ${S.round}.</span>`; draw(); return true;
  }
  return false;
}
function endTeam() {
  if (captures()) return;
  if (S.turn === "cops") { S.turn = "robbers"; S.active = 0; return nextTurn(); }
  if (S.round >= G.max_rounds) {
    S.phase = "over"; S.msg = `<span style="color:${ROB}">Robbers win: still free after ${G.max_rounds} rounds.</span>`; return draw();
  }
  S.round++; S.turn = "cops"; S.active = 0; nextTurn();
}
wrap.addEventListener("keydown", e => {
  const k = e.key.toLowerCase();
  if (k === "r") { clearTimeout(S.timer); return reset(); }
  if (S.phase !== "play" || humanTeam() !== S.turn) return;
  const dirs = {w: [0, -1], arrowup: [0, -1], a: [-1, 0], arrowleft: [-1, 0], s: [0, 1], arrowdown: [0, 1], d: [1, 0], arrowright: [1, 0]};
  const cur = S.turn === "cops" ? S.cops[S.active] : S.robbers[S.active];
  if (k === " " || k === "spacebar" || k === "x") { e.preventDefault(); return humanMove(cur); }
  if (dirs[k]) {
    e.preventDefault();
    const u = neighbourInDir(cur, dirs[k]);
    if (u === undefined) { S.msg = "No link in that direction: try another key, or click a neighbour."; return draw(); }
    humanMove(u);
  }
});
document.getElementById("restart").onclick = () => { clearTimeout(S.timer); reset(); wrap.focus(); };
document.getElementById("pause").onclick = e => {
  if (S.phase === "play") { S.phase = "paused"; clearTimeout(S.timer); e.target.textContent = "Resume"; }
  else if (S.phase === "paused") { S.phase = "play"; e.target.textContent = "Pause"; nextTurn(); }
};
reset(); wrap.focus();
</script></body></html>"""


# =========================================================================
# 6. On your own computer: python cops_robbers_game.py --network dodeca --cops 3
# =========================================================================
def main():
    import argparse
    import os
    import webbrowser
    ap = argparse.ArgumentParser(
        description="Cops and robbers on networks: opens the board in your web browser.")
    ap.add_argument("--network", default="Square (Round 1)",
                    help="network name or part of it, e.g. 'dodeca', 'grid 4', 'octagon'")
    ap.add_argument("--cops", type=int, default=1)
    ap.add_argument("--robbers", type=int, default=1)
    ap.add_argument("--mode", default="robber", choices=list(MODES))
    ap.add_argument("--ai", default="smart", choices=["smart", "greedy", "random"])
    ap.add_argument("--size", type=int, default=16, help="nodes, for random networks")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--corners", action="store_true", help="mark corners (Olsen's pitfalls)")
    ap.add_argument("--out", default="cops_robbers_board.html")
    ap.add_argument("--list", action="store_true", help="list the networks and exit")
    ap.add_argument("--simulate", action="store_true",
                    help="print computer-vs-computer results instead of opening a board")
    a = ap.parse_args()
    if a.list:
        print("\n".join(NETWORKS))
        return
    name = find_network(a.network)
    if a.simulate:
        print(simulate(name, cops=tuple(range(1, a.cops + 1)), robbers=a.robbers,
                       n=a.size, seed=a.seed).to_string(index=False))
        return
    print(f"Building '{name}' with {a.cops} cop(s) and {a.robbers} robber(s)...")
    html = board_html(name, a.cops, a.robbers, a.mode, a.ai, a.size, a.seed, show_corners=a.corners)
    path = os.path.abspath(a.out)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved {path}. Opening it in your browser: click the board, then W A S D.")
    webbrowser.open("file:///" + path.replace("\\", "/"))


if __name__ == "__main__":
    main()
