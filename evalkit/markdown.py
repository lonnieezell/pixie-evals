"""Just enough Markdown parsing to read Pixie's inventory and critique report."""
import re


def section(text, heading, level=2):
    """The body of the first heading named `heading` at `level` (`##` by default), up to the next heading at that
    level or higher, or None when the heading isn't there."""
    hashes = "#" * level
    match = re.search(rf"^{hashes} {re.escape(heading)}[ \t]*\n(.*?)(?=^#{{1,{level}}} |\Z)", text, re.M | re.S)
    return match.group(1) if match else None


def table_rows(text):
    """Each data row of the Markdown tables in `text`, as a list of cell strings. Header and divider rows are left
    out: the divider is recognised, and the row right above it is the header."""
    lines = [line.strip() for line in (text or "").splitlines()]
    rows = []
    for i, line in enumerate(lines):
        if not line.startswith("|") or DIVIDER.match(line):
            continue
        if i + 1 < len(lines) and DIVIDER.match(lines[i + 1]):
            continue
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


DIVIDER = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?$")
