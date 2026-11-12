"""Put your GitHub username into the Colab links, once, before the first push.

    python set_github_user.py YOUR-USER

Replaces the placeholder GITHUB_USER in the Markdown files, in every notebook
in labs/ (the "Open in Colab" badges and the Colab setup cells) and in
slides/main.tex (the "Lab in Colab" buttons on the slides).
"""
import pathlib
import sys

if len(sys.argv) != 2:
    sys.exit(__doc__)
user = sys.argv[1].strip()
root = pathlib.Path(__file__).parent
changed = 0
files = [*sorted(root.glob("*.md")), *sorted((root / "labs").glob("*.ipynb")), root / "slides" / "main.tex"]
for path in files:
    text = path.read_text(encoding="utf-8")
    if "GITHUB_USER" in text:
        path.write_text(text.replace("GITHUB_USER", user), encoding="utf-8")
        changed += 1
        print("updated", path.relative_to(root))
print(f"{changed} files now point to github.com/{user}/economic-networks-seminar")
print("Recompile the slides (xelatex main.tex, twice, in slides/) so the PDF buttons use it too.")
