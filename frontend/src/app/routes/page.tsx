"use client";

import { useEffect, useState } from "react";
import { Plus, Wand2, Trash2, RefreshCw, Shuffle } from "lucide-react";

import { PageHeader } from "@/components/page-header";
import { Input, Status, Table } from "@/components/data-table";
import { routes, routeIntegration, type Route } from "@/lib/api";

type StopForm = { sequence: number; address: string; lat: number; lng: number };

export default function RoutesPage() {
  const [items, setItems] = useState<Route[]>([]);
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("");
  const [stops, setStops] = useState<StopForm[]>([{ sequence: 0, address: "", lat: 0, lng: 0 }]);
  const [busy, setBusy] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<string | null>(null);

  async function refresh() {
    const r = await routes.list();
    setItems(r.items);
  }

  useEffect(() => { refresh().catch(console.error); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    await routes.create({ name, stops });
    setName("");
    setStops([{ sequence: 0, address: "", lat: 0, lng: 0 }]);
    setCreating(false);
    await refresh();
  }

  async function handleOptimize(id: string) {
    await routes.optimize(id);
    await refresh();
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this route?")) return;
    await routes.remove(id);
    await refresh();
  }

  async function handleSync() {
    setBusy("sync");
    try {
      const r = await routeIntegration.sync();
      setLastResult(`Synced ${r.synced_count} route(s) to DClaw Route. ${r.failed_count} skipped (must be optimized first).`);
      await refresh();
    } finally {
      setBusy(null);
    }
  }

  async function handleAutoAssign() {
    setBusy("assign");
    try {
      const r = await routeIntegration.autoAssign();
      const assigned = r.assignments.filter((a) => a.vehicle_id).length;
      setLastResult(`Auto-assigned ${assigned} route(s). ${r.skipped_count} vehicle(s) skipped (${r.skipped_reasons.join("; ") || "none"}).`);
      await refresh();
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="p-8">
      <PageHeader
        title="Routes"
        description="AI-optimized stop ordering, DClaw Route sync, and auto-dispatch."
        action={
          <div className="flex items-center gap-2">
            <button onClick={handleAutoAssign} disabled={!!busy} className="inline-flex items-center gap-1 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm text-blue-700 hover:bg-blue-100 disabled:opacity-60">
              <Shuffle className={`h-4 w-4 ${busy === "assign" ? "animate-spin" : ""}`} /> Auto-assign
            </button>
            <button onClick={handleSync} disabled={!!busy} className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50 disabled:opacity-60">
              <RefreshCw className={`h-4 w-4 ${busy === "sync" ? "animate-spin" : ""}`} /> Sync to DClaw Route
            </button>
            <button onClick={() => setCreating((c) => !c)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
              <Plus className="h-4 w-4" /> New route
            </button>
          </div>
        }
      />

      {lastResult && (
        <div className="mb-4 rounded-lg border border-blue-200 bg-blue-50 px-4 py-2 text-sm text-blue-800">{lastResult}</div>
      )}

      {creating && (
        <form onSubmit={handleCreate} className="mb-6 rounded-xl border bg-white p-5">
          <Input label="Route name" value={name} onChange={setName} required />
          <div className="mt-4 space-y-3">
            {stops.map((s, i) => (
              <div key={i} className="grid grid-cols-1 gap-3 md:grid-cols-4">
                <Input label={`Stop ${i + 1} address`} value={s.address} onChange={(v) => updateStop(i, { address: v })} required />
                <Input label="Lat" type="number" value={String(s.lat)} onChange={(v) => updateStop(i, { lat: Number(v) })} required />
                <Input label="Lng" type="number" value={String(s.lng)} onChange={(v) => updateStop(i, { lng: Number(v) })} required />
                <div className="flex items-end">
                  <button type="button" onClick={() => removeStop(i)} className="text-xs text-red-600 hover:underline">Remove</button>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-3 flex justify-between">
            <button type="button" onClick={addStop} className="text-sm text-blue-600 hover:underline">+ Add stop</button>
            <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Create route</button>
          </div>
        </form>
      )}

      <Table
        headers={["Name", "Stops", "Distance", "Duration", "Vehicle", "Sync", "Status", ""]}
        rows={items.map((r) => [
          r.name,
          r.stops.length,
          r.optimized_distance_miles != null ? `${r.optimized_distance_miles.toFixed(1)} mi` : "—",
          r.optimized_duration_min != null ? `${r.optimized_duration_min} min` : "—",
          r.vehicle_id ? <span key="v" className="font-mono text-xs">{r.vehicle_id.slice(0, 8)}…</span> : <span className="text-slate-400">unassigned</span>,
          r.external_id ? <span key="e" className="font-mono text-xs text-green-700">{r.external_id}</span> : <span className="text-slate-400">—</span>,
          <Status key="s" value={r.status} />,
          <div key="a" className="flex items-center gap-2">
            <button onClick={() => handleOptimize(r.id)} className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline"><Wand2 className="h-3 w-3" /> Optimize</button>
            <button onClick={() => handleDelete(r.id)} aria-label="Delete route" className="text-slate-400 hover:text-red-600"><Trash2 className="h-4 w-4" /></button>
          </div>,
        ])}
      />
    </div>
  );

  function updateStop(i: number, patch: Partial<StopForm>) {
    setStops((s) => s.map((stop, idx) => (idx === i ? { ...stop, ...patch } : stop)));
  }
  function addStop() {
    setStops((s) => [...s, { sequence: s.length, address: "", lat: 0, lng: 0 }]);
  }
  function removeStop(i: number) {
    setStops((s) => s.filter((_, idx) => idx !== i).map((stop, idx) => ({ ...stop, sequence: idx })));
  }
}
