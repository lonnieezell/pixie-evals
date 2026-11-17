<!-- Hand-made negative control: misses the stat card repeated in Dashboard.tsx and Orders.tsx. -->
# Design system

## Stack

- **Framework:** React 19 (Vite)
- **Styling:** Tailwind CSS 4

## Tokens

Source files: `src/index.css`

## Components

| Name | Path / import | Props and variants | When to use | Status |
|---|---|---|---|---|
| `Button` | `@/components/ui/button` (`src/components/ui/button.tsx`) | `variant`, `size` | Every clickable action | preferred (inferred: shadcn) |
| `PrimaryButton` | `@/components/PrimaryButton` (`src/components/PrimaryButton.tsx`) | `className` | Don't use in new code | legacy (inferred: `@deprecated` comment) |

## Patterns

| Pattern | Canonical example | Occurrences | Extraction suggestion |
|---|---|---|---|
| Table cell: `td.p-3` | `src/pages/Orders.tsx:36` | 4 in 1 file | Extract a `Cell` component |

## Annotations

## Rubric overrides

