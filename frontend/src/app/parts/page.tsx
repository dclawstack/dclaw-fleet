"use client";

import { useEffect, useState } from "react";
import { Plus, ShoppingCart } from "lucide-react";

import { Input, Table } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { parts, type Part, type ReorderRecommendation } from "@/lib/api";

const CATEGORIES = ["tire", "brake", "filter", "fluid", "battery", "other"];

export default function PartsPage() {
  const [items, setItems] = useState<Part[]>([]);
  const [recs, setRecs] = useState<ReorderRecommendation[]>([]);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    name: "", sku: "", category: "filter", vendor: "", stock: 0, reorder_threshold: 5, unit_cost: 0,
  });

  async function refresh() {
    const [list, r] = await Promise.all([parts.list(), parts.recommendations()]);
    setItems(list);
    setRecs(r);
  }

  useEffect(() => { refresh().catch(console.error); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    await parts.create(form);
    setForm({ name: "", sku: "", category: "filter", vendor: "", stock: 0, reorder_threshold: 5, unit_cost: 0 });
    setCreating(false);
    await refresh();
  }

  return (
    <div className="p-8">
      <PageHeader
        title="Parts & Inventory"
        description="Spare parts stock with AI reorder recommendations."
        action={
          <button onClick={() => setCreating((c) => !c)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
            <Plus className="h-4 w-4" /> Add part
          </button>
        }
      />

      {recs.length > 0 && (
        <section className="mb-6 rounded-xl border border-amber-200 bg-amber-50 p-5">
          <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold text-amber-800">
            <ShoppingCart className="h-4 w-4" /> {recs.length} part(s) need reorder
          </h2>
          <div className="space-y-2">
            {recs.map((r) => (
              <div key={r.part_id} className="flex items-center justify-between rounded-lg bg-white px-3 py-2 text-sm">
                <div>
                  <span className="font-medium">{r.name}</span>
                  <span className="ml-2 font-mono text-xs text-slate-500">{r.sku}</span>
                </div>
                <div className="text-right">
                  <div className="text-amber-800">Order {r.suggested_order_qty} units · ${r.estimated_cost.toFixed(0)}</div>
                  <div className="text-xs text-slate-500">{r.current_stock}/{r.reorder_threshold} threshold</div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {creating && (
        <form onSubmit={handleCreate} className="mb-6 grid grid-cols-1 gap-3 rounded-xl border bg-white p-5 md:grid-cols-3">
          <Input label="Name" value={form.name} onChange={(v) => setForm({ ...form, name: v })} required />
          <Input label="SKU" value={form.sku} onChange={(v) => setForm({ ...form, sku: v })} required />
          <div>
            <label className="block text-xs font-medium text-slate-600">Category</label>
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
              {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
            </select>
          </div>
          <Input label="Vendor" value={form.vendor} onChange={(v) => setForm({ ...form, vendor: v })} />
          <Input label="Stock" type="number" value={String(form.stock)} onChange={(v) => setForm({ ...form, stock: Number(v) })} required />
          <Input label="Reorder threshold" type="number" value={String(form.reorder_threshold)} onChange={(v) => setForm({ ...form, reorder_threshold: Number(v) })} />
          <Input label="Unit cost ($)" type="number" value={String(form.unit_cost)} onChange={(v) => setForm({ ...form, unit_cost: Number(v) })} />
          <div className="md:col-span-3 flex justify-end">
            <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Create</button>
          </div>
        </form>
      )}

      <Table
        headers={["Name", "SKU", "Category", "Stock", "Threshold", "Unit cost"]}
        rows={items.map((p) => [
          p.name,
          <span key="sk" className="font-mono text-xs">{p.sku}</span>,
          p.category,
          <span key="s" className={p.stock <= p.reorder_threshold ? "font-semibold text-amber-700" : ""}>{p.stock}</span>,
          p.reorder_threshold,
          `$${Number(p.unit_cost).toFixed(2)}`,
        ])}
      />
    </div>
  );
}
