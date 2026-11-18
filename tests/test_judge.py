"""Judgements, with canned judge output in place of `claude -p`: no model is called here."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from evalkit.judge import distinctness, judge_command, preference

RECORD = """\
# Design decision: the recent-orders section of the dashboard

## Axes

| Axis | Poles |
|---|---|
| Density | compact ↔ roomy |
| Emphasis | data first ↔ action first |

## Directions
"""


def repo(root, shots):
    """A run's repo holding a decision record and these screenshots in its folder."""
    decisions = root / "docs/design/decisions"
    (decisions / "2026-11-18-recent-orders").mkdir(parents=True)
    (decisions / "2026-11-18-recent-orders.md").write_text(RECORD)
    for shot in shots:
        (decisions / "2026-11-18-recent-orders" / shot).write_bytes(b"\x89PNG")
    return root


def claude_says(*answers):
    """A stand-in for subprocess.run that answers each judge call in turn, as `claude -p --output-format json`
    would. An answer that is an exception is raised; a dict is the judge's JSON; a string is its raw stdout.
    Each call's folder listing is kept on the mock as `.folders`."""
    folders, replies = [], iter(answers)

    def run(command, cwd, **_):
        folders.append(sorted(str(p.relative_to(cwd)) for p in Path(cwd).rglob("*") if p.is_file()))
        reply = next(replies)
        if isinstance(reply, BaseException):
            raise reply
        if isinstance(reply, int):
            return subprocess.CompletedProcess(command, reply, "", "boom")
        stdout = json.dumps({"result": json.dumps(reply)}) if isinstance(reply, dict) else reply
        return subprocess.CompletedProcess(command, 0, stdout, "")

    fake = mock.Mock(side_effect=run)
    fake.folders = folders
    return fake


SHOT = "production-typical-1280.png"


def pick(choice, cited=(f"A/{SHOT}", f"B/{SHOT}")):
    return {"preferred": choice, "reason": "it reads better", "screenshots": list(cited)}


class JudgeCommandTest(unittest.TestCase):
    def test_loads_no_plugins_and_no_settings_and_allows_only_read(self):
        command = judge_command("Which is better?", "opus")
        flag = lambda name: command[command.index(name) + 1]
        self.assertEqual(command[:3], ["claude", "-p", "Which is better?"])
        self.assertEqual(flag("--setting-sources"), "")
        self.assertEqual(flag("--tools"), "Read")
        self.assertEqual(flag("--allowedTools"), "Read")
        self.assertEqual(flag("--model"), "opus")
        self.assertIn("--strict-mcp-config", command)
        self.assertIn("--restricted", command, "Read is confined to the judge's folder")
        self.assertNotIn("--plugin-dir", command)


class PreferenceTest(unittest.TestCase):
    def judge(self, *answers, new_shots=(SHOT, "compact-list-typical-1280.png"), old_shots=(SHOT,)):
        with tempfile.TemporaryDirectory() as tmp:
            new, old = repo(Path(tmp) / "new", new_shots), repo(Path(tmp) / "old", old_shots)
            fake = claude_says(*answers)
            with mock.patch("evalkit.judge.subprocess.run", fake):
                return preference(new, old, "Build a recent-orders section.", "opus"), fake

    def test_order_swapped_answers(self):
        cases = {
            # The first call shows new as A, the second shows old as A.
            "both pick new": ((pick("A"), pick("B")), "new preferred"),
            "both pick old": ((pick("B"), pick("A")), "old preferred"),
            "the two orders disagree": ((pick("A"), pick("A")), "no preference"),
            "neither is preferred": ((pick("none"), pick("none")), "no preference"),
        }
        for name, (answers, expected) in cases.items():
            with self.subTest(name):
                result, fake = self.judge(*answers)
                self.assertEqual(result["result"], expected)
                self.assertEqual(fake.folders, [[f"A/{SHOT}", f"B/{SHOT}"]] * 2,
                                 "the judge sees only the production shots both versions captured")

    def test_not_judged(self):
        cases = {
            "invalid JSON": (("this is not JSON",), "not judged: "),
            "an answer that isn't the fixed shape": (({"preferred": "C"},), "not judged: "),
            "a screenshot outside its folder": ((pick("A", ["../../etc/passwd"]),), "not judged: "),
            "a screenshot it wasn't given": ((pick("A", ["A/production-error-390.png"]),), "not judged: "),
            "claude fails": ((1,), "not judged: claude exited with 1"),
            "claude times out": ((subprocess.TimeoutExpired("claude", 600),), "not judged: timed out"),
            "the second order fails": ((pick("A"), "oops"), "not judged: "),
            "a result that isn't text": ((json.dumps({"result": 7}),), "not judged: "),
            "a cited name with a NUL byte": ((pick("A", ["A/\0.png"]),), "not judged: "),
        }
        for name, (answers, prefix) in cases.items():
            with self.subTest(name):
                result, _ = self.judge(*answers)
                self.assertTrue(result["result"].startswith(prefix), result["result"])

    def test_no_shared_production_shots_is_not_judged_without_calling_the_judge(self):
        result, fake = self.judge(old_shots=("production-error-390.png",))
        self.assertEqual(result["result"], "not judged: no production screenshots that both versions captured")
        fake.assert_not_called()


class DistinctnessTest(unittest.TestCase):
    SHOTS = ("compact-list-typical-1280.png", "card-grid-typical-1280.png", SHOT)

    def judge(self, *answers):
        with tempfile.TemporaryDirectory() as tmp:
            fake = claude_says(*answers)
            with mock.patch("evalkit.judge.subprocess.run", fake):
                return distinctness(repo(Path(tmp), self.SHOTS), "opus"), fake

    def axis(self, name, differs):
        return {"axis": name, "differs": differs, "reason": "seen", "screenshots": ["card-grid-typical-1280.png"]}

    def test_each_axis_the_record_names(self):
        result, fake = self.judge({"axes": [self.axis("Density", True), self.axis("Emphasis", False)]})
        self.assertEqual(result, {"result": "judged", "axes": [
            {"axis": "Density", "differs": True, "reason": "seen"},
            {"axis": "Emphasis", "differs": False, "reason": "seen"},
        ]})
        self.assertEqual(fake.folders, [["axes.md", "card-grid-typical-1280.png", "compact-list-typical-1280.png"]],
                         "the judge sees the axes table and the directions' screenshots, not production shots")

    def test_not_judged(self):
        cases = {
            "an answer missing an axis": {"axes": [self.axis("Density", True)]},
            "an answer citing the axes table, not a screenshot": {"axes": [
                {**self.axis("Density", True), "screenshots": ["axes.md"]}, self.axis("Emphasis", False)]},
        }
        for name, answer in cases.items():
            with self.subTest(name):
                result, _ = self.judge(answer)
                self.assertTrue(result["result"].startswith("not judged: "), result)

    def test_the_prompt_names_every_screenshot(self):
        _, fake = self.judge({"axes": [self.axis("Density", True), self.axis("Emphasis", False)]})
        prompt = fake.call_args.args[0][2]
        for shot in ("compact-list-typical-1280.png", "card-grid-typical-1280.png"):
            self.assertIn(shot, prompt, "Read can't list a folder, so the judge must be told each file's name")


if __name__ == "__main__":
    unittest.main()
