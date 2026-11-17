import type { ReactElement } from "react";

export const previews: Record<string, () => Promise<{ states: Record<string, () => ReactElement> }>> = {
  "recent-orders-compact-list": () => import("./previews/recent-orders-compact-list.preview"),
  "recent-orders-card-grid": () => import("./previews/recent-orders-card-grid.preview"),
};
