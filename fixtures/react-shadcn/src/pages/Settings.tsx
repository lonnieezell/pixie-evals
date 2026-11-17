import { AppLayout } from "@/components/layouts/AppLayout";
import { PrimaryButton } from "@/components/PrimaryButton";

export function Settings() {
  return (
    <AppLayout title="Settings">
      <form className="max-w-md space-y-4 rounded-card border border-border bg-surface p-6">
        <div>
          <label htmlFor="shop-name" className="mb-1 block text-sm font-medium">
            Shop name
          </label>
          <input id="shop-name" defaultValue="Acme Shop" className="w-full rounded-md border border-border px-3 py-2" />
        </div>
        <PrimaryButton type="submit">Save settings</PrimaryButton>
      </form>
    </AppLayout>
  );
}
