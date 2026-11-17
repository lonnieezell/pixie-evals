import { AppLayout } from "@/components/layouts/AppLayout";
import { Button } from "@/components/ui/button";
import { makeOrders } from "@/factories";

const orders = makeOrders(12);
const revenue = orders.reduce((sum, o) => sum + o.total, 0);

export function Dashboard() {
  return (
    <AppLayout title="Dashboard">
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-card border border-border bg-surface p-6">
          <p className="text-sm text-muted">Revenue</p>
          <p className="mt-1 text-2xl font-semibold">${revenue.toFixed(2)}</p>
        </div>
        <div className="rounded-card border border-border bg-surface p-6">
          <p className="text-sm text-muted">Orders</p>
          <p className="mt-1 text-2xl font-semibold">{orders.length}</p>
        </div>
        <div className="rounded-card border border-border bg-surface p-6">
          <p className="text-sm text-muted">Refunds</p>
          <p className="mt-1 text-2xl font-semibold">{orders.filter((o) => o.status === "refunded").length}</p>
        </div>
      </div>
      <div className="mt-6">
        <Button>New order</Button>
      </div>
    </AppLayout>
  );
}
