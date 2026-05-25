"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { FleetCopilot } from "@/components/fleet-copilot";
import { NavShell } from "@/components/nav-shell";
import { getToken } from "@/lib/auth";

const PUBLIC_PATHS = new Set(["/login"]);

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname() ?? "/";
  const router = useRouter();
  const [authed, setAuthed] = useState<boolean | null>(null);

  useEffect(() => {
    const t = getToken();
    if (!t && !PUBLIC_PATHS.has(pathname)) {
      router.replace("/login");
      setAuthed(false);
      return;
    }
    setAuthed(!!t);
  }, [pathname, router]);

  if (PUBLIC_PATHS.has(pathname)) {
    return <>{children}</>;
  }

  if (authed === null) {
    return <div className="flex min-h-screen items-center justify-center text-sm text-slate-400">Loading…</div>;
  }

  if (!authed) {
    return null; // redirect already in flight
  }

  return (
    <>
      <NavShell>{children}</NavShell>
      <FleetCopilot />
    </>
  );
}
