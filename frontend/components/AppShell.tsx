"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ScanProvider, useScan } from "@/context/ScanContext";

const links = [
  { href: "/jobs", label: "Jobs" },
  { href: "/companies", label: "Companies" },
  { href: "/parsers", label: "Parsers" },
];

function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        {links.map((link) => {
          const active = pathname === link.href || pathname.startsWith(`${link.href}/`);
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`sidebar-link${active ? " active" : ""}`}
            >
              {link.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

function TopNav() {
  const { scanning, runScan } = useScan();

  return (
    <header className="top-nav">
      <Link href="/jobs" className="brand">
        Fleeting Jobs
      </Link>
      <button className="btn btn-sm" onClick={runScan} disabled={scanning}>
        {scanning ? "Scanning…" : "Scan jobs"}
      </button>
    </header>
  );
}

function ShellLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <TopNav />
      <div className="app-body">
        <Sidebar />
        <main className="main-content">{children}</main>
      </div>
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <ScanProvider>
      <ShellLayout>{children}</ShellLayout>
    </ScanProvider>
  );
}
