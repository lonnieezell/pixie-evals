"""Run each case with `claude -p` against a local Pixie checkout, then grade it. Results use skill-creator's
workspace layout: results/iteration-N/CASE/{eval_metadata.json, with_skill/{outputs/, grading.json, timing.json}}."""
import json
import os
import shutil
import signal
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from .checks import AXE, Context, axe_targets
from .grade import grade
from .workdir import prepare

TOOLS = "Bash,Read,Write,Edit,Glob,Grep,Agent,Skill,TodoWrite"
SERVE_TIMEOUT = 900
AXE_TIMEOUT = 600
AXE_SCRIPT = Path(__file__).with_name("axe.mjs")
PLAYWRIGHT = Path.home() / ".cache" / "pixie" / "playwright"


def check_pixie(pixie):
    if not (pixie / ".claude-plugin" / "plugin.json").is_file() or not (pixie / "skills" / "design-setup").is_dir():
        raise SystemExit(f"{pixie} isn't a Pixie checkout (no .claude-plugin/plugin.json or skills/design-setup)")
    if not shutil.which("claude"):
        raise SystemExit("`claude` isn't on PATH")


def playwright_problem():
    """Why Pixie's Playwright cache can't capture yet, or None. Same test as /design-setup's offer 2."""
    version = lambda path: json.loads(path.read_text())["version"] if path.is_file() else None
    if version(PLAYWRIGHT / "node_modules/playwright/package.json") != "1.65.1":
        return "playwright 1.65.1 isn't installed"
    if version(PLAYWRIGHT / "node_modules/axe-core/package.json") != "4.14.1":
        return "axe-core 4.14.1 isn't installed"
    if not any((PLAYWRIGHT / "browsers").glob("chromium*")):
        return "Chromium isn't installed"
    return None


def next_iteration(results):
    results.mkdir(parents=True, exist_ok=True)
    taken = [int(p.name.split("-")[1]) for p in results.glob("iteration-*") if p.name.split("-")[1].isdigit()]
    path = results / f"iteration-{max(taken, default=0) + 1}"
    path.mkdir()
    return path


def port_in_use(port):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def serve(repo, spec, log):
    """Start the fixture with its start.sh and wait until its ready URL answers. Returns the process."""
    port = spec["port"]
    if port_in_use(port):
        raise RuntimeError(f"port {port} is already in use; stop whatever is serving it")
    process = subprocess.Popen(
        ["./start.sh"], cwd=repo, env={**os.environ, "PORT": str(port)},
        stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
    )
    deadline = time.monotonic() + SERVE_TIMEOUT
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"start.sh exited with {process.returncode}; see {log.name}")
        try:
            urllib.request.urlopen(spec["ready"], timeout=5)
            return process
        except (urllib.error.URLError, OSError):
            time.sleep(2)
    stop(process)
    raise RuntimeError(f"{spec['ready']} didn't answer within {SERVE_TIMEOUT}s; see {log.name}")


def stop(process):
    if process and process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)


def run_claude(case, repo, pixie, transcript):
    """`claude -p` with only this Pixie checkout as a plugin: user settings (and the plugins they enable) are left
    out, so an installed copy of Pixie can't stand in for the one under test. Returns an error note, or None."""
    command = [
        "claude", "-p", case.prompt, "--plugin-dir", str(pixie), "--setting-sources", "project,local",
        "--output-format", "stream-json", "--verbose", "--no-session-persistence",
        "--permission-mode", "acceptEdits", "--allowedTools", TOOLS, "--disallowedTools", "AskUserQuestion",
    ]
    with transcript.open("w") as out:
        try:
            result = subprocess.run(command, cwd=repo, stdout=out, stderr=subprocess.STDOUT, timeout=case.timeout)
        except subprocess.TimeoutExpired:
            return f"timed out after {case.timeout}s"
    return f"claude exited with {result.returncode}" if result.returncode else None


def check_axe(case, repo, pixie, outputs):
    """While the app is still up, run axe on the pages the production-axe-clean check covers, into
    outputs/axe.json. Returns an error note, or None."""
    targets = axe_targets(Context(repo, case.spec, pixie))
    origin = f"http://localhost:{case.spec['serve']['port']}"
    command = ["node", str(AXE_SCRIPT), str(outputs / AXE), origin, *(f"{label}={path}" for label, path in targets)]
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=AXE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return f"axe timed out after {AXE_TIMEOUT}s"
    return f"axe exited with {done.returncode}: {done.stderr.strip()[-300:]}" if done.returncode else None


def write_grading(run_dir, results, timing):
    passed = sum(r["passed"] for r in results)
    grading = {
        "expectations": [{k: r[k] for k in ("text", "passed", "evidence")} for r in results],
        "summary": {"passed": passed, "failed": len(results) - passed, "total": len(results),
                    "pass_rate": round(passed / len(results), 2) if results else 0.0},
        "timing": timing,
    }
    (run_dir / "grading.json").write_text(json.dumps(grading, indent=2) + "\n")


def run_case(case, index, iteration, pixie, fixtures):
    case_dir = iteration / case.name
    run_dir = case_dir / "with_skill"
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True)
    (case_dir / "eval_metadata.json").write_text(json.dumps({
        "eval_id": index, "eval_name": case.name, "prompt": case.prompt,
        "assertions": [text for _, text in case.graders],
    }, indent=2) + "\n")
    repo = outputs / "repo"
    prepare(case, fixtures, repo)

    error, server, started = None, None, time.monotonic()
    try:
        if case.spec.get("serve"):
            if problem := playwright_problem():
                raise RuntimeError(f"{problem} in {PLAYWRIGHT}; install it as the README says")
            with (outputs / "server.log").open("w") as log:
                server = serve(repo, case.spec["serve"], log)
        error = run_claude(case, repo, pixie, outputs / "transcript.jsonl")
        if case.spec.get("screen") and server:
            error = "; ".join(filter(None, [error, check_axe(case, repo, pixie, outputs)])) or None
    except RuntimeError as e:
        error = str(e)
    finally:
        stop(server)
    executor = time.monotonic() - started

    started = time.monotonic()
    results = grade(case, repo, pixie, outputs)
    timing = {"executor_duration_seconds": round(executor, 1),
              "grader_duration_seconds": round(time.monotonic() - started, 1)}
    timing["total_duration_seconds"] = round(sum(timing.values()), 1)
    write_grading(run_dir, results, timing)
    (run_dir / "timing.json").write_text(json.dumps(timing, indent=2) + "\n")
    return results, error


def regrade(iteration, cases, pixie):
    """Grade an earlier iteration's repos again, for when a grader changes."""
    out = []
    for case in cases:
        run_dir = iteration / case.name / "with_skill"
        if not (run_dir / "outputs" / "repo").is_dir():
            continue
        results = grade(case, run_dir / "outputs" / "repo", pixie, run_dir / "outputs")
        timing = json.loads((run_dir / "timing.json").read_text()) if (run_dir / "timing.json").is_file() else {}
        write_grading(run_dir, results, timing)
        out.append((case, results, None))
    return out


def report(rows):
    """Print pass/fail per case and per grader. Returns True when everything passed."""
    total = passed = 0
    for case, results, error in rows:
        ok = all(r["passed"] for r in results) and not error
        print(f"\n{'PASS' if ok else 'FAIL'}  {case.name}" + (f"  ({error})" if error else ""))
        for r in results:
            print(f"  {'pass' if r['passed'] else 'FAIL'}  {r['check']:<28} {r['evidence']}")
        total += len(results)
        passed += sum(r["passed"] for r in results)
    tasks_ok = sum(all(r["passed"] for r in results) and not error for _, results, error in rows)
    print(f"\n{tasks_ok}/{len(rows)} tasks passed, {passed}/{total} graders passed")
    return tasks_ok == len(rows)
