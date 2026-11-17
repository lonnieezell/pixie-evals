import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { Customers } from "@/pages/Customers";
import { Dashboard } from "@/pages/Dashboard";
import { Orders } from "@/pages/Orders";
import { Reports } from "@/pages/Reports";
import { Settings } from "@/pages/Settings";

const ROUTES: Record<string, () => React.JSX.Element> = {
  "/": Dashboard,
  "/orders": Orders,
  "/customers": Customers,
  "/reports": Reports,
  "/settings": Settings,
};

const root = createRoot(document.getElementById("root")!);

// Pixie's preview harness, for /design-critique. Vite drops this branch from production builds.
if (import.meta.env.DEV && location.pathname.startsWith("/__preview/")) {
  import("./__preview/PreviewPage").then(({ default: PreviewPage }) => {
    const slug = location.pathname.slice("/__preview/".length).replace(/\/$/, "");
    const state = new URLSearchParams(location.search).get("state") ?? "typical";
    root.render(
      <StrictMode>
        <PreviewPage slug={slug} state={state} />
      </StrictMode>,
    );
  });
} else {
  const Page = ROUTES[window.location.pathname.replace(/\/$/, "") || "/"] ?? Dashboard;
  root.render(
    <StrictMode>
      <Page />
    </StrictMode>,
  );
}
