"""Scripted, deterministic graders. Each check reads what a Pixie skill left in the eval's repo and returns
(passed, evidence). A case's `graders/NN-CHECK-ID.md` files say which checks run, in which order."""
import json
import os
import re
import subprocess
import tempfile
from fnmatch import fnmatch
from pathlib import Path

from .markdown import section, table_rows
from .workdir import BASE, INVENTORY

CRITIQUES = "docs/design/critiques"
DECISIONS = "docs/design/decisions"
RUBRIC = "skills/design-critique/references/rubric.md"


class Context:
    """What a check sees: the eval's repo after the run, the case's checks.json, the Pixie checkout, and the
    runner's outputs folder."""

    def __init__(self, repo, spec, pixie, outputs=None):
        self.repo, self.spec, self.pixie = Path(repo), spec, Path(pixie)
        self.outputs = Path(outputs) if outputs else None
        self._changes = None

    def inventory(self):
        path = self.repo / INVENTORY
        return path.read_text() if path.is_file() else None

    def report(self):
        """The newest critique report, or None."""
        reports = sorted((self.repo / CRITIQUES).glob("*.md")) if (self.repo / CRITIQUES).is_dir() else []
        return reports[-1] if reports else None

    def record(self):
        """The newest design decision record (named YYYY-MM-DD-SLUG.md), or None."""
        folder = self.repo / DECISIONS
        records = sorted(p for p in folder.glob("*.md") if record_slug(p)) if folder.is_dir() else []
        return records[-1] if records else None

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True, text=True).stdout

    def files(self):
        """Every file in the repo that git doesn't ignore, committed or not, as repo-relative paths."""
        listed = self.git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
        return [rel for rel in dict.fromkeys(filter(None, listed.split("\0"))) if (self.repo / rel).is_file()]

    def changes(self):
        """What the run changed, against the repo prepare() left (or the first commit of an older run):
        {repo-relative path: (is it a new file, the lines it added)}. Binary files are left out."""
        if self._changes is None:
            tagged = subprocess.run(["git", "rev-parse", "-q", "--verify", f"refs/tags/{BASE}"], cwd=self.repo,
                                    capture_output=True, text=True).stdout.strip()
            base = tagged or self.git("rev-list", "--max-parents=0", "HEAD").split()[0]
            self._changes = added_lines(self.git("diff", "--no-renames", "--no-color", "-U0", base, "--"))
            for rel in filter(None, self.git("ls-files", "-z", "--others", "--exclude-standard").split("\0")):
                text = (self.repo / rel).read_text(errors="replace") if (self.repo / rel).is_file() else "\0"
                if "\0" not in text:
                    self._changes[rel] = (True, text.splitlines())
        return self._changes


def added_lines(diff):
    """{path: (is it a new file, its added lines)} from `git diff`. File headers come between a `diff --git` line and
    the first hunk, so an added line that starts with `++` is never taken for one."""
    changes, current, header, new = {}, None, False, False
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            current, header, new = None, True, False
        elif header and line.startswith("@@"):
            header = False
        elif header and line.startswith("--- "):
            new = line == "--- /dev/null"
        elif header and line.startswith("+++ b/"):
            current = line[len("+++ b/"):]
            changes[current] = (new, [])
        elif not header and current and line.startswith("+"):
            changes[current][1].append(line[1:])
    return changes


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


# --- /design -------------------------------------------------------------------------------------------------

RECORD_SECTIONS = ("Frame", "Axes", "Directions", "Production", "Not checked")
DIRECTION = re.compile(r"^### (\S+)(.*)$", re.M)


def missing_record():
    return False, f"no decision record in {DECISIONS}/"


def directions(text):
    """(name, chosen, body) of each direction under the record's ## Directions, in order."""
    parts = DIRECTION.split(section(text, "Directions") or "")
    return [(name, "(chosen)" in rest, body) for name, rest, body in zip(parts[1::3], parts[2::3], parts[3::3])]


def chosen_direction(text):
    """(name, body) of the direction the record marks chosen, or (None, '')."""
    return next(((name, body) for name, chosen, body in directions(text) if chosen), (None, ""))


WORD = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z0-9]+")


def words(text):
    """`RecentOrders`, `recent_orders` and `recent-orders` all give ['recent', 'orders']."""
    return [w.lower() for w in WORD.findall(text)]


@check
def decision_record_written(ctx):
    record = ctx.record()
    if not record:
        return missing_record()
    text = record.read_text()
    absent = [name for name in RECORD_SECTIONS if section(text, name) is None]
    if not re.search(r"^## Why ", text, re.M):
        absent.append("Why NAME")
    if absent:
        return False, f"{record.name} has no ## {', ## '.join(absent)} section"
    found = directions(text)
    chosen = [name for name, is_chosen, _ in found if is_chosen]
    if len(found) < 2:
        return False, f"{record.name} has {len(found)} direction under ## Directions, not at least 2"
    if len(chosen) != 1:
        return False, f"{record.name} marks {len(chosen)} directions (chosen), not exactly 1"
    shots = re.findall(r"\]\(([^)\s]+\.png)\)", text)
    missing = [shot for shot in shots if not (record.parent / shot).is_file()]
    if missing:
        return False, f"{record.name} links screenshots that don't exist: {', '.join(missing)}"
    return True, (f"{DECISIONS}/{record.name} has every section, {len(found)} directions with {chosen[0]} chosen, "
                  f"and its {len(shots)} screenshots")


def record_slug(record):
    """SLUG of a record named YYYY-MM-DD-SLUG.md."""
    match = re.match(r"\d{4}-\d{2}-\d{2}-(.+)\.md$", record.name)
    return match.group(1) if match else None


@check
def losers_deleted(ctx):
    record = ctx.record()
    if not record:
        return missing_record()
    slug = record_slug(record)
    losers = [f"{slug}-{name}" for name, chosen, _ in directions(record.read_text()) if not chosen]
    if not slug or not losers:
        return False, f"{record.name} names no losing direction to look for"
    left = []
    own = record.relative_to(ctx.repo).as_posix()
    for rel in ctx.files():
        if rel == own:  # the record names the losers on purpose
            continue
        text = (ctx.repo / rel).read_text(errors="replace")
        left += [f"{rel} ({loser})" for loser in losers if loser in rel or loser in text]
    if left:
        return False, f"losing directions are still in the repo: {', '.join(left)}"
    return True, f"no file but the decision record holds {', '.join(losers)}"


def matches(rel, patterns):
    """Whether a repo-relative path is one of the patterns: a glob, or else a file or a folder it's under."""
    return any(fnmatch(rel, p) if any(c in p for c in "*?[") else rel == p or rel.startswith(p + "/")
               for p in patterns)


def production(ctx):
    """The run's changes to production code: under the case's source folders, not previews and not tests."""
    return {rel: change for rel, change in ctx.changes().items()
            if matches(rel, ctx.spec["source"]) and not matches(rel, ctx.spec["previews"])
            and not matches(rel, ctx.spec["tests"]["files"])}


def component_name(text):
    """`RecentOrders`, `recent-orders.blade.php`, `<x-recent-orders>` and `RecentOrdersCell` all give
    'recent orders': a file's extensions, a Blade tag's `x-` and a CI4 `Cell` or `Component` suffix are dropped."""
    found = words(re.split(r"[./\\]", text.strip("<>/` ").removeprefix("x-"))[0])
    return " ".join(found[:-1] if len(found) > 1 and found[-1] in ("cell", "component") else found)


def reasons(line):
    """{component name: the reason after it} from a record's `New components:` line, such as
    "`RecentOrders`, because nothing catalogued lists orders, and `Badge`, because ..."."""
    parts = re.split(r"`([^`]+)`", line)
    return {component_name(name): after for name, after in zip(parts[1::2], parts[2::2])}


@check
def reuse(ctx):
    changes = production(ctx)
    used = sorted({needle for _, lines in changes.values() for line in lines for needle in ctx.spec["preferred"]
                   if needle in line})
    if not used:
        return False, (f"no production line the run added uses a preferred component "
                       f"({', '.join(ctx.spec['preferred'])}); it changed {', '.join(changes) or 'nothing'}")
    new = {component_name(Path(rel).name) for rel, (is_new, _) in changes.items()
           if is_new and matches(rel, ctx.spec["components"])}
    if new:
        record = ctx.record()
        if not record:
            return missing_record()
        line = re.search(r"\*\*New components:\*\*(.*)", chosen_direction(record.read_text())[1])
        given = reasons(line.group(1)) if line else {}
        unexplained = sorted(name for name in new if len(words(given.get(name, ""))) < 3)
        if unexplained:
            return False, f"new components without a reason in the chosen direction: {', '.join(unexplained)}"
    return True, (f"production code uses {', '.join(used)}"
                  + (f", and the record gives a reason for {', '.join(sorted(new))}" if new else ""))


REQUIRED_STATES = ("empty", "single", "typical", "overflow", "error", "loading")
# The start of a preview's states: `export const states = {` in TSX, `'states' => [` in PHP.
STATES = re.compile(r"""\bstates["']?\s*(?:=>|=|:)\s*[\[{]""")
# One state in it: `empty: () =>` in TSX, `'empty' => fn` or `'empty' => static fn` in PHP.
STATE_KEY = re.compile(r"""^(\s*)["']?([A-Za-z][\w -]*?)["']?\s*(?::|=>)\s*(?:static\s+)?(?:fn\b|\(|function\b)""")
INTERACTION = re.compile(r"""\bname["']?\s*(?::|=>)\s*["']([^"']+)""")
JS_TEST = re.compile(r"""\b(?:it|test)(?:\.\w+)?\(\s*(["'`])(.+?)\1""")
PHP_TEST = re.compile(r"function\s+(test\w*)\s*\(|#\[Test\][^{;]*?function\s+(\w+)\s*\(")


def winner_preview(record):
    """The winner's preview slug, from the record's `Winner's preview` line, or SLUG-NAME of the chosen direction."""
    text = record.read_text()
    line = re.search(r"\*\*Winner's preview:\*\*\s*`/__preview/([a-z0-9-]+)", text)
    if line:
        return line.group(1)
    chosen = chosen_direction(text)[0]
    return f"{record_slug(record)}-{chosen}" if chosen else None


def preview_states(text):
    """(states, interaction names) a preview file declares. States are the keys at the top level of its states
    block, so a nested `onRetry: () => ...` is never taken for one."""
    start = STATES.search(text)
    states, indent = [], None
    for line in text[start.end():].splitlines() if start else []:
        depth = len(line) - len(line.lstrip())
        key = STATE_KEY.match(line)
        if indent is None and key:
            indent = depth
        if indent is not None and line.strip() and depth < indent:
            break
        if key and depth == indent:
            states.append(key.group(2))
    return list(dict.fromkeys(states)), INTERACTION.findall(text)


@check
def state_matrix_covered(ctx):
    record = ctx.record()
    if not record:
        return missing_record()
    slug = winner_preview(record)
    preview = ctx.repo / ctx.spec["preview_file"].format(slug=slug)
    if not slug or not preview.is_file():
        return False, f"the winner's preview isn't at {ctx.spec['preview_file'].format(slug=slug)}"
    states, interactions = preview_states(preview.read_text())
    added = "\n".join(line for rel, (_, lines) in ctx.changes().items()
                      if matches(rel, ctx.spec["tests"]["files"]) for line in lines)
    titles = [set(words(m[1])) for m in JS_TEST.findall(added)] + \
             [set(words(a or b)) for a, b in PHP_TEST.findall(added)]
    wanted = list(dict.fromkeys([*REQUIRED_STATES, *states]))
    missing = [s for s in wanted if not any(set(words(s)) <= title for title in titles)]
    if missing:
        return False, f"no added test is named for {', '.join(missing)} ({len(titles)} tests added)"
    if len(titles) < len(wanted) + len(interactions):
        return False, (f"{len(titles)} tests added for {len(wanted)} states and {len(interactions)} interactions "
                       f"of {preview.name}")
    return True, (f"{len(titles)} tests added, one named for each of the {len(wanted)} states, for the states and "
                  f"{len(interactions)} interactions of {preview.name}")


TOOL_TIMEOUT = 900


def run_tool(ctx, command, env=None):
    """(exit code, output) of one of the fixture's own tools, run in the repo."""
    try:
        done = subprocess.run(command, cwd=ctx.repo, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                              timeout=TOOL_TIMEOUT, env={**os.environ, "CI": "1", **(env or {})})
    except subprocess.TimeoutExpired:
        return None, f"timed out after {TOOL_TIMEOUT}s"
    return done.returncode, done.stdout


def tail(output, lines=3):
    return " / ".join(line.strip() for line in output.strip().splitlines()[-lines:] if line.strip())


@check
def tests_pass(ctx):
    command = ctx.spec["tests"]["command"]
    code, output = run_tool(ctx, command)
    if code != 0:
        return False, f"`{' '.join(command)}` exited with {code}: {tail(output, 6)}"
    return True, f"`{' '.join(command)}` passed: {tail(output)}"


def vite_build_has_preview(ctx, development):
    """Whether a Vite build holds the preview harness. A development build needs NODE_ENV too, or Vite still
    builds with import.meta.env.DEV false."""
    with tempfile.TemporaryDirectory() as out:
        command = ["npx", "vite", "build", "--outDir", out, "--emptyOutDir", "--logLevel", "error"]
        env = {"NODE_ENV": "development"} if development else {"NODE_ENV": "production"}
        code, output = run_tool(ctx, command + (["--mode", "development"] if development else []), env)
        if code != 0:
            return None, f"`{' '.join(command[:3])}` failed: {tail(output)}"
        found = [p.name for p in Path(out).rglob("*") if p.is_file() and "__preview" in p.read_text(errors="replace")]
        return bool(found), ", ".join(found) or "no built file"


def routes_have_preview(ctx, command, env):
    """Whether the app's route list, in one environment, holds the preview route."""
    code, output = run_tool(ctx, command, env)
    if code not in (0, 1):  # Laravel's route:list exits 1 when no route matches
        return None, f"`{' '.join(command)}` failed: {tail(output)}"
    found = [line.strip() for line in output.splitlines() if "__preview" in line]
    return bool(found), " ".join(found[0].split()) if found else tail(output, 1)


HARNESS = {
    "vite": vite_build_has_preview,
    "laravel": lambda ctx, dev: routes_have_preview(
        ctx, ["php", "artisan", "route:list", "--path=__preview"], {"APP_ENV": "local" if dev else "production"}),
    "ci4": lambda ctx, dev: routes_have_preview(
        ctx, ["php", "-d", "variables_order=EGPCS", "spark", "routes"],
        {"CI_ENVIRONMENT": "development" if dev else "production"}),
}


@check
def harness_gated(ctx):
    kind = ctx.spec["harness"]
    in_dev, dev_detail = HARNESS[kind](ctx, True)
    in_prod, prod_detail = HARNESS[kind](ctx, False)
    if in_dev is None or in_prod is None:
        return False, dev_detail if in_dev is None else prod_detail
    if not in_dev:
        return False, f"{kind}: the preview harness isn't there in development ({dev_detail})"
    if in_prod:
        return False, f"{kind}: production holds the preview harness ({prod_detail})"
    return True, f"{kind}: the preview harness is there in development and not in production"


# The eval's own token grep, kept apart from Pixie's gate so a regression there can't hide here. A Tailwind
# arbitrary value (`text-[#333]`, not a variant such as `data-[state=open]:`), and a hex colour in a property value
# (`color: #333`, `{ color: "#333" }`), not plain text such as `<td>#1001</td>`.
ARBITRARY = re.compile(r"(?<![\w\[-])-?[a-z][a-z0-9-]*-\[[^\]\s]+\](?!:)")
VALUE = re.compile(r":([^;{}<>\n]*)")
HEX = re.compile(r"(?<![\w#&/\[])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![\w-])")


def raw_values(line):
    return ARBITRARY.findall(line) + [hex for value in VALUE.findall(line) for hex in HEX.findall(value)]


@check
def production_tokens_clean(ctx):
    text = ctx.inventory()
    if text is None:
        return missing_inventory()
    source = re.search(r"^Source files:(.*)$", section(text, "Tokens") or "", re.M)
    token_files = set(re.findall(r"`([^`]+)`", source.group(1))) if source else set()
    changes = {rel: lines for rel, (_, lines) in production(ctx).items() if rel not in token_files}
    found = [f"{rel}: {value}" for rel, lines in changes.items() for line in lines for value in raw_values(line)]
    if found:
        return False, f"raw values in production lines the run added: {', '.join(found)}"
    return True, f"no raw values in the production lines the run added ({len(changes)} files, token files skipped)"


AXE = "axe.json"


def axe_targets(ctx):
    """(label, path) of each page the axe check covers: the production screen, and each state of the winner's
    preview, once the run has left one. The runner checks them while the app is up; the check reads its report."""
    targets = [("screen", ctx.spec["screen"])]
    record = ctx.record()
    slug = winner_preview(record) if record else None
    preview = ctx.repo / ctx.spec["preview_file"].format(slug=slug) if slug else None
    if preview and preview.is_file():
        states, _ = preview_states(preview.read_text())
        targets += [(state, f"/__preview/{slug}?state={state}") for state in states]
    return targets


@check
def production_axe_clean(ctx):
    report = ctx.outputs / AXE if ctx.outputs else None
    if not report or not report.is_file():
        return False, f"no {AXE} next to the repo: the runner writes it while the app is up"
    pages = {page["label"]: page for page in json.loads(report.read_text())}
    unchecked = [label for label, _ in axe_targets(ctx) if label not in pages]
    if unchecked:
        return False, f"{AXE} doesn't cover {', '.join(unchecked)}"
    failed = [f"{label}: {page['error']}" for label, page in pages.items() if page.get("error")]
    failed += [f"{label}: {v['id']} ({v['impact']})" for label, page in pages.items() for v in page["violations"]]
    if failed:
        return False, f"axe violations: {', '.join(failed)}"
    return True, f"axe finds no violations on {', '.join(pages)}"


@check
def legacy_avoided(ctx):
    changes = production(ctx)
    found = sorted({f"{rel} ({needle})" for rel, (_, lines) in changes.items() for line in lines
                    for needle in ctx.spec["legacy"] if needle in line})
    if found:
        return False, f"production lines the run added use a legacy component: {', '.join(found)}"
    return True, f"no production line the run added uses {', '.join(ctx.spec['legacy'])} ({len(changes)} files changed)"
