# pixie-evals

Evals for [Pixie](../pixie)'s design skills, kept out of the Pixie repo so they never ship with the plugin. Each eval runs a Pixie skill with `claude -p` against a small fixture app, then grades what the skill left behind with scripted, deterministic pass/fail checks. No LLM judges any result.

This repo is local only: it has no remote.

## Requirements

- Python 3.11+ (standard library only)
- Node 20+ and npm
- PHP 8.3+ with `pdo_sqlite` and `sqlite3`, and Composer
- The `claude` CLI, signed in
- For `critique-*` cases: Pixie's Playwright cache, installed the way `/pixie:design-setup` installs it:

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

`--pixie` is the path to any local Pixie checkout, such as a branch's worktree. The runner prints pass/fail for each task and each grader, and exits 1 if anything failed. These are real, billed model runs. A setup case takes a few minutes, and the critique case takes longer.

Each case runs like this:

1. Copy the case's fixture into `results/iteration-N/CASE/with_skill/outputs/repo/`. Only tracked and unignored files are copied, so no `vendor/` or `node_modules/` comes along. Then add the case's input files and commit, so the skill sees a clean git repo.
2. For a case with `serve` in its `checks.json`, start the fixture with its `start.sh` on the port given there, and wait for it to answer. `critique-react-reports` serves on port 5273, so it doesn't clash with a Vite app you're already running on 5173. The run fails early if the port is taken.
3. Run `claude -p "PROMPT" --plugin-dir PIXIE --setting-sources project,local` in that repo. Skipping user settings keeps an installed copy of Pixie, and your other plugins and hooks, out of the run. The prompt tells the skill it's unattended, and how to answer its questions. `AskUserQuestion` is disallowed. The transcript is saved as `outputs/transcript.jsonl`.
4. Stop the server, and grade the repo.

Results follow skill-creator's workspace layout (`eval_metadata.json`, `with_skill/grading.json` with `text`, `passed` and `evidence` per grader, and `timing.json`), so skill-creator's viewer and benchmark scripts can read them.

## Cases

Cases live in `evals/`, in skill-creator's case-folder format: `prompt.md`, `case.yaml`, `graders/NN-CHECK-ID.md`, and an optional `place-files.sh` with `files/`. Each grader file's name says which scripted check runs it (`03-legacy-marked-legacy.md` runs `legacy-marked-legacy` in `evalkit/checks.py`). Its body states the assertion in words, so skill-creator and `claude plugin eval` can read it too. `checks.json` holds what the checks need: the fixture, and the expected answers. It lives in the case folder, never in the fixture, so the model never sees it.

| Case | Skill | Graders |
|---|---|---|
| `setup-react`, `setup-laravel`, `setup-ci4` | `/pixie:design-setup` | inventory written, stack detected, legacy component marked legacy, its replacement marked preferred, repeated pattern mined |
| `critique-react-reports` | `/pixie:design-critique` | report written, every axe violation reported, every raw colour reported, every finding cites a rubric item, a saved screenshot and its state |

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

**The broken screen.** `/reports` in the React fixture is broken on purpose, as the critique graders' negative control. It has 4 axe violations (`image-alt`, `label`, `button-name`, `color-contrast`) and 3 raw colours in `src/pages/Reports.tsx` (`text-[#c4c4c4]`, `bg-[#ff00aa]`, `#b0b0b0`). A critique that leaves any of them unreported fails.

## Testing the graders

`controls/CASE/VARIANT/` holds hand-made skill outputs, which are laid over the case's fixture and graded. `good` must pass every grader. `bad-CHECK` must fail that check: for example, `controls/setup-react/bad-legacy-marked-legacy` is an inventory that falls for the legacy trap.

```bash
python3 -m unittest discover -s tests -t .
```

`PIXIE=/path/to/pixie` points the tests at another checkout. The critique graders read Pixie's rubric from it.

## Adding a case

1. Make `evals/NAME/` with `prompt.md`, `case.yaml` and `checks.json` (`fixture`, plus whatever its checks read).
2. Add `graders/NN-CHECK-ID.md` for each check. A new check is a function decorated with `@check` in `evalkit/checks.py`.
3. Add `controls/NAME/good/`, plus a `bad-CHECK/` for each mistake a grader must catch, and run the tests.
