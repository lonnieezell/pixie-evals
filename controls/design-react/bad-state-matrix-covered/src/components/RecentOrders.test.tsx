import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, test } from "vitest";
import { RecentOrders } from "@/components/RecentOrders";
import { makeOrders } from "@/factories";

afterEach(cleanup);

test("empty: shows the new-order action when there are no orders", () => {
  render(<RecentOrders orders={[]} />);
  expect(screen.getByRole("button", { name: "New order" })).toBeTruthy();
});

test("single: shows the one order without a list of many", () => {
  render(<RecentOrders orders={makeOrders(1)} />);
  expect(screen.getAllByRole("listitem")).toHaveLength(1);
});

test("typical: shows each order", () => {
  render(<RecentOrders orders={makeOrders(5)} />);
  expect(screen.getAllByRole("listitem")).toHaveLength(5);
});

test("error: shows the message with a way to retry", () => {
  render(<RecentOrders orders={[]} error="We couldn't load recent orders." />);
  expect(screen.getByRole("button", { name: "Try again" })).toBeTruthy();
});
