"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Plus, Trash2 } from "lucide-react";

import { PageHeader } from "@/components/page-header";
import { Input, Status, Table } from "@/components/data-table";
import { drivers, type Driver } from "@/lib/api";

export default function DriversPage() {
  const [items, setItems] = useState<Driver[]>([]);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", phone: "", license_number: "", safety_score: 100 });

  async function refresh() {
    const r = await drivers.list();
    setItems(r.items);
  }

  useEffect(() => { refresh().catch(console.error); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    await drivers.create(form);
    setForm({ name: "", email: "", phone: "", license_number: "", safety_score: 100 });
    setCreating(false);
    await refresh();
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this driver?")) return;
    await drivers.remove(id);
    await refresh();
  }

  return (
    <div className="p-8">
      <PageHeader
        title="Drivers"
        description="Roster, licenses, and AI safety scores."
        action={
          <button onClick={() => setCreating((c) => !c)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
            <Plus className="h-4 w-4" /> Add driver
          </button>
        }
      />

      {creating && (
        <form onSubmit={handleCreate} className="mb-6 grid grid-cols-1 gap-3 rounded-xl border bg-white p-5 md:grid-cols-3">
          <Input label="Name" value={form.name} onChange={(v) => setForm({ ...form, name: v })} required />
          <Input label="Email" type="email" value={form.email} onChange={(v) => setForm({ ...form, email: v })} required />
          <Input label="Phone" value={form.phone} onChange={(v) => setForm({ ...form, phone: v })} />
          <Input label="License #" value={form.license_number} onChange={(v) => setForm({ ...form, license_number: v })} required />
          <Input label="Safety score" type="number" value={String(form.safety_score)} onChange={(v) => setForm({ ...form, safety_score: Number(v) })} />
          <div className="md:col-span-3 flex justify-end">
            <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Create</button>
          </div>
        </form>
      )}

      <Table
        headers={["Name", "Email", "License", "Safety", "Status", ""]}
        rows={items.map((d) => [
          <Link key="n" href={`/drivers/${d.id}`} className="text-blue-600 hover:underline">{d.name}</Link>,
          d.email, d.license_number,
          <SafetyBar key="s" score={d.safety_score} />,
          <Status key="st" value={d.status} />,
          <button key="del" onClick={() => handleDelete(d.id)} className="text-slate-400 hover:text-red-600"><Trash2 className="h-4 w-4" /></button>,
        ])}
      />
    </div>
  );
}

function SafetyBar({ score }: { score: number }) {
  const color = score >= 80 ? "bg-green-500" : score >= 60 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-20 rounded-full bg-slate-200 overflow-hidden">
        <div className={`h-full ${color}`} style={{ width: `${Math.min(100, Math.max(0, score))}%` }} />
      </div>
      <span className="text-xs text-slate-600">{score}</span>
    </div>
  );
}
