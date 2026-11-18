"""A comparison: the same cases run against two Pixie checkouts, `new_skill` (--pixie) and `old_skill` (--against).
Reads a comparison iteration, CASE/{new_skill,old_skill}/run-K/grading.json and CASE/judgement.json, into
comparison.json and a printed report. Judgements sit apart from the graders: they never change a pass count, and
only run errors fail a comparison."""
import json

CONFIGS = ("new_skill", "old_skill")
JUDGEMENT = "judgement.json"
ERROR = "error.txt"  # a run's error, saved so --grade-only still reports it
PREFERENCES = ("new preferred", "old preferred", "no preference", "not judged")


def run_dirs(config_dir):
    """The run-K folders of one config, in run order."""
    found = [p for p in config_dir.glob("run-*") if p.name[len("run-"):].isdigit()]
    return sorted(found, key=lambda p: int(p.name[len("run-"):]))


def rate(counts):
    """A config's pass rate for one grader, or None when it has no graded runs."""
    return counts["passed"] / counts["runs"] if counts["runs"] else None


def compare(iteration, cases):
    """comparison.json's data: for each case with results, each grader's pass count in both configs, and the
    case's judgements, if it has any."""
    out = []
    for case in cases:
        case_dir = iteration / case.name
        if not any((case_dir / config).is_dir() for config in CONFIGS):
            continue
        gradings = {config: [json.loads((run / "grading.json").read_text()) for run in run_dirs(case_dir / config)
                             if (run / "grading.json").is_file()] for config in CONFIGS}
        graders = []
        for check, text in case.graders:
            row = {"check": check, "text": text}
            for config, runs in gradings.items():
                passed = sum(any(e["text"] == text and e["passed"] for e in g["expectations"]) for g in runs)
                row[config] = {"passed": passed, "runs": len(runs), "indicative_only": len(runs) == 1}
            row["differs"] = rate(row["new_skill"]) != rate(row["old_skill"])
            graders.append(row)
        errors = [f"{config} {run.name}: {(run / ERROR).read_text().strip()}" for config in CONFIGS
                  for run in run_dirs(case_dir / config) if (run / ERROR).is_file()]
        judgement = case_dir / JUDGEMENT
        out.append({"case": case.name, "graders": graders, "errors": errors,
                    "judgements": json.loads(judgement.read_text()) if judgement.is_file() else None})
    return {"cases": out}


def figure(counts):
    text = f"{counts['passed']}/{counts['runs']}"
    return f"{text} (indicative only)" if counts["indicative_only"] else text


def distinctness_lines(run):
    """Each axis with both versions' verdicts side by side, then any version that wasn't judged."""
    found = run.get("distinctness", {})
    verdicts = {}
    for config, result in found.items():
        for axis in result.get("axes", []):
            verdict = "differ" if axis["differs"] else "don't differ"
            verdicts.setdefault(axis["axis"], []).append(f"{config[:3]} {verdict} ({axis['reason']})")
    lines = [f"  run-{run['run']} directions on {axis}: {' | '.join(v)}" for axis, v in verdicts.items()]
    lines += [f"  run-{run['run']} {config} direction distinctness: {result['result']}"
              for config, result in found.items() if "axes" not in result]
    return lines


def report(data):
    errors = [f"{case['case']} {error}" for case in data["cases"] for error in case["errors"]]
    print("\nComparison: new_skill (--pixie) against old_skill (--against). * marks a grader whose pass rate differs.")
    for case in data["cases"]:
        print(f"\n{case['case']}")
        for g in case["graders"]:
            mark = "*" if g["differs"] else " "
            print(f"  {mark} new {figure(g['new_skill']):<22} old {figure(g['old_skill']):<22} {g['check']}")
    judged = [case for case in data["cases"] if case["judgements"]]
    if judged:
        print("\nJudgements (a model's tiebreaker, never pass/fail)")
    for case in judged:
        runs = case["judgements"]["runs"]
        results = [r["preference"]["result"] for r in runs]
        tally = {p: results.count(p) for p in PREFERENCES[:-1]}
        tally["not judged"] = len(results) - sum(tally.values())
        print(f"\n{case['case']}\n  screenshot preference: " + ", ".join(f"{p} {n}" for p, n in tally.items()))
        for r in runs:
            if not r["preference"]["result"].endswith("preferred"):
                print(f"    run-{r['run']}: {r['preference']['result']}")
            for line in distinctness_lines(r):
                print(line)
    for error in errors:
        print(f"\nRUN ERROR  {error}")
    print(f"\n{len(errors)} run errors" if errors else "\nEvery run completed")
    return not errors


def write_and_report(iteration, cases):
    """Write comparison.json at the iteration's root and print the report. True when no run had an error."""
    data = compare(iteration, cases)
    (iteration / "comparison.json").write_text(json.dumps(data, indent=2) + "\n")
    return report(data)
