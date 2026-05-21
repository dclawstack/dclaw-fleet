"use client";

import { useEffect, useState } from "react";
import { Plus, AlertOctagon, Clock } from "lucide-react";

import { Input, Status, Table } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import {
  drivers as driversApi,
  hos,
  permits,
  vehicles as vehiclesApi,
  type ComplianceSummary,
  type Driver,
  type HOSStatus,
  type Permit,
  type Vehicle,
} from "@/lib/api";

export default function CompliancePage() {
  const [summary, setSummary] = useState<ComplianceSummary | null>(null);
  const [permitList, setPermitList] = useState<Permit[]>([]);
  const [vs, setVs] = useState<Vehicle[]>([]);
  const [ds, setDs] = useState<Driver[]>([]);
  const [hosBoard, setHosBoard] = useState<HOSStatus[]>([]);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    entity_type: "vehicle",
    entity_id: "",
    permit_type: "DOT",
    permit_number: "",
    expiry_date: "",
    issuer: "",
  });

  async function refresh() {
    const [sm, pl, v, d] = await Promise.all([
      permits.summary(),
      permits.list(),
      vehiclesApi.list(),
      driversApi.list(),
    ]);
    setSummary(sm);
    setPermitList(pl);
    setVs(v.items);
    setDs(d.items);
    const statuses = await Promise.all(d.items.map((dr) => hos.status(dr.id).catch(() => null)));
    setHosBoard(statuses.filter((s): s is HOSStatus => s !== null));
  }

  useEffect(() => { refresh().catch(console.error); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    await permits.create(form);
    setForm({ entity_type: "vehicle", entity_id: "", permit_type: "DOT", permit_number: "", expiry_date: "", issuer: "" });
    setCreating(false);
    await refresh();
  }

  const entities = form.entity_type === "vehicle"
    ? vs.map((v) => ({ id: v.id, label: `${v.license_plate} — ${v.make} ${v.model}` }))
    : ds.map((d) => ({ id: d.id, label: d.name }));

  return (
    <div className="p-8">
      <PageHeader
        title="Compliance & ELD"
        description="HOS clocks, permits, inspections, and DOT compliance."
        action={
          <button onClick={() => setCreating((c) => !c)} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">
            <Plus className="h-4 w-4" /> New permit
          </button>
        }
      />

      <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <SummaryCard title="Expired permits" value={summary?.expired_permits ?? "—"} tone={summary && summary.expired_permits > 0 ? "danger" : "ok"} icon={<AlertOctagon className="h-5 w-5" />} />
        <SummaryCard title="Expiring < 30d" value={summary?.expiring_soon ?? "—"} tone={summary && summary.expiring_soon > 0 ? "warn" : "ok"} icon={<Clock className="h-5 w-5" />} />
        <SummaryCard title="Failed DVIR (30d)" value={summary?.failed_dvir ?? "—"} tone="warn" icon={<AlertOctagon className="h-5 w-5" />} />
        <SummaryCard title="HOS violations" value={summary?.hos_violations ?? "—"} tone="warn" icon={<Clock className="h-5 w-5" />} />
      </div>

      {creating && (
        <form onSubmit={handleCreate} className="mb-6 grid grid-cols-1 gap-3 rounded-xl border bg-white p-5 md:grid-cols-3">
          <div>
            <label className="block text-xs font-medium text-slate-600">Attached to</label>
            <select value={form.entity_type} onChange={(e) => setForm({ ...form, entity_type: e.target.value, entity_id: "" })} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="vehicle">Vehicle</option>
              <option value="driver">Driver</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-slate-600">Entity</label>
            <select value={form.entity_id} required onChange={(e) => setForm({ ...form, entity_id: e.target.value })} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="">Select…</option>
              {entities.map((x) => <option key={x.id} value={x.id}>{x.label}</option>)}
            </select>
          </div>
          <Input label="Permit type" value={form.permit_type} onChange={(v) => setForm({ ...form, permit_type: v })} required />
          <Input label="Permit number" value={form.permit_number} onChange={(v) => setForm({ ...form, permit_number: v })} required />
          <Input label="Issuer" value={form.issuer} onChange={(v) => setForm({ ...form, issuer: v })} />
          <Input label="Expiry date" type="date" value={form.expiry_date} onChange={(v) => setForm({ ...form, expiry_date: v })} required />
          <div className="md:col-span-3 flex justify-end">
            <button type="submit" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700">Create</button>
          </div>
        </form>
      )}

      <section className="mb-8">
        <h2 className="mb-3 text-sm font-semibold text-slate-700">Permits</h2>
        <Table
          headers={["Type", "Number", "Attached to", "Expires", "Status"]}
          rows={permitList.map((p) => {
            const ref = p.entity_type === "vehicle"
              ? vs.find((v) => v.id === p.entity_id)?.license_plate ?? p.entity_id.slice(0, 8)
              : ds.find((d) => d.id === p.entity_id)?.name ?? p.entity_id.slice(0, 8);
            const expired = new Date(p.expiry_date) < new Date();
            return [
              p.permit_type,
              <span key="n" className="font-mono text-xs">{p.permit_number}</span>,
              `${p.entity_type}: ${ref}`,
              <span key="e" className={expired ? "text-red-600 font-medium" : ""}>{p.expiry_date}</span>,
              <Status key="s" value={p.status} />,
            ];
          })}
        />
      </section>

      <section>
        <h2 className="mb-3 text-sm font-semibold text-slate-700">HOS board (today)</h2>
        <Table
          headers={["Driver", "Status", "Drive hrs", "On-duty hrs", "Drive left", "Violations"]}
          rows={hosBoard.map((s) => {
            const driver = ds.find((d) => d.id === s.driver_id);
            return [
              driver?.name ?? s.driver_id.slice(0, 8),
              <Status key="s" value={s.current_status} />,
              s.driving_hours_today.toFixed(1),
              s.on_duty_hours_today.toFixed(1),
              `${s.remaining_drive_hours.toFixed(1)} h`,
              s.violations.length > 0 ? (
                <span key="v" className="text-red-600 text-xs">{s.violations.join("; ")}</span>
              ) : "—",
            ];
          })}
        />
      </section>
    </div>
  );
}

function SummaryCard({ title, value, icon, tone }: { title: string; value: number | string; icon: React.ReactNode; tone: "ok" | "warn" | "danger" }) {
  const toneClass = tone === "danger" ? "text-red-600" : tone === "warn" ? "text-amber-600" : "text-green-600";
  return (
    <div className="rounded-xl border bg-white p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-slate-500">{title}</span>
        <span className={toneClass}>{icon}</span>
      </div>
      <div className={`mt-2 text-2xl font-bold ${toneClass}`}>{value}</div>
    </div>
  );
}
