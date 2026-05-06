import Link from "next/link";
import { Truck } from "lucide-react";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 px-4">
      <div className="flex flex-col items-center gap-6 text-center">
        <Truck className="h-16 w-16" style={{ color: "#7C3AED" }} />
        <h1 className="text-5xl font-extrabold tracking-tight" style={{ color: "#7C3AED" }}>
          DClaw Fleet
        </h1>
        <p className="text-lg text-slate-300 max-w-md">
          Fleet management
        </p>
        <Link
          href="/dashboard"
          className="inline-flex items-center justify-center rounded-lg px-6 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-90"
          style={{ backgroundColor: "#7C3AED" }}
        >
          Go to Dashboard
        </Link>
      </div>
    </main>
  );
}
