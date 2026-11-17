"""Build the throwaway repo a case runs in: the fixture's files, the case's input files, committed."""
import re
import shutil
import subprocess
from pathlib import Path

INVENTORY = "docs/agents/design-system.md"
UNSTAMPED = "0" * 40
# What a run changed is read against this tag: the repo as prepare() left it.
BASE = "eval-base"


def copy_fixture(fixture, dest):
    """Copy the fixture's tracked and untracked-but-not-ignored files, so installed dependencies, built assets and
    local databases never come along."""
    fixture, dest = Path(fixture), Path(dest)
    listed = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "."],
        cwd=fixture, check=True, capture_output=True, text=True,
    ).stdout
    for rel in filter(None, listed.split("\0")):
        if not (fixture / rel).is_file():  # deleted but still in the index
            continue
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(fixture / rel, dest / rel)


def prepare(case, fixtures_dir, dest):
    """A git repo at `dest` holding the case's fixture, then its input files, committed, as Pixie's skills expect.
    An input inventory whose Source commit is all zeros gets the fixture's commit, so the skill finds it fresh."""
    dest = Path(dest)
    dest.mkdir(parents=True)
    copy_fixture(Path(fixtures_dir) / case.spec["fixture"], dest)
    git = ["git", "-c", "user.name=pixie-evals", "-c", "user.email=evals@localhost", "-c", "commit.gpgsign=false"]
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=dest, check=True)
    subprocess.run(["git", "add", "-A"], cwd=dest, check=True)
    subprocess.run([*git, "commit", "-q", "-m", f"Fixture for {case.name}"], cwd=dest, check=True)
    if case.scaffold:
        subprocess.run(["bash", str(case.scaffold)], cwd=dest, check=True)
        inventory = dest / INVENTORY
        if inventory.is_file() and UNSTAMPED in inventory.read_text():
            sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=dest, check=True, capture_output=True,
                                 text=True).stdout.strip()
            inventory.write_text(re.sub(rf"\*\*Source commit:\*\* {UNSTAMPED}", f"**Source commit:** {sha}",
                                        inventory.read_text()))
        subprocess.run(["git", "add", "-A"], cwd=dest, check=True)
        subprocess.run([*git, "commit", "-q", "-m", f"Input files for {case.name}"], cwd=dest, check=True)
    subprocess.run(["git", "tag", BASE], cwd=dest, check=True)
