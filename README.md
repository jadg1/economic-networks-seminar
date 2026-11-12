# Economic Networks Fundamentals: Nodes, Influence, and Applications in Machine Learning

Seminar materials for the **Master in Quantitative Economic Analysis**, Universidad Autónoma de Madrid.
Delivered by **Javier De Golferichs**, Friday 13 November 2026.

Everything starts from a game or a story; the maths comes after.

| Document | What's in it |
| --- | --- |
| [SETUP.md](SETUP.md) | Copy-and-paste setup for Windows, macOS and Linux; the libraries; how to get updates and propose changes |
| [BIBLIOGRAPHY.md](BIBLIOGRAPHY.md) | Recommended readings, by part of the seminar |
| [MAINTAINING.md](MAINTAINING.md) | For the maintainer: first push, updates, reviewing pull requests |
| [slides/seminar_deck.pdf](slides/seminar_deck.pdf) | The slides. The green "Lab in Colab" buttons open the matching notebook. |

The seminar has three parts:

| Part | Topic | Labs |
| --- | --- | --- |
| 1 · Nodes | Network structure and representation: cops and robbers, notation, Euler, reaching the dean (shortest paths, value of information), centrality | `cops_robbers_game`, `cops_and_robbers`, `dean_reach`, `dean_timing` |
| 2 · Influence | Diffusion and contagion: hubs and gravity, SIR on networks, dynamic networks, spectral graphs, the 2008 and 2023 crises, the bank game | `market_speed`, `crisis_networks`, `trust_network`, `clue_bank_game` |
| 3 · Applications | Machine learning on networks, knowledge graphs for literature reviews, industry and the TFM | `school_gossip`, `kg_lab` |

## Two ways to run the labs

**Option A: Google Colab, nothing to install (recommended for class).** Click a badge below. Colab opens the notebook straight from GitHub; run the first code cell (*Setup for Google Colab*), which copies this repository into your Colab session and installs the two extra packages, then run the rest. You need a Google account, and the repository must be public.

To browse every notebook from Colab instead: in Colab choose *File → Open notebook → GitHub*, type `jadg1/economic-networks-seminar`, and pick one.

Your changes live in your Colab session only. To keep them, use *File → Save a copy in Drive*.

**Option B: your own computer.** Copy-and-paste instructions for Windows, macOS and Linux are in [SETUP.md](SETUP.md); the short version is below.

### Open in Colab

| Lab | What it does | Open |
| --- | --- | --- |
| Cops and robbers: the game | Play on 18 networks with W A S D; exact solver; simulations; Olsen (2023)'s examples | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jadg1/economic-networks-seminar/blob/main/labs/cops_and_robbers_game.ipynb) |
| Cops and robbers: the solver | Who wins, cop number, the corner test | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jadg1/economic-networks-seminar/blob/main/labs/cops_and_robbers.ipynb) |
| Reaching the dean | Reliable routes, word of mouth (independent cascade) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jadg1/economic-networks-seminar/blob/main/labs/dean_reach.ipynb) |
| Reaching the dean over time | Keep asking (Markov chain), weekly timetables (temporal network) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jadg1/economic-networks-seminar/blob/main/labs/dean_timing.ipynb) |
| Market speed | How fast news of a fire sale spreads; the Fiedler value | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jadg1/economic-networks-seminar/blob/main/labs/market_speed.ipynb) |
| Crisis networks | The actors of 2008 and of Credit Suisse 2023 | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jadg1/economic-networks-seminar/blob/main/labs/crisis_networks.ipynb) |
| Trust network | What each bank can see; distrust splits the market | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jadg1/economic-networks-seminar/blob/main/labs/trust_network.ipynb) |
| The bank game | Game engine, live resolver, policies, changing the network, spectral view | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jadg1/economic-networks-seminar/blob/main/labs/clue_bank_game.ipynb) |
| School gossip | Which centrality predicts the best spreader (Glasgow school data) | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jadg1/economic-networks-seminar/blob/main/labs/school_gossip.ipynb) |
| Knowledge graphs | A literature review as a knowledge graph, from the OpenAlex API | [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jadg1/economic-networks-seminar/blob/main/labs/kg_lab.ipynb) |

## Run them on your own computer

With [Anaconda or Miniconda](https://www.anaconda.com/download):

```bash
git clone https://github.com/jadg1/economic-networks-seminar.git
cd economic-networks-seminar
conda env create -f environment.yml
conda activate econ-networks
python check_setup.py          # checks the packages and runs the solver
jupyter lab                    # open any notebook in labs/
```

Without conda: `python -m venv .venv`, activate it, then `pip install -r requirements.txt`.

Some scripts also run on their own:

```bash
python labs/cops_robbers_game.py --network dodeca --cops 3 --mode robber   # opens the board in your browser
python labs/cops_robbers_game.py --list                                     # all networks
python labs/kg_lab.py --query "Financial contagion" --year 2000             # literature knowledge graph
python labs/clue_bank_game.py                                               # bank game scenarios and charts
```

The two boards in `games/` open in any browser with no Python at all.

## For the maintainer

Before the first push, run `python set_github_user.py YOUR-USER` to put your username into every link. The full steps are in [MAINTAINING.md](MAINTAINING.md).

## Repository layout

```
labs/        one .py and one .ipynb per lab (the notebooks are the scripts, cell by cell)
games/       standalone cops-and-robbers boards (HTML)
docs/        the bank game phone site (GitHub Pages; cards are password-encrypted)
slides/      the Beamer deck (LaTeX) and its figures; seminar_deck.pdf is the compiled version
timetable/   the one-page timetable (PowerPoint and PDF) and the script that builds it
```

**Slides.** Build with XeLaTeX (it uses Calibri, or the metric-compatible Carlito): run `xelatex main.tex` twice inside `slides/`. In `main.tex`, `\optionaltrue` adds the optional slides and `\appendixfalse` removes the printable bank-game cards.

**Timetable.** `cd timetable && npm install pptxgenjs && node build.js`.

## Data and third-party material

- **Glasgow school data** (`school_gossip`): the Teenage Friends and Lifestyle Study excerpt distributed with the [RSiena](https://github.com/stocnet/rsiena) package. It is downloaded when the lab runs and is not included here.
- **OpenAlex** (`kg_lab`): free API, no key needed for light use; answers are cached locally and not committed.
- **Not included**: film clips and GIFs (*Catch Me If You Can*, *The Big Short*, *Margin Call*), photos and logos used in the live deck. The deck shows grey placeholders where these go.

## Main references

- Olsen, A. (2023). Cops and Robbers: A Game of Pursuit on Graphs. *Procedia Computer Science* 221, 434–441. https://doi.org/10.1016/j.procs.2023.07.058
- Hogan, A. et al. (2021). Knowledge Graphs. *ACM Computing Surveys* 54(4), 71. https://doi.org/10.1145/3447772
- Barabási, A.-L. *Network Science* (free online); Jackson, M. *Social and Economic Networks*.
- Suggested readings: Wilson, *Introduction to Graph Theory*; Shakarian et al., *Diffusion in Social Networks*, ch. 4; Vapnik, *The Nature of Statistical Learning Theory*; Ribeiro, *Graph Neural Networks* (UPenn).
