"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Truck, Users, Wrench, Fuel, Map as MapIcon, Route, Package, LayoutDashboard,
  ShieldCheck, Receipt, Zap, AlertOctagon, Boxes, Sparkles, LogOut,
} from "lucide-react";

import { clearAuth, getUser, type AuthUser } from "@/lib/auth";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/vehicles", label: "Vehicles", icon: Truck },
  { href: "/drivers", label: "Drivers", icon: Users },
  { href: "/fleet/map", label: "Live Map", icon: MapIcon },
  { href: "/maintenance", label: "Maintenance", icon: Wrench },
  { href: "/fuel", label: "Fuel", icon: Fuel },
  { href: "/routes", label: "Routes", icon: Route },
  { href: "/compliance", label: "Compliance", icon: ShieldCheck },
  { href: "/expenses", label: "Expenses", icon: Receipt },
  { href: "/ev", label: "EV", icon: Zap },
  { href: "/accidents", label: "Accidents", icon: AlertOctagon },
  { href: "/parts", label: "Parts", icon: Boxes },
  { href: "/operations", label: "AI Ops", icon: Sparkles },
  { href: "/assets", label: "Assets", icon: Package },
];

export function NavShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUserState] = useState<AuthUser | null>(null);

  useEffect(() => {
    setUserState(getUser());
  }, []);

  function handleLogout() {
    clearAuth();
    router.replace("/login");
  }

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      <aside className="flex w-60 flex-col border-r bg-white">
        <div className="px-5 py-5 flex items-center gap-2 border-b">
          <Truck className="h-5 w-5 text-blue-600" />
          <span className="font-bold text-blue-600">DClaw Fleet</span>
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = pathname === href || pathname?.startsWith(href + "/");
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm",
                  active
                    ? "bg-blue-50 text-blue-700 font-semibold"
                    : "text-slate-700 hover:bg-slate-100"
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t p-3">
          {user && (
            <div className="mb-2 px-2 text-xs">
              <div className="font-medium text-slate-900">{user.name}</div>
              <div className="text-slate-500 truncate">{user.email}</div>
              <div className="mt-0.5 inline-block rounded-full bg-slate-100 px-2 py-0.5 text-[10px] uppercase tracking-wide text-slate-600">{user.role}</div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
          >
            <LogOut className="h-4 w-4" /> Sign out
          </button>
        </div>
      </aside>
      <main className="flex-1 min-w-0">{children}</main>
    </div>
  );
}
