import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import { RecentOrders } from "@/components/RecentOrders";

afterEach(cleanup);

// Red: the run left this test failing. RecentOrders labels its retry button "Try again".
test("error: retries when the retry button is pressed", () => {
  const onRetry = vi.fn();
  render(<RecentOrders orders={[]} error="We couldn't load recent orders." onRetry={onRetry} />);
  fireEvent.click(screen.getByRole("button", { name: "Retry" }));
  expect(onRetry).toHaveBeenCalledOnce();
});
