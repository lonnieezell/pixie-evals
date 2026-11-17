"""Scripted, deterministic graders. Each check reads what a Pixie skill left in the eval's repo and returns
(passed, evidence). A case's `graders/NN-CHECK-ID.md` files say which checks run, in which order."""
import re
from pathlib import Path

from .markdown import section, table_rows

INVENTORY = "docs/agents/design-system.md"
CRITIQUES = "docs/design/critiques"
RUBRIC = "skills/design-critique/references/rubric.md"


class Context:
    """What a check sees: the eval's repo after the run, the case's checks.json, and the Pixie checkout."""

    def __init__(self, repo, spec, pixie):
        self.repo, self.spec, self.pixie = Path(repo), spec, Path(pixie)

    def inventory(self):
        path = self.repo / INVENTORY
        return path.read_text() if path.is_file() else None

    def report(self):
        """The newest critique report, or None."""
        reports = sorted((self.repo / CRITIQUES).glob("*.md")) if (self.repo / CRITIQUES).is_dir() else []
        return reports[-1] if reports else None


CHECKS = {}


def check(fn):
    CHECKS[fn.__name__.replace("_", "-")] = fn
    return fn


def missing_inventory():
    return False, f"{INVENTORY} was not written"


# --- /design-setup -------------------------------------------------------------------------------------------


@check
def inventory_written(ctx):
    text = ctx.inventory()
    if text is None:
        return missing_inventory()
    absent = [name for name in ("Stack", "Tokens", "Components", "Patterns") if section(text, name) is None]
    if absent:
        return False, f"{INVENTORY} has no ## {', ## '.join(absent)} section"
    return True, f"{INVENTORY} exists with Stack, Tokens, Components and Patterns sections"


@check
def stack_detected(ctx):
    text = ctx.inventory()
    if text is None:
        return missing_inventory()
    stack = section(text, "Stack") or ""
    absent = [word for word in ctx.spec["stack"] if word.lower() not in stack.lower()]
    if absent:
        return False, f"## Stack doesn't name {', '.join(absent)}: {stack.strip()[:200]!r}"
    return True, f"## Stack names {', '.join(ctx.spec['stack'])}"


def component_status(ctx, role):
    """The status cell of the Components row whose Path / import column names the role's file."""
    text = ctx.inventory()
    if text is None:
        return None, missing_inventory()
    needles = ctx.spec[role]
    rows = [r for r in table_rows(section(text, "Components")) if len(r) >= 2 and any(n in r[1] for n in needles)]
    if not rows:
        return None, (False, f"no ## Components row has {' or '.join(needles)} in its Path / import column")
    return rows[0][-1], None


@check
def legacy_marked_legacy(ctx):
    status, failed = component_status(ctx, "legacy")
    if failed:
        return failed
    return status.lower().startswith("legacy"), f"{ctx.spec['legacy'][0]} status: {status!r}"


@check
def preferred_marked_preferred(ctx):
    status, failed = component_status(ctx, "preferred")
    if failed:
        return failed
    return status.lower().startswith("preferred"), f"{ctx.spec['preferred'][0]} status: {status!r}"


def pattern_blocks(ctx):
    """(file, first line, last line) of each occurrence of the fixture's repeated markup: an element whose class
    list is the pattern's (in any order), plus the `span` lines of its children."""
    classes = sorted(ctx.spec["pattern"]["classes"].split())
    span = ctx.spec["pattern"]["span"]
    blocks = []
    for rel in ctx.spec["pattern"]["files"]:
        for number, line in enumerate((ctx.repo / rel).read_text().splitlines(), 1):
            for attr in re.findall(r'class(?:Name)?="([^"]+)"', line):
                if sorted(attr.split()) == classes:
                    blocks.append((rel, number, number + span))
    return blocks


@check
def pattern_mined(ctx):
    text = ctx.inventory()
    if text is None:
        return missing_inventory()
    blocks = pattern_blocks(ctx)
    for row in table_rows(section(text, "Patterns")):
        for path, line in re.findall(r"([\w./-]+):(\d+)", " ".join(row)):
            if any(path.endswith(rel) and first <= int(line) <= last for rel, first, last in blocks):
                return True, f"## Patterns row cites {path}:{line}, an occurrence of {ctx.spec['pattern']['classes']!r}"
    return False, (f"no ## Patterns row cites an occurrence of {ctx.spec['pattern']['classes']!r} "
                   f"({len(blocks)} in {', '.join(ctx.spec['pattern']['files'])})")


# --- /design-critique ----------------------------------------------------------------------------------------


def missing_report():
    return False, f"no report in {CRITIQUES}/"


@check
def report_written(ctx):
    report = ctx.report()
    if not report:
        return missing_report()
    text = report.read_text()
    absent = [name for name in ("Gates", "Findings") if section(text, name) is None]
    if absent:
        return False, f"{report.name} has no ## {', ## '.join(absent)} section"
    return True, f"{CRITIQUES}/{report.name} has Gates and Findings sections"


def gate_table(ctx, heading):
    report = ctx.report()
    if not report:
        return None
    return table_rows(section(section(report.read_text(), "Gates") or "", heading, level=3))


@check
def axe_reported(ctx):
    rows = gate_table(ctx, "Accessibility (axe)")
    if rows is None:
        return missing_report()
    reported = {rule for row in rows for rule in re.findall(r"`([a-z0-9-]+)`", " ".join(row))}
    absent = [rule for rule in ctx.spec["axe_rules"] if rule not in reported]
    if absent:
        return False, f"axe violations on the screen but not in the report: {', '.join(absent)}"
    return True, f"the report lists every seeded axe violation: {', '.join(ctx.spec['axe_rules'])}"


@check
def tokens_reported(ctx):
    rows = gate_table(ctx, "Raw values")
    if rows is None:
        return missing_report()
    lines = [" ".join(row) for row in rows]
    absent = [v["match"] for v in ctx.spec["raw_values"] if not any(v["match"] in l and v["file"] in l for l in lines)]
    if absent:
        return False, f"raw values in the screen's files but not in the report: {', '.join(absent)}"
    return True, f"the report lists every seeded raw value: {', '.join(v['match'] for v in ctx.spec['raw_values'])}"


FINDING = re.compile(r"^### (F\d+)\b(.*)$", re.M)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def finding_problem(heading, body, ids, folder):
    """Why one finding doesn't cite a rubric item, an existing screenshot and its state, or None."""
    rubric = re.findall(r"`([^`]+)`", heading)
    if not rubric:
        return "no rubric item in its heading"
    if rubric[0] not in ids and not rubric[0].startswith(("fd.", "wdg.")):
        return f"cites {rubric[0]!r}, which isn't in Pixie's rubric"
    shot = re.search(r"\*\*Screenshot:\*\*\s*\[[^\]]*\]\(([^)\s]+)\)(.*)", body)
    if not shot:
        return "no Screenshot link"
    if not (folder / shot.group(1)).is_file():
        return f"its screenshot {shot.group(1)} doesn't exist"
    state = re.search(r"state `([^`]+)`", shot.group(2))
    if not state:
        return "no state named after its screenshot"
    if not Path(shot.group(1)).name.startswith(slug(state.group(1)) + "-"):
        return f"state {state.group(1)!r} doesn't match its screenshot {Path(shot.group(1)).name}"
    return None


@check
def findings_cite_evidence(ctx):
    report = ctx.report()
    if not report:
        return missing_report()
    findings = section(report.read_text(), "Findings") or ""
    ids = set(re.findall(r"^\|\s*`([^`]+)`\s*\|", (ctx.pixie / RUBRIC).read_text(), re.M))
    parts = FINDING.split(findings)
    found = list(zip(parts[1::3], parts[2::3], parts[3::3]))
    if not found:
        return False, "the report has no findings"
    problems = [f"{name} {problem}" for name, heading, body in found
                if (problem := finding_problem(heading, body, ids, report.parent))]
    if problems:
        return False, "; ".join(problems)
    return True, f"all {len(found)} findings cite a rubric item, an existing screenshot and its state"
