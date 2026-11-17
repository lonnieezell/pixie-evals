<!-- Hand-made negative control: falls for the legacy trap, ranking PrimaryButton by its usage count. -->
# Design system

## Stack

- **Framework:** React 19 (Vite)
- **Styling:** Tailwind CSS 4

## Tokens

Source files: `src/index.css`

## Components

| Name | Path / import | Props and variants | When to use | Status |
|---|---|---|---|---|
| `PrimaryButton` | `@/components/PrimaryButton` (`src/components/PrimaryButton.tsx`) | `className`, button attributes | Every primary action | preferred (inferred: used in 3 pages, more than `Button`) |
| `Button` | `@/components/ui/button` (`src/components/ui/button.tsx`) | `variant`, `size` | Secondary actions | legacy (inferred: used in 2 pages) |

## Patterns

| Pattern | Canonical example | Occurrences | Extraction suggestion |
|---|---|---|---|
| Stat card | `src/pages/Dashboard.tsx:12` | 5 in 2 files | Extract a `StatCard` component |

## Annotations

## Rubric overrides

