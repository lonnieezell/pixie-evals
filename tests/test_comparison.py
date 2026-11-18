"""A comparison: the same cases run against two Pixie checkouts, each grader's results side by side, and judgements
kept apart from them. Model calls are never made here: the judge gets canned output."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from evalkit.cases import Case
from evalkit.comparison import compare, write_and_report


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


if __name__ == "__main__":
    unittest.main()
