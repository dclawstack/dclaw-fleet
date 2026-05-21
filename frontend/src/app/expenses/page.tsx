"use client";

import { useEffect, useState } from "react";
import { Plus, Check, X, AlertTriangle } from "lucide-react";

import { Input, Status, Table } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import {
  expenses,
  drivers as driversApi,
  vehicles as vehiclesApi,
  type Driver,
  type Expense,
  type ExpenseAnalytics,
  type Vehicle,
} from "@/lib/api";

const CATEGORIES = ["fuel", "toll", "maintenance", "insurance", "lodging", "other"];

export default function ExpensesPage() {
  const [items, setItems] = useState<Expense[]>([]);
  const [analytics, setAnalytics] = useState<ExpenseAnalytics | null>(null);
  const [vs, setVs] = useState<Vehicle[]>([]);
  const [ds, setDs] = useState<Driver[]>([]);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    vehicle_id: "",
    driver_id: "",
    category: "other",
    amount: 0,
    vendor: "",
    expense_date: new Date().toISOString().slice(0, 10),
    notes: "",
  });

  async function refresh() {
    const [list, an, v, d] = await Promise.all([
      expenses.list(),
      expenses.analytics(),
      vehiclesApi.list(),
      driversApi.list(),
    ]);
    setItems(list);
    setAnalytics(an);
    setVs(v.items);
    setDs(d.items);
  }

  useEffect(() => { refresh().catch(console.error); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    const payload: any = { ...form };
    if (!payload.vehicle_id) delete payload.vehicle_id;
    if (!payload.driver_id) delete payload.driver_id;
    await expenses.create(payload);
    setForm({ ...form, amount: 0, vendor: "", notes: "" });
    setCreating(false);
    await refresh();
  }

  async function handleApprove(id: string, approve: boolean) {
    await expenses.approve(id, "manager@fleet.io", approve);
    await refresh();
  }

  return (
    <div className="p-8">
      <PageHeader
        title="Expenses"
        description="Track and approve fleet expenses with auto-categorization and fraud detection."
        action={
          <button onClick={() => setCreating((c) => !c)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
            <Plus className="h-4 w-4" /> New expense
          </button>
        }
      />

      {analytics && (
        <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-xl border bg-white p-5">
            <div className="text-xs font-medium uppercase text-slate-500">Total spend</div>
            <div className="mt-2 text-2xl font-bold text-slate-900">${analytics.total_amount.toFixed(0)}</div>
            <div className="mt-2 flex flex-wrap gap-1">
              {Object.entries(analytics.by_category).map(([c, v]) => (
                <span key={c} className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                  {c}: ${v.toFixed(0)}
                </span>
              ))}
            </div>
          </div>
          <div className="rounded-xl border bg-white p-5">
            <div className="text-xs font-medium uppercase text-slate-500">Pending approval</div>
            <div className="mt-2 text-2xl font-bold text-amber-700">{analytics.pending_approval_count}</div>
            <div className="text-xs text-slate-500 mt-1">${analytics.pending_approval_amount.toFixed(0)} awaiting decision</div>
          </div>
          <div className="rounded-xl border bg-white p-5">
            <div className="flex items-center gap-2 text-xs font-medium uppercase text-slate-500">
              <AlertTriangle className="h-4 w-4 text-amber-600" /> AI flags
            </div>
            <div className="mt-2 text-2xl font-bold text-amber-700">{analytics.flagged_count}</div>
            <ul className="mt-2 space-y-1 max-h-28 overflow-y-auto">
              {analytics.flags.slice(0, 5).map((f, i) => (
                <li key={i} className="text-xs text-slate-600">• {f}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {creating && (
        <form onSubmit={handleCreate} className="mb-6 grid grid-cols-1 gap-3 rounded-xl border bg-white p-5 md:grid-cols-3">
          <div>
            <label className="block text-xs font-medium text-slate-600">Category</label>
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
              {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
            </select>
          </div>
          <Input label="Amount ($)" type="number" value={String(form.amount)} onChange={(v) => setForm({ ...form, amount: Number(v) })} required />
          <Input label="Vendor" value={form.vendor} onChange={(v) => setForm({ ...form, vendor: v })} />
          <Input label="Date" type="date" value={form.expense_date} onChange={(v) => setForm({ ...form, expense_date: v })} required />
          <div>
            <label className="block text-xs font-medium text-slate-600">Vehicle (optional)</label>
            <select value={form.vehicle_id} onChange={(e) => setForm({ ...form, vehicle_id: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="">—</option>
              {vs.map((v) => <option key={v.id} value={v.id}>{v.license_plate}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600">Driver (optional)</label>
            <select value={form.driver_id} onChange={(e) => setForm({ ...form, driver_id: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="">—</option>
              {ds.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>
          <div className="md:col-span-3 flex justify-end">
            <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Submit</button>
          </div>
        </form>
      )}

      <Table
        headers={["Date", "Category", "Vendor", "Amount", "Vehicle", "Status", "Actions"]}
        rows={items.map((e) => {
          const veh = vs.find((v) => v.id === e.vehicle_id);
          return [
            e.expense_date,
            e.category,
            e.vendor ?? "—",
            <span key="a" className="font-semibold">${Number(e.amount).toFixed(2)}</span>,
            veh?.license_plate ?? "—",
            <Status key="s" value={e.approval_status} />,
            e.approval_status === "pending" ? (
              <div key="ac" className="flex items-center gap-2">
                <button onClick={() => handleApprove(e.id, true)} className="inline-flex items-center gap-1 rounded bg-green-100 px-2 py-1 text-xs text-green-700 hover:bg-green-200">
                  <Check className="h-3 w-3" /> Approve
                </button>
                <button onClick={() => handleApprove(e.id, false)} className="inline-flex items-center gap-1 rounded bg-red-100 px-2 py-1 text-xs text-red-700 hover:bg-red-200">
                  <X className="h-3 w-3" /> Reject
                </button>
              </div>
            ) : (
              <span className="text-xs text-slate-400">by {e.approved_by ?? "—"}</span>
            ),
          ];
        })}
      />
    </div>
  );
}
