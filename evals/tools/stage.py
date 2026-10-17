"""Copy the plugin (tracked and new files, plus evals/private) to a clean folder for `claude plugin eval`.
The working tree holds a local Python env with hard links, which the eval harness refuses.
--holdout <ids file>: remove those evidence records so winner cases are unseen by the pack.
Usage: stage.py <out-dir> [--holdout evals/holdout.txt]"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
out = Path(sys.argv[1]).resolve()
if out.exists():
    shutil.rmtree(out)
files = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split("\n")
files += [str(p.relative_to(ROOT)) for p in (ROOT / "evals" / "private").rglob("*") if p.is_file()]
for f in filter(None, files):
    src = ROOT / f
    if src.is_file() and not f.startswith("evals/results/"):
        dst = out / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        shutil.copymode(src, dst)
if "--holdout" in sys.argv:
    ids = [l.strip() for l in open(ROOT / sys.argv[sys.argv.index("--holdout") + 1]) if l.strip() and not l.startswith("#")]
    for i in ids:
        (out / "skills/cro/evidence/tests" / f"{i}.json").unlink(missing_ok=True)
    cat = out / "skills/cro/evidence/CATALOG.md"
    if cat.exists():
        # Each record is a "### ... (`id`)" section; drop the whole section, not just its heading.
        keep, skip = [], False
        for line in cat.read_text().splitlines():
            if line.startswith("#"):
                skip = line.startswith("### ") and any(f"(`{i}`)" in line for i in ids)
            if not skip and not (line.endswith("flat/inconclusive.") and "records:" in line):
                keep.append(line)
        cat.write_text("\n".join(keep) + "\n")
print("STAGED", out)
