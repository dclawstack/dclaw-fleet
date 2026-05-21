"use client";

import { useEffect, useState } from "react";
import { Sparkles, Leaf, Shuffle, Eye, Cpu } from "lucide-react";

import { Table } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import {
  dashcam,
  predictive,
  telematics,
  vehicles as vehiclesApi,
  type CarbonReport,
  type DashcamEvent,
  type PredictiveReport,
  type TelematicsDevice,
  type Vehicle,
  type AutonomousDispatchResult,
} from "@/lib/api";

type Tab = "predictive" | "carbon" | "dispatch" | "dashcam" | "telematics";

const TABS: { key: Tab; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { key: "predictive", label: "Predictive Maint", icon: Sparkles },
  { key: "carbon", label: "Carbon", icon: Leaf },
  { key: "dispatch", label: "Autonomous Dispatch", icon: Shuffle },
  { key: "dashcam", label: "Dashcam events", icon: Eye },
  { key: "telematics", label: "Telematics", icon: Cpu },
];

export default function OperationsPage() {
  const [tab, setTab] = useState<Tab>("predictive");

  return (
    <div className="p-8">
      <PageHeader
        title="AI Operations"
        description="Predictive maintenance, carbon, autonomous dispatch, dashcam, and telematics — all under one roof."
      />

      <div className="mb-6 flex flex-wrap gap-2 border-b">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`inline-flex items-center gap-2 border-b-2 px-3 pb-2 text-sm font-medium ${tab === t.key ? "border-blue-600 text-blue-700" : "border-transparent text-slate-500 hover:text-slate-800"}`}
          >
            <t.icon className="h-4 w-4" /> {t.label}
          </button>
        ))}
      </div>

      {tab === "predictive" && <PredictiveTab />}
      {tab === "carbon" && <CarbonTab />}
      {tab === "dispatch" && <DispatchTab />}
      {tab === "dashcam" && <DashcamTab />}
      {tab === "telematics" && <TelematicsTab />}
    </div>
  );
}

function PredictiveTab() {
  const [vs, setVs] = useState<Vehicle[]>([]);
  const [reports, setReports] = useState<Record<string, PredictiveReport>>({});

  useEffect(() => {
    (async () => {
      const v = await vehiclesApi.list();
      setVs(v.items);
      const r: Record<string, PredictiveReport> = {};
      for (const veh of v.items) {
        try { r[veh.id] = await predictive.maintenance(veh.id); } catch {}
      }
      setReports(r);
    })().catch(console.error);
  }, []);

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
      {vs.map((v) => {
        const r = reports[v.id];
        const tone = r?.overall_risk === "high" ? "text-red-700" : r?.overall_risk === "medium" ? "text-amber-700" : "text-green-700";
        return (
          <div key={v.id} className="rounded-xl border bg-white p-5">
            <div className="text-xs font-medium uppercase text-slate-500">{v.license_plate} — {v.make} {v.model}</div>
            <div className={`mt-2 text-2xl font-bold capitalize ${tone}`}>{r?.overall_risk ?? "—"} risk</div>
            <div className="mt-2 space-y-1">
              {(r?.predictions ?? []).map((p, i) => (
                <div key={i} className="text-xs text-slate-600">
                  <span className="font-semibold">{p.component}</span> · {(p.probability * 100).toFixed(0)}% — {p.suggested_action}
                </div>
              ))}
              {(!r || r.predictions.length === 0) && <div className="text-xs text-slate-400">No predictions yet</div>}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function CarbonTab() {
  const [fleet, setFleet] = useState<CarbonReport | null>(null);
  const [vs, setVs] = useState<Vehicle[]>([]);
  const [perVehicle, setPerVehicle] = useState<Record<string, CarbonReport>>({});

  useEffect(() => {
    (async () => {
      const [f, v] = await Promise.all([predictive.carbonFleet(), vehiclesApi.list()]);
      setFleet(f);
      setVs(v.items);
      const r: Record<string, CarbonReport> = {};
      for (const veh of v.items) {
        try { r[veh.id] = await predictive.carbonVehicle(veh.id); } catch {}
      }
      setPerVehicle(r);
    })().catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      {fleet && (
        <div className="rounded-xl border bg-white p-5">
          <div className="text-xs font-medium uppercase text-slate-500">Fleet CO₂ footprint</div>
          <div className="mt-2 text-3xl font-bold text-slate-900">{fleet.co2_kg.toLocaleString()} kg</div>
          <div className="text-xs text-slate-500 mt-1">
            {fleet.fuel_gallons.toFixed(0)} gal · {fleet.miles.toLocaleString()} mi · {fleet.co2_per_mile_g.toFixed(0)} g/mi
          </div>
          {fleet.suggestions.length > 0 && (
            <ul className="mt-3 list-disc list-inside text-sm text-slate-600 space-y-1">
              {fleet.suggestions.map((s, i) => <li key={i}>{s}</li>)}
            </ul>
          )}
        </div>
      )}

      <Table
        headers={["Vehicle", "Fuel type", "CO₂ kg", "Gallons", "Miles", "g CO₂/mi"]}
        rows={vs.map((v) => {
          const r = perVehicle[v.id];
          return [
            v.license_plate,
            v.fuel_type,
            r ? r.co2_kg.toFixed(1) : "—",
            r ? r.fuel_gallons.toFixed(1) : "—",
            r ? r.miles.toLocaleString() : "—",
            r ? r.co2_per_mile_g.toFixed(0) : "—",
          ];
        })}
      />
    </div>
  );
}

function DispatchTab() {
  const [result, setResult] = useState<AutonomousDispatchResult | null>(null);
  const [busy, setBusy] = useState(false);

  async function runPlan() {
    setBusy(true);
    try {
      setResult(await predictive.dispatchPlan());
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <button onClick={runPlan} disabled={busy} className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60">
        <Shuffle className={`h-4 w-4 ${busy ? "animate-spin" : ""}`} /> Run autonomous dispatch
      </button>

      {result && (
        <div className="mt-6 space-y-4">
          <div className="rounded-xl border bg-white p-5">
            <div className="text-xs font-medium uppercase text-slate-500">Plan score</div>
            <div className="mt-2 text-2xl font-bold text-slate-900">{result.score}</div>
            <div className="text-xs text-slate-500 mt-1">
              {result.assignments.length} assigned · {result.rejected.length} rejected
            </div>
          </div>

          <Table
            headers={["Route", "Vehicle", "Plate", "Score"]}
            rows={result.assignments.map((a) => [
              <span key="r" className="font-mono text-xs">{a.route_id.slice(0, 8)}…</span>,
              <span key="v" className="font-mono text-xs">{a.vehicle_id.slice(0, 8)}…</span>,
              a.vehicle_plate,
              a.score,
            ])}
          />
          {result.rejected.length > 0 && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
              <div className="font-medium">Rejected:</div>
              <ul className="mt-1 list-disc list-inside text-xs">
                {result.rejected.map((r, i) => <li key={i}>{r.route_id.slice(0, 8)}… — {r.reason}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function DashcamTab() {
  const [events, setEvents] = useState<DashcamEvent[]>([]);
  const [vs, setVs] = useState<Vehicle[]>([]);

  useEffect(() => {
    (async () => {
      const [e, v] = await Promise.all([dashcam.list(), vehiclesApi.list()]);
      setEvents(e);
      setVs(v.items);
    })().catch(console.error);
  }, []);

  return (
    <Table
      headers={["Vehicle", "Event type", "Severity", "Recorded"]}
      rows={events.map((e) => [
        vs.find((v) => v.id === e.vehicle_id)?.license_plate ?? e.vehicle_id.slice(0, 8),
        e.event_type,
        <span key="s" className={e.severity >= 8 ? "font-semibold text-red-700" : ""}>{e.severity}/10</span>,
        new Date(e.recorded_at).toLocaleString(),
      ])}
    />
  );
}

function TelematicsTab() {
  const [devices, setDevices] = useState<TelematicsDevice[]>([]);
  const [vs, setVs] = useState<Vehicle[]>([]);

  useEffect(() => {
    (async () => {
      const [d, v] = await Promise.all([telematics.devices(), vehiclesApi.list()]);
      setDevices(d);
      setVs(v.items);
    })().catch(console.error);
  }, []);

  return (
    <Table
      headers={["Vehicle", "Vendor", "Device ID", "Status", "Last seen"]}
      rows={devices.map((d) => [
        vs.find((v) => v.id === d.vehicle_id)?.license_plate ?? d.vehicle_id.slice(0, 8),
        d.vendor,
        <span key="i" className="font-mono text-xs">{d.device_id}</span>,
        d.status,
        d.last_seen_at ? new Date(d.last_seen_at).toLocaleString() : "—",
      ])}
    />
  );
}
