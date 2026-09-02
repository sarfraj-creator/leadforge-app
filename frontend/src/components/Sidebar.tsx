"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  Building2,
  Contact2,
  Compass,
  Gauge,
  Kanban,
  Send,
  Inbox,
  CheckSquare,
  BarChart3,
  ShieldCheck,
  ClipboardCheck,
  Settings,
  Flame,
  LogOut,
  Sparkles
} from "lucide-react";

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  badge?: string;
}

const navItems: NavItem[] = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Leads", href: "/leads", icon: Flame, badge: "3 New" },
  { name: "Review Queue", href: "/review", icon: ClipboardCheck },
  { name: "Companies", href: "/companies", icon: Building2 },
  { name: "Contacts", href: "/contacts", icon: Contact2 },
  { name: "Discovery", href: "/discovery", icon: Compass },
  { name: "Website Audits", href: "/audits", icon: Gauge },
  { name: "CRM Pipeline", href: "/crm", icon: Kanban },
  { name: "Campaigns", href: "/campaigns", icon: Send },
  { name: "Inbox", href: "/inbox", icon: Inbox, badge: "1 Reply" },
  { name: "Tasks", href: "/tasks", icon: CheckSquare },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Data Quality", href: "/data-quality", icon: ShieldCheck },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div>
        {/* Brand Header */}
        <div className="h-16 flex items-center px-6 border-b border-slate-200 gap-3">
          <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center text-white font-bold text-base shadow-sm">
            LF
          </div>
          <div>
            <div className="font-bold text-sm text-slate-900 tracking-tight flex items-center gap-1.5">
              <span>LeadForge</span>
              <span className="text-[10px] font-semibold bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded border border-blue-200">
                PRO
              </span>
            </div>
            <div className="text-[11px] text-slate-500 font-medium">B2B Intelligence & CRM</div>
          </div>
        </div>

        {/* Navigation Items */}
        <div className="px-3 py-4 space-y-0.5">
          {navItems.map((item) => {
            const isActive = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition ${
                  isActive
                    ? "bg-blue-50 text-blue-700 font-semibold"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? "text-blue-600" : "text-slate-400"}`} />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${
                      isActive ? "bg-blue-200 text-blue-800" : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </div>
      </div>

      {/* User & Workspace Footer */}
      <div className="p-4 border-t border-slate-200 bg-slate-50/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center font-bold text-slate-700 text-xs">
              AM
            </div>
            <div className="min-w-0">
              <div className="text-xs font-bold text-slate-900 truncate">Alex Mercer</div>
              <div className="text-[11px] text-slate-500 truncate">Acme Growth Agency</div>
            </div>
          </div>
          <button
            title="Logout"
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded hover:bg-slate-200/50 transition"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
}
