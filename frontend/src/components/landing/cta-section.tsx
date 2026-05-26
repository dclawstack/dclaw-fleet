import Link from "next/link";
import { ArrowRight, Github } from "lucide-react";

export function CtaSection() {
  return (
    <section className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white">
      <div className="mx-auto max-w-4xl px-6 py-20 text-center">
        <h2 className="text-3xl font-bold md:text-4xl">Take it for a spin</h2>
        <p className="mx-auto mt-4 max-w-2xl text-blue-50">
          Seed sample fleet data above, sign in as the demo dispatcher, and explore every page —
          live map, maintenance calendar, expense approvals, AI copilot, the works.
        </p>
        <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <Link
            href="/login"
            className="inline-flex items-center gap-2 rounded-lg bg-white px-6 py-3 text-sm font-semibold text-blue-700 hover:bg-blue-50"
          >
            Sign in <ArrowRight className="h-4 w-4" />
          </Link>
          <a
            href="https://github.com/dclawstack/dclaw-fleet"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-lg border border-white/30 px-6 py-3 text-sm font-semibold text-white hover:bg-white/10"
          >
            <Github className="h-4 w-4" /> View source
          </a>
        </div>
      </div>
    </section>
  );
}

export function LandingFooter() {
  return (
    <footer className="border-t bg-slate-50">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-2 px-6 py-6 text-xs text-slate-500 md:flex-row">
        <span>© DClaw Fleet · built on the DClaw Stack</span>
        <span>
          <a className="hover:text-slate-700" href="https://github.com/dclawstack/dclaw-fleet" target="_blank" rel="noreferrer">
            github.com/dclawstack/dclaw-fleet
          </a>
        </span>
      </div>
    </footer>
  );
}
