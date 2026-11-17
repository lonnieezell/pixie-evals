# Design decision: the recent-orders section of the dashboard

- **Date:** 2026-11-18, commit 0000000
- **Chosen:** compact-list
- **Winner's preview:** `/__preview/recent-orders-compact-list` in `resources/previews/recent-orders-compact-list.php`
- **Captured with:** Playwright, widths 390 and 1280

## Frame

- **Who and what for:** the shop owner, checking which orders came in since they last looked
- **Data:** `Order` (number, total, status, user); 0 to 5 recent orders, long customer names
- **Neighbours:** `/orders`, the rest of the dashboard

## Axes

| Axis | Poles |
|---|---|
| Density | compact ↔ roomy |
| Emphasis | data first ↔ action first |

## Directions

### compact-list (chosen)

- **Position:** Density compact, Emphasis data first
- **Built from:** `<x-alert>`
- **New components:** `<x-recent-orders>`, because nothing catalogued lists orders with their status and total
- **Trade-off:** Scans five orders at a glance, but gives each order little room on a phone.
- **Gates:** axe 0, raw values 0
- **Critique:** 1 round. Remaining: none
- **Screenshots:** [typical, 1280](2026-11-18-recent-orders/compact-list-typical-1280.png), [typical, 390](2026-11-18-recent-orders/compact-list-typical-390.png)

### card-grid

- **Position:** Density roomy, Emphasis action first
- **Built from:** `<x-alert>`
- **New components:** `<x-order-card>`, because nothing catalogued shows one order as a card
- **Trade-off:** Each order gets its own actions, but only two fit above the fold.
- **Gates:** axe 0, raw values 0
- **Critique:** 1 round. Remaining: none
- **Screenshots:** [typical, 1280](2026-11-18-recent-orders/card-grid-typical-1280.png), [typical, 390](2026-11-18-recent-orders/card-grid-typical-390.png)

## Why compact-list

The first direction, picked unattended. It shows the most orders in the space the dashboard has.

## Production

- **Files:** `resources/views/components/recent-orders.blade.php`, `resources/views/dashboard.blade.php`, `routes/web.php`
- **Tests:** one per state, each red before its code was written:

  | State | Test | Red |
  |---|---|---|
  | empty | `RecentOrdersTest` `test_empty_shows_the_new_order_action` | `Unable to locate a class or view for component [recent-orders].` |

- **Gates:** axe 0, raw values 0
- **Drift from the approved direction:** none
- **Other findings:** none

## Not checked

Nothing.
