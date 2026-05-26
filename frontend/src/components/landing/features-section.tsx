import {
  Truck, Users, Wrench, Fuel, Map as MapIcon, Route,
  ShieldCheck, Receipt, Zap, AlertOctagon, Boxes, Sparkles, Leaf, Shuffle, Eye, Cpu,
} from "lucide-react";

type Feature = { icon: React.ComponentType<{ className?: string }>; title: string; desc: string };

const OPERATIONS: Feature[] = [
  { icon: Truck, title: "Vehicles & drivers", desc: "Full CRUD registry with VIN, plate, odometer, license, safety score. Assign drivers to vehicles in a click." },
  { icon: MapIcon, title: "Live GPS + geofencing", desc: "Leaflet/OpenStreetMap live map with real-time markers. Inclusion/exclusion geofences with breach alerts on every ping." },
  { icon: Wrench, title: "Maintenance scheduling", desc: "Auto-schedule preventive maintenance by mileage or time. Overdue detection, work-order history, per-vehicle health score." },
  { icon: Route, title: "Route planner & dispatch", desc: "Drag-and-drop stops, AI-optimized ordering with ETAs, auto-assign to vehicles skipping any on maintenance hold." },
];

const SAFETY: Feature[] = [
  { icon: Users, title: "Driver safety scoring", desc: "30-day rolling score from harsh-brake, speeding, idle, and hard-corner events. Personalized coaching tips per driver." },
  { icon: ShieldCheck, title: "HOS & DVIR compliance", desc: "11-hour drive / 14-hour on-duty clocks with violations. Pre/post-trip DVIR reports with pass/fail and defect notes." },
  { icon: AlertOctagon, title: "Accidents & claims", desc: "Incident log with AI severity-to-cost prediction. Photo count multiplier improves claim estimates." },
  { icon: Eye, title: "AI dashcams", desc: "Collision, distraction, lane-drift and hard-corner events stream into the predictive layer and the driver safety score." },
];

const COSTS: Feature[] = [
  { icon: Fuel, title: "Fuel anomaly detection", desc: "Per-vehicle MPG and total spend. Flags low MPG, suspected fraud (>50% over average price), and odometer rollbacks." },
  { icon: Receipt, title: "Expense management", desc: "Vendor-keyword auto-categorization (Shell→fuel, Marriott→lodging). Duplicate / oversize / near-duplicate detection." },
  { icon: Zap, title: "EV charging & range", desc: "Charging-session log with AI range prediction (3 mi/kWh) and off-peak charge-window recommendations." },
  { icon: Leaf, title: "Carbon footprint", desc: "Per-vehicle and fleet CO₂ computed from fuel logs using EPA factors. Eco-routing and B20-blend suggestions." },
];

const INTELLIGENCE: Feature[] = [
  { icon: Sparkles, title: "AI Fleet Copilot", desc: "Floating chat on every page that reads live state across all 16 modules and suggests the next action — not just answers." },
  { icon: Shuffle, title: "Autonomous dispatch", desc: "Scoring-based vehicle/route pairing. Bonus for safe drivers, penalty for overdue maintenance, skips inactive vehicles." },
  { icon: Boxes, title: "Parts inventory & reorder", desc: "Stock tracking with reorder thresholds. AI orders back to 2× threshold and tallies estimated cost per vendor." },
  { icon: Cpu, title: "Telematics & predictive maint", desc: "Register OEM / aftermarket / OBD-II devices. Heartbeats flag implausible speed and hot engines. Predicts component failure from telemetry." },
];

export function FeaturesSection() {
  return (
    <section id="features" className="border-b bg-white">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <div className="text-center">
          <span className="text-xs font-semibold uppercase tracking-wider text-blue-600">What's in the box</span>
          <h2 className="mt-2 text-3xl font-bold text-slate-900 md:text-4xl">Sixteen modules, one platform</h2>
          <p className="mx-auto mt-4 max-w-2xl text-slate-600">
            Everything a fleet team needs day-to-day, plus the AI layer that ties it all together.
            Every feature is real CRUD, real services, real tests — no mocks.
          </p>
        </div>

        <Group title="Fleet operations" desc="Track every vehicle, driver, and stop in real time." features={OPERATIONS} />
        <Group title="Safety & compliance" desc="DOT-grade reporting, driver coaching, and incident management." features={SAFETY} />
        <Group title="Cost & sustainability" desc="Find waste, prevent fraud, and shrink your carbon footprint." features={COSTS} />
        <Group title="AI intelligence" desc="Copilot, prediction, dispatch — built into every workflow." features={INTELLIGENCE} />
      </div>
    </section>
  );
}

function Group({ title, desc, features }: { title: string; desc: string; features: Feature[] }) {
  return (
    <div className="mt-16">
      <div className="mb-6">
        <h3 className="text-xl font-semibold text-slate-900">{title}</h3>
        <p className="mt-1 text-sm text-slate-500">{desc}</p>
      </div>
      <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-4">
        {features.map((f) => (
          <div key={f.title} className="rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-blue-200 hover:shadow-sm">
            <f.icon className="h-6 w-6 text-blue-600" />
            <h4 className="mt-3 text-sm font-semibold text-slate-900">{f.title}</h4>
            <p className="mt-1 text-sm text-slate-600">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
