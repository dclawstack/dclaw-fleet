"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Truck, Users, Wrench, Fuel, Map as MapIcon, Route, Package, LayoutDashboard,
  ShieldCheck, Receipt,
} from "lucide-react";

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
  { href: "/assets", label: "Assets", icon: Package },
];

export function NavShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      <aside className="w-60 border-r bg-white">
        <div className="px-5 py-5 flex items-center gap-2 border-b">
          <Truck className="h-5 w-5 text-blue-600" />
          <span className="font-bold text-blue-600">DClaw Fleet</span>
        </div>
        <nav className="p-3 space-y-1">
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
      </aside>
      <main className="flex-1 min-w-0">{children}</main>
    </div>
  );
}
