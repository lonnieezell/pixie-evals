import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, test } from "vitest";
import { RecentOrders } from "@/components/RecentOrders";
import { makeOrder, makeOrders } from "@/factories";

afterEach(cleanup);

test("empty: shows the new-order action when there are no orders", () => {
  render(<RecentOrders orders={[]} />);
  expect(screen.getByText("No orders yet.")).toBeTruthy();
  expect(screen.getByRole("button", { name: "New order" })).toBeTruthy();
});

test("single: shows the one order without a list of many", () => {
  render(<RecentOrders orders={makeOrders(1)} />);
  expect(screen.getAllByRole("listitem")).toHaveLength(1);
  expect(screen.getByText("#1001")).toBeTruthy();
});

test("typical: shows each order's number in order", () => {
  render(<RecentOrders orders={makeOrders(5)} />);
  const numbers = screen.getAllByRole("listitem").map((item) => item.textContent?.match(/#\d+/)?.[0]);
  expect(numbers).toEqual(["#1001", "#1002", "#1003", "#1004", "#1005"]);
});

test("overflow: keeps a long customer name in its title", () => {
  const name = "Maximiliana Featherstonehaugh-Wolfeschlegel";
  render(<RecentOrders orders={[makeOrder(0, { customer: name })]} />);
  expect(screen.getByTitle(name)).toBeTruthy();
});

test("error: shows the message with a way to retry and no stale orders", () => {
  render(<RecentOrders orders={makeOrders(3)} error="We couldn't load recent orders." />);
  expect(screen.getByRole("alert").textContent).toContain("We couldn't load recent orders.");
  expect(screen.getByRole("button", { name: "Try again" })).toBeTruthy();
  expect(screen.queryAllByRole("listitem")).toHaveLength(0);
});

test("loading: announces that orders are loading, with no orders or empty message", () => {
  render(<RecentOrders orders={[]} loading />);
  expect(screen.getByRole("status").textContent).toContain("Loading recent orders");
  expect(screen.queryByText("No orders yet.")).toBeNull();
});
