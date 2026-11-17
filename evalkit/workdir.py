"""Build the throwaway repo a case runs in: the fixture's files, the case's input files, one commit."""
import shutil
import subprocess
from pathlib import Path


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
    """A git repo at `dest` holding the case's fixture and input files, committed, as Pixie's skills expect."""
    dest = Path(dest)
    dest.mkdir(parents=True)
    copy_fixture(Path(fixtures_dir) / case.spec["fixture"], dest)
    if case.scaffold:
        subprocess.run(["bash", str(case.scaffold)], cwd=dest, check=True)
    git = ["git", "-c", "user.name=pixie-evals", "-c", "user.email=evals@localhost", "-c", "commit.gpgsign=false"]
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=dest, check=True)
    subprocess.run(["git", "add", "-A"], cwd=dest, check=True)
    subprocess.run([*git, "commit", "-q", "-m", f"Fixture for {case.name}"], cwd=dest, check=True)
