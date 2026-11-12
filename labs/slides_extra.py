"""
Extra pictures for the slides: the dean network with costs, the Krackhardt kite,
Königsberg as a graph, random versus scale-free degrees, and the textbook SIR curves.
Needs: pip install networkx matplotlib numpy scipy
"""
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from scipy.integrate import odeint

INK, MUTED, LINE, BLUE, CORAL, GREEN, AMBER = "#1B1F3B", "#8A8FA8", "#C9CCD8", "#2D6CF6", "#F2464F", "#12A873", "#E89400"
plt.rcParams.update({"font.size": 11, "text.parse_math": False})


def box(ax, x, y, text, fc, tc="white", fs=11):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, fontweight="bold", color=tc, zorder=4,
            bbox=dict(boxstyle="round,pad=0.45", fc=fc, ec="none"))


# 1. The dean network with costs, cheapest route highlighted
def dean_costs(path):
    links = {("You", "Classmate"): 1, ("You", "Professor"): 2, ("Classmate", "Professor"): 2,
             ("Professor", "Head of dept"): 1, ("Professor", "Secretary"): 3, ("Head of dept", "Secretary"): 1,
             ("Head of dept", "Vice-dean"): 2, ("Vice-dean", "Dean"): 2, ("Secretary", "Dean"): 1,
             ("You", "Secretary"): 5}
    pos = {"You": (0, 2), "Classmate": (0, 0.4), "Professor": (2, 2), "Head of dept": (4, 1.2),
           "Secretary": (6, 3), "Vice-dean": (6, -0.2), "Dean": (8, 1.6)}
    best = [("You", "Professor"), ("Professor", "Head of dept"), ("Head of dept", "Secretary"), ("Secretary", "Dean")]
    best = {frozenset(e) for e in best}
    fig, ax = plt.subplots(figsize=(10, 4.8))
    for (a, b), c in links.items():
        (xa, ya), (xb, yb) = pos[a], pos[b]
        on = frozenset((a, b)) in best
        cold = {a, b} == {"You", "Secretary"}
        ax.plot([xa, xb], [ya, yb], color=BLUE if on else (CORAL if cold else LINE), lw=5 if on else 2.2,
                ls="--" if cold else "-", zorder=1, solid_capstyle="round")
        ax.text((xa + xb) / 2, (ya + yb) / 2, str(c), ha="center", va="center", fontsize=12, color=INK,
                bbox=dict(boxstyle="circle,pad=0.25", fc="white", ec=LINE), zorder=3)
    for n, (x, y) in pos.items():
        box(ax, x, y, n, INK if n in ("You", "Dean") else MUTED)
    ax.set_title("Cheapest route (blue) costs 5; the cold email to the secretary (coral) costs 6",
                 loc="left", fontsize=12)
    ax.text(-0.4, -1.0, "Numbers: how awkward each ask is (1 = easy chat, 5 = cold email).", fontsize=10, color=MUTED)
    ax.set_xlim(-0.8, 8.8)
    ax.set_ylim(-1.2, 3.6)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=180)


# 2. The Krackhardt kite: same network, four winners
def kite(path):
    G = nx.krackhardt_kite_graph()
    G = nx.relabel_nodes(G, dict(enumerate("ABCDEFGHIJ")))
    deg, bet, clo = nx.degree_centrality(G), nx.betweenness_centrality(G), nx.closeness_centrality(G)
    top = lambda d: {k for k, v in d.items() if abs(v - max(d.values())) < 1e-9}
    D, H, FG = top(deg), top(bet), top(clo)
    pos = {"A": (1, 3), "B": (3, 3), "C": (0, 2), "D": (2, 2), "E": (4, 2), "F": (1, 1), "G": (3, 1),
           "H": (2, 0), "I": (2, -1), "J": (2, -2)}
    fig, ax = plt.subplots(figsize=(6.4, 6.4))
    for a, b in G.edges():
        ax.plot(*zip(pos[a], pos[b]), color=LINE, lw=2.2, zorder=1)
    for n, (x, y) in pos.items():
        col = BLUE if n in D else CORAL if n in H else GREEN if n in FG else MUTED
        ax.scatter(x, y, s=900, color=col, zorder=3, edgecolors="white", linewidths=2)
        ax.text(x, y, n, ha="center", va="center", color="white", fontsize=13, fontweight="bold", zorder=4)
    ax.text(4.6, 0.2, "Most links (degree)", color=BLUE, fontsize=11, fontweight="bold")
    ax.text(4.6, -0.3, "Only bridge (betweenness)", color=CORAL, fontsize=11, fontweight="bold")
    ax.text(4.6, -0.8, "Reach everyone fastest\n(closeness)", color=GREEN, fontsize=11, fontweight="bold", va="top")
    ax.set_title("The Krackhardt kite: same network, different winners", loc="left", fontsize=12)
    ax.set_xlim(-0.6, 7.6)
    ax.set_ylim(-2.6, 3.6)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    return sorted(D), sorted(H), sorted(FG)


# 3. Königsberg as a graph: four land masses, seven bridges
def konigsberg(path):
    pos = {"North bank": (2, 3), "Island": (2, 1.5), "East island": (4.2, 1.5), "South bank": (2, 0)}
    bridges = [("North bank", "Island", 0.25), ("North bank", "Island", -0.25), ("South bank", "Island", 0.25),
               ("South bank", "Island", -0.25), ("North bank", "East island", 0.0), ("South bank", "East island", 0.0),
               ("Island", "East island", 0.0)]
    fig, ax = plt.subplots(figsize=(7, 5))
    for a, b, rad in bridges:
        ax.add_patch(FancyArrowPatch(pos[a], pos[b], connectionstyle=f"arc3,rad={rad}", arrowstyle="-",
                                     color=INK, lw=2.4, shrinkA=18, shrinkB=18, zorder=1))
    deg = {"North bank": 3, "Island": 5, "East island": 3, "South bank": 3}
    for n, (x, y) in pos.items():
        box(ax, x, y, f"{n}\n{deg[n]} bridges", CORAL, fs=10)
    ax.set_title("Königsberg: every land mass has an odd number of bridges,\nso no walk crosses each bridge exactly once",
                 loc="left", fontsize=12)
    ax.set_xlim(0.6, 5.4)
    ax.set_ylim(-0.6, 3.6)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=180)


# 4. Random versus scale-free degree distributions
def hubs(path, n=2000, seed=1):
    er = nx.gnm_random_graph(n, 3 * n, seed=seed)
    ba = nx.barabasi_albert_graph(n, 3, seed=seed)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, G, name, col in [(axes[0], er, "Random (Erdős–Rényi)", MUTED), (axes[1], ba, "Scale-free (Barabási–Albert)", BLUE)]:
        k = np.array([d for _, d in G.degree()])
        vals, counts = np.unique(k, return_counts=True)
        ax.bar(vals, counts / n, color=col, width=0.85)
        ax.set_title(f"{name}: largest hub has {k.max()} links", loc="left", fontsize=11)
        ax.set_xlabel("number of links")
        ax.set_ylabel("share of nodes")
        ax.set_xlim(0, 60)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(f"Same number of nodes ({n}) and links: a bell curve against a long tail", x=0.01, ha="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    return int(max(d for _, d in er.degree())), int(max(d for _, d in ba.degree()))


# 5. The textbook (deterministic) SIR model
def sir(path, beta=0.3, gamma=0.1):
    t = np.linspace(0, 120, 600)
    f = lambda y, t: [-beta * y[0] * y[1], beta * y[0] * y[1] - gamma * y[1], gamma * y[1]]
    S, I, R = odeint(f, [0.999, 0.001, 0], t).T
    fig, ax = plt.subplots(figsize=(8, 4))
    for y, name, col in [(S, "Susceptible", BLUE), (I, "Infected", CORAL), (R, "Recovered", GREEN)]:
        ax.plot(t, y, lw=2.6, color=col)
        if name == "Infected":
            k = int(np.argmax(y))
            ax.text(t[k] + 4, y[k] + 0.03, name, color=col, va="bottom", fontsize=11, fontweight="bold")
        else:
            ax.text(t[-1] + 1, y[-1], name, color=col, va="center", fontsize=11, fontweight="bold")
    ax.set_xlim(0, 140)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("time")
    ax.set_ylabel("share of the population")
    ax.set_title(f"The textbook SIR model: β = {beta}, γ = {gamma}, so R0 = {beta / gamma:.0f}: each case infects about 3 others at the start",
                 loc="left", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    return round(float(R[-1]), 2)


# 6. Four centrality measures, each explained on the Krackhardt kite
KITE_POS = {"A": (1, 3), "B": (3, 3), "C": (0, 2), "D": (2, 2), "E": (4, 2), "F": (1, 1), "G": (3, 1),
            "H": (2, 0), "I": (2, -1), "J": (2, -2)}


def _kite():
    return nx.relabel_nodes(nx.krackhardt_kite_graph(), dict(enumerate("ABCDEFGHIJ")))


def _draw_kite(ax, G, colors, labels=None, edge_colors=None, widths=None, sizes=None):
    for a, b in G.edges():
        key = frozenset((a, b))
        ax.plot(*zip(KITE_POS[a], KITE_POS[b]), color=(edge_colors or {}).get(key, LINE),
                lw=(widths or {}).get(key, 2.2), zorder=1)
    for n, (x, y) in KITE_POS.items():
        ax.scatter(x, y, s=(sizes or {}).get(n, 900), color=colors.get(n, MUTED), zorder=3,
                   edgecolors="white", linewidths=2)
        ax.text(x, y, n, ha="center", va="center", color="white", fontsize=13, fontweight="bold", zorder=4)
        if labels and n in labels:
            ax.text(x + 0.3, y + 0.3, labels[n], fontsize=11, color=INK, fontweight="bold", zorder=5,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    ax.set_xlim(-0.6, 4.8)
    ax.set_ylim(-2.6, 3.7)
    ax.set_aspect("equal")
    ax.axis("off")


def centrality_figures(prefix="slides_centrality"):
    G = _kite()
    # Degree: count the links
    fig, ax = plt.subplots(figsize=(6, 6.2))
    deg = dict(G.degree())
    edge_col = {frozenset(e): BLUE for e in G.edges("D")}
    _draw_kite(ax, G, {"D": BLUE}, labels={n: str(k) for n, k in deg.items()}, edge_colors=edge_col,
               widths={k: 4 for k in edge_col})
    ax.set_title("Degree: count the links.\nD has 6, more than anyone", loc="left", fontsize=12)
    fig.tight_layout(); fig.savefig(f"{prefix}_degree.png", dpi=180); plt.close(fig)

    # Betweenness: shortest paths that pass through you
    fig, ax = plt.subplots(figsize=(6, 6.2))
    bet = nx.betweenness_centrality(G, normalized=False)
    route = nx.shortest_path(G, "J", "A")
    ec = {frozenset(e): CORAL for e in zip(route, route[1:])}
    _draw_kite(ax, G, {"H": CORAL}, labels={n: f"{v:.0f}" for n, v in bet.items() if v >= 3},
               edge_colors=ec, widths={k: 4 for k in ec})
    ax.set_title("Betweenness: how many shortest routes pass through you.\n"
                 "Every route from I or J to the rest goes through H", loc="left", fontsize=12)
    fig.tight_layout(); fig.savefig(f"{prefix}_betweenness.png", dpi=180); plt.close(fig)

    # Closeness: few steps to everyone
    fig, ax = plt.subplots(figsize=(6, 6.2))
    d = nx.single_source_shortest_path_length(G, "F")
    shade = {0: GREEN, 1: "#5CC79C", 2: "#A6E3C8", 3: "#D9F2E6"}
    cols = {n: shade.get(k, LINE) for n, k in d.items()}
    _draw_kite(ax, G, cols, labels={n: str(k) for n, k in d.items() if n != "F"})
    ax.set_title(f"Closeness: few steps to everyone.\nFrom F, steps to all others add up to {sum(d.values())} (G ties)", loc="left", fontsize=12)
    fig.tight_layout(); fig.savefig(f"{prefix}_closeness.png", dpi=180); plt.close(fig)

    # Eigenvector: linked to the well-linked
    fig, ax = plt.subplots(figsize=(6, 6.2))
    eig = nx.eigenvector_centrality_numpy(G)
    top = max(eig.values())
    sizes = {n: 250 + 1500 * v / top for n, v in eig.items()}
    _draw_kite(ax, G, {n: BLUE if v == top else MUTED for n, v in eig.items()},
               labels={n: f"{v / top:.2f}" for n, v in eig.items()}, sizes=sizes)
    ax.set_title("Eigenvector: you score high if your neighbours score high.\n"
                 "Bigger circle = higher score (the best is set to 1)", loc="left", fontsize=12)
    fig.tight_layout(); fig.savefig(f"{prefix}_eigenvector.png", dpi=180); plt.close(fig)
    return deg, {k: round(v, 1) for k, v in bet.items()}, d, {k: round(v / top, 2) for k, v in eig.items()}


if __name__ == "__main__":
    dean_costs("slides_dean_costs.png")
    print("kite winners (degree, betweenness, closeness):", kite("slides_kite.png"))
    konigsberg("slides_konigsberg.png")
    print("largest hub (random, scale-free):", hubs("slides_hubs.png"))
    print("SIR final share ever infected:", sir("slides_sir.png"))
    print("centrality (degree, betweenness, distances from F, eigenvector):", centrality_figures())
