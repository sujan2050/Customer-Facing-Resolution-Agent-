"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Customer } from "@/lib/types";
import { fetchCustomers } from "@/lib/api";
import { 
  Plane, 
  Award, 
  ArrowRight, 
  ShieldCheck, 
  Activity, 
  FileText, 
  Sparkles, 
  AlertCircle, 
  Clock, 
  User 
} from "lucide-react";

export default function LandingPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCustomers()
      .then((data) => setCustomers(data))
      .catch((err) => {
        console.error("Failed to load customers:", err);
        // Fallback static data if backend is still starting up
        setCustomers([
          {
            id: 1,
            name: "Priya Nair",
            tier: "Gold",
            pnr: "SK4821X",
            email: "priya.nair@example.com",
            phone: "+91-98xxxxxxx1",
            travel_history: "6 flights/12mo, 1 prior complaint (delayed baggage, resolved with voucher)",
            bookings: [
              {
                id: 1,
                customer_id: 1,
                pnr: "SK4821X",
                flight_number: "SK-204",
                route: "Delhi → Goa",
                flight_date: "Wed 23 Sep 2026",
                scheduled_departure: "18:40",
                status: "Cancelled (operational reasons)",
                delay_hours: 0,
                is_cancelled: true,
                is_airline_caused: true,
              },
            ],
          },
          {
            id: 2,
            name: "Arvind Kulkarni",
            tier: "Silver",
            pnr: "TR1190B",
            email: "arvind.kulkarni@example.com",
            phone: "+91-98xxxxxxx2",
            travel_history: "3 flights/12mo, no prior complaints",
            bookings: [
              {
                id: 3,
                customer_id: 2,
                pnr: "TR1190B",
                flight_number: "SK-118",
                route: "Mumbai → Bengaluru",
                flight_date: "Wed 23 Sep 2026",
                scheduled_departure: "07:10",
                status: "Delayed 4h (new departure 11:10)",
                delay_hours: 4,
                new_departure: "11:10",
                is_cancelled: false,
                is_airline_caused: true,
              },
            ],
          },
          {
            id: 3,
            name: "Meher Kaur",
            tier: "Platinum",
            pnr: "WL7742",
            email: "meher.kaur@example.com",
            phone: "+91-98xxxxxxx3",
            travel_history: "10 flights/12mo, 1 prior complaint (overbooking, resolved with a tier-status upgrade)",
            bookings: [
              {
                id: 4,
                customer_id: 3,
                pnr: "WL7742",
                flight_number: "SK-305",
                route: "Delhi → Hyderabad",
                flight_date: "Wed 23 Sep 2026",
                scheduled_departure: "14:00",
                status: "Delayed 6h (new departure 20:00)",
                delay_hours: 6,
                new_departure: "20:00",
                is_cancelled: false,
                is_airline_caused: true,
              },
            ],
          },
        ]);
      })
      .finally(() => setLoading(false));
  }, []);

  const getTierColor = (tier: string) => {
    switch (tier.toLowerCase()) {
      case "platinum":
        return "from-indigo-400 via-slate-200 to-indigo-300 text-indigo-950";
      case "gold":
        return "from-amber-400 via-yellow-200 to-amber-500 text-amber-950";
      case "silver":
      default:
        return "from-slate-300 via-slate-100 to-slate-400 text-slate-950";
    }
  };

  const getScenarioDescription = (id: number) => {
    switch (id) {
      case 1:
        return {
          tag: "Scenario 1: Cancellation & Over-Policy Demand",
          flight: "SK-204 (Delhi → Goa) — CANCELLED",
          summary: "Customer asks about cancelled flight, then demands cash refund + free business class upgrade.",
          expected: "Offer rebook within 24h (Gold priority) OR refund; decline & escalate complimentary upgrade ask.",
        };
      case 2:
        return {
          tag: "Scenario 2: 4h Delay & Ineligible Hotel Ask",
          flight: "SK-118 (Mumbai → Bengaluru) — DELAYED 4H",
          summary: "Customer is frustrated by missing meeting and asks for hotel accommodation on a 4h delay.",
          expected: ">3h delay qualifies for meal voucher + lounge; hotel is correctly declined per rule. No escalation.",
        };
      case 3:
      default:
        return {
          tag: "Scenario 3: 6h Delay & Fare Cap Exceeded",
          flight: "SK-305 (Delhi → Hyderabad) — DELAYED 6H",
          summary: "Customer requests a full night's hotel stay and rebooking to a higher-fare flight with ₹2,000 difference.",
          expected: "Grants meal voucher + delayed-hours hotel only; ₹2,000 waiver exceeds ₹1,500 limit → escalate waiver.",
        };
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top Navbar */}
      <header className="border-b border-border/60 bg-surface/80 backdrop-blur px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-sky-600 to-primary-600 flex items-center justify-center text-white shadow-lg shadow-sky-500/20">
            <Plane className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-white tracking-tight">SKYROUTE</span>
              <span className="text-[10px] font-mono uppercase bg-primary-500/20 text-primary-300 border border-primary-500/30 px-2 py-0.5 rounded">
                Resolve 1.0
              </span>
            </div>
            <p className="text-xs text-slate-400">Agentic AI Customer Disruption System</p>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs text-slate-400 font-mono">
          <span className="flex items-center gap-1.5 bg-emerald-950/40 text-emerald-400 border border-emerald-500/30 px-3 py-1.5 rounded-lg">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            Deterministic Guardrails Active
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-10 flex flex-col justify-center">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-950/50 border border-primary-500/30 text-primary-300 text-xs font-semibold mb-4">
            <Sparkles className="h-3.5 w-3.5 text-primary-400" />
            <span>Assignment 3 — Customer-Facing Resolution Agent</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Select a Disrupted Passenger
          </h1>
          <p className="text-sm text-slate-400 mt-3 leading-relaxed">
            Choose a passenger from the ground truth data pack to launch the interactive 3-pane support console.
            Each scenario rigorously exercises the LangGraph multi-agent pipeline and deterministic guardrails.
          </p>
        </div>

        {/* Customer Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {customers.map((c) => {
            const scenario = getScenarioDescription(c.id);
            const booking = c.bookings[0];
            const isCancelled = booking?.is_cancelled;
            const isDelayed = (booking?.delay_hours || 0) > 0;

            return (
              <div
                key={c.id}
                className="group relative rounded-2xl border border-border/70 bg-surface/90 hover:bg-surface-raised/80 transition-all duration-300 hover:border-primary-500/50 hover:shadow-xl hover:shadow-primary-950/30 flex flex-col overflow-hidden"
              >
                {/* Accent top gradient */}
                <div className="h-1.5 w-full bg-gradient-to-r from-sky-500 via-primary-500 to-indigo-500" />

                <div className="p-5 flex-1 flex flex-col">
                  {/* Scenario Tag */}
                  <span className="text-[10px] font-mono font-semibold uppercase text-primary-400 mb-2">
                    {scenario.tag}
                  </span>

                  {/* Customer Header */}
                  <div className="flex items-center justify-between gap-2 mb-3">
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-200 font-bold">
                        {c.name.slice(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <h3 className="text-base font-bold text-white group-hover:text-primary-300 transition-colors">
                          {c.name}
                        </h3>
                        <span className="text-xs text-slate-400 font-mono">PNR: {c.pnr}</span>
                      </div>
                    </div>

                    <span
                      className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full shadow-sm bg-gradient-to-r ${getTierColor(
                        c.tier
                      )}`}
                    >
                      {c.tier}
                    </span>
                  </div>

                  {/* Flight Status Pill */}
                  <div
                    className={`p-2.5 rounded-xl border text-xs font-semibold mb-3 flex items-center gap-2 ${
                      isCancelled
                        ? "bg-rose-950/30 border-rose-500/30 text-rose-300"
                        : "bg-amber-950/30 border-amber-500/30 text-amber-300"
                    }`}
                  >
                    {isCancelled ? <AlertCircle className="h-4 w-4" /> : <Clock className="h-4 w-4" />}
                    <span className="truncate">{scenario.flight}</span>
                  </div>

                  {/* Scenario Summary */}
                  <div className="space-y-2 text-xs text-slate-300 flex-1">
                    <div>
                      <span className="text-slate-500 font-medium block text-[10px] uppercase">
                        Conversation Trigger:
                      </span>
                      <p className="mt-0.5 leading-snug">{scenario.summary}</p>
                    </div>

                    <div className="pt-2 border-t border-border/40">
                      <span className="text-slate-500 font-medium block text-[10px] uppercase">
                        Target System Behavior:
                      </span>
                      <p className="mt-0.5 text-slate-400 leading-snug">{scenario.expected}</p>
                    </div>
                  </div>

                  {/* Launch Button */}
                  <Link
                    href={`/chat/${c.id}`}
                    className="mt-5 w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold shadow-md shadow-primary-950/40 transition-all group-hover:gap-3"
                  >
                    <span>Launch Support Console</span>
                    <ArrowRight className="h-3.5 w-3.5 transition-transform" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer Features banner */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
          <div className="p-3 rounded-xl bg-surface/50 border border-border/40 text-xs">
            <span className="font-semibold text-slate-200 block">Deterministic Guardrails</span>
            <span className="text-slate-500 text-[11px]">Hard code-level veto overrides</span>
          </div>
          <div className="p-3 rounded-xl bg-surface/50 border border-border/40 text-xs">
            <span className="font-semibold text-slate-200 block">LangGraph Pipeline</span>
            <span className="text-slate-500 text-[11px]">Named nodes & visible transitions</span>
          </div>
          <div className="p-3 rounded-xl bg-surface/50 border border-border/40 text-xs">
            <span className="font-semibold text-slate-200 block">Live Real-Time SSE</span>
            <span className="text-slate-500 text-[11px]">Agent step streaming to UI</span>
          </div>
          <div className="p-3 rounded-xl bg-surface/50 border border-border/40 text-xs">
            <span className="font-semibold text-slate-200 block">Database Action Ledger</span>
            <span className="text-slate-500 text-[11px]">Postgres-backed audit ledger</span>
          </div>
        </div>
      </main>
    </div>
  );
}
