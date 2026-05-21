"use client";

import { useEffect, useState } from "react";
import { Plus, AlertOctagon } from "lucide-react";

import { Input, Status, Table } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import {
  accidents,
  drivers as driversApi,
  vehicles as vehiclesApi,
  type AccidentReport,
  type Driver,
  type Vehicle,
} from "@/lib/api";

export default function AccidentsPage() {
  const [items, setItems] = useState<AccidentReport[]>([]);
  const [vs, setVs] = useState<Vehicle[]>([]);
  const [ds, setDs] = useState<Driver[]>([]);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    vehicle_id: "", driver_id: "", severity_score: 3, photos_count: 0, description: "",
  });

  async function refresh() {
    const [list, v, d] = await Promise.all([accidents.list(), vehiclesApi.list(), driversApi.list()]);
    setItems(list);
    setVs(v.items);
    setDs(d.items);
  }

  useEffect(() => { refresh().catch(console.error); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    const payload: any = { ...form };
    if (!payload.driver_id) delete payload.driver_id;
    await accidents.create(payload);
    setForm({ vehicle_id: "", driver_id: "", severity_score: 3, photos_count: 0, description: "" });
    setCreating(false);
    await refresh();
  }

  const openCount = items.filter((a) => a.claim_status === "open").length;
  const predictedTotal = items.filter((a) => a.claim_status === "open").reduce((s, a) => s + (a.predicted_claim_amount ?? 0), 0);

  return (
    <div className="p-8">
      <PageHeader
        title="Accidents & Claims"
        description="Log incidents and let AI predict claim severity and amount."
        action={
          <button onClick={() => setCreating((c) => !c)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
            <Plus className="h-4 w-4" /> Log incident
          </button>
        }
      />

      <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-xl border bg-white p-5">
          <div className="text-xs font-medium uppercase text-slate-500">Open claims</div>
          <div className="mt-2 text-2xl font-bold text-amber-700">{openCount}</div>
        </div>
        <div className="rounded-xl border bg-white p-5">
          <div className="text-xs font-medium uppercase text-slate-500">AI-predicted exposure</div>
          <div className="mt-2 text-2xl font-bold text-slate-900">${predictedTotal.toFixed(0)}</div>
        </div>
        <div className="rounded-xl border bg-white p-5">
          <div className="flex items-center gap-2 text-xs font-medium uppercase text-slate-500">
            <AlertOctagon className="h-4 w-4 text-red-600" /> Total incidents
          </div>
          <div className="mt-2 text-2xl font-bold text-slate-900">{items.length}</div>
        </div>
      </div>

      {creating && (
        <form onSubmit={handleCreate} className="mb-6 grid grid-cols-1 gap-3 rounded-xl border bg-white p-5 md:grid-cols-3">
          <div>
            <label className="block text-xs font-medium text-slate-600">Vehicle</label>
            <select value={form.vehicle_id} required onChange={(e) => setForm({ ...form, vehicle_id: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="">Select vehicle…</option>
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
          <Input label="Severity (1-10)" type="number" value={String(form.severity_score)} onChange={(v) => setForm({ ...form, severity_score: Number(v) })} required />
          <Input label="Photos" type="number" value={String(form.photos_count)} onChange={(v) => setForm({ ...form, photos_count: Number(v) })} />
          <div className="md:col-span-2">
            <label className="block text-xs font-medium text-slate-600">Description</label>
            <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={2} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm" />
          </div>
          <div className="md:col-span-3 flex justify-end">
            <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Log</button>
          </div>
        </form>
      )}

      <Table
        headers={["Vehicle", "Severity", "Photos", "Claim status", "Predicted claim", "When"]}
        rows={items.map((a) => [
          vs.find((v) => v.id === a.vehicle_id)?.license_plate ?? a.vehicle_id.slice(0, 8),
          <span key="s" className={a.severity_score >= 7 ? "font-semibold text-red-700" : ""}>{a.severity_score}/10</span>,
          a.photos_count,
          <Status key="cs" value={a.claim_status} />,
          a.predicted_claim_amount ? `$${a.predicted_claim_amount.toLocaleString()}` : "—",
          new Date(a.occurred_at).toLocaleString(),
        ])}
      />
    </div>
  );
}
