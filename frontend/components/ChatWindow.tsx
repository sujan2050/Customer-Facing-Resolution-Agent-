"use client";

import React, { useState, useRef, useEffect } from "react";
import { Customer, MessageItem } from "@/lib/types";
import { EscalationBanner } from "./EscalationBanner";
import { formatTimestamp } from "@/lib/utils";
import { Send, RotateCcw, Bot, User, Sparkles, AlertCircle, ArrowRight, ShieldCheck } from "lucide-react";

interface ChatWindowProps {
  customer: Customer;
  messages: MessageItem[];
  isStreaming: boolean;
  escalated: boolean;
  escalationReason?: string | null;
  onSendMessage: (message: string) => void;
  onResetConversation: () => void;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({
  customer,
  messages,
  isStreaming,
  escalated,
  escalationReason,
  onSendMessage,
  onResetConversation,
}) => {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;
    onSendMessage(input.trim());
    setInput("");
  };

  const handleQuickPrompt = (promptText: string) => {
    if (isStreaming) return;
    onSendMessage(promptText);
  };

  // Scenario quick helpers tailored to current customer
  const renderQuickPrompts = () => {
    if (customer.id === 1) {
      return (
        <div className="flex flex-wrap gap-2 mb-3">
          <button
            onClick={() => handleQuickPrompt("My flight SK-204 from Delhi to Goa was cancelled. What are my options?")}
            disabled={isStreaming}
            className="text-xs bg-surface-raised hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 disabled:opacity-50"
          >
            <span className="font-semibold text-skyroute-gold">Scenario 1 (Part 1):</span>
            <span>Check Cancellation</span>
            <ArrowRight className="h-3 w-3 text-slate-400" />
          </button>
          <button
            onClick={() =>
              handleQuickPrompt(
                "I am furious! I want a full cash refund plus a free upgrade to business class on my return flight for the trouble."
              )
            }
            disabled={isStreaming}
            className="text-xs bg-rose-950/40 hover:bg-rose-900/50 text-rose-200 border border-rose-800/60 px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 disabled:opacity-50"
          >
            <span className="font-semibold text-rose-300">Scenario 1 (Part 2):</span>
            <span>Demand Refund + Business Upgrade</span>
            <ArrowRight className="h-3 w-3 text-rose-400" />
          </button>
        </div>
      );
    }

    if (customer.id === 2) {
      return (
        <div className="flex flex-wrap gap-2 mb-3">
          <button
            onClick={() =>
              handleQuickPrompt(
                "My flight SK-118 is delayed 4 hours. I am frustrated about missing my meeting. Can you arrange hotel accommodation since it has been such a long delay?"
              )
            }
            disabled={isStreaming}
            className="text-xs bg-surface-raised hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 disabled:opacity-50"
          >
            <span className="font-semibold text-skyroute-silver">Scenario 2:</span>
            <span>Ask for Hotel on 4h Delay</span>
            <ArrowRight className="h-3 w-3 text-slate-400" />
          </button>
        </div>
      );
    }

    if (customer.id === 3) {
      return (
        <div className="flex flex-wrap gap-2 mb-3">
          <button
            onClick={() =>
              handleQuickPrompt(
                "My flight SK-305 is delayed 6 hours. I want a full night's hotel stay rather than just waiting at the airport, and I want to be moved onto a different, higher-fare flight instead with a ₹2,000 fare difference."
              )
            }
            disabled={isStreaming}
            className="text-xs bg-surface-raised hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-1.5 rounded-lg transition-all flex items-center gap-1.5 disabled:opacity-50"
          >
            <span className="font-semibold text-indigo-300">Scenario 3:</span>
            <span>Full Night Hotel + ₹2,000 Fare Difference Rebook</span>
            <ArrowRight className="h-3 w-3 text-slate-400" />
          </button>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-background relative overflow-hidden">
      {/* Top Header */}
      <div className="px-6 py-3 border-b border-border/50 bg-surface/50 flex items-center justify-between backdrop-blur">
        <div className="flex items-center gap-3">
          <div className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <div>
            <h2 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              SkyRoute Live Support Console
              <span className="text-xs font-normal text-slate-400 font-mono">
                [Session Active: {customer.name}]
              </span>
            </h2>
          </div>
        </div>

        <button
          onClick={onResetConversation}
          title="Reset this conversation history and action ledger"
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 bg-surface-raised px-2.5 py-1.5 rounded-lg border border-border/60 transition-colors"
        >
          <RotateCcw className="h-3.5 w-3.5" />
          <span>Reset Session</span>
        </button>
      </div>

      {/* Escalation Alert Banner */}
      <div className="px-6 pt-4">
        <EscalationBanner escalated={escalated} reason={escalationReason} />
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 max-w-md mx-auto">
            <div className="h-12 w-12 rounded-2xl bg-primary-500/10 border border-primary-500/30 flex items-center justify-center text-primary-400 mb-4">
              <Bot className="h-6 w-6" />
            </div>
            <h3 className="text-base font-semibold text-slate-100">
              SkyRoute Disruption Resolution Agent
            </h3>
            <p className="text-xs text-slate-400 mt-1.5 leading-relaxed">
              Assisting passenger <span className="font-semibold text-slate-200">{customer.name}</span> ({customer.tier} Tier).
              Select one of the pre-configured scenarios below or ask any disruption question.
            </p>

            <div className="mt-6 w-full space-y-2 text-left">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block">
                Recommended Test Action:
              </span>
              {renderQuickPrompts()}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, index) => {
              const isAssistant = msg.role === "assistant";
              return (
                <div
                  key={index}
                  className={`flex gap-3 max-w-3xl ${isAssistant ? "mr-auto" : "ml-auto flex-row-reverse"}`}
                >
                  <div
                    className={`h-8 w-8 rounded-lg shrink-0 flex items-center justify-center text-xs font-semibold ${
                      isAssistant
                        ? "bg-primary-600 text-white shadow-md shadow-primary-900/40"
                        : "bg-slate-700 text-slate-200"
                    }`}
                  >
                    {isAssistant ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                  </div>

                  <div className={`space-y-1 ${isAssistant ? "text-left" : "text-right"}`}>
                    <div
                      className={`p-4 rounded-2xl text-sm leading-relaxed whitespace-pre-line shadow-sm ${
                        isAssistant
                          ? "bg-surface border border-border/70 text-slate-200 rounded-tl-none"
                          : "bg-primary-600 text-white rounded-tr-none font-normal"
                      }`}
                    >
                      {msg.content}
                    </div>

                    <div className="text-[10px] text-slate-500 font-mono px-1">
                      {isAssistant ? "SkyRoute Agent Pipeline" : customer.name} •{" "}
                      {formatTimestamp(msg.created_at)}
                    </div>
                  </div>
                </div>
              );
            })}

            {isStreaming && (
              <div className="flex gap-3 max-w-2xl mr-auto animate-pulse">
                <div className="h-8 w-8 rounded-lg bg-primary-600 text-white flex items-center justify-center">
                  <Bot className="h-4 w-4 animate-spin" />
                </div>
                <div className="bg-surface border border-border/70 p-3.5 rounded-2xl rounded-tl-none text-xs text-slate-400 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-sky-400 animate-spin" />
                  <span>Agents reasoning through state graph…</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Bottom Input Area */}
      <div className="p-4 border-t border-border/50 bg-surface/60 backdrop-blur">
        {messages.length > 0 && renderQuickPrompts()}

        {/* Universal sample prompt: legal threat test */}
        <div className="flex items-center justify-between mb-2">
          <button
            onClick={() =>
              handleQuickPrompt("This is unacceptable, I'm going to file a formal complaint and consider legal action over this.")
            }
            disabled={isStreaming}
            className="text-[11px] text-rose-400 hover:text-rose-300 transition-colors flex items-center gap-1 disabled:opacity-40"
          >
            <AlertCircle className="h-3 w-3" />
            <span>Test Legal Threat / Formal Complaint Trigger (Sample C)</span>
          </button>
          <span className="text-[10px] text-slate-500 font-mono">LangGraph State Orchestrator</span>
        </div>

        <form onSubmit={handleSubmit} className="flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isStreaming}
            placeholder={`Message SkyRoute Support on behalf of ${customer.name}...`}
            className="flex-1 bg-surface-raised border border-border/80 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 outline-none transition-all disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isStreaming}
            className="h-11 px-5 rounded-xl bg-primary-600 hover:bg-primary-500 text-white text-xs font-semibold flex items-center gap-2 transition-all shadow-md shadow-primary-950/50 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Send className="h-3.5 w-3.5" />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  );
};
