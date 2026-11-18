"""A comparison: the same cases run against two Pixie checkouts, each grader's results side by side, and judgements
kept apart from them. Model calls are never made here: the judge gets canned output."""
import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from evalkit.cases import Case, load_case
from evalkit.comparison import compare, write_and_report
from evalkit.runner import run_comparison

ROOT = Path(__file__).resolve().parents[1]
PIXIE = Path(os.environ.get("PIXIE", ROOT.parent / "pixie")).resolve()


def case(name):
    return Case(name=name, path=Path(name), prompt="Build a recent-orders section.", timeout=1,
                graders=[("record-written", "A decision record is written."), ("tests-pass", "The tests pass.")],
                spec={}, scaffold=None)


def write_run(run_dir, passed):
    """A run-K folder whose grading.json holds one expectation per grader text in `passed`."""
    run_dir.mkdir(parents=True)
    expectations = [{"text": text, "passed": ok, "evidence": "made by hand"} for text, ok in passed.items()]
    (run_dir / "grading.json").write_text(json.dumps({"expectations": expectations}))


RECORD, TESTS = "A decision record is written.", "The tests pass."


class ComparisonReportTest(unittest.TestCase):
    def test_reads_a_hand_built_results_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            iteration = Path(tmp)
            design = iteration / "design-react"
            write_run(design / "new_skill" / "run-1", {RECORD: True, TESTS: False})
            write_run(design / "new_skill" / "run-2", {RECORD: True, TESTS: True})
            write_run(design / "old_skill" / "run-1", {RECORD: True, TESTS: True})
            write_run(design / "old_skill" / "run-2", {RECORD: True, TESTS: True})
            judgement = {"runs": [{"run": 1, "preference": {"result": "new preferred"}}]}
            (design / "judgement.json").write_text(json.dumps(judgement))
            setup = iteration / "setup-react"
            write_run(setup / "new_skill" / "run-1", {RECORD: False, TESTS: True})
            write_run(setup / "old_skill" / "run-1", {RECORD: True, TESTS: True})

            cases = [case("design-react"), case("setup-react"), case("design-ci4")]
            printed = io.StringIO()
            with contextlib.redirect_stdout(printed):
                ok = write_and_report(iteration, cases, [])
            written = json.loads((iteration / "comparison.json").read_text())
            self.assertEqual(written, compare(iteration, cases))

        self.assertTrue(ok)
        by_case = {c["case"]: c for c in written["cases"]}
        self.assertEqual(set(by_case), {"design-react", "setup-react"}, "a case with no results is left out")
        figures = {(name, g["check"]): (g["new_skill"], g["old_skill"], g["differs"])
                   for name, c in by_case.items() for g in c["graders"]}
        two = {"runs": 2, "indicative_only": False}
        one = {"runs": 1, "indicative_only": True}
        self.assertEqual(figures, {
            ("design-react", "record-written"): ({"passed": 2, **two}, {"passed": 2, **two}, False),
            ("design-react", "tests-pass"): ({"passed": 1, **two}, {"passed": 2, **two}, True),
            ("setup-react", "record-written"): ({"passed": 0, **one}, {"passed": 1, **one}, True),
            ("setup-react", "tests-pass"): ({"passed": 1, **one}, {"passed": 1, **one}, False),
        })
        self.assertEqual(by_case["design-react"]["judgements"], judgement)
        self.assertIsNone(by_case["setup-react"]["judgements"])
        report = printed.getvalue()
        self.assertIn("1/2", report)
        self.assertIn("indicative only", report)
        self.assertIn("new preferred 1, old preferred 0, no preference 0, not judged 0", report)

    def test_run_errors_fail_a_comparison_and_failing_graders_do_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            iteration = Path(tmp)
            write_run(iteration / "setup-react" / "new_skill" / "run-1", {RECORD: False, TESTS: False})
            write_run(iteration / "setup-react" / "old_skill" / "run-1", {RECORD: False, TESTS: False})
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(write_and_report(iteration, [case("setup-react")], []))
                self.assertFalse(write_and_report(iteration, [case("setup-react")], ["setup-react: timed out"]))


class ComparisonRunTest(unittest.TestCase):
    """A real comparison run of setup-react, with the `claude -p` call that runs the skill stubbed out."""

    def test_layout_metadata_and_grade_only(self):
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PIXIE, check=True, capture_output=True,
                                text=True).stdout.strip()
        with tempfile.TemporaryDirectory() as tmp:
            iteration = Path(tmp) / "iteration-1"
            configs = {"new_skill": PIXIE, "old_skill": PIXIE}
            setup = load_case(ROOT / "evals" / "setup-react")
            with mock.patch("evalkit.runner.run_claude", return_value=None) as claude:
                errors = run_comparison(setup, 1, iteration, configs, 2, ROOT / "fixtures", "opus")
            self.assertEqual(errors, [])
            self.assertEqual(claude.call_count, 4)

            case_dir = iteration / "setup-react"
            runs = sorted(str(p.parent.relative_to(case_dir)) for p in case_dir.glob("*/*/grading.json"))
            self.assertEqual(runs, ["new_skill/run-1", "new_skill/run-2", "old_skill/run-1", "old_skill/run-2"])
            metadata = json.loads((case_dir / "eval_metadata.json").read_text())
            self.assertEqual(metadata["configs"], {name: {"pixie": str(PIXIE), "commit": commit} for name in configs})
            self.assertFalse((case_dir / "judgement.json").exists(), "only design-* cases are judged")

            judgement = '{"runs": []}\n'
            (case_dir / "judgement.json").write_text(judgement)
            (case_dir / "old_skill" / "run-2" / "grading.json").unlink()
            # A `claude` that leaves a mark if anything calls it, such as the judge.
            called = Path(tmp) / "claude-was-called"
            (Path(tmp) / "bin").mkdir()
            (Path(tmp) / "bin" / "claude").write_text(f"#!/bin/sh\ntouch '{called}'\nexit 1\n")
            (Path(tmp) / "bin" / "claude").chmod(0o755)
            done = subprocess.run([str(ROOT / "run-evals"), "--pixie", str(PIXIE), "--grade-only", str(iteration),
                                   "--case", "setup-react"], cwd=ROOT, capture_output=True, text=True,
                                  env={**os.environ, "PATH": f"{Path(tmp) / 'bin'}{os.pathsep}{os.environ['PATH']}"})
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertTrue((case_dir / "old_skill" / "run-2" / "grading.json").is_file(), "every run is graded again")
            self.assertEqual((case_dir / "judgement.json").read_text(), judgement, "saved judgements are kept")
            self.assertFalse(called.exists(), "--grade-only never runs the judge")
            graders = json.loads((iteration / "comparison.json").read_text())["cases"][0]["graders"]
            self.assertEqual({g["old_skill"]["runs"] for g in graders}, {2})


if __name__ == "__main__":
    unittest.main()
