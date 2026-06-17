"use client";

import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";

import { Input, Status, Table } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { vehicles, type Vehicle } from "@/lib/api";

const FUEL_TYPES = ["gasoline", "diesel", "electric", "hybrid"];

export default function VehiclesPage() {
  const [items, setItems] = useState<Vehicle[]>([]);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    vin: "", license_plate: "", make: "", model: "", year: 2024, fuel_type: "gasoline", odometer_miles: 0,
  });

  async function refresh() {
    const r = await vehicles.list();
    setItems(r.items);
  }

  useEffect(() => { refresh().catch(console.error); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    await vehicles.create(form);
    setForm({ vin: "", license_plate: "", make: "", model: "", year: 2024, fuel_type: "gasoline", odometer_miles: 0 });
    setCreating(false);
    await refresh();
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this vehicle?")) return;
    await vehicles.remove(id);
    await refresh();
  }

  return (
    <div className="p-8">
      <PageHeader
        title="Vehicles"
        description="Active fleet registry."
        action={
          <button onClick={() => setCreating((c) => !c)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
            <Plus className="h-4 w-4" /> Add vehicle
          </button>
        }
      />

      {creating && (
        <form onSubmit={handleCreate} className="mb-6 grid grid-cols-1 gap-3 rounded-xl border bg-white p-5 md:grid-cols-3">
          <Input label="VIN" value={form.vin} onChange={(v) => setForm({ ...form, vin: v })} required />
          <Input label="License plate" value={form.license_plate} onChange={(v) => setForm({ ...form, license_plate: v })} required />
          <Input label="Make" value={form.make} onChange={(v) => setForm({ ...form, make: v })} required />
          <Input label="Model" value={form.model} onChange={(v) => setForm({ ...form, model: v })} required />
          <Input label="Year" type="number" value={String(form.year)} onChange={(v) => setForm({ ...form, year: Number(v) })} required />
          <div>
            <label className="block text-xs font-medium text-slate-600">Fuel type</label>
            <select value={form.fuel_type} onChange={(e) => setForm({ ...form, fuel_type: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
              {FUEL_TYPES.map((f) => <option key={f}>{f}</option>)}
            </select>
          </div>
          <Input label="Odometer (mi)" type="number" value={String(form.odometer_miles)} onChange={(v) => setForm({ ...form, odometer_miles: Number(v) })} />
          <div className="md:col-span-3 flex justify-end">
            <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Create</button>
          </div>
        </form>
      )}

      <Table
        headers={["VIN", "Plate", "Make/Model", "Year", "Fuel", "Odometer", "Status", ""]}
        rows={items.map((v) => [
          <span key="vin" className="font-mono text-xs">{v.vin}</span>,
          v.license_plate, `${v.make} ${v.model}`, v.year, v.fuel_type,
          v.odometer_miles.toLocaleString() + " mi",
          <Status key="s" value={v.status} />,
          <button key="d" onClick={() => handleDelete(v.id)} aria-label="Delete vehicle" className="text-slate-400 hover:text-red-600"><Trash2 className="h-4 w-4" /></button>,
        ])}
      />
    </div>
  );
}

