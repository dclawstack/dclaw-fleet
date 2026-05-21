"use client";

export function Input({
  label, value, onChange, type = "text", required,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-600">{label}</label>
      <input
        type={type}
        value={value}
        required={required}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-blue-500"
      />
    </div>
  );
}

export function Status({ value }: { value: string }) {
  const colors: Record<string, string> = {
    active: "bg-green-100 text-green-800",
    inactive: "bg-slate-200 text-slate-700",
    in_shop: "bg-amber-100 text-amber-800",
    scheduled: "bg-blue-100 text-blue-700",
    completed: "bg-green-100 text-green-800",
    overdue: "bg-red-100 text-red-700",
    available: "bg-green-100 text-green-800",
    in_use: "bg-blue-100 text-blue-700",
    optimized: "bg-green-100 text-green-800",
    draft: "bg-slate-200 text-slate-700",
  };
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${colors[value] ?? "bg-slate-200 text-slate-700"}`}>
      {value}
    </span>
  );
}

export function Table({ headers, rows }: { headers: string[]; rows: React.ReactNode[][] }) {
  return (
    <div className="overflow-hidden rounded-xl border bg-white">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-slate-50 text-left text-xs font-medium uppercase text-slate-500">
            {headers.map((h, i) => <th key={i} className="px-4 py-3">{h}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr><td colSpan={headers.length} className="px-4 py-10 text-center text-slate-400">No entries yet.</td></tr>
          ) : rows.map((cells, i) => (
            <tr key={i} className="border-t">
              {cells.map((c, j) => <td key={j} className="px-4 py-3 text-slate-700">{c}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
