import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, test } from "vitest";
import { Button } from "@/components/ui/button";

afterEach(cleanup);

test("renders its label as an accessible button", () => {
  render(<Button>New order</Button>);
  expect(screen.getByRole("button", { name: "New order" })).toBeTruthy();
});
