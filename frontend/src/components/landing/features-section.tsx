import {
  Truck, Users, Wrench, Fuel, Map as MapIcon, Route,
  ShieldCheck, Receipt, Zap, AlertOctagon, Boxes, Sparkles, Leaf, Shuffle, Eye, Cpu,
} from "lucide-react";

type Feature = { icon: React.ComponentType<{ className?: string }>; title: string; desc: string };

const P0: Feature[] = [
  { icon: Sparkles, title: "AI Fleet Copilot", desc: "Floating chat that reads live fleet state — vehicles, drivers, maintenance, fuel, safety, compliance, expenses, EV, accidents, parts. Suggests next actions." },
  { icon: MapIcon, title: "Live GPS + Geofencing", desc: "Leaflet/OpenStreetMap live map, real-time vehicle markers, inclusion/exclusion geofences with breach alerts on every ping." },
  { icon: Wrench, title: "Preventive Maintenance", desc: "Auto-schedule PMs by mileage or time. Overdue detection, vehicle health score, work-order history." },
  { icon: Fuel, title: "Fuel Management", desc: "Per-vehicle MPG, anomaly detection (low MPG, suspected fraud >50% over average, odometer rollbacks)." },
];

const P1: Feature[] = [
  { icon: Users, title: "Driver Safety Scoring", desc: "Harsh-brake / speeding / idle / hard-corner events scored on a 30-day rolling window; personalized coaching tips per driver." },
  { icon: ShieldCheck, title: "Compliance & ELD", desc: "HOS clock (11h drive / 14h on-duty) with violations, DVIR reports, polymorphic permits with expired/expiring alerts." },
  { icon: Receipt, title: "Expense Management", desc: "Vendor-keyword auto-categorization (Shell→fuel, Marriott→lodging), fraud detection (oversize, duplicates, near-duplicates)." },
  { icon: Route, title: "DClaw Route Integration", desc: "Routes sync to external dispatcher with external_id; auto-assign rounds-robin across active vehicles, skips maintenance hold." },
];

const P2: Feature[] = [
  { icon: Zap, title: "EV Management", desc: "Charging sessions, AI range prediction (3 mi/kWh), off-peak charge-window recommendations." },
  { icon: AlertOctagon, title: "Accident & Claims", desc: "Incident log with severity-to-cost claim prediction and photo-count multiplier." },
  { icon: Boxes, title: "Parts & Inventory", desc: "Stock tracking with reorder thresholds; AI recommendations order back to 2× threshold." },
  { icon: Cpu, title: "Telematics", desc: "Register OEM/aftermarket/OBD-II devices; heartbeat ingest with anomaly detection (implausible speed, hot engine)." },
  { icon: Leaf, title: "Carbon Tracking", desc: "EPA factors over fuel logs; per-vehicle + fleet CO₂ with eco-routing and B20-blend suggestions." },
  { icon: Shuffle, title: "Autonomous Dispatch", desc: "Scoring-based vehicle/route pairing — active + safety-score bonus, overdue-maintenance penalty." },
  { icon: Eye, title: "AI Dashcams", desc: "Collision / distraction / lane-drift / hard-corner events feed the predictive layer and driver score." },
  { icon: Truck, title: "Predictive Maintenance", desc: "Component-level failure risk from odometer + driving events + dashcam history. Brake pads, transmission, tires, alignment." },
];

export function FeaturesSection() {
  return (
    <section id="features" className="border-b bg-white">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <div className="text-center">
          <span className="text-xs font-semibold uppercase tracking-wider text-blue-600">Feature roadmap</span>
          <h2 className="mt-2 text-3xl font-bold text-slate-900 md:text-4xl">Everything the v1.2 PRD calls for</h2>
          <p className="mx-auto mt-4 max-w-2xl text-slate-600">
            Sixteen modules shipped across P0 demo-ready, P1 platform, and P2 vertical tiers. Every feature ties back into the AI Copilot.
          </p>
        </div>

        <Tier label="P0 — Demo-ready" features={P0} accent="blue" />
        <Tier label="P1 — Platform" features={P1} accent="indigo" />
        <Tier label="P2 — Vertical" features={P2} accent="slate" />
      </div>
    </section>
  );
}

function Tier({ label, features, accent }: { label: string; features: Feature[]; accent: "blue" | "indigo" | "slate" }) {
  const chip =
    accent === "blue" ? "bg-blue-100 text-blue-700"
    : accent === "indigo" ? "bg-indigo-100 text-indigo-700"
    : "bg-slate-200 text-slate-700";
  return (
    <div className="mt-16">
      <span className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${chip}`}>{label}</span>
      <div className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-4">
        {features.map((f) => (
          <div key={f.title} className="rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-blue-200 hover:shadow-sm">
            <f.icon className="h-6 w-6 text-blue-600" />
            <h3 className="mt-3 text-sm font-semibold text-slate-900">{f.title}</h3>
            <p className="mt-1 text-sm text-slate-600">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
