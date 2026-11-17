"""Edge cases of the parsing the /design graders rely on, which the controls don't reach."""
import unittest

from evalkit.checks import added_lines, preview_states

DIFF = """\
diff --git a/src/a.ts b/src/a.ts
index 1111111..2222222 100644
--- a/src/a.ts
+++ b/src/a.ts
@@ -1,0 +2,2 @@
++ counter;
+const after = 1;
diff --git a/src/b.ts b/src/b.ts
new file mode 100644
--- /dev/null
+++ b/src/b.ts
@@ -0,0 +1 @@
+export const b = 2;
diff --git a/src/gone.ts b/src/gone.ts
deleted file mode 100644
--- a/src/gone.ts
+++ /dev/null
@@ -1 +0,0 @@
-export const gone = 3;
"""

TSX = """\
export const states = {
  empty: () => <List orders={[]} />,
  error: () => <List orders={[]} handlers={{
    onRetry: () => retry(),
  }} />,
  "read-only": () => <List orders={one} readOnly />,
};
export const interactions = [{ name: "menu open", from: "typical", steps: [] }];
"""

PHP = """\
<?php
$list = static fn (array $orders) => view_cell('ListCell', ['orders' => $orders]);
return [
    'states' => [
        'empty'    => static fn () => $list([]),
        'loading'  => fn () => $list([], ['onDone' => fn () => null]),
    ],
    'interactions' => [['name' => 'menu open', 'from' => 'typical', 'steps' => []]],
];
"""


class AddedLinesTest(unittest.TestCase):
    def test_added_lines(self):
        changes = added_lines(DIFF)
        cases = {
            "an added line starting with ++ stays an added line": ("src/a.ts", (False, ["+ counter;", "const after = 1;"])),
            "a new file is marked new": ("src/b.ts", (True, ["export const b = 2;"])),
        }
        for name, (path, expected) in cases.items():
            with self.subTest(name):
                self.assertEqual(changes[path], expected)
        self.assertNotIn("src/gone.ts", changes, "a deleted file adds nothing")


class PreviewStatesTest(unittest.TestCase):
    def test_preview_states(self):
        cases = {
            "tsx": (TSX, (["empty", "error", "read-only"], ["menu open"])),
            "php": (PHP, (["empty", "loading"], ["menu open"])),
            "no states block": ("const x = { empty: () => 1 };", ([], [])),
        }
        for name, (text, expected) in cases.items():
            with self.subTest(name):
                self.assertEqual(preview_states(text), expected)


if __name__ == "__main__":
    unittest.main()
