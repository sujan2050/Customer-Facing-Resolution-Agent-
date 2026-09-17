"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Customer } from "@/lib/types";
import { Plane, Users, Shield, Award, Cpu } from "lucide-react";

interface HeaderProps {
  customers: Customer[];
  activeCustomerId: number;
}

export const Header: React.FC<HeaderProps> = ({ customers, activeCustomerId }) => {
  const router = useRouter();

  return (
    <header className="h-16 border-b border-border/60 bg-surface/90 backdrop-blur-md px-6 flex items-center justify-between z-20 shrink-0">
      {/* Brand & System Title */}
      <div className="flex items-center gap-4">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-sky-600 via-primary-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20 group-hover:scale-105 transition-transform">
            <Plane className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-base tracking-tight text-white">SKYROUTE</span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-primary-500/20 text-primary-300 border border-primary-500/30">
                Resolve 1.0
              </span>
            </div>
            <span className="text-[11px] text-slate-400 block -mt-0.5">
              Customer Disruption Resolution System
            </span>
          </div>
        </Link>
      </div>

      {/* Customer Switcher */}
      <div className="flex items-center gap-1.5 bg-surface-raised/80 p-1 rounded-xl border border-border/60">
        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 px-2.5">
          Active Passenger:
        </span>
        {customers.map((c) => {
          const isActive = c.id === activeCustomerId;
          return (
            <button
              key={c.id}
              onClick={() => router.push(`/chat/${c.id}`)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? "bg-primary-600 text-white shadow-sm shadow-primary-950/40"
                  : "text-slate-300 hover:text-white hover:bg-surface-raised"
              }`}
            >
              <span className="truncate max-w-[100px]">{c.name.split(" ")[0]}</span>
              <span
                className={`text-[9px] px-1.5 py-0.2 rounded font-bold uppercase ${
                  c.tier === "Gold"
                    ? "bg-amber-400/20 text-amber-300 border border-amber-400/30"
                    : c.tier === "Platinum"
                    ? "bg-indigo-300/20 text-indigo-200 border border-indigo-300/30"
                    : "bg-slate-400/20 text-slate-300 border border-slate-400/30"
                }`}
              >
                {c.tier}
              </span>
            </button>
          );
        })}
      </div>

      {/* Status & Engine Badge */}
      <div className="hidden md:flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-raised/60 border border-border/50 text-xs text-slate-300">
          <Cpu className="h-3.5 w-3.5 text-emerald-400" />
          <span className="font-mono text-[11px]">LangGraph Multi-Agent Engine</span>
        </div>
      </div>
    </header>
  );
};
