import { AppLayout } from "@/components/layouts/AppLayout";
import { PrimaryButton } from "@/components/PrimaryButton";
import { makeCustomers } from "@/factories";

const customers = makeCustomers(6);

export function Customers() {
  return (
    <AppLayout title="Customers">
      <ul className="divide-y divide-border rounded-card border border-border bg-surface">
        {customers.map((c) => (
          <li key={c.id} className="flex items-center justify-between p-4">
            <div>
              <p className="font-medium">{c.name}</p>
              <p className="text-sm text-muted">{c.email}</p>
            </div>
            <span className="text-sm text-muted">{c.orders} orders</span>
          </li>
        ))}
      </ul>
      <div className="mt-6">
        <PrimaryButton>Invite customer</PrimaryButton>
      </div>
    </AppLayout>
  );
}
