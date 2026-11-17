"""Grade one run: every grader of the case, in order, against the repo the run left behind."""
from .checks import CHECKS, Context


def grade(case, repo, pixie):
    """One result per grader, in skill-creator's grading.json expectation shape plus the check id."""
    ctx = Context(repo, case.spec, pixie)
    results = []
    for check_id, text in case.graders:
        if check_id not in CHECKS:
            raise ValueError(f"{case.name}: no check named {check_id!r} (have {', '.join(sorted(CHECKS))})")
        try:
            passed, evidence = CHECKS[check_id](ctx)
        except (OSError, KeyError, ValueError) as error:
            passed, evidence = False, f"grader error: {error!r}"
        results.append({"check": check_id, "text": text, "passed": bool(passed), "evidence": evidence})
    return results
