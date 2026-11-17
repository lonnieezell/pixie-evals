import type { Order } from "@/factories";

export interface RecentOrdersProps {
  orders: Order[];
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
}

const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });
const action = "rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground";

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
          <button type="button" className={action} onClick={onRetry}>
            Try again
          </button>
        </div>
      ) : orders.length === 0 ? (
        <div>
          <p>No orders yet.</p>
          <button type="button" className={action}>
            New order
          </button>
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
