import { RecentOrders } from "@/components/RecentOrders";
import { makeOrder, makeOrders } from "@/factories";

// Built once, so a re-render shows the same data. The same data as RecentOrders.test.tsx.
const one = makeOrders(1);
const five = makeOrders(5);
const long = [makeOrder(0, { customer: "Maximiliana Featherstonehaugh-Wolfeschlegel" }), ...makeOrders(4)];

export const states = {
  empty: () => <RecentOrders orders={[]} />,
  single: () => <RecentOrders orders={one} />,
  typical: () => <RecentOrders orders={five} />,
  overflow: () => <RecentOrders orders={long} />,
  error: () => <RecentOrders orders={[]} error="We couldn't load recent orders." />,
  loading: () => <RecentOrders orders={[]} loading />,
};
