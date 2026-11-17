import { type ReactNode, useEffect, useState } from "react";
import { previews } from "./registry";

const REQUIRED = ["empty", "single", "typical", "overflow", "error", "loading"];

const Problem = ({ children }: { children: ReactNode }) => (
  <p role="alert" data-pixie-preview-error="">
    {children}
  </p>
);

export default function PreviewPage({ slug, state }: { slug: string; state: string }) {
  const load = Object.hasOwn(previews, slug) ? previews[slug] : undefined;
  const [mod, setMod] = useState<Awaited<ReturnType<NonNullable<typeof load>>> | null>(null);
  const [failed, setFailed] = useState<string | null>(null);
  useEffect(() => {
    load?.().then(setMod, (e) => setFailed(String(e)));
  }, [load]);
  if (!load) return <Problem>No preview named {slug}</Problem>;
  if (failed) return <Problem>Preview {slug} failed to load: {failed}</Problem>;
  if (!mod) return null;
  const missing = REQUIRED.filter((s) => !mod.states[s]);
  if (missing.length) return <Problem>Preview {slug} is missing required states: {missing.join(", ")}</Problem>;
  const Render = Object.hasOwn(mod.states, state) ? mod.states[state] : undefined;
  if (!Render) return <Problem>Preview {slug} has no state {state}</Problem>;
  return (
    <div data-pixie-preview="">
      <Render />
    </div>
  );
}
