"use client";

import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";

import { PageHeader } from "@/components/page-header";
import { Input, Status, Table } from "@/components/data-table";
import { assets, type Asset } from "@/lib/api";

export default function AssetsPage() {
  const [items, setItems] = useState<Asset[]>([]);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ name: "", asset_type: "trailer", serial_number: "", location: "" });

  async function refresh() {
    const r = await assets.list();
    setItems(r.items);
  }

  useEffect(() => { refresh().catch(console.error); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    await assets.create(form);
    setForm({ name: "", asset_type: "trailer", serial_number: "", location: "" });
    setCreating(false);
    await refresh();
  }

  async function handleDelete(id: string) {
    if (!confirm("Delete this asset?")) return;
    await assets.remove(id);
    await refresh();
  }

  return (
    <div className="p-8">
      <PageHeader
        title="Assets"
        description="Trailers, containers, tools — non-vehicle inventory."
        action={
          <button onClick={() => setCreating((c) => !c)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
            <Plus className="h-4 w-4" /> Add asset
          </button>
        }
      />

      {creating && (
        <form onSubmit={handleCreate} className="mb-6 grid grid-cols-1 gap-3 rounded-xl border bg-white p-5 md:grid-cols-4">
          <Input label="Name" value={form.name} onChange={(v) => setForm({ ...form, name: v })} required />
          <Input label="Type" value={form.asset_type} onChange={(v) => setForm({ ...form, asset_type: v })} required />
          <Input label="Serial" value={form.serial_number} onChange={(v) => setForm({ ...form, serial_number: v })} />
          <Input label="Location" value={form.location} onChange={(v) => setForm({ ...form, location: v })} />
          <div className="md:col-span-4 flex justify-end">
            <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Create</button>
          </div>
        </form>
      )}

      <Table
        headers={["Name", "Type", "Serial", "Location", "Status", ""]}
        rows={items.map((a) => [
          a.name, a.asset_type,
          <span key="sn" className="font-mono text-xs">{a.serial_number ?? "—"}</span>,
          a.location ?? "—",
          <Status key="st" value={a.status} />,
          <button key="del" onClick={() => handleDelete(a.id)} aria-label="Delete asset" className="text-slate-400 hover:text-red-600"><Trash2 className="h-4 w-4" /></button>,
        ])}
      />
    </div>
  );
}
