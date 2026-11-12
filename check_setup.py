"""Quick check that the environment works: python check_setup.py"""
import importlib
import sys

ok = True
print(f"Python {sys.version.split()[0]}")
for pkg in ["numpy", "scipy", "pandas", "networkx", "matplotlib", "requests",
            "ipywidgets", "nbformat", "pyreadr", "pyvis"]:
    try:
        m = importlib.import_module(pkg)
        print(f"  ok  {pkg} {getattr(m, '__version__', '')}")
    except ImportError:
        optional = pkg in ("pyvis", "ipywidgets")
        print(f"  {'--' if optional else 'XX'}  {pkg} missing{' (optional)' if optional else ''}")
        ok = ok and optional

sys.path.insert(0, "labs")
import matplotlib
matplotlib.use("Agg")
import cops_robbers_game as g

for name, expected in [("Square (Round 1)", 2), ("Square + diagonal", 1), ("dodecahedron", 3)]:
    got = g.cop_number(g.network(name))
    print(f"  {'ok' if got == expected else 'XX'}  cop number of {g.find_network(name)}: {got}")
    ok = ok and got == expected

print("\nAll good." if ok else "\nSomething is missing: see the XX lines above.")
sys.exit(0 if ok else 1)
