import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { FleetCopilot } from "@/components/fleet-copilot";
import { NavShell } from "@/components/nav-shell";

import "./globals.css";
import "leaflet/dist/leaflet.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "DClaw Fleet",
  description: "Fleet management on the DClaw Stack",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <NavShell>{children}</NavShell>
        <FleetCopilot />
      </body>
    </html>
  );
}
