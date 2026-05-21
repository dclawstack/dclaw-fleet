"use client";

import { useEffect, useState } from "react";
import { Truck, Users, Wrench, Fuel } from "lucide-react";

import { vehicles, drivers, maintenance, fuel as fuelApi } from "@/lib/api";

interface Summary {
  vehicles: number;
  drivers: number;
  overdueTasks: number;
  fuelLogs: number;
}

export default function DashboardPage() {
  const [s, setS] = useState<Summary | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const [v, d, ov, f] = await Promise.all([
          vehicles.list(),
          drivers.list(),
          maintenance.overdue(),
          fuelApi.list(),
        ]);
        setS({
          vehicles: v.meta.total,
          drivers: d.meta.total,
          overdueTasks: ov.length,
          fuelLogs: f.meta.total,
        });
      } catch (e) {
        console.error(e);
      }
    })();
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
      <p className="mt-1 text-sm text-slate-500">Operational snapshot of your fleet.</p>

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card title="Vehicles" value={s?.vehicles ?? "—"} icon={<Truck className="h-5 w-5" />} />
        <Card title="Drivers" value={s?.drivers ?? "—"} icon={<Users className="h-5 w-5" />} />
        <Card title="Overdue tasks" value={s?.overdueTasks ?? "—"} icon={<Wrench className="h-5 w-5" />} tone="warn" />
        <Card title="Fuel logs" value={s?.fuelLogs ?? "—"} icon={<Fuel className="h-5 w-5" />} />
      </div>

      <div className="mt-8 rounded-xl border bg-white p-6">
        <h2 className="text-sm font-semibold text-slate-700">Tip</h2>
        <p className="mt-1 text-sm text-slate-500">
          Click the <span className="font-medium text-blue-600">Fleet Copilot</span> button in the bottom-right
          to ask questions about your fleet — vehicles, drivers, maintenance, fuel, routes and geofences.
        </p>
      </div>
    </div>
  );
}

function Card({
  title, value, icon, tone,
}: { title: string; value: number | string; icon: React.ReactNode; tone?: "warn" }) {
  return (
    <div className="rounded-xl border bg-white p-5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide text-slate-500">{title}</span>
        <span className={tone === "warn" ? "text-amber-600" : "text-blue-600"}>{icon}</span>
      </div>
      <div className={`mt-2 text-2xl font-bold ${tone === "warn" ? "text-amber-700" : "text-slate-900"}`}>
        {value}
      </div>
    </div>
  );
}
