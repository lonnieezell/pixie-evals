"""The graders against hand-made outputs in controls/CASE/VARIANT/. `good` must pass every grader of its case.
`bad-CHECK` must fail CHECK: it's the negative control that proves the grader catches that mistake.

A control is laid over the case's repo, built as a real run builds it, so it reads as the run's changes. A `bad-`
control is laid over the case's `good` one, so it holds only its mistake. A control's `_outputs/` folder stands in
for what the runner saves next to the repo (the axe report)."""
import dataclasses
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from evalkit.cases import load_case
from evalkit.grade import grade
from evalkit.workdir import prepare

ROOT = Path(__file__).resolve().parents[1]
PIXIE = Path(os.environ.get("PIXIE", ROOT.parent / "pixie"))
CONTROLS = sorted(p for p in (ROOT / "controls").glob("*/*") if p.is_dir())
OUTPUTS = "_outputs"
# Checks that run the fixture's own tools, so they need its installed dependencies.
TOOLED = {"tests-pass", "harness-gated"}


def add_local_setup(fixture, repo):
    """What the fixture's start.sh set up and git ignores, as the eval's repo has it after serving: installed
    dependencies and .env. node_modules is linked; vendor is copied, because Composer's autoloader resolves the
    app's classes from vendor's real path."""
    if not any((fixture / name).is_dir() for name in ("node_modules", "vendor")):
        raise unittest.SkipTest(f"{fixture.name} has no installed dependencies: run its start.sh once")
    if (fixture / "node_modules").is_dir():
        (repo / "node_modules").symlink_to(fixture / "node_modules")
    if (fixture / "vendor").is_dir():
        shutil.copytree(fixture / "vendor", repo / "vendor", symlinks=True)
    if (fixture / ".env").is_file():
        shutil.copy2(fixture / ".env", repo / ".env")


def grade_control(control):
    case = load_case(ROOT / "evals" / control.parent.name)
    if control.name != "good":
        case = dataclasses.replace(case, graders=[g for g in case.graders if g[0] == control.name[len("bad-"):]])
    layers = [control] if control.name == "good" else [control.parent / "good", control]
    with tempfile.TemporaryDirectory() as tmp:
        repo, outputs = Path(tmp) / "repo", Path(tmp) / "outputs"
        prepare(case, ROOT / "fixtures", repo)
        outputs.mkdir()
        for layer in layers:
            shutil.copytree(layer, repo, dirs_exist_ok=True, ignore=shutil.ignore_patterns(OUTPUTS))
            if (layer / OUTPUTS).is_dir():
                shutil.copytree(layer / OUTPUTS, outputs, dirs_exist_ok=True)
        if TOOLED & {check for check, _ in case.graders}:
            add_local_setup(ROOT / "fixtures" / case.spec["fixture"], repo)
        return {r["check"]: r for r in grade(case, repo, PIXIE, outputs)}


class ControlsTest(unittest.TestCase):
    def test_every_case_has_a_good_control(self):
        cases = {p.name for p in (ROOT / "evals").iterdir() if (p / "case.yaml").is_file()}
        self.assertEqual(cases, {c.parent.name for c in CONTROLS if c.name == "good"})

    def test_controls(self):
        for control in CONTROLS:
            with self.subTest(control=f"{control.parent.name}/{control.name}"):
                results = grade_control(control)
                if control.name == "good":
                    failed = {k: r["evidence"] for k, r in results.items() if not r["passed"]}
                    self.assertEqual(failed, {})
                else:
                    target = control.name.removeprefix("bad-")
                    self.assertIn(target, results, f"{control.name} names no grader of its case")
                    self.assertFalse(results[target]["passed"], results[target]["evidence"])


if __name__ == "__main__":
    unittest.main()
