"use client";

import { useEffect, useState } from "react";
import { Plus, Wand2, Trash2 } from "lucide-react";

import { PageHeader } from "@/components/page-header";
import { Input, Status, Table } from "@/components/data-table";
import { routes, type Route } from "@/lib/api";

type StopForm = { sequence: number; address: string; lat: number; lng: number };

export default function RoutesPage() {
  const [items, setItems] = useState<Route[]>([]);
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("");
  const [stops, setStops] = useState<StopForm[]>([{ sequence: 0, address: "", lat: 0, lng: 0 }]);

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

  return (
    <div className="p-8">
      <PageHeader
        title="Routes"
        description="AI-optimized stop ordering and ETA estimates."
        action={
          <button onClick={() => setCreating((c) => !c)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
            <Plus className="h-4 w-4" /> New route
          </button>
        }
      />

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
        headers={["Name", "Stops", "Distance", "Duration", "Status", ""]}
        rows={items.map((r) => [
          r.name,
          r.stops.length,
          r.optimized_distance_miles != null ? `${r.optimized_distance_miles.toFixed(1)} mi` : "—",
          r.optimized_duration_min != null ? `${r.optimized_duration_min} min` : "—",
          <Status key="s" value={r.status} />,
          <div key="a" className="flex items-center gap-2">
            <button onClick={() => handleOptimize(r.id)} className="inline-flex items-center gap-1 text-xs text-blue-600 hover:underline"><Wand2 className="h-3 w-3" /> Optimize</button>
            <button onClick={() => handleDelete(r.id)} className="text-slate-400 hover:text-red-600"><Trash2 className="h-4 w-4" /></button>
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
