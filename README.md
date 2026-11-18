# pixie-evals

Evals for [Pixie](../pixie)'s design skills, kept out of the Pixie repo so they never ship with the plugin. Each eval runs a Pixie skill with `claude -p` against a small fixture app, then grades what the skill left behind with scripted, deterministic pass/fail checks. A model never decides whether a grader passes. The only model opinions are a [comparison](#compare-two-pixie-versions)'s judgements, which are a tiebreaker and never pass/fail.

This repo lives at [lonnieezell/pixie-evals](https://github.com/lonnieezell/pixie-evals). [GLOSSARY.md](GLOSSARY.md) defines its terms.

## Requirements

- Python 3.11+ (standard library only)
- Node 20+ and npm
- PHP 8.3+ with `pdo_sqlite` and `sqlite3`, and Composer
- The `claude` CLI, signed in
- For `critique-*` and `design-*` cases: Pixie's Playwright cache, installed the way `/pixie:design-setup` installs it:

  ```bash
  npm install --prefix ~/.cache/pixie/playwright --save-exact playwright@1.65.1 axe-core@4.14.1
  PLAYWRIGHT_BROWSERS_PATH=~/.cache/pixie/playwright/browsers \
    ~/.cache/pixie/playwright/node_modules/.bin/playwright install chromium
  ```

## Run the evals

```bash
./run-evals --pixie ../pixie                          # every case
./run-evals --pixie ../pixie --case setup-react       # some cases (repeat --case)
./run-evals --pixie ../pixie --grade-only results/iteration-3   # grade an earlier run again
```

`--pixie` is the path to any local Pixie checkout, such as a branch's worktree. The runner prints pass/fail for each task and each grader, and exits 1 if anything failed. These are real, billed model runs. A setup case takes a few minutes, the critique case longer, and a design case longest: it explores, critiques and builds a design, with a 90-minute timeout.

Each case runs like this:

1. Copy the case's fixture into `results/iteration-N/CASE/with_skill/outputs/repo/` and commit it. Only tracked and unignored files are copied, so no `vendor/` or `node_modules/` comes along. Then add the case's input files and commit them too, so the skill sees a clean git repo. An input inventory whose `Source commit` is all zeros gets the fixture's commit, so the skill finds it fresh instead of rescanning. The repo is tagged `eval-base`: graders read what the run changed against it.
2. For a case with `serve` in its `checks.json`, start the fixture with its `start.sh` on the port given there, and wait for it to answer. The ports (5273 for `critique-react-reports`, 5274, 8001 and 8081 for the design cases) don't clash with a fixture you're already running on its default port. The run fails early if the port is taken.
3. Run `claude -p "PROMPT" --plugin-dir PIXIE --setting-sources project,local` in that repo. Skipping user settings keeps an installed copy of Pixie, and your other plugins and hooks, out of the run. The prompt tells the skill it's unattended, and how to answer its questions. `AskUserQuestion` is disallowed. The transcript is saved as `outputs/transcript.jsonl`.
4. For a case with `screen` in its `checks.json` (the design cases), run axe while the app is still up, with `evalkit/axe.mjs` and Pixie's Playwright cache, on that screen and on every state of the winner's preview. The report is saved as `outputs/axe.json`.
5. Stop the server, and grade the repo.

Results follow skill-creator's workspace layout (`eval_metadata.json`, `with_skill/grading.json` with `text`, `passed` and `evidence` per grader, and `timing.json`), so skill-creator's viewer and benchmark scripts can read them.

## Compare two Pixie versions

```bash
./run-evals --pixie ../pixie --against ../pixie-main --runs 3                       # every case
./run-evals --pixie ../pixie --against ../pixie-main --case design-react --judge-model sonnet
./run-evals --pixie ../pixie --grade-only results/iteration-7                       # grade a comparison again
```

A comparison runs the same cases against two local Pixie checkouts: `--pixie` is `new_skill`, `--against` is `old_skill`. Check the old version out into its own worktree first (`git worktree add ../pixie-main main`); the runner takes paths, not git refs. Each case runs `--runs` times (default 1) against each checkout, one run after another, since each case serves its fixture on a fixed port.

Results follow skill-creator's benchmark layout: `results/iteration-N/CASE/{new_skill,old_skill}/run-K/{outputs/, grading.json, timing.json}`. `eval_metadata.json` records each checkout's path and commit.

The report shows, for each case and each grader, how many runs passed in each version (`2/3` against `3/3`), with a `*` where they differ. A figure from a single run is marked "indicative only": a model's runs vary, so one run can't tell a real change from noise. Use `--runs 3` or more before trusting a difference. The same data is written to `comparison.json` at the iteration's root.

A comparison exits 1 only when a run errored (a timeout, a crash, a server that didn't start). A failing grader doesn't change its exit code: the point is the difference, not the pass.

**Judgements.** For `design-*` cases, a model also gives its opinion, as a tiebreaker for when the graders can't settle which version is better. It reads only what the decision record left in `docs/design/decisions/`:

- **Screenshot preference:** run K of each version, compared on the `production-STATE-WIDTH.png` shots both captured. The judge is told the case's prompt and asked which version better serves its user. It's asked twice, with the versions in swapped order, and unless both answers pick the same version, the result is "no preference". The report tallies it over the runs.
- **Direction distinctness:** for each axis in a run's **Axes** table, whether its directions' screenshots visibly differ on it.

Judgements are saved in `CASE/judgement.json`, never in `grading.json`, so they can't change a grader's result, a pass count or the exit code. The judge runs as `claude -p` with `--judge-model` (default `opus`), no settings, no MCP servers, none of your plugins, and `Read` as its only tool, in a temporary folder holding only copies of the screenshots and the axes table. Its answer must be a fixed JSON shape that cites only screenshots in that folder. If the judge fails, times out or answers anything else, that judgement is "not judged" with the reason, and the rest of the comparison is still reported.

**Cost.** A comparison is two full eval runs per `--runs`: `--runs 3` on every case is six of them, and a design case is the longest run there is. Each design case then adds four judge calls per run (two for the preference, one distinctness check per version). `--grade-only` on a comparison grades every run again, each against the checkout it ran with, and rebuilds `comparison.json`. It keeps the saved judgements and never calls the judge, so it costs nothing.

## Cases

Cases live in `evals/`, in skill-creator's case-folder format: `prompt.md`, `case.yaml`, `graders/NN-CHECK-ID.md`, and an optional `place-files.sh` with `files/`. Each grader file's name says which scripted check runs it (`03-legacy-marked-legacy.md` runs `legacy-marked-legacy` in `evalkit/checks.py`). Its body states the assertion in words, so skill-creator and `claude plugin eval` can read it too. `checks.json` holds what the checks need: the fixture, and the expected answers. It lives in the case folder, never in the fixture, so the model never sees it.

| Case | Skill | Graders |
|---|---|---|
| `setup-react`, `setup-laravel`, `setup-ci4` | `/pixie:design-setup` | inventory written, stack detected, legacy component marked legacy, its replacement marked preferred, repeated pattern mined |
| `critique-react-reports` | `/pixie:design-critique` | report written, every axe violation reported, every raw colour reported, every finding cites a rubric item, a saved screenshot and its state |
| `design-react`, `design-laravel`, `design-ci4` | `/pixie:design` | decision record written, losing directions deleted, a preferred component reused (and each new component's reason recorded), no legacy component used, one test per state of the winner's matrix, the test suite passes, the preview harness gated out of production, no raw values, and no axe violations on the screen or the winner's preview |

The design cases all ask for the same thing, "a recent-orders section for the dashboard", so results compare across stacks. Each starts from a correct inventory (`files/docs/agents/design-system.md`), so a `/design-setup` mistake can't fail them. The prompt approves the first brief, picks the first direction and installs the permanent preview harness, so there's a harness to grade. The code graders read only the lines the run added, under the case's `source` folders, leaving out previews and tests.

## Fixtures

Each fixture has the same traps:

- **Legacy trap:** a legacy component marked `@deprecated` next to its preferred replacement. The legacy one is used in more views, so ranking by usage gets it wrong.
- **Mined pattern:** a stat card repeated 5 times across 2 views, and never extracted into a component.
- **Factories** for seed data.

| Fixture | Stack | Legacy → preferred | Start (one command) | URL |
|---|---|---|---|---|
| `fixtures/react-shadcn` | React 19, Vite, Tailwind 4, shadcn-style `cva` button | `PrimaryButton` → `ui/button` | `fixtures/react-shadcn/start.sh` | http://localhost:5173 |
| `fixtures/laravel-bootstrap` | Laravel 13, Blade, Bootstrap 5.3 (SCSS) | `@include('partials.alert')` → `<x-alert>` | `fixtures/laravel-bootstrap/start.sh` | http://localhost:8000 |
| `fixtures/ci4` | CodeIgniter 4.7, PHP views, CSS custom properties | `view('partials/alert')` → `view_cell('AlertCell')` | `fixtures/ci4/start.sh` | http://localhost:8080 |

Each `start.sh` installs dependencies, builds, seeds a SQLite database from the factories where the app has one, and serves the app. Set `PORT` to serve on another port.

Each fixture's test suite passes from a clean checkout once its dependencies are installed. The `tests-pass` grader runs it: `npm test` (Vitest and Testing Library) in `react-shadcn`, `php artisan test` in `laravel-bootstrap`, and `vendor/bin/phpunit` in `ci4`.

**The broken screen.** `/reports` in the React fixture is broken on purpose, as the critique graders' negative control. It has 4 axe violations (`image-alt`, `label`, `button-name`, `color-contrast`) and 3 raw colours in `src/pages/Reports.tsx` (`text-[#c4c4c4]`, `bg-[#ff00aa]`, `#b0b0b0`). A critique that leaves any of them unreported fails.

## Testing the graders

`controls/CASE/VARIANT/` holds hand-made skill outputs. Each is laid over the case's repo, built the way a real run builds it, so the control reads as the run's changes, and then graded. `good` must pass every grader. `bad-CHECK` is laid over `good`, so it holds only its mistake, and it must fail that check: for example, `controls/setup-react/bad-legacy-marked-legacy` is an inventory that falls for the legacy trap. A control's `_outputs/` folder stands in for what the runner saves next to the repo, such as `axe.json`.

```bash
python3 -m unittest discover -s tests -t .
```

`PIXIE=/path/to/pixie` points the tests at another checkout. The critique graders read Pixie's rubric from it. The `tests-pass` and `harness-gated` graders run the fixture's own tools, so their controls need each fixture's dependencies and `.env`: run each fixture's `start.sh` once first. Without them, those controls are skipped. The suite takes about 30 seconds.

## Adding a case

1. Make `evals/NAME/` with `prompt.md`, `case.yaml` and `checks.json` (`fixture`, plus whatever its checks read).
2. Add `graders/NN-CHECK-ID.md` for each check. A new check is a function decorated with `@check` in `evalkit/checks.py`.
3. Add `controls/NAME/good/`, plus a `bad-CHECK/` for each mistake a grader must catch, and run the tests.
