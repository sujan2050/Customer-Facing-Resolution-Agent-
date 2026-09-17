"use client";

import React, { useState } from "react";
import { AgentTraceItem } from "@/lib/types";
import { formatTimestamp } from "@/lib/utils";
import { 
  Bot, 
  CheckCircle2, 
  AlertCircle, 
  ShieldAlert, 
  Clock, 
  ChevronDown, 
  ChevronRight, 
  Sparkles, 
  Scale, 
  Database, 
  FileText,
  Activity
} from "lucide-react";

interface AgentTracePanelProps {
  traces: AgentTraceItem[];
  isStreaming: boolean;
}

export const AgentTracePanel: React.FC<AgentTracePanelProps> = ({ traces, isStreaming }) => {
  const [expandedIndices, setExpandedIndices] = useState<Record<number, boolean>>({});

  const toggleExpand = (idx: number) => {
    setExpandedIndices((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  const getAgentIcon = (agent: string) => {
    if (agent.includes("Context")) return <Database className="h-4 w-4 text-sky-400" />;
    if (agent.includes("Tone")) return <Sparkles className="h-4 w-4 text-pink-400" />;
    if (agent.includes("Router")) return <Bot className="h-4 w-4 text-indigo-400" />;
    if (agent.includes("Policy")) return <Scale className="h-4 w-4 text-amber-400" />;
    if (agent.includes("Guardrail")) return <ShieldAlert className="h-4 w-4 text-rose-400" />;
    if (agent.includes("Execution")) return <Activity className="h-4 w-4 text-emerald-400" />;
    return <FileText className="h-4 w-4 text-slate-400" />;
  };

  const getStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case "COMPLETED":
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded-full border border-emerald-500/30">
            <CheckCircle2 className="h-3 w-3" />
            COMPLETED
          </span>
        );
      case "ESCALATED":
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-rose-400 bg-rose-950/50 px-2 py-0.5 rounded-full border border-rose-500/40 animate-pulse">
            <ShieldAlert className="h-3 w-3" />
            ESCALATED / VETO
          </span>
        );
      case "WARNING":
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-amber-400 bg-amber-950/40 px-2 py-0.5 rounded-full border border-amber-500/30">
            <AlertCircle className="h-3 w-3" />
            LIMIT ENFORCED
          </span>
        );
      case "RUNNING":
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-blue-400 bg-blue-950/40 px-2 py-0.5 rounded-full border border-blue-500/30">
            <Clock className="h-3 w-3 animate-spin" />
            RUNNING
          </span>
        );
    }
  };

  return (
    <div className="flex flex-col h-full bg-surface/80 backdrop-blur-md rounded-xl border border-border/60 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-border/50 flex items-center justify-between bg-surface-raised/40">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-sky-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            Agent Reasoning Trace
          </h3>
        </div>
        <div className="flex items-center gap-2">
          {isStreaming && (
            <span className="flex items-center gap-1.5 text-[10px] font-medium text-sky-400 bg-sky-950/40 px-2 py-0.5 rounded-full border border-sky-500/30 animate-pulse">
              <span className="h-1.5 w-1.5 rounded-full bg-sky-400" />
              Graph Executing Live
            </span>
          )}
          <span className="text-[11px] font-mono text-slate-400">
            {traces.length} Node Transition{traces.length === 1 ? "" : "s"}
          </span>
        </div>
      </div>

      {/* Traces List */}
      <div className="flex-1 p-3 overflow-y-auto space-y-2.5">
        {traces.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-500">
            <Bot className="h-8 w-8 mb-2 opacity-40" />
            <p className="text-xs font-medium">No active agent pipeline execution.</p>
            <p className="text-[11px] mt-1 text-slate-600">
              Send a customer prompt or select a test scenario to watch the LangGraph nodes reason live.
            </p>
          </div>
        ) : (
          traces.map((trace, idx) => {
            const isExpanded = !!expandedIndices[idx];
            const isVeto = trace.status === "ESCALATED";

            return (
              <div
                key={idx}
                className={`rounded-lg border text-xs transition-all duration-200 ${
                  isVeto
                    ? "border-rose-500/50 bg-rose-950/20 shadow-sm shadow-rose-950/30"
                    : trace.status === "WARNING"
                    ? "border-amber-500/40 bg-amber-950/15"
                    : "border-border/60 bg-surface-raised/30 hover:bg-surface-raised/50"
                }`}
              >
                {/* Agent Header Item */}
                <div
                  className="p-3 cursor-pointer select-none"
                  onClick={() => toggleExpand(idx)}
                >
                  <div className="flex items-center justify-between gap-2 mb-1.5">
                    <div className="flex items-center gap-2">
                      <div className="p-1 rounded bg-slate-800/80 border border-slate-700/60">
                        {getAgentIcon(trace.agent)}
                      </div>
                      <span className="font-semibold text-slate-200 text-[13px]">
                        {trace.agent}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusBadge(trace.status)}
                      <button className="text-slate-400 hover:text-slate-200">
                        {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>

                  {/* Summary */}
                  <p className="text-slate-300 text-xs font-normal leading-relaxed pl-1">
                    {trace.summary}
                  </p>

                  {/* Rule cited pill */}
                  {trace.rule_cited && (
                    <div className="mt-2 flex items-center gap-1.5 pl-1">
                      <Scale className="h-3 w-3 text-amber-400 shrink-0" />
                      <span className="text-[11px] font-mono text-amber-300/90 bg-amber-950/40 px-2 py-0.5 rounded border border-amber-500/30 truncate">
                        {trace.rule_cited}
                      </span>
                    </div>
                  )}

                  <div className="mt-2 flex items-center justify-between text-[10px] text-slate-500 pl-1 font-mono">
                    <span>Step #{idx + 1}</span>
                    <span>{formatTimestamp(trace.timestamp)}</span>
                  </div>
                </div>

                {/* Expanded Details JSON */}
                {isExpanded && trace.details && (
                  <div className="px-3 pb-3 pt-1 border-t border-border/40 bg-black/40">
                    <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider block mb-1">
                      Agent State Payload:
                    </span>
                    <pre className="text-[11px] font-mono text-slate-300 bg-slate-950 p-2.5 rounded border border-slate-800 overflow-x-auto">
                      {JSON.stringify(trace.details, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
