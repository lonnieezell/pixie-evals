// Deterministic factories for seed and preview data. The same index always gives the same record.

export interface Customer {
  id: number;
  name: string;
  email: string;
  orders: number;
}

export interface Order {
  id: number;
  number: string;
  customer: string;
  total: number;
  status: "paid" | "pending" | "refunded";
}

const NAMES = ["Ada Lovelace", "Grace Hopper", "Alan Turing", "Katherine Johnson", "Linus Torvalds", "Barbara Liskov"];
const STATUSES: Order["status"][] = ["paid", "pending", "refunded"];

export function makeCustomer(i: number, overrides: Partial<Customer> = {}): Customer {
  const name = NAMES[i % NAMES.length];
  return {
    id: i + 1,
    name,
    email: `${name.toLowerCase().replace(/[^a-z]+/g, ".")}@example.com`,
    orders: (i * 7) % 13,
    ...overrides,
  };
}

export function makeOrder(i: number, overrides: Partial<Order> = {}): Order {
  return {
    id: i + 1,
    number: `#${1001 + i}`,
    customer: NAMES[(i * 5) % NAMES.length],
    total: Math.round(((i * 37.5) % 400) * 100 + 1999) / 100,
    status: STATUSES[i % STATUSES.length],
    ...overrides,
  };
}

export const makeCustomers = (n: number) => Array.from({ length: n }, (_, i) => makeCustomer(i));
export const makeOrders = (n: number) => Array.from({ length: n }, (_, i) => makeOrder(i));
