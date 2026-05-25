import { Bot, Sparkles } from "lucide-react";

const EXAMPLES = [
  { q: "How many drivers under 70 safety score?", a: "3 driver(s) under threshold. Pull /api/v1/driving-events/drivers/{id}/coaching for personalized tips." },
  { q: "Open claims?", a: "2 open claim(s); AI-predicted exposure ~$48,000." },
  { q: "Show overdue maintenance", a: "5 overdue tasks. Top items: oil_change (vehicle a3f5b…), brake_inspection (vehicle 8c2e1…)." },
  { q: "EV range?", a: "You have 4 electric vehicle(s). Per-vehicle range and charge recommendations at /api/v1/charging/vehicles/{id}/range." },
];

export function CopilotSection() {
  return (
    <section className="border-b bg-slate-900 text-white">
      <div className="mx-auto grid max-w-6xl gap-12 px-6 py-20 lg:grid-cols-2 lg:items-center">
        <div>
          <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-blue-300">
            <Sparkles className="h-3 w-3" /> AI Copilot mandate
          </span>
          <h2 className="mt-4 text-3xl font-bold md:text-4xl">
            Ask, and the fleet answers
          </h2>
          <p className="mt-4 leading-relaxed text-slate-300">
            Every page ships with a floating Copilot. It reads live state — vehicle counts, overdue PMs,
            low-MPG anomalies, expiring permits, pending expenses, open claims, low-stock parts — and
            classifies your question across 18 intents.
          </p>
          <ul className="mt-6 space-y-2 text-sm text-slate-300">
            <li>· Contextually aware of every domain (vehicles → carbon footprint)</li>
            <li>· Suggests next actions, not just answers</li>
            <li>· Stub LLM today, OpenRouter + Ollama-fallback ready</li>
            <li>· Persistent chat sessions stored in Postgres</li>
          </ul>
        </div>

        <div className="rounded-2xl border border-white/10 bg-slate-800/70 p-6 shadow-2xl">
          <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-slate-200">
            <Bot className="h-4 w-4 text-blue-400" /> Fleet Copilot
          </div>
          <div className="space-y-3">
            {EXAMPLES.map((e, i) => (
              <div key={i}>
                <div className="ml-auto max-w-[85%] rounded-xl bg-blue-600 px-3 py-2 text-sm text-white">
                  {e.q}
                </div>
                <div className="mt-1 mr-auto max-w-[85%] rounded-xl bg-slate-700 px-3 py-2 text-sm text-slate-100">
                  {e.a}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
