import type { ReactElement } from "react";

export const previews: Record<string, () => Promise<{ states: Record<string, () => ReactElement> }>> = {
  "recent-orders-compact-list": () => import("./previews/recent-orders-compact-list.preview"),
};
