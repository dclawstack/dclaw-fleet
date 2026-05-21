"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, RefreshCw } from "lucide-react";
import Link from "next/link";

import { PageHeader } from "@/components/page-header";
import { Table } from "@/components/data-table";
import {
  drivers as driversApi,
  drivingEvents,
  hos,
  type Driver,
  type DriverCoaching,
  type HOSStatus,
} from "@/lib/api";

export default function DriverDetailPage() {
  const params = useParams<{ id: string }>();
  const driverId = params?.id;

  const [driver, setDriver] = useState<Driver | null>(null);
  const [coaching, setCoaching] = useState<DriverCoaching | null>(null);
  const [hosStatus, setHosStatus] = useState<HOSStatus | null>(null);
  const [recomputing, setRecomputing] = useState(false);

  async function refresh() {
    if (!driverId) return;
    const [c, s] = await Promise.all([
      drivingEvents.coaching(driverId),
      hos.status(driverId),
    ]);
    setCoaching(c);
    setHosStatus(s);
    const list = await driversApi.list();
    setDriver(list.items.find((d) => d.id === driverId) ?? null);
  }

  useEffect(() => { refresh().catch(console.error); }, [driverId]);

  async function handleRecompute() {
    if (!driverId) return;
    setRecomputing(true);
    try {
      await drivingEvents.recompute(driverId);
      await refresh();
    } finally {
      setRecomputing(false);
    }
  }

  if (!driver) return <div className="p-8 text-slate-500">Loading driver…</div>;

  const tone = (coaching?.score ?? 100) >= 80 ? "text-green-600" : (coaching?.score ?? 100) >= 60 ? "text-amber-600" : "text-red-600";

  return (
    <div className="p-8">
      <Link href="/drivers" className="mb-4 inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700">
        <ArrowLeft className="h-4 w-4" /> Back to drivers
      </Link>
      <PageHeader
        title={driver.name}
        description={`${driver.email} · License ${driver.license_number}`}
        action={
          <button onClick={handleRecompute} disabled={recomputing} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60">
            <RefreshCw className={`h-4 w-4 ${recomputing ? "animate-spin" : ""}`} /> Recompute score
          </button>
        }
      />

      <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-xl border bg-white p-5">
          <div className="text-xs font-medium uppercase text-slate-500">Safety score</div>
          <div className={`mt-2 text-3xl font-bold ${tone}`}>{coaching?.score ?? "—"}</div>
          <div className="mt-1 text-xs text-slate-500">{coaching?.tips.length ?? 0} coaching tip(s) generated</div>
        </div>
        <div className="rounded-xl border bg-white p-5">
          <div className="text-xs font-medium uppercase text-slate-500">HOS today</div>
          <div className="mt-2 text-2xl font-bold text-slate-900">{hosStatus?.driving_hours_today.toFixed(1) ?? "—"} h</div>
          <div className="mt-1 text-xs text-slate-500">{hosStatus?.remaining_drive_hours.toFixed(1) ?? "—"} h drive remaining</div>
        </div>
        <div className="rounded-xl border bg-white p-5">
          <div className="text-xs font-medium uppercase text-slate-500">HOS status</div>
          <div className="mt-2 text-2xl font-bold capitalize text-slate-900">{hosStatus?.current_status.replace("_", " ") ?? "—"}</div>
          {(hosStatus?.violations.length ?? 0) > 0 && (
            <ul className="mt-2 list-inside list-disc text-xs text-red-600">
              {hosStatus!.violations.map((v, i) => <li key={i}>{v}</li>)}
            </ul>
          )}
        </div>
      </div>

      <section>
        <h2 className="mb-3 text-sm font-semibold text-slate-700">Coaching tips</h2>
        {(!coaching || coaching.tips.length === 0) ? (
          <div className="rounded-xl border bg-white p-6 text-center text-sm text-slate-400">
            No coaching tips — this driver hasn't logged risky events in the last 30 days.
          </div>
        ) : (
          <Table
            headers={["Severity", "Event type", "Recommendation"]}
            rows={coaching.tips.map((t) => [
              <span key="s" className={
                t.severity === "critical" ? "rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700"
                : t.severity === "warning" ? "rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700"
                : "rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-700"
              }>{t.severity}</span>,
              t.event_type,
              t.message,
            ])}
          />
        )}
      </section>
    </div>
  );
}
