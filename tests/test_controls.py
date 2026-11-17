"""The graders against hand-made outputs in controls/CASE/VARIANT/. `good` must pass every grader of its case.
`bad-CHECK` must fail CHECK: it's the negative control that proves the grader catches that mistake."""
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from evalkit.cases import load_case
from evalkit.grade import grade
from evalkit.workdir import copy_fixture

ROOT = Path(__file__).resolve().parents[1]
PIXIE = Path(os.environ.get("PIXIE", ROOT.parent / "pixie"))
CONTROLS = sorted(p for p in (ROOT / "controls").glob("*/*") if p.is_dir())


def grade_control(control):
    case = load_case(ROOT / "evals" / control.parent.name)
    with tempfile.TemporaryDirectory() as tmp:
        copy_fixture(ROOT / "fixtures" / case.spec["fixture"], tmp)
        shutil.copytree(control, tmp, dirs_exist_ok=True)
        return {r["check"]: r for r in grade(case, tmp, PIXIE)}


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
