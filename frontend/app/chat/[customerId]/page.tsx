"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { Customer, MessageItem, AgentTraceItem, ActionLedgerItem } from "@/lib/types";
import { 
  fetchCustomers, 
  fetchCustomer, 
  fetchConversationHistory, 
  fetchConversationActions, 
  resetConversation, 
  streamChatMessage 
} from "@/lib/api";
import { Header } from "@/components/Header";
import { BookingSidebar } from "@/components/BookingSidebar";
import { ChatWindow } from "@/components/ChatWindow";
import { AgentTracePanel } from "@/components/AgentTracePanel";
import { ActionLedger } from "@/components/ActionLedger";

export default function ChatConsolePage() {
  const params = useParams();
  const router = useRouter();
  const customerId = Number(params?.customerId) || 1;

  const [allCustomers, setAllCustomers] = useState<Customer[]>([]);
  const [currentCustomer, setCurrentCustomer] = useState<Customer | null>(null);
  const [conversationId, setConversationId] = useState<string>("");
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [traces, setTraces] = useState<AgentTraceItem[]>([]);
  const [actions, setActions] = useState<ActionLedgerItem[]>([]);
  const [escalated, setEscalated] = useState<boolean>(false);
  const [escalationReason, setEscalationReason] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Initialize customer and session
  useEffect(() => {
    setLoading(true);
    fetchCustomers()
      .then((custList) => {
        setAllCustomers(custList);
        const active = custList.find((c) => c.id === customerId) || custList[0];
        setCurrentCustomer(active);

        // Deterministic conversation ID per customer session
        const convId = `conv-${active.pnr}-session`;
        setConversationId(convId);

        // Load any existing conversation history & actions
        fetchConversationHistory(convId)
          .then((hist) => {
            if (hist && hist.messages) {
              setMessages(hist.messages);
              setEscalated(hist.status === "ESCALATED");
              setEscalationReason(hist.escalation_reason || null);
            }
          })
          .catch(() => {
            setMessages([]);
            setEscalated(false);
            setEscalationReason(null);
          });

        fetchConversationActions(convId)
          .then((actList) => {
            if (actList) setActions(actList);
          })
          .catch(() => setActions([]));
      })
      .catch((err) => console.error("Error loading chat context:", err))
      .finally(() => setLoading(false));
  }, [customerId]);

  // Send message with SSE live streaming
  const handleSendMessage = useCallback(
    async (text: string) => {
      if (!currentCustomer || isStreaming) return;

      // Append user message immediately
      const userMsg: MessageItem = {
        role: "user",
        content: text,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsStreaming(true);

      // Clear previous turn traces for focused live visibility of current turn
      setTraces([]);

      await streamChatMessage({
        customerId: currentCustomer.id,
        message: text,
        conversationId,
        onTrace: (newTrace) => {
          setTraces((prev) => [...prev, newTrace]);
        },
        onComplete: (data) => {
          setIsStreaming(false);
          const assistantMsg: MessageItem = {
            role: "assistant",
            content: data.message,
            created_at: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, assistantMsg]);
          if (data.escalated) {
            setEscalated(true);
            setEscationReasonSafe(data.escalation_reason);
          }
          if (data.actions && data.actions.length > 0) {
            setActions(data.actions);
          }
        },
        onError: (err) => {
          setIsStreaming(false);
          console.error("Streaming chat error:", err);
          const errMsg: MessageItem = {
            role: "assistant",
            content:
              "We encountered an issue processing your request. Please check backend connection.",
            created_at: new Date().toISOString(),
          };
          setMessages((prev) => [...prev, errMsg]);
        },
      });
    },
    [currentCustomer, conversationId, isStreaming]
  );

  const setEscationReasonSafe = (reason?: string | null) => {
    if (reason) setEscalationReason(reason);
  };

  // Reset conversation
  const handleReset = async () => {
    if (!conversationId) return;
    try {
      await resetConversation(conversationId);
      setMessages([]);
      setTraces([]);
      setActions([]);
      setEscalated(false);
      setEscalationReason(null);
    } catch (e) {
      console.error("Failed to reset conversation:", e);
    }
  };

  if (loading || !currentCustomer) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-background text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 rounded-full border-2 border-primary-500 border-t-transparent animate-spin" />
          <span className="text-xs font-mono">Initializing SkyRoute Console...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-background text-slate-100 overflow-hidden">
      {/* Top Navigation */}
      <Header customers={allCustomers} activeCustomerId={currentCustomer.id} />

      {/* Main 3-Pane Body */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Pane: Customer Context & Bookings */}
        <BookingSidebar customer={currentCustomer} loading={loading} />

        {/* Center Pane: Active Conversation */}
        <ChatWindow
          customer={currentCustomer}
          messages={messages}
          isStreaming={isStreaming}
          escalated={escalated}
          escalationReason={escalationReason}
          onSendMessage={handleSendMessage}
          onResetConversation={handleReset}
        />

        {/* Right Pane: Agent Trace + Action Ledger */}
        <div className="w-96 shrink-0 border-l border-border/60 bg-surface/50 flex flex-col p-3 gap-3 overflow-hidden">
          {/* Top Half: Live Agent Trace */}
          <div className="h-3/5 overflow-hidden">
            <AgentTracePanel traces={traces} isStreaming={isStreaming} />
          </div>

          {/* Bottom Half: Database Action Ledger */}
          <div className="h-2/5 overflow-hidden">
            <ActionLedger actions={actions} />
          </div>
        </div>
      </div>
    </div>
  );
}
