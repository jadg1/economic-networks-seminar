"""
kg_lab.py: a small knowledge-graphs lab for literature reviews.

Economic Networks Fundamentals (UAM, Master in Quantitative Economic Analysis)
Part 3: knowledge graphs for study and literature review.

What it does
------------
1. Finds a seed paper in OpenAlex (a free, open catalogue of research).
2. Downloads its references (one step back) and the most-cited papers that
   cite it (one step forward): snowballing, which is breadth-first search.
3. Builds a knowledge graph: typed nodes (Paper, Author, Venue, Topic) and
   typed links (cites, writtenBy, publishedIn, hasTopic), stored as triples.
4. Reads it with the measures from the seminar: in-degree (the classics),
   co-citation and bibliographic coupling (related papers), communities
   (schools of thought), betweenness (bridges), and a reading order
   (a topological sort).
5. Shows two knowledge-graph ideas from Hogan et al. (2021): pattern queries
   with variables, and a rule that adds facts nobody typed.
6. Exports everything (CSV triples, GraphML, Neo4j import files) so you can
   load it into a graph database later, on your own computer.

Runs on Google Colab as is. To run locally later: see README.md.

API notes (checked November 2026)
---------------------------------
- Base URL https://api.openalex.org. No key needed for light use.
- A free key (openalex.org, Settings > API key) gives a 10x larger daily
  budget. Set it in the environment variable OPENALEX_API_KEY, or pass
  api_key=... to OpenAlex().
- Lookups of a single work are free; list/filter calls use a small part of
  the daily budget. One run of this lab makes about 5-10 calls.
- Every response is cached in ./openalex_cache, so re-running costs nothing
  and the lab still works offline once it has run once.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import networkx as nx
import pandas as pd
import requests

API = "https://api.openalex.org"
WORK_FIELDS = ("id,doi,display_name,publication_year,cited_by_count,authorships,"
               "primary_location,topics,referenced_works")


# =========================================================================
# 1. A tiny OpenAlex client with a disk cache
# =========================================================================
class OpenAlex:
    """Minimal OpenAlex client: polite retries and a disk cache."""

    def __init__(self, api_key: str | None = None, cache_dir: str = "openalex_cache",
                 verbose: bool = True):
        self.api_key = api_key or os.environ.get("OPENALEX_API_KEY")
        self.cache = Path(cache_dir)
        self.cache.mkdir(exist_ok=True)
        self.verbose = verbose
        self.calls = 0          # live calls made (cached ones don't count)

    def get(self, path: str, params: dict | None = None) -> dict:
        params = dict(params or {})
        key = hashlib.md5(json.dumps([path, params], sort_keys=True).encode()).hexdigest()
        cached = self.cache / f"{key}.json"
        if cached.exists():
            return json.loads(cached.read_text())
        if self.api_key:
            params["api_key"] = self.api_key
        for attempt in range(5):
            r = requests.get(f"{API}{path}", params=params, timeout=30)
            if r.status_code in (429, 500, 502, 503):
                time.sleep(2 ** attempt)          # exponential backoff
                continue
            r.raise_for_status()
            data = r.json()
            self.calls += 1
            cached.write_text(json.dumps(data))
            return data
        r.raise_for_status()
        raise RuntimeError(f"OpenAlex did not answer: {path}")

    # --- the four calls the lab needs ------------------------------------
    def find_work(self, query: str, year: int | None = None) -> dict:
        """Best match for a title search: the most-cited hit."""
        params = {"search": query, "per_page": 10, "select": WORK_FIELDS,
                  "sort": "cited_by_count:desc"}
        if year:
            params["filter"] = f"publication_year:{year}"
        results = self.get("/works", params)["results"]
        if not results:
            raise ValueError(f"No work found for: {query!r}")
        return results[0]

    def work_by_doi(self, doi: str) -> dict:
        doi = doi.replace("https://doi.org/", "")
        return self.get(f"/works/doi:{doi}", {"select": WORK_FIELDS})

    def works_by_ids(self, ids: list[str], batch: int = 50) -> list[dict]:
        """Up to 50 works per call, using the OR filter openalex:W1|W2|..."""
        short = [short_id(i) for i in ids]
        out = []
        for k in range(0, len(short), batch):
            chunk = short[k:k + batch]
            data = self.get("/works", {"filter": "openalex:" + "|".join(chunk),
                                       "per_page": 100, "select": WORK_FIELDS})
            out += data["results"]
        return out

    def citing_works(self, work_id: str, n: int = 100) -> list[dict]:
        """The n most-cited papers that cite this one (one step forward)."""
        data = self.get("/works", {"filter": f"cites:{short_id(work_id)}",
                                   "sort": "cited_by_count:desc",
                                   "per_page": min(n, 100), "select": WORK_FIELDS})
        return data["results"]


def short_id(openalex_id: str) -> str:
    """'https://openalex.org/W123' -> 'W123'."""
    return openalex_id.rstrip("/").split("/")[-1]


# =========================================================================
# 2. Snowballing: one step back, one step forward
# =========================================================================
def snowball(client: OpenAlex, seed: dict, n_citing: int = 100) -> dict:
    """Seed + its references + its most-cited citers. Returns {id: work}."""
    works = {short_id(seed["id"]): seed}
    refs = client.works_by_ids(seed.get("referenced_works") or [])
    citers = client.citing_works(seed["id"], n=n_citing)
    for w in refs + citers:
        works[short_id(w["id"])] = w
    if client.verbose:
        print(f"Seed: {label(seed)}")
        print(f"  {len(refs)} references (one step back), "
              f"{len(citers)} citing papers (one step forward); "
              f"{client.calls} live API calls")
    return {"seed": short_id(seed["id"]), "works": works,
            "refs": [short_id(w["id"]) for w in refs],
            "citers": [short_id(w["id"]) for w in citers]}


def _surname(authorship: dict) -> str:
    name = ((authorship or {}).get("author") or {}).get("display_name") or "?"
    return name.split()[-1]


def label(w: dict, width: int = 60) -> str:
    """'Allen & Gale (2000) Financial Contagion'."""
    authors = w.get("authorships") or []
    surname = _surname(authors[0]) if authors else "?"
    etal = (" et al." if len(authors) > 2 else
            f" & {_surname(authors[1])}" if len(authors) == 2 else "")
    title = (w.get("display_name") or "").strip()
    title = title if len(title) <= width else title[:width - 1] + "…"
    return f"{surname}{etal} ({w.get('publication_year', '?')}) {title}"


# =========================================================================
# 3. The knowledge graph: typed nodes, typed links, stored as triples
# =========================================================================
def build_kg(corpus: dict) -> nx.MultiDiGraph:
    """Nodes: Paper, Author, Venue, Topic. Links: cites, writtenBy,
    publishedIn, hasTopic. Only citations between papers in the corpus
    are kept as 'cites' links."""
    G = nx.MultiDiGraph()
    works = corpus["works"]
    for wid, w in works.items():
        G.add_node(wid, kind="Paper", name=label(w), year=w.get("publication_year"),
                   cited_by=w.get("cited_by_count", 0),
                   role=("seed" if wid == corpus["seed"] else
                         "reference" if wid in corpus["refs"] else "citing"))
        for a in w.get("authorships") or []:
            au = a.get("author") or {}
            if au.get("id"):
                aid = short_id(au["id"])
                G.add_node(aid, kind="Author", name=au.get("display_name", aid))
                G.add_edge(wid, aid, key="writtenBy", rel="writtenBy")
        src = ((w.get("primary_location") or {}).get("source") or {})
        if src.get("id"):
            vid = short_id(src["id"])
            G.add_node(vid, kind="Venue", name=src.get("display_name", vid))
            G.add_edge(wid, vid, key="publishedIn", rel="publishedIn")
        for t in (w.get("topics") or [])[:1]:          # the main topic only
            if t.get("id"):
                tid = short_id(t["id"])
                G.add_node(tid, kind="Topic", name=t.get("display_name", tid),
                           field=((t.get("field") or {}).get("display_name")))
                G.add_edge(wid, tid, key="hasTopic", rel="hasTopic")
        for ref in w.get("referenced_works") or []:
            rid = short_id(ref)
            if rid in works:
                G.add_edge(wid, rid, key="cites", rel="cites")
    return G


def triples(G: nx.MultiDiGraph) -> pd.DataFrame:
    """The graph as (subject, relation, object) rows, with readable names."""
    rows = [(G.nodes[s].get("name", s), d["rel"], G.nodes[o].get("name", o), s, o)
            for s, o, d in G.edges(data=True)]
    return pd.DataFrame(rows, columns=["subject", "relation", "object", "s_id", "o_id"])


def summary(G: nx.MultiDiGraph) -> pd.DataFrame:
    nodes = Counter(d["kind"] for _, d in G.nodes(data=True))
    links = Counter(d["rel"] for _, _, d in G.edges(data=True))
    return pd.DataFrame({"count": {**{f"node: {k}": v for k, v in nodes.items()},
                                   **{f"link: {k}": v for k, v in links.items()}}})


# =========================================================================
# 4. Querying: graph patterns with variables (Hogan et al., section 2.2)
# =========================================================================
def match(G: nx.MultiDiGraph, s=None, p=None, o=None) -> list[tuple]:
    """All triples matching a pattern; None is a variable (?x).
    match(G, p="writtenBy", o="A123") -> every paper written by author A123."""
    return [(a, d["rel"], b) for a, b, d in G.edges(data=True)
            if (s is None or a == s) and (p is None or d["rel"] == p)
            and (o is None or b == o)]


def path_query(G: nx.MultiDiGraph, start: str, relations: list[str]) -> set:
    """Regular path query start -rel1-> ? -rel2-> ? ...
    path_query(G, seed, ['cites', 'cites']) = references of references."""
    frontier = {start}
    for rel in relations:
        frontier = {b for a in frontier for _, b, d in G.out_edges(a, data=True)
                    if d["rel"] == rel}
    return frontier


# =========================================================================
# 5. Reasoning: a rule adds facts nobody typed (Hogan et al., section 3.3)
# =========================================================================
def apply_coauthor_rule(G: nx.MultiDiGraph) -> int:
    """(?p writtenBy ?x) and (?p writtenBy ?y) => (?x coauthorOf ?y).
    Adds the new links to G (materialisation). Returns how many were added."""
    added = 0
    for p in [n for n, d in G.nodes(data=True) if d["kind"] == "Paper"]:
        authors = sorted({b for _, b, d in G.out_edges(p, data=True) if d["rel"] == "writtenBy"})
        for x, y in combinations(authors, 2):
            for a, b in ((x, y), (y, x)):
                if not G.has_edge(a, b, key="coauthorOf"):
                    G.add_edge(a, b, key="coauthorOf", rel="coauthorOf")
                    added += 1
    return added


# =========================================================================
# 6. Reading the literature with the seminar's measures
# =========================================================================
def paper_graph(G: nx.MultiDiGraph) -> nx.DiGraph:
    """Only papers and 'cites' links: the citation network."""
    P = nx.DiGraph()
    P.add_nodes_from((n, d) for n, d in G.nodes(data=True) if d["kind"] == "Paper")
    P.add_edges_from((a, b) for a, b, d in G.edges(data=True) if d["rel"] == "cites")
    return P


def classics(corpus: dict, top: int = 10) -> pd.DataFrame:
    """In-degree inside our corpus: how many of the seed's citers also cite
    each reference. Plus the global citation count from OpenAlex."""
    works, citers = corpus["works"], corpus["citers"]
    cited_in_corpus = Counter(short_id(r) for c in citers
                              for r in works[c].get("referenced_works") or [])
    rows = [(label(works[r]), cited_in_corpus[r], works[r].get("cited_by_count", 0))
            for r in corpus["refs"]]
    df = pd.DataFrame(rows, columns=["paper", "cited by the seed's citers", "cited by (all of OpenAlex)"])
    return df.sort_values(["cited by the seed's citers", "cited by (all of OpenAlex)"],
                          ascending=False).head(top).reset_index(drop=True)


def co_citation(corpus: dict, client: OpenAlex | None = None, top: int = 10) -> pd.DataFrame:
    """Small (1973): two papers cited together by many papers are related.
    Counts, across the seed's citers, which pairs of works they cite together.
    Papers outside the corpus are looked up by name (one extra API call)."""
    pairs = Counter()
    for c in corpus["citers"]:
        # every citer cites the seed, so leave the seed out of the pairs
        refs = sorted({short_id(r) for r in corpus["works"][c].get("referenced_works") or []}
                      - {corpus["seed"]})
        pairs.update(combinations(refs, 2))
    best = pairs.most_common(top)
    known = {**corpus["works"], **corpus.setdefault("extra", {})}
    missing = sorted({x for (a, b), _ in best for x in (a, b)} - set(known))
    if missing and client is not None:
        for w in client.works_by_ids(missing):
            corpus["extra"][short_id(w["id"])] = known[short_id(w["id"])] = w
    name = lambda x: label(known[x]) if x in known else x
    return pd.DataFrame([(name(a), name(b), n) for (a, b), n in best],
                        columns=["paper A", "paper B", "cited together by"])


def coupling_graph(corpus: dict, min_shared: int = 2) -> nx.Graph:
    """Kessler (1963): two citing papers that share references are related.
    Link weight = number of shared references."""
    works = corpus["works"]
    refs = {c: {short_id(r) for r in works[c].get("referenced_works") or []}
            for c in corpus["citers"]}
    C = nx.Graph()
    for c in corpus["citers"]:
        C.add_node(c, name=label(works[c]), year=works[c].get("publication_year"))
    for a, b in combinations(corpus["citers"], 2):
        shared = len(refs[a] & refs[b])
        if shared >= min_shared:
            C.add_edge(a, b, weight=shared)
    return C


def schools_of_thought(G: nx.MultiDiGraph, corpus: dict, min_shared: int = 2) -> pd.DataFrame:
    """Communities in the coupling graph, each labelled by its commonest topic."""
    C = coupling_graph(corpus, min_shared)
    C.remove_nodes_from([n for n in list(C) if C.degree(n) == 0])
    if C.number_of_edges() == 0:
        return pd.DataFrame(columns=["group", "papers", "main topic", "most-cited paper"])
    groups = nx.community.greedy_modularity_communities(C, weight="weight")
    rows = []
    for k, g in enumerate(groups, 1):
        topics = Counter(G.nodes[t]["name"] for p in g for _, t, d in G.out_edges(p, data=True)
                         if d["rel"] == "hasTopic")
        main = topics.most_common(1)[0][0] if topics else "?"
        example = max(g, key=lambda p: G.nodes[p].get("cited_by", 0))
        rows.append((k, len(g), main, G.nodes[example]["name"]))
    return pd.DataFrame(rows, columns=["group", "papers", "main topic", "most-cited paper"])


def bridges(G: nx.MultiDiGraph, top: int = 5) -> pd.DataFrame:
    """Betweenness on the citation network (ignoring direction): papers that
    connect parts of the literature that otherwise don't talk. The seed is
    left out of the ranking: it sits in the middle by construction."""
    P = paper_graph(G).to_undirected()
    b = nx.betweenness_centrality(P)
    seed = [n for n in P if P.nodes[n].get("role") == "seed"]
    best = sorted((n for n in b if n not in seed), key=b.get, reverse=True)[:top]
    return pd.DataFrame([(G.nodes[p]["name"], round(b[p], 3)) for p in best],
                        columns=["paper", "betweenness"])


def reading_order(G: nx.MultiDiGraph, top: int = 15) -> list[str]:
    """A study order: oldest foundations first, each paper after the papers
    it cites (a topological sort of the citation network among the
    `top` most-cited papers). Citation networks have almost no cycles; any
    that exist are broken by dropping the newer-to-newer link."""
    P = paper_graph(G)
    keep = sorted(P, key=lambda n: P.nodes[n].get("cited_by", 0), reverse=True)[:top]
    S = P.subgraph(keep).copy()
    while not nx.is_directed_acyclic_graph(S):
        cycle = nx.find_cycle(S)
        S.remove_edge(*cycle[0][:2])
    # 'cites' points from new to old, so read the reversed order: old first
    order = list(nx.lexicographical_topological_sort(
        S.reverse(), key=lambda n: (S.nodes[n].get("year") or 0)))
    return [S.nodes[n]["name"] for n in order]


# =========================================================================
# 7. Pictures
# =========================================================================
def draw(G: nx.MultiDiGraph, top: int = 40, path: str | None = "kg_citations.png"):
    """The citation network of the `top` most-cited papers; the seed in green,
    references grey, citing papers black."""
    import matplotlib.pyplot as plt
    P = paper_graph(G)
    keep = sorted(P, key=lambda n: P.nodes[n].get("cited_by", 0), reverse=True)[:top]
    seed = [n for n in P if P.nodes[n]["role"] == "seed"]
    S = P.subgraph(set(keep) | set(seed))
    pos = nx.spring_layout(S, seed=1, k=0.6)
    colour = {"seed": "#1E6B3A", "reference": "#8C8C8C", "citing": "#000000"}
    fig, ax = plt.subplots(figsize=(11, 7))
    nx.draw_networkx_edges(S, pos, ax=ax, alpha=0.25, arrowsize=6, width=0.6)
    sizes = [60 + 6 * (S.nodes[n].get("cited_by", 0) ** 0.5) for n in S]
    nx.draw_networkx_nodes(S, pos, ax=ax, node_size=sizes,
                           node_color=[colour[S.nodes[n]["role"]] for n in S])
    labels = {n: S.nodes[n]["name"].split(")")[0] + ")" for n in
              sorted(S, key=lambda n: S.nodes[n].get("cited_by", 0), reverse=True)[:12]}
    label_pos = {n: (x, y + 0.06) for n, (x, y) in pos.items()}
    nx.draw_networkx_labels(S, label_pos, labels, ax=ax, font_size=7,
                            bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=0.4))
    ax.set_title("Citation network around the seed (size = citations; green = seed, "
                 "grey = its references, black = papers citing it)", fontsize=10)
    ax.axis("off")
    if path:
        fig.savefig(path, dpi=160, bbox_inches="tight")
    return fig


def interactive(G: nx.MultiDiGraph, path: str = "kg_interactive.html", top: int = 60):
    """An interactive HTML view with every node type (needs: pip install pyvis)."""
    from pyvis.network import Network
    papers = sorted((n for n, d in G.nodes(data=True) if d["kind"] == "Paper"),
                    key=lambda n: G.nodes[n].get("cited_by", 0), reverse=True)[:top]
    keep = set(papers) | {b for p in papers for _, b in G.out_edges(p)}
    net = Network(height="700px", width="100%", directed=True, notebook=False,
                  cdn_resources="in_line")
    colour = {"Paper": "#1E6B3A", "Author": "#595959", "Venue": "#8C8C8C", "Topic": "#C9A227"}
    for n in keep:
        d = G.nodes[n]
        net.add_node(n, label=d["name"][:40], title=d["name"], color=colour[d["kind"]],
                     shape="dot" if d["kind"] == "Paper" else "box")
    for a, b, d in G.edges(data=True):
        if a in keep and b in keep and d["rel"] != "coauthorOf":
            net.add_edge(a, b, label=d["rel"], font={"size": 8})
    net.write_html(path)
    return path


# =========================================================================
# 8. Export: take it to a graph database later
# =========================================================================
def export(G: nx.MultiDiGraph, folder: str = "kg_export") -> Path:
    """Writes: triples.csv, graph.graphml, and Neo4j import files
    (nodes.csv, relationships.csv, load.cypher)."""
    out = Path(folder)
    out.mkdir(exist_ok=True)
    triples(G).to_csv(out / "triples.csv", index=False)
    H = nx.MultiDiGraph()
    for n, d in G.nodes(data=True):
        H.add_node(n, **{k: ("" if v is None else v) for k, v in d.items()})
    for a, b, d in G.edges(data=True):
        H.add_edge(a, b, rel=d["rel"])
    nx.write_graphml(H, out / "graph.graphml")
    pd.DataFrame([{"id": n, "kind": d["kind"], "name": d.get("name", ""),
                   "year": d.get("year") or "", "cited_by": d.get("cited_by", "")}
                  for n, d in G.nodes(data=True)]).to_csv(out / "nodes.csv", index=False)
    pd.DataFrame([{"source": a, "target": b, "type": d["rel"]}
                  for a, b, d in G.edges(data=True)]).to_csv(out / "relationships.csv", index=False)
    (out / "load.cypher").write_text(
        "// Neo4j: put nodes.csv and relationships.csv in the import folder, then run:\n"
        "LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row\n"
        "CALL apoc.create.node([row.kind], {id: row.id, name: row.name,\n"
        "  year: row.year, cited_by: row.cited_by}) YIELD node RETURN count(node);\n\n"
        "CREATE INDEX node_id IF NOT EXISTS FOR (n:Paper) ON (n.id);\n\n"
        "LOAD CSV WITH HEADERS FROM 'file:///relationships.csv' AS row\n"
        "MATCH (a {id: row.source}), (b {id: row.target})\n"
        "CALL apoc.create.relationship(a, row.type, {}, b) YIELD rel RETURN count(rel);\n\n"
        "// Example query: papers two citation steps back from the seed\n"
        "// MATCH (s:Paper {id: 'W...'})-[:cites*2]->(p:Paper) RETURN DISTINCT p.name;\n")
    return out


# =========================================================================
# Command line: python kg_lab.py --query "Financial contagion" --year 2000
# =========================================================================
if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Knowledge-graph literature lab (OpenAlex)")
    ap.add_argument("--doi")
    ap.add_argument("--query", default="Financial contagion")
    ap.add_argument("--year", type=int, default=2000)
    ap.add_argument("--citing", type=int, default=100)
    args = ap.parse_args()
    oa = OpenAlex()
    seed = oa.work_by_doi(args.doi) if args.doi else oa.find_work(args.query, args.year)
    corpus = snowball(oa, seed, n_citing=args.citing)
    G = build_kg(corpus)
    print(summary(G).to_string())
    print("\nThe classics:\n", classics(corpus).to_string())
    print("\nCo-cited pairs:\n", co_citation(corpus, oa).to_string())
    print("\nSchools of thought:\n", schools_of_thought(G, corpus).to_string())
    print("\nBridges:\n", bridges(G).to_string())
    print("\nReading order:\n  " + "\n  ".join(reading_order(G)))
    print(f"\nCoauthor links added by the rule: {apply_coauthor_rule(G)}")
    draw(G)
    print(f"Exported to {export(G)}/  ({oa.calls} live API calls)")
