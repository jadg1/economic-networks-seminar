# Setup: copy and paste

Three ways to use the labs, from easiest to most flexible. Pick one.

| | You need | Good for |
| --- | --- | --- |
| [A. Google Colab](#a-google-colab-nothing-to-install) | A Google account and a browser | The seminar itself. Nothing to install. |
| [B. Download the ZIP](#b-download-the-zip-no-git) | Python (via Miniforge) | Running on your own computer without Git |
| [C. Clone with Git](#c-clone-with-git-recommended-if-you-want-updates) | Git and Python | Getting updates later with one command |

---

## A. Google Colab (nothing to install)

1. Open the repository page: `https://github.com/jadg1/economic-networks-seminar`
2. In the README, click an **Open in Colab** badge.
3. In Colab, run the first code cell (*Setup for Google Colab*), then the rest (**Runtime → Run all**).
4. To keep your changes: **File → Save a copy in Drive**.

That's all. The rest of this page is for running on your own computer.

---

## Install the tools once

You need **Git** (to download and update the repository) and **conda** (to install Python and the libraries). We recommend **Miniforge**, a free, minimal conda that uses the open conda-forge channel.

Already have Anaconda or Miniconda? Skip the conda step: everything below works the same.

### Windows

Open **PowerShell** (Start menu → type *PowerShell*) and paste:

```powershell
winget install -e --id Git.Git
winget install -e --id CondaForge.Miniforge3
```

Close PowerShell. From now on, use **Miniforge Prompt** (Start menu → type *Miniforge*). If you use Anaconda, use **Anaconda Prompt** instead.

No `winget`? Download the installers by hand: [Git for Windows](https://git-scm.com/download/win) and [Miniforge](https://github.com/conda-forge/miniforge#install) (keep the default options).

### macOS

Open **Terminal** (Applications → Utilities) and paste:

```bash
xcode-select --install
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh -b
~/miniforge3/bin/conda init zsh
```

The first line installs Git (a window opens: click *Install*). Close Terminal and open it again before continuing.

With Homebrew instead: `brew install git miniforge`, then `conda init zsh`.

### Linux (Ubuntu, Debian and similar)

```bash
sudo apt update && sudo apt install -y git curl
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
bash Miniforge3-$(uname)-$(uname -m).sh -b
~/miniforge3/bin/conda init bash
exec bash
```

Fedora: replace the first line with `sudo dnf install -y git curl`.

---

## B. Download the ZIP (no Git)

1. On the repository page, click the green **Code** button → **Download ZIP**.
2. Unzip it, for example into your Documents folder.
3. Open Miniforge Prompt (Windows) or Terminal (macOS, Linux), go into the folder and create the environment:

**Windows**

```bat
cd %USERPROFILE%\Documents\economic-networks-seminar-main
conda env create -f environment.yml
conda activate econ-networks
python check_setup.py
jupyter lab
```

**macOS and Linux**

```bash
cd ~/Documents/economic-networks-seminar-main
conda env create -f environment.yml
conda activate econ-networks
python check_setup.py
jupyter lab
```

`check_setup.py` should end with **All good.** `jupyter lab` opens your browser: open any notebook in `labs/`.

---

## C. Clone with Git (recommended if you want updates)

**Windows** (Miniforge Prompt)

```bat
cd %USERPROFILE%\Documents
git clone https://github.com/jadg1/economic-networks-seminar.git
cd economic-networks-seminar
conda env create -f environment.yml
conda activate econ-networks
python check_setup.py
jupyter lab
```

**macOS and Linux** (Terminal)

```bash
cd ~/Documents
git clone https://github.com/jadg1/economic-networks-seminar.git
cd economic-networks-seminar
conda env create -f environment.yml
conda activate econ-networks
python check_setup.py
jupyter lab
```

### Get the latest version later

```bash
cd economic-networks-seminar
git pull
conda env update -f environment.yml --prune
```

`git pull` downloads whatever changed since you cloned. If you edited a notebook, Git may refuse to overwrite it: save your version under a new name first, or run `git stash` before `git pull`.

---

## Every time you come back

```bash
cd economic-networks-seminar        # Windows: cd %USERPROFILE%\Documents\economic-networks-seminar
conda activate econ-networks
jupyter lab
```

## Run things without Jupyter

```bash
python labs/cops_robbers_game.py --network dodeca --cops 3 --mode robber   # the game opens in your browser
python labs/cops_robbers_game.py --list                                     # list all networks
python labs/kg_lab.py --query "Financial contagion" --year 2000             # literature knowledge graph
python labs/clue_bank_game.py                                               # bank game scenarios
```

## Without conda (plain Python 3.10 or newer)

**Windows**

```bat
cd economic-networks-seminar
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python check_setup.py
```

**macOS and Linux**

```bash
cd economic-networks-seminar
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python check_setup.py
```

## Libraries

All of these are installed by `environment.yml` (conda) or `requirements.txt` (pip).

| Library | Used for | Labs |
| --- | --- | --- |
| `networkx` | Networks: building them, paths, centrality, communities | all |
| `numpy`, `scipy` | Matrices, eigenvalues, layouts | all |
| `pandas` | Result tables | all |
| `matplotlib` | Figures | all |
| `requests` | Downloading data and calling the OpenAlex API | `school_gossip`, `kg_lab` |
| `pyreadr` | Reading the Glasgow school data (an R file) | `school_gossip` |
| `pyvis` | Interactive network view (optional) | `kg_lab` |
| `ipywidgets` | Drop-down menus in notebooks | `cops_and_robbers_game` |
| `jupyterlab`, `nbformat` | Opening and running the notebooks | all notebooks |

## Something went wrong?

| Message | Fix |
| --- | --- |
| `conda: command not found` / `'conda' is not recognized` | Use Miniforge Prompt (Windows), or close and reopen Terminal after `conda init` (macOS, Linux) |
| `git: command not found` | Install Git (see above), then open a new window |
| `CondaValueError: prefix already exists` | The environment exists already: `conda env update -f environment.yml --prune` |
| `ModuleNotFoundError: No module named ...` | You forgot `conda activate econ-networks`, or VS Code uses another Python: Ctrl+Shift+P → *Python: Select Interpreter* → `econ-networks` |
| `& : The term '...\envs\...' is not recognized` (PowerShell) | You pointed at the environment folder, not at Python. Activate the environment and run `python file.py` |
| The game board ignores the keys | Click on the board first, then use W A S D |
| `school_gossip` fails to download the data | Check your internet connection; the data comes from the RSiena repository on GitHub |

---

## Contributing: suggest a change with a pull request

Found a mistake, or want to add an exercise? A *pull request* proposes your change; the maintainer reviews it and merges it.

**On the website (easiest, for small changes).** Open the file on GitHub → click the pencil icon → edit → **Commit changes…** → **Propose changes** → **Create pull request**. GitHub makes a copy (a *fork*) for you automatically.

**From the command line.**

1. On the repository page, click **Fork** (top right). This creates `https://github.com/YOUR-USER/economic-networks-seminar`.
2. Then:

```bash
git clone https://github.com/YOUR-USER/economic-networks-seminar.git
cd economic-networks-seminar
git checkout -b my-change               # a branch for your change
# ... edit files ...
git add .
git commit -m "Describe your change in one line"
git push -u origin my-change
```

3. GitHub prints a link after the push (or shows a yellow banner on your fork): click **Compare & pull request**, describe the change, and click **Create pull request**.

With the GitHub CLI (`gh`), steps 1 to 3 are: `gh repo fork jadg1/economic-networks-seminar --clone`, then edit, commit, push, and `gh pr create`.

Before you open the pull request, run `python check_setup.py` and rerun any notebook you changed.
