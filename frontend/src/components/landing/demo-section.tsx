"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Database, Sparkles, Trash2, LogIn, AlertCircle, Terminal, RefreshCw,
} from "lucide-react";

import { api } from "@/lib/api";
import { setToken, setUser } from "@/lib/auth";

interface DemoStatus {
  enabled: boolean;
  seeded: boolean;
  vehicle_count: number;
  driver_count: number;
}

interface DemoSeedResult {
  status: DemoStatus;
  credentials: { email: string; password: string };
}

type DemoView =
  | { kind: "loading" }
  | { kind: "unreachable" }
  | { kind: "disabled" }
  | { kind: "ready"; seeded: boolean; vehicle_count: number; driver_count: number };

export function DemoSection() {
  const router = useRouter();
  const [view, setView] = useState<DemoView>({ kind: "loading" });
  const [credentials, setCredentials] = useState<{ email: string; password: string } | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadStatus() {
    setView({ kind: "loading" });
    try {
      const s = await api<DemoStatus>("/api/v1/demo/status");
      if (!s.enabled) {
        setView({ kind: "disabled" });
      } else {
        setView({
          kind: "ready",
          seeded: s.seeded,
          vehicle_count: s.vehicle_count,
          driver_count: s.driver_count,
        });
      }
    } catch {
      setView({ kind: "unreachable" });
    }
  }

  useEffect(() => { loadStatus(); }, []);

  async function handleSeed() {
    setBusy("seed");
    setError(null);
    try {
      const r = await api<DemoSeedResult>("/api/v1/demo/seed", { method: "POST" });
      setView({
        kind: "ready",
        seeded: r.status.seeded,
        vehicle_count: r.status.vehicle_count,
        driver_count: r.status.driver_count,
      });
      setCredentials(r.credentials);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Seed failed");
    } finally {
      setBusy(null);
    }
  }

  async function handleReset() {
    if (!confirm("Delete all DEMO-* records? Your real data is untouched.")) return;
    setBusy("reset");
    setError(null);
    try {
      const r = await api<DemoStatus>("/api/v1/demo/reset", { method: "DELETE" });
      setView({
        kind: "ready",
        seeded: r.seeded,
        vehicle_count: r.vehicle_count,
        driver_count: r.driver_count,
      });
      setCredentials(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Reset failed");
    } finally {
      setBusy(null);
    }
  }

  async function handleSignIn() {
    if (!credentials) return;
    setBusy("login");
    try {
      const res = await api<{ access_token: string }>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: credentials.email, password: credentials.password }),
      });
      setToken(res.access_token);
      const me = await api<{ id: string; email: string; name: string; role: string }>("/api/v1/auth/me");
      setUser({ id: me.id, email: me.email, name: me.name, role: me.role });
      router.push("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sign-in failed");
      setBusy(null);
    }
  }

  return (
    <section id="demo" className="border-b bg-gradient-to-b from-white to-blue-50/40">
      <div className="mx-auto max-w-4xl px-6 py-20">
        <div className="text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-white px-3 py-1 text-xs font-semibold text-blue-700">
            <Database className="h-3 w-3" /> Try it instantly
          </span>
          <h2 className="mt-3 text-3xl font-bold text-slate-900 md:text-4xl">Seed sample data and dive in</h2>
          <p className="mx-auto mt-4 max-w-2xl text-slate-600">
            One-click sample fleet — vehicles, drivers, maintenance, fuel, geofences — plus a
            demo dispatcher account. Reset wipes only the DEMO-* records.
          </p>
        </div>

        <div className="mx-auto mt-10 max-w-2xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          {view.kind === "loading" && (
            <div className="flex items-center justify-center gap-2 py-6 text-sm text-slate-400">
              <RefreshCw className="h-4 w-4 animate-spin" /> Checking backend…
            </div>
          )}

          {view.kind === "unreachable" && <UnreachableState onRetry={loadStatus} />}

          {view.kind === "disabled" && <DisabledState onRetry={loadStatus} />}

          {view.kind === "ready" && (
            <>
              <div className="grid grid-cols-2 gap-4 text-center">
                <Stat label="Sample vehicles" value={view.vehicle_count} />
                <Stat label="Sample drivers" value={view.driver_count} />
              </div>

              {error && (
                <div className="mt-4 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                  <AlertCircle className="h-4 w-4 mt-0.5" /> {error}
                </div>
              )}

              {!view.seeded ? (
                <button
                  onClick={handleSeed}
                  disabled={busy !== null}
                  className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
                >
                  <Sparkles className={`h-4 w-4 ${busy === "seed" ? "animate-spin" : ""}`} />
                  {busy === "seed" ? "Seeding…" : "Seed demo data"}
                </button>
              ) : (
                <>
                  {credentials && (
                    <div className="mt-6 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm">
                      <p className="font-semibold text-blue-900">Demo credentials</p>
                      <p className="mt-1 font-mono text-blue-800">
                        {credentials.email} / {credentials.password}
                      </p>
                    </div>
                  )}
                  <div className="mt-6 flex flex-col gap-3 sm:flex-row">
                    <button
                      onClick={handleSignIn}
                      disabled={busy !== null || !credentials}
                      className="inline-flex flex-1 items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
                    >
                      <LogIn className="h-4 w-4" />
                      {busy === "login" ? "Signing in…" : "Sign in as demo dispatcher"}
                    </button>
                    <button
                      onClick={handleReset}
                      disabled={busy !== null}
                      className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 px-6 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
                    >
                      <Trash2 className={`h-4 w-4 ${busy === "reset" ? "animate-spin" : ""}`} />
                      Clear demo data
                    </button>
                  </div>
                  {!credentials && (
                    <p className="mt-3 text-center text-xs text-slate-400">
                      Demo data already seeded. Click "Clear demo data" then "Seed demo data" to retrieve credentials.
                    </p>
                  )}
                </>
              )}
            </>
          )}
        </div>
      </div>
    </section>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
      <div className="text-2xl font-bold text-slate-900">{value}</div>
      <div className="text-xs text-slate-500">{label}</div>
    </div>
  );
}

function UnreachableState({ onRetry }: { onRetry: () => void }) {
  return (
    <div>
      <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
        <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
        <div>
          <p className="font-semibold">Backend not reachable from this page</p>
          <p className="mt-1 text-amber-800">
            This Vercel preview hosts the frontend only. To use the seed flow, run the full stack
            locally — Docker Compose ships with demo mode enabled.
          </p>
        </div>
      </div>

      <div className="mt-4 rounded-xl border border-slate-200 bg-slate-900 p-4 text-xs text-slate-100">
        <div className="mb-2 flex items-center gap-2 text-slate-400">
          <Terminal className="h-4 w-4" /> Run locally
        </div>
        <pre className="overflow-x-auto font-mono text-xs leading-relaxed">{`git clone https://github.com/dclawstack/dclaw-fleet
cd dclaw-fleet
docker compose up
# → frontend: http://localhost:3051
# → backend:  http://localhost:8051`}</pre>
      </div>

      <button
        onClick={onRetry}
        className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        <RefreshCw className="h-4 w-4" /> Retry status check
      </button>
    </div>
  );
}

function DisabledState({ onRetry }: { onRetry: () => void }) {
  return (
    <div>
      <div className="flex items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
        <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0 text-slate-500" />
        <div>
          <p className="font-semibold text-slate-900">Demo mode is disabled</p>
          <p className="mt-1">
            The backend is up but <code className="rounded bg-slate-200 px-1 py-0.5 font-mono text-xs">ENABLE_DEMO_MODE</code> is off.
            Set the env var to <code className="rounded bg-slate-200 px-1 py-0.5 font-mono text-xs">true</code> on the backend
            (already on in <code className="rounded bg-slate-200 px-1 py-0.5 font-mono text-xs">docker-compose.yml</code>) to enable.
          </p>
        </div>
      </div>
      <button
        onClick={onRetry}
        className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        <RefreshCw className="h-4 w-4" /> Retry status check
      </button>
    </div>
  );
}
