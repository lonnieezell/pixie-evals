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
      <div className="flex items-center justify-between gap-4">
        <h2 id="recent-orders-title" className="text-lg font-semibold">
          Recent orders
        </h2>
        <a href="/orders" className="text-sm text-primary hover:underline">
          View all orders
        </a>
      </div>
      {loading ? (
        <p role="status" className="mt-4 text-sm text-muted">
          Loading recent orders…
        </p>
      ) : error ? (
        <div role="alert" className="mt-4 flex items-center justify-between gap-4 text-sm text-danger">
          <p>{error}</p>
          <Button variant="outline" size="sm" onClick={onRetry}>
            Try again
          </Button>
        </div>
      ) : orders.length === 0 ? (
        <div className="mt-4 text-sm text-muted">
          <p>No orders yet.</p>
          <Button className="mt-3" size="sm">
            New order
          </Button>
        </div>
      ) : (
        <ul className="mt-4 divide-y divide-border">
          {orders.map((order) => (
            <li key={order.id} className="flex items-center justify-between gap-4 py-3 text-sm">
              <span className="font-medium">{order.number}</span>
              <span className="min-w-0 flex-1 truncate text-muted" title={order.customer}>
                {order.customer}
              </span>
              <span className="capitalize text-muted">{order.status}</span>
              <span className="font-semibold">{money.format(order.total)}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
