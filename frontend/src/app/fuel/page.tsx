"use client";

import { useEffect, useState } from "react";
import { Plus, AlertTriangle } from "lucide-react";

import { PageHeader } from "@/components/page-header";
import { Input, Table } from "@/components/data-table";
import { fuel, vehicles, type FuelLog, type FuelReport, type Vehicle } from "@/lib/api";

export default function FuelPage() {
  const [logs, setLogs] = useState<FuelLog[]>([]);
  const [vs, setVs] = useState<Vehicle[]>([]);
  const [reports, setReports] = useState<Record<string, FuelReport>>({});
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ vehicle_id: "", gallons: 0, cost: 0, odometer_miles: 0, fuel_type: "gasoline" });

  async function refresh() {
    const [l, v] = await Promise.all([fuel.list(), vehicles.list()]);
    setLogs(l.items);
    setVs(v.items);
    const seen = new Set<string>();
    const reps: Record<string, FuelReport> = {};
    for (const log of l.items) {
      if (seen.has(log.vehicle_id)) continue;
      seen.add(log.vehicle_id);
      try { reps[log.vehicle_id] = await fuel.report(log.vehicle_id); } catch {}
    }
    setReports(reps);
  }

  useEffect(() => { refresh().catch(console.error); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    await fuel.create(form);
    setForm({ vehicle_id: "", gallons: 0, cost: 0, odometer_miles: 0, fuel_type: "gasoline" });
    setCreating(false);
    await refresh();
  }

  return (
    <div className="p-8">
      <PageHeader
        title="Fuel"
        description="Per-vehicle MPG, anomaly detection, fraud flags."
        action={
          <button onClick={() => setCreating((c) => !c)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
            <Plus className="h-4 w-4" /> Log fill-up
          </button>
        }
      />

      {creating && (
        <form onSubmit={handleCreate} className="mb-6 grid grid-cols-1 gap-3 rounded-xl border bg-white p-5 md:grid-cols-3">
          <div>
            <label className="block text-xs font-medium text-slate-600">Vehicle</label>
            <select value={form.vehicle_id} required onChange={(e) => setForm({ ...form, vehicle_id: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="">Select vehicle…</option>
              {vs.map((v) => <option key={v.id} value={v.id}>{v.license_plate} — {v.make} {v.model}</option>)}
            </select>
          </div>
          <Input label="Gallons" type="number" value={String(form.gallons)} onChange={(v) => setForm({ ...form, gallons: Number(v) })} required />
          <Input label="Cost ($)" type="number" value={String(form.cost)} onChange={(v) => setForm({ ...form, cost: Number(v) })} required />
          <Input label="Odometer" type="number" value={String(form.odometer_miles)} onChange={(v) => setForm({ ...form, odometer_miles: Number(v) })} required />
          <div className="md:col-span-3 flex justify-end">
            <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Log</button>
          </div>
        </form>
      )}

      <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Object.entries(reports).map(([vid, r]) => {
          const veh = vs.find((v) => v.id === vid);
          return (
            <div key={vid} className="rounded-xl border bg-white p-5">
              <div className="text-xs font-medium text-slate-500">{veh ? `${veh.license_plate} — ${veh.make} ${veh.model}` : vid.slice(0, 8)}</div>
              <div className="mt-2 flex items-end gap-2">
                <div className="text-2xl font-bold text-slate-900">{r.mpg ? r.mpg.toFixed(1) : "—"}</div>
                <div className="text-xs text-slate-500 mb-1">MPG</div>
              </div>
              <div className="mt-1 text-xs text-slate-500">
                {r.total_gallons.toFixed(1)} gal · ${r.total_cost.toFixed(0)} · {r.total_miles.toLocaleString()} mi
              </div>
              {r.anomalies.length > 0 && (
                <div className="mt-3 space-y-1">
                  {r.anomalies.map((a, i) => (
                    <div key={i} className="flex items-start gap-1 text-xs text-amber-700">
                      <AlertTriangle className="h-3.5 w-3.5 mt-0.5" /> {a}
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <Table
        headers={["Vehicle", "Gallons", "Cost", "Odometer", "Fuel", "Filled"]}
        rows={logs.map((l) => {
          const veh = vs.find((v) => v.id === l.vehicle_id);
          return [
            veh?.license_plate ?? l.vehicle_id.slice(0, 8),
            l.gallons.toFixed(1),
            `$${Number(l.cost).toFixed(2)}`,
            l.odometer_miles.toLocaleString(),
            l.fuel_type,
            new Date(l.filled_at).toLocaleDateString(),
          ];
        })}
      />
    </div>
  );
}
