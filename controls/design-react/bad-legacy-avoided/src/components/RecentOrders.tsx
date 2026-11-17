import { PrimaryButton } from "@/components/PrimaryButton";
import { Button } from "@/components/ui/button";
import type { Order } from "@/factories";

export interface RecentOrdersProps {
  orders: Order[];
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
}

const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

export function RecentOrders({ orders, loading = false, error = null, onRetry }: RecentOrdersProps) {
  return (
    <section aria-labelledby="recent-orders-title" className="rounded-card border border-border bg-surface p-6">
      <h2 id="recent-orders-title" className="text-lg font-semibold">
        Recent orders
      </h2>
      {loading ? (
        <p role="status">Loading recent orders…</p>
      ) : error ? (
        <div role="alert">
          <p>{error}</p>
          <Button variant="outline" size="sm" onClick={onRetry}>
            Try again
          </Button>
        </div>
      ) : orders.length === 0 ? (
        <div>
          <p>No orders yet.</p>
          <PrimaryButton>New order</PrimaryButton>
        </div>
      ) : (
        <ul>
          {orders.map((order) => (
            <li key={order.id} title={order.customer}>
              {order.number} {order.customer} {money.format(order.total)}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
