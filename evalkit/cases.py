"""Read one eval case folder, in skill-creator's layout plus a checks.json for the scripted graders."""
import json
import re
from dataclasses import dataclass
from pathlib import Path

GRADER = re.compile(r"^\d+-(.+)\.md$")


@dataclass
class Case:
    name: str
    path: Path
    prompt: str
    timeout: int
    graders: list  # (check id, statement), in file order
    spec: dict  # checks.json
    scaffold: Path | None


def front_matter(text):
    """(settings block, body) of a file that starts with a `---` block."""
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    return (match.group(1), match.group(2)) if match else ("", text)


def load_case(path):
    path = Path(path)
    settings, prompt = front_matter((path / "prompt.md").read_text())
    timeout = re.search(r"^timeout_seconds:\s*(\d+)", settings, re.M)
    scaffold = re.search(r"^\s*scaffold_script:\s*(\S+)", (path / "case.yaml").read_text(), re.M)
    graders = []
    for file in sorted((path / "graders").glob("*.md")):
        match = GRADER.match(file.name)
        if not match:
            raise ValueError(f"{file}: grader files are named NN-CHECK-ID.md")
        graders.append((match.group(1), front_matter(file.read_text())[1].strip()))
    return Case(
        name=path.name,
        path=path,
        prompt=prompt.strip(),
        timeout=int(timeout.group(1)) if timeout else 1800,
        graders=graders,
        spec=json.loads((path / "checks.json").read_text()),
        scaffold=path / scaffold.group(1) if scaffold else None,
    )


def load_cases(evals_dir, names=None):
    paths = sorted(p for p in Path(evals_dir).iterdir() if (p / "case.yaml").is_file())
    if names:
        unknown = set(names) - {p.name for p in paths}
        if unknown:
            raise SystemExit(f"no such case: {', '.join(sorted(unknown))}")
        paths = [p for p in paths if p.name in names]
    return [load_case(p) for p in paths]
