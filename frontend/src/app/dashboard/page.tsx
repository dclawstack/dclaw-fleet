"use client";

import React, { useState } from "react";
import { Truck, Activity } from "lucide-react";
import { api, FleetStatus, VehicleStatus } from "@/lib/api";

export default function DashboardPage() {
  const [fleetId, setFleetId] = useState("");
  const [status, setStatus] = useState<FleetStatus | null>(null);
  const [vehicles, setVehicles] = useState<VehicleStatus[] | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleGetStatus(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setVehicles(null);
    try {
      const result = await api<FleetStatus>("/statuses", {
        method: "POST",
        body: JSON.stringify({ fleet_id: fleetId }),
      });
      setStatus(result);
      const veh = await api<VehicleStatus[]>(`/statuses/${result.id}/vehicles`);
      setVehicles(veh);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4 flex items-center gap-3">
        <Truck className="h-6 w-6" style={{ color: "#7C3AED" }} />
        <h1 className="text-xl font-bold" style={{ color: "#7C3AED" }}>
          DClaw Fleet
        </h1>
      </header>

      <section className="mx-auto max-w-2xl px-6 py-10">
        <h2 className="mb-6 text-2xl font-semibold text-slate-800">Dashboard</h2>

        <form onSubmit={handleGetStatus} className="mb-8 rounded-xl border bg-white p-6 shadow-sm">
          <div className="mb-6">
            <label htmlFor="fleet" className="mb-1 block text-sm font-medium text-slate-700">
              Fleet ID
            </label>
            <input
              id="fleet"
              type="text"
              value={fleetId}
              onChange={(e) => setFleetId(e.target.value)}
              placeholder="FLEET-001"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-[#7C3AED] focus:ring-1 focus:ring-[#7C3AED]"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-60"
            style={{ backgroundColor: "#7C3AED" }}
          >
            <Activity className="h-4 w-4" />
            {loading ? "Loading..." : "Get Fleet Status"}
          </button>
        </form>

        {status && (
          <div className="rounded-xl border bg-white p-6 shadow-sm">
            <h3 className="mb-4 text-lg font-semibold text-slate-800">Fleet Status</h3>
            <dl className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="rounded-lg bg-slate-50 p-3">
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">Active vehicles</dt>
                <dd className="mt-1 text-sm font-semibold text-slate-900">{status.active_vehicles}</dd>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">Avg fuel efficiency</dt>
                <dd className="mt-1 text-sm font-semibold text-slate-900">{status.avg_fuel_efficiency} km/L</dd>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">Maintenance due</dt>
                <dd className="mt-1 text-sm font-semibold text-slate-900">{status.maintenance_due_count}</dd>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">Route compliance</dt>
                <dd className="mt-1 text-sm font-semibold text-slate-900">{status.route_compliance_percent}%</dd>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">Status ID</dt>
                <dd className="mt-1 text-sm font-mono text-slate-900">{status.id}</dd>
              </div>
              <div className="rounded-lg bg-slate-50 p-3">
                <dt className="text-xs font-medium uppercase tracking-wide text-slate-500">Created at</dt>
                <dd className="mt-1 text-sm text-slate-900">{status.created_at}</dd>
              </div>
            </dl>

            {vehicles && vehicles.length > 0 && (
              <div className="mt-6">
                <h4 className="mb-3 text-sm font-semibold text-slate-700">Vehicle Statuses</h4>
                <div className="space-y-2">
                  {vehicles.map((v, i) => (
                    <div key={i} className="flex items-center justify-between rounded-lg bg-slate-50 p-3">
                      <div>
                        <div className="text-sm font-medium text-slate-900">{v.vehicle_id}</div>
                        <div className="text-xs text-slate-500">Driver: {v.driver}</div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-xs text-slate-500">{v.location}</span>
                        <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-700">{v.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </section>
    </main>
  );
}
