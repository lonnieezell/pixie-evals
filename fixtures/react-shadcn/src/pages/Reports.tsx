import { AppLayout } from "@/components/layouts/AppLayout";
import { Button } from "@/components/ui/button";
import { makeOrders } from "@/factories";

const orders = makeOrders(5);

export function Reports() {
  return (
    <AppLayout title="Reports">
      <div className="mb-6 flex items-center gap-4">
        <img src="/chart.svg" width="48" height="48" />
        <p className="text-[#c4c4c4]">Sales for the last 30 days, by order.</p>
      </div>
      <div className="mb-6 flex items-center gap-2">
        <span className="text-sm">Filter</span>
        <input type="search" className="rounded-md border border-border px-3 py-2" />
        <button className="h-9 w-9 rounded-md bg-[#ff00aa]">
          <svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">
            <path d="M2 4h12M4 8h8M6 12h4" stroke="white" strokeWidth="2" />
          </svg>
        </button>
      </div>
      <ul className="space-y-2">
        {orders.map((o) => (
          <li key={o.id} className="flex justify-between rounded-md bg-surface p-3" style={{ color: "#b0b0b0" }}>
            <span>{o.number}</span>
            <span>${o.total.toFixed(2)}</span>
          </li>
        ))}
      </ul>
      <div className="mt-6">
        <Button>Download report</Button>
      </div>
    </AppLayout>
  );
}
