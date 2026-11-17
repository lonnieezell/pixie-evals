import type { ButtonHTMLAttributes } from "react";

/**
 * @deprecated Use `Button` from `@/components/ui/button` instead.
 */
export function PrimaryButton({ className = "", ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={`rounded bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground ${className}`}
      {...props}
    />
  );
}
