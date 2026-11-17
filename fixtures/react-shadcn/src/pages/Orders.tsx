import { AppLayout } from "@/components/layouts/AppLayout";
import { PrimaryButton } from "@/components/PrimaryButton";
import { makeOrders } from "@/factories";

const orders = makeOrders(8);

export function Orders() {
  return (
    <AppLayout title="Orders">
      <div className="mb-6 grid gap-4 sm:grid-cols-2">
        <div className="rounded-card border border-border bg-surface p-6">
          <p className="text-sm text-muted">Pending</p>
          <p className="mt-1 text-2xl font-semibold">{orders.filter((o) => o.status === "pending").length}</p>
        </div>
        <div className="rounded-card border border-border bg-surface p-6">
          <p className="text-sm text-muted">Paid</p>
          <p className="mt-1 text-2xl font-semibold">{orders.filter((o) => o.status === "paid").length}</p>
        </div>
      </div>
      <table className="w-full border-collapse bg-surface text-sm">
        <thead>
          <tr className="border-b border-border text-left">
            <th className="p-3">Order</th>
            <th className="p-3">Customer</th>
            <th className="p-3">Status</th>
            <th className="p-3 text-right">Total</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id} className="border-b border-border">
              <td className="p-3">{o.number}</td>
              <td className="p-3">{o.customer}</td>
              <td className="p-3">{o.status}</td>
              <td className="p-3 text-right">${o.total.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-6">
        <PrimaryButton>Export orders</PrimaryButton>
      </div>
    </AppLayout>
  );
}
