"use client";

import React from "react";
import { ActionLedgerItem } from "@/lib/types";
import { formatTimestamp } from "@/lib/utils";
import { 
  CheckCircle2, 
  ShieldAlert, 
  Ticket, 
  Coffee, 
  Hotel, 
  RotateCcw, 
  CalendarClock, 
  Scale,
  DollarSign
} from "lucide-react";

interface ActionLedgerProps {
  actions: ActionLedgerItem[];
}

export const ActionLedger: React.FC<ActionLedgerProps> = ({ actions }) => {
  const getActionIcon = (type: string) => {
    switch (type) {
      case "voucher_issued":
        return <Ticket className="h-3.5 w-3.5 text-amber-400" />;
      case "lounge_granted":
        return <Coffee className="h-3.5 w-3.5 text-sky-400" />;
      case "hotel_arranged":
        return <Hotel className="h-3.5 w-3.5 text-purple-400" />;
      case "refund_initiated":
        return <RotateCcw className="h-3.5 w-3.5 text-emerald-400" />;
      case "rebooked":
        return <CalendarClock className="h-3.5 w-3.5 text-blue-400" />;
      case "fare_waived":
        return <DollarSign className="h-3.5 w-3.5 text-cyan-400" />;
      case "escalated_to_supervisor":
      default:
        return <ShieldAlert className="h-3.5 w-3.5 text-rose-400" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case "COMPLETED":
        return (
          <span className="text-[10px] font-semibold text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-500/30 flex items-center gap-1">
            <CheckCircle2 className="h-2.5 w-2.5" />
            COMMITTED
          </span>
        );
      case "ESCALATED":
        return (
          <span className="text-[10px] font-semibold text-rose-400 bg-rose-950/50 px-2 py-0.5 rounded border border-rose-500/40 flex items-center gap-1">
            <ShieldAlert className="h-2.5 w-2.5" />
            ESCALATED
          </span>
        );
      default:
        return (
          <span className="text-[10px] font-semibold text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-700">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="flex flex-col h-full bg-surface/80 backdrop-blur-md rounded-xl border border-border/60 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-border/50 flex items-center justify-between bg-surface-raised/40">
        <div className="flex items-center gap-2">
          <Scale className="h-4 w-4 text-emerald-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Database Action Ledger
          </h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          {actions.length} Action{actions.length === 1 ? "" : "s"}
        </span>
      </div>

      {/* Actions List */}
      <div className="flex-1 p-3 overflow-y-auto space-y-2">
        {actions.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4 text-slate-500">
            <Scale className="h-6 w-6 mb-1.5 opacity-40" />
            <p className="text-xs font-medium">No actions committed yet.</p>
            <p className="text-[11px] text-slate-600 mt-0.5">
              Actions cleared by deterministic guardrails will be recorded here.
            </p>
          </div>
        ) : (
          actions.map((act) => (
            <div
              key={act.id}
              className={`p-3 rounded-lg border text-xs transition-all ${
                act.status === "ESCALATED"
                  ? "border-rose-500/40 bg-rose-950/20"
                  : "border-border/60 bg-surface-raised/40 hover:bg-surface-raised/60"
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-2">
                  <div className="p-1 rounded bg-slate-900 border border-slate-700">
                    {getActionIcon(act.action_type)}
                  </div>
                  <span className="font-semibold text-slate-200 font-mono text-xs">
                    {act.action_type.replace(/_/g, " ").toUpperCase()}
                  </span>
                </div>
                {getStatusBadge(act.status)}
              </div>

              {/* Rule Citation */}
              <div className="mt-1 flex items-start gap-1.5 text-[11px] text-slate-400">
                <span className="text-slate-500 shrink-0 font-medium">Rule Cited:</span>
                <span className="text-amber-300 font-mono bg-amber-950/30 px-1.5 py-0.5 rounded border border-amber-500/20 truncate">
                  {act.rule_cited}
                </span>
              </div>

              {/* Details if available */}
              {act.details_json && (
                <p className="mt-1.5 text-[11px] text-slate-300 leading-snug pl-1 border-l border-primary-500/40">
                  {act.details_json.description ||
                    act.details_json.reason ||
                    JSON.stringify(act.details_json)}
                </p>
              )}

              <div className="mt-2 text-[10px] text-slate-500 font-mono flex items-center justify-between">
                <span>Ledger #{act.id}</span>
                <span>{formatTimestamp(act.created_at)}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
