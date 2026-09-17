"use client";

import React from "react";
import { AlertTriangle, UserCheck, ShieldAlert, ArrowUpRight } from "lucide-react";

interface EscalationBannerProps {
  escalated: boolean;
  reason?: string | null;
}

export const EscalationBanner: React.FC<EscalationBannerProps> = ({ escalated, reason }) => {
  if (!escalated) return null;

  return (
    <div className="relative overflow-hidden rounded-xl border border-rose-500/30 bg-gradient-to-r from-rose-950/60 via-amber-950/40 to-surface p-4 shadow-lg shadow-rose-950/20 transition-all duration-300 animate-fadeIn">
      {/* Glowing accent bar */}
      <div className="absolute top-0 left-0 bottom-0 w-1.5 bg-gradient-to-b from-rose-500 to-amber-500" />
      
      <div className="flex items-start justify-between gap-4 pl-2">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-rose-500/20 text-rose-400 ring-1 ring-rose-500/40">
            <ShieldAlert className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-500/20 px-2.5 py-0.5 text-xs font-semibold text-rose-300 ring-1 ring-inset ring-rose-500/30">
                <span className="h-1.5 w-1.5 rounded-full bg-rose-400 animate-ping" />
                HUMAN ESCALATION TRIGGERED
              </span>
              <span className="text-xs text-rose-300/80 font-mono">Agent Authority Exceeded</span>
            </div>
            <h4 className="mt-1 text-sm font-medium text-slate-100">
              Deterministic Guardrail Override
            </h4>
            <p className="mt-0.5 text-xs text-slate-300 leading-relaxed">
              {reason || "Request violates strict policy parameters and has been transferred to a human supervisor."}
            </p>
          </div>
        </div>

        <div className="hidden sm:flex flex-col items-end shrink-0 gap-1">
          <div className="flex items-center gap-1.5 rounded-lg bg-surface-raised px-3 py-1.5 text-xs font-medium text-amber-300 border border-amber-500/30">
            <UserCheck className="h-3.5 w-3.5" />
            <span>Supervisor Queued</span>
          </div>
          <span className="text-[10px] text-slate-400">Response SLA &lt; 5 mins</span>
        </div>
      </div>
    </div>
  );
};
