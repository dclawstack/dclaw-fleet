"use client";

import { useEffect, useState } from "react";
import { Plus } from "lucide-react";

import { PageHeader } from "@/components/page-header";
import { Input, Status, Table } from "@/components/data-table";
import { maintenance, vehicles, type MaintenanceTask, type Vehicle } from "@/lib/api";

export default function MaintenancePage() {
  const [tasks, setTasks] = useState<MaintenanceTask[]>([]);
  const [overdue, setOverdue] = useState<MaintenanceTask[]>([]);
  const [vs, setVs] = useState<Vehicle[]>([]);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ vehicle_id: "", task_type: "oil_change", description: "", due_date: "", due_mileage: 0 });

  async function refresh() {
    const [list, od, vlist] = await Promise.all([
      maintenance.list(), maintenance.overdue(), vehicles.list(),
    ]);
    setTasks(list.items);
    setOverdue(od);
    setVs(vlist.items);
  }

  useEffect(() => { refresh().catch(console.error); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    const payload: any = { ...form, due_date: form.due_date || null, due_mileage: form.due_mileage || null };
    await maintenance.create(payload);
    setForm({ vehicle_id: "", task_type: "oil_change", description: "", due_date: "", due_mileage: 0 });
    setCreating(false);
    await refresh();
  }

  return (
    <div className="p-8">
      <PageHeader
        title="Maintenance"
        description="Preventive scheduling, overdue alerts, vehicle health."
        action={
          <button onClick={() => setCreating((c) => !c)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
            <Plus className="h-4 w-4" /> New task
          </button>
        }
      />

      {overdue.length > 0 && (
        <div className="mb-6 rounded-xl border border-amber-200 bg-amber-50 p-4">
          <h3 className="text-sm font-semibold text-amber-800">{overdue.length} overdue maintenance task{overdue.length === 1 ? "" : "s"}</h3>
          <p className="mt-1 text-xs text-amber-700">Resolve these to keep vehicle health scores high.</p>
        </div>
      )}

      {creating && (
        <form onSubmit={handleCreate} className="mb-6 grid grid-cols-1 gap-3 rounded-xl border bg-white p-5 md:grid-cols-3">
          <div>
            <label className="block text-xs font-medium text-slate-600">Vehicle</label>
            <select value={form.vehicle_id} required onChange={(e) => setForm({ ...form, vehicle_id: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="">Select vehicle…</option>
              {vs.map((v) => <option key={v.id} value={v.id}>{v.license_plate} — {v.make} {v.model}</option>)}
            </select>
          </div>
          <Input label="Task type" value={form.task_type} onChange={(v) => setForm({ ...form, task_type: v })} required />
          <Input label="Description" value={form.description} onChange={(v) => setForm({ ...form, description: v })} />
          <Input label="Due date" type="date" value={form.due_date} onChange={(v) => setForm({ ...form, due_date: v })} />
          <Input label="Due mileage" type="number" value={String(form.due_mileage)} onChange={(v) => setForm({ ...form, due_mileage: Number(v) })} />
          <div className="md:col-span-3 flex justify-end">
            <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Create</button>
          </div>
        </form>
      )}

      <Table
        headers={["Vehicle", "Type", "Description", "Due date", "Due mi", "Status"]}
        rows={tasks.map((t) => {
          const veh = vs.find((v) => v.id === t.vehicle_id);
          return [
            veh ? `${veh.license_plate}` : t.vehicle_id.slice(0, 8),
            t.task_type, t.description ?? "—", t.due_date ?? "—",
            t.due_mileage ? t.due_mileage.toLocaleString() : "—",
            <Status key="st" value={t.status} />,
          ];
        })}
      />
    </div>
  );
}
