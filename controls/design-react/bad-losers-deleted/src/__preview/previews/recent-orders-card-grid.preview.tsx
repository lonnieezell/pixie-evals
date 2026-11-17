import { OrderCard } from "./recent-orders-card-grid/OrderCard";
import { makeOrders } from "@/factories";

const five = makeOrders(5);

export const states = {
  empty: () => <p>No orders yet.</p>,
  single: () => <OrderCard order={five[0]} />,
  typical: () => <>{five.map((order) => <OrderCard key={order.id} order={order} />)}</>,
  overflow: () => <>{five.map((order) => <OrderCard key={order.id} order={order} />)}</>,
  error: () => <p role="alert">We couldn't load recent orders.</p>,
  loading: () => <p role="status">Loading recent orders…</p>,
};
