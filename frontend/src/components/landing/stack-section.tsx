const STACK = [
  { layer: "Frontend", tech: "Next.js 14 App Router, Tailwind, Leaflet/OpenStreetMap" },
  { layer: "Backend", tech: "FastAPI, Pydantic v2, SQLAlchemy 2.0 (async), asyncpg" },
  { layer: "Database", tech: "PostgreSQL 16 (CloudNativePG on K8s)" },
  { layer: "Auth", tech: "JWT (HS256) via python-jose, bcrypt password hashing" },
  { layer: "Migrations", tech: "Alembic — 4 revisions covering 22 tables" },
  { layer: "AI", tech: "OpenRouter (cloud) + Ollama (local fallback) — stubbed in v1.2" },
  { layer: "Deploy", tech: "Docker Compose for dev · Helm for K8s · Vercel for frontend" },
  { layer: "Testing", tech: "pytest-asyncio · 42 tests · real Postgres in CI" },
];

export function StackSection() {
  return (
    <section className="border-b bg-white">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <div className="text-center">
          <span className="text-xs font-semibold uppercase tracking-wider text-blue-600">Stack</span>
          <h2 className="mt-2 text-3xl font-bold text-slate-900 md:text-4xl">Boring tech, modern defaults</h2>
          <p className="mx-auto mt-4 max-w-2xl text-slate-600">
            The same non-negotiable DClaw stack you'd build by hand — assembled, migrated, and tested.
          </p>
        </div>

        <div className="mx-auto mt-12 max-w-3xl divide-y divide-slate-200 rounded-2xl border border-slate-200 bg-white">
          {STACK.map((row) => (
            <div key={row.layer} className="grid grid-cols-1 gap-2 px-6 py-4 md:grid-cols-[10rem_1fr] md:items-center md:gap-6">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">{row.layer}</span>
              <span className="text-sm text-slate-700">{row.tech}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
