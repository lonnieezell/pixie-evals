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

const Page = ROUTES[window.location.pathname.replace(/\/$/, "") || "/"] ?? Dashboard;

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Page />
  </StrictMode>,
);
