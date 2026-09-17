"use client";

import React from "react";
import { Customer } from "@/lib/types";
import { Plane, Calendar, Clock, MapPin, Award, User, Phone, Mail, History, AlertCircle, CheckCircle2 } from "lucide-react";

interface BookingSidebarProps {
  customer: Customer | null;
  loading: boolean;
}

export const BookingSidebar: React.FC<BookingSidebarProps> = ({ customer, loading }) => {
  if (loading || !customer) {
    return (
      <aside className="w-80 shrink-0 border-r border-border/60 bg-surface/50 p-4 space-y-4 animate-pulse">
        <div className="h-6 w-3/4 rounded bg-surface-raised" />
        <div className="h-24 rounded-lg bg-surface-raised" />
        <div className="h-48 rounded-lg bg-surface-raised" />
      </aside>
    );
  }

  const getTierBadge = (tier: string) => {
    switch (tier.toLowerCase()) {
      case "platinum":
        return "bg-gradient-to-r from-slate-200 via-indigo-100 to-slate-300 text-slate-900 border-white/60 shadow-indigo-500/20";
      case "gold":
        return "bg-gradient-to-r from-amber-400 via-yellow-300 to-amber-500 text-slate-950 border-amber-300/80 shadow-amber-500/30";
      case "silver":
      default:
        return "bg-gradient-to-r from-slate-400 via-slate-300 to-slate-400 text-slate-950 border-slate-300/80 shadow-slate-500/20";
    }
  };

  return (
    <aside className="w-80 shrink-0 border-r border-border/60 bg-surface/80 backdrop-blur-md flex flex-col h-full overflow-y-auto">
      {/* Header Profile */}
      <div className="p-4 border-b border-border/50">
        <div className="flex items-center justify-between mb-3">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Passenger Context
          </span>
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold border shadow-sm ${getTierBadge(
              customer.tier
            )}`}
          >
            <Award className="h-3 w-3" />
            {customer.tier} Tier
          </span>
        </div>

        <div className="flex items-start gap-3">
          <div className="h-10 w-10 rounded-xl bg-primary-600/20 border border-primary-500/30 flex items-center justify-center text-primary-400 font-semibold text-base">
            {customer.name.slice(0, 2).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="text-base font-semibold text-slate-100 truncate">{customer.name}</h3>
            <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono mt-0.5">
              <span>PNR:</span>
              <span className="font-semibold text-primary-400">{customer.pnr}</span>
            </div>
          </div>
        </div>

        {/* Contact Info */}
        <div className="mt-3 space-y-1 text-xs text-slate-400">
          <div className="flex items-center gap-2 truncate">
            <Mail className="h-3.5 w-3.5 shrink-0 text-slate-500" />
            <span className="truncate">{customer.email}</span>
          </div>
          {customer.phone && (
            <div className="flex items-center gap-2">
              <Phone className="h-3.5 w-3.5 shrink-0 text-slate-500" />
              <span>{customer.phone}</span>
            </div>
          )}
        </div>
      </div>

      {/* Travel History */}
      <div className="p-4 border-b border-border/50 bg-surface-raised/30">
        <div className="flex items-center gap-1.5 text-xs font-medium text-slate-300 mb-1.5">
          <History className="h-3.5 w-3.5 text-skyroute-blue" />
          <span>Verified Travel History (12mo)</span>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed bg-surface/70 p-2.5 rounded-lg border border-border/40">
          {customer.travel_history || "No recorded travel history"}
        </p>
      </div>

      {/* Bookings Section */}
      <div className="p-4 flex-1">
        <div className="flex items-center justify-between mb-3">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Booking Records (23 Sep 2026)
          </span>
          <span className="text-xs font-mono text-slate-500">{customer.bookings.length} Flight(s)</span>
        </div>

        <div className="space-y-3">
          {customer.bookings.map((booking) => {
            const isCancelled = booking.is_cancelled;
            const isDelayed = booking.delay_hours > 0;
            const isUnaffected = !isCancelled && !isDelayed;

            return (
              <div
                key={booking.id}
                className={`rounded-xl p-3 border transition-all ${
                  isCancelled
                    ? "border-rose-500/40 bg-rose-950/20 shadow-sm shadow-rose-950/20"
                    : isDelayed
                    ? "border-amber-500/40 bg-amber-950/20 shadow-sm shadow-amber-950/20"
                    : "border-slate-700/60 bg-surface-raised/40"
                }`}
              >
                {/* Flight header & badge */}
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <Plane className={`h-4 w-4 ${isCancelled ? "text-rose-400" : isDelayed ? "text-amber-400" : "text-emerald-400"}`} />
                    <span className="font-semibold text-sm text-slate-200">{booking.flight_number}</span>
                  </div>

                  {isCancelled && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                      <AlertCircle className="h-3 w-3" />
                      CANCELLED
                    </span>
                  )}
                  {isDelayed && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                      <Clock className="h-3 w-3" />
                      DELAYED {booking.delay_hours}H
                    </span>
                  )}
                  {isUnaffected && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      <CheckCircle2 className="h-3 w-3" />
                      UNAFFECTED
                    </span>
                  )}
                </div>

                {/* Route */}
                <div className="flex items-center gap-1.5 text-xs text-slate-300 font-medium mb-2">
                  <MapPin className="h-3.5 w-3.5 text-slate-500" />
                  <span>{booking.route}</span>
                </div>

                {/* Schedule Info */}
                <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400 bg-surface/60 p-2 rounded-lg border border-border/30">
                  <div>
                    <span className="block text-[10px] text-slate-500 uppercase">Scheduled</span>
                    <span className="text-slate-200 font-mono">{booking.scheduled_departure}</span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-slate-500 uppercase">
                      {isCancelled ? "Disruption" : isDelayed ? "New Departure" : "Status"}
                    </span>
                    <span className={`font-mono ${isCancelled ? "text-rose-400 font-semibold" : isDelayed ? "text-amber-400 font-semibold" : "text-emerald-400"}`}>
                      {isCancelled ? "Operational" : booking.new_departure || "On Time"}
                    </span>
                  </div>
                </div>

                {/* Status description */}
                <div className="mt-2 text-[10px] text-slate-400 flex items-center justify-between">
                  <span>{booking.status}</span>
                  {booking.is_airline_caused && (
                    <span className="text-[9px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded border border-slate-700">
                      Airline-Caused
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </aside>
  );
};
