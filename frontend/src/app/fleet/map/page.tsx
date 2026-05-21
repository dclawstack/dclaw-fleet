"use client";

import dynamic from "next/dynamic";

const LiveMap = dynamic(() => import("@/components/live-map").then((m) => m.LiveMap), {
  ssr: false,
  loading: () => <div className="flex h-[70vh] items-center justify-center text-slate-400">Loading map…</div>,
});

export default function FleetMapPage() {
  return (
    <div className="p-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Live Map</h1>
        <p className="mt-1 text-sm text-slate-500">Latest vehicle positions and active geofences.</p>
      </div>
      <LiveMap />
    </div>
  );
}
