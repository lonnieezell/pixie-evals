# Glossary

**Case**: one task an eval gives a Pixie skill: a prompt, the fixture it runs against, any input files, and the graders that score the result. `design-react` is a case.

**Fixture**: a small app with known traps, which a case's run works in. A run gets its own copy, so the fixture itself never changes.

**Grader**: one pass/fail statement about what a run left behind, scored by a script, never by a model. Each grader says why it passed or failed.

**Comparison**: the same cases run against two Pixie versions, so each grader's results can be set side by side.

**MWG variant**: a comparison of one Pixie version run with and without Modern Web Guidance installed, to measure whether MWG helps.

**Judgement**: a model's assessment of results in a comparison: either a preference between the two Pixie versions, or an observation about one version's run. It is never pass/fail and never a grader: it only breaks ties a person can't settle from the graders.

**Control**: a hand-made run result that proves graders work. A **clean control** (`good`) is a correct result, and must pass every grader of its case. A **mistake control** (`bad-…`) is the clean one with a single planted mistake, and must fail the grader that's there to catch it.

**Direction**: one of the distinct designs `/pixie:design` explores for the same thing, placed at a named position on each design axis.

**Winner**: the direction picked from a design run, and built into production code. The others are the **losing directions**, and a run must delete them.

**Reuse rate**: how far new UI is built from the components the inventory marks preferred. Graded as a floor, not a ratio: the run uses at least one preferred component, and gives a reason for every new component it makes.
