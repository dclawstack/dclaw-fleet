import Link from "next/link";
import { ArrowRight, Truck, Sparkles } from "lucide-react";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden border-b bg-gradient-to-b from-blue-50/60 via-white to-white">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,_rgba(37,99,235,0.12),_transparent_55%)]" />
      <div className="mx-auto max-w-6xl px-6 py-24 md:py-32">
        <div className="mx-auto max-w-3xl text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
            <Sparkles className="h-3 w-3" /> AI Fleet Copilot · YC S25/W26 mandate
          </span>
          <h1 className="mt-6 text-4xl font-bold tracking-tight text-slate-900 md:text-6xl">
            Run your fleet on
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent"> autopilot</span>
          </h1>
          <p className="mt-6 text-lg leading-relaxed text-slate-600 md:text-xl">
            DClaw Fleet is the open vertical SaaS for logistics teams. Vehicles, drivers, maintenance,
            compliance, fuel, expenses, EV charging, dashcam, accidents — all in one stack, all with
            an AI copilot that knows your data.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-700"
            >
              Sign in <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="#features"
              className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            >
              Explore features
            </Link>
          </div>
          <p className="mt-6 text-xs text-slate-400">
            <Truck className="mr-1 inline h-3 w-3" /> 12 feature modules · 50+ endpoints · self-host on K8s or run on Vercel
          </p>
        </div>
      </div>
    </section>
  );
}
