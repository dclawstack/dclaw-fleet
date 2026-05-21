"use client";

import { useEffect, useState } from "react";
import { Plus, BatteryCharging, Gauge } from "lucide-react";

import { Input, Table } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import {
  charging,
  vehicles as vehiclesApi,
  type ChargingSession,
  type ChargeRecommendation,
  type RangePrediction,
  type Vehicle,
} from "@/lib/api";

export default function EVPage() {
  const [sessions, setSessions] = useState<ChargingSession[]>([]);
  const [evs, setEvs] = useState<Vehicle[]>([]);
  const [ranges, setRanges] = useState<Record<string, RangePrediction>>({});
  const [recs, setRecs] = useState<Record<string, ChargeRecommendation>>({});
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    vehicle_id: "", station_id: "", energy_kwh: 0, cost: 0, soc_start: 20, soc_end: 80,
  });

  async function refresh() {
    const [list, v] = await Promise.all([charging.list(), vehiclesApi.list()]);
    setSessions(list);
    const electric = v.items.filter((x) => x.fuel_type === "electric");
    setEvs(electric);
    const rngs: Record<string, RangePrediction> = {};
    const rcs: Record<string, ChargeRecommendation> = {};
    for (const ev of electric) {
      try {
        rngs[ev.id] = await charging.range(ev.id);
        rcs[ev.id] = await charging.recommendation(ev.id);
      } catch {}
    }
    setRanges(rngs);
    setRecs(rcs);
  }

  useEffect(() => { refresh().catch(console.error); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    await charging.create(form);
    setForm({ ...form, energy_kwh: 0, cost: 0 });
    setCreating(false);
    await refresh();
  }

  return (
    <div className="p-8">
      <PageHeader
        title="EV Management"
        description="Charging sessions, AI range prediction, and overnight charge scheduling."
        action={
          <button onClick={() => setCreating((c) => !c)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
            <Plus className="h-4 w-4" /> Log session
          </button>
        }
      />

      <section className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {evs.length === 0 && (
          <div className="md:col-span-2 lg:col-span-3 rounded-xl border bg-white p-6 text-center text-sm text-slate-400">
            No electric vehicles registered. Add one with fuel_type = electric to see range predictions.
          </div>
        )}
        {evs.map((ev) => {
          const r = ranges[ev.id];
          const rec = recs[ev.id];
          return (
            <div key={ev.id} className="rounded-xl border bg-white p-5">
              <div className="text-xs font-medium uppercase text-slate-500">{ev.license_plate} — {ev.make} {ev.model}</div>
              <div className="mt-3 flex items-end gap-3">
                <Gauge className="h-6 w-6 text-blue-600" />
                <div>
                  <div className="text-2xl font-bold text-slate-900">{r?.estimated_range_miles?.toFixed(0) ?? "—"} mi</div>
                  <div className="text-xs text-slate-500">SoC {r?.current_soc ?? "—"}% · confidence {r?.confidence ?? "—"}</div>
                </div>
              </div>
              <div className={`mt-3 flex items-start gap-2 rounded-lg p-2 text-xs ${rec?.needs_charge ? "bg-amber-50 text-amber-800" : "bg-green-50 text-green-800"}`}>
                <BatteryCharging className="h-4 w-4 mt-0.5" />
                <div>{rec?.reason} · Window: {rec?.suggested_window}</div>
              </div>
            </div>
          );
        })}
      </section>

      {creating && (
        <form onSubmit={handleCreate} className="mb-6 grid grid-cols-1 gap-3 rounded-xl border bg-white p-5 md:grid-cols-3">
          <div>
            <label className="block text-xs font-medium text-slate-600">Vehicle</label>
            <select value={form.vehicle_id} required onChange={(e) => setForm({ ...form, vehicle_id: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="">Select EV…</option>
              {evs.map((v) => <option key={v.id} value={v.id}>{v.license_plate}</option>)}
            </select>
          </div>
          <Input label="Station ID" value={form.station_id} onChange={(v) => setForm({ ...form, station_id: v })} />
          <Input label="Energy (kWh)" type="number" value={String(form.energy_kwh)} onChange={(v) => setForm({ ...form, energy_kwh: Number(v) })} required />
          <Input label="Cost ($)" type="number" value={String(form.cost)} onChange={(v) => setForm({ ...form, cost: Number(v) })} required />
          <Input label="SoC start (%)" type="number" value={String(form.soc_start)} onChange={(v) => setForm({ ...form, soc_start: Number(v) })} />
          <Input label="SoC end (%)" type="number" value={String(form.soc_end)} onChange={(v) => setForm({ ...form, soc_end: Number(v) })} />
          <div className="md:col-span-3 flex justify-end">
            <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Log</button>
          </div>
        </form>
      )}

      <Table
        headers={["Vehicle", "Station", "Energy", "Cost", "SoC", "Started"]}
        rows={sessions.map((s) => {
          const ev = evs.find((v) => v.id === s.vehicle_id);
          return [
            ev?.license_plate ?? s.vehicle_id.slice(0, 8),
            s.station_id ?? "—",
            `${s.energy_kwh.toFixed(1)} kWh`,
            `$${Number(s.cost).toFixed(2)}`,
            `${s.soc_start ?? "—"} → ${s.soc_end ?? "—"}%`,
            new Date(s.started_at).toLocaleString(),
          ];
        })}
      />
    </div>
  );
}
