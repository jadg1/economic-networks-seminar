# Maintaining the repository: push, update, review pull requests

For the person who owns the GitHub repository. Students only need [SETUP.md](SETUP.md).

## What you need before the first push

| Requirement | How to get it | Check |
| --- | --- | --- |
| A GitHub account | github.com → Sign up | You can log in |
| Git | See [SETUP.md](SETUP.md#install-the-tools-once) | `git --version` |
| Your name and email in Git | Commands below | `git config --global --list` |
| Login from your computer to GitHub | Automatic on the first push (a browser window opens), or `gh auth login` | `git push` works |
| The environment (to test before pushing) | `conda env create -f environment.yml` | `python check_setup.py` says *All good* |
| An empty repository on GitHub | github.com → **New repository** → name `economic-networks-seminar`, **Public** (Colab links need it), **no** README, .gitignore or licence (they are already here) | The page shows "Quick setup" |

Files already in this folder that GitHub needs or uses:

| File | Why |
| --- | --- |
| `README.md` | The front page of the repository, with the Colab badges |
| `SETUP.md`, `BIBLIOGRAPHY.md`, `MAINTAINING.md` | Instructions and readings |
| `environment.yml`, `requirements.txt` | The libraries (conda and pip) |
| `.gitignore` | Keeps out downloaded data, caches, LaTeX build files |
| `.gitattributes` | Consistent line endings between Windows, macOS and Linux |
| `check_setup.py` | Tests the environment |
| `set_github_user.py` | Puts your username into every link |

Not included yet: a `LICENSE`. Without one, people can view the code but have no right to reuse it. GitHub can add one later: **Add file → Create new file → name it `LICENSE` → Choose a license template**.

## Your Git identity (once per computer)

Use the private email GitHub gives you (Settings → Emails → *Keep my email addresses private*), so your real address doesn't appear in the history:

```bash
git config --global user.name "Javier De Golferichs"
git config --global user.email "ID+USERNAME@users.noreply.github.com"
```

## The first push

Windows: in Miniforge Prompt or Anaconda Prompt. macOS and Linux: in Terminal. Replace `YOUR-USER`.

```bash
cd economic-networks-seminar
python set_github_user.py YOUR-USER
conda activate econ-networks
python check_setup.py
git init -b main
git add .
git commit -m "Seminar materials: labs, games, slides, timetable"
git remote add origin https://github.com/YOUR-USER/economic-networks-seminar.git
git push -u origin main
```

The first `git push` opens a browser window to log in to GitHub (Git Credential Manager, which comes with Git for Windows). On macOS or Linux, if it asks for a password, use a personal access token instead (GitHub → Settings → Developer settings → Personal access tokens), or install the GitHub CLI and run `gh auth login` first.

Then open `https://github.com/YOUR-USER/economic-networks-seminar` and click a Colab badge to check it works.

## Push a change later

```bash
git status                      # what changed
git add .
git commit -m "Fix the bank game scores"
git push
```

If you edited something on the GitHub website too, run `git pull` before `git push`.

## Rebuild the slides after a change

```bash
cd slides
xelatex main.tex
xelatex main.tex
copy main.pdf seminar_deck.pdf      # macOS/Linux: cp main.pdf seminar_deck.pdf
```

Needs a TeX distribution with XeLaTeX (MiKTeX on Windows, MacTeX on macOS, `texlive-xetex` on Linux) and the Calibri or Carlito font.

## Review and merge a pull request

1. GitHub emails you, and the **Pull requests** tab shows it.
2. Open it → **Files changed** to read the change. Comment on a line with the **+** button.
3. To test it on your computer first:

```bash
git fetch origin pull/NUMBER/head:pr-NUMBER
git switch pr-NUMBER
python check_setup.py
git switch main
```

4. Happy with it: **Merge pull request** → **Confirm merge**. Then on your computer: `git pull`.
5. Not right: **Review changes** → **Request changes**, with a comment saying what to fix.

## Students who downloaded earlier

They get your new version with:

```bash
cd economic-networks-seminar
git pull
```

Those who downloaded the ZIP download it again. In Colab, the badges always open the latest version.

## The bank game phone site (GitHub Pages)

Teams open their bank card on their phone instead of a paper card. The site is `docs/bank-game/index.html`; every card is encrypted with its team's password, so publishing it gives nothing away.

1. Build it (and the password slips) on your computer:

```bash
pip install cryptography
python presenter/make_bank_site.py          # add --new for new passwords
```

2. Push, then on GitHub: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / `/docs` → Save.**
3. After a minute it is live at `https://YOUR-USER.github.io/economic-networks-seminar/bank-game/`. The QR code on the "You are a bank" slide points there once you have run `set_github_user.py` and recompiled the slides.
4. Print `presenter/bank_passwords.pdf` and hand one slip to each team.

If a password leaks, run the script with `--new`, push, and print new slips.

## What stays private, and what is released after the seminar

`.gitignore` keeps two groups of files off GitHub even when you run `git add .`:

| Group | Files | Why |
| --- | --- | --- |
| **Never publish** | `presenter/` (bank cards, truth sheet, pull slips, team passwords, the site builder, presenter cheat sheet), `slides/appendix_cards.tex`, film GIFs, logos and photos in `slides/figures/` | Answers, and material that isn't ours to share |
| **Hold back until after the seminar** | `slides/` (the deck and its source), `labs/clue_bank_game.*`, `labs/trust_network.*` | They reveal the bank game's hidden network and the answers |

After the seminar, delete the *HOLD BACK* block at the end of `.gitignore`, then:

```bash
git add .
git commit -m "Add the bank game labs and slides"
git push
```

The public `slides/seminar_deck.pdf` is already built without the printable cards. To print the cards, use `presenter/bank_game_printables.pdf`.

Check what would be published at any time with `git status` (ignored files are not listed) or `git check-ignore -v FILE`.
