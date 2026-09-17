import { Customer, ActionLedgerItem, MessageItem, StreamEvent, AgentTraceItem } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchCustomers(): Promise<Customer[]> {
  const res = await fetch(`${API_BASE}/api/customers`);
  if (!res.ok) throw new Error("Failed to fetch customers");
  return res.json();
}

export async function fetchCustomer(id: number): Promise<Customer> {
  const res = await fetch(`${API_BASE}/api/customers/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch customer ${id}`);
  return res.json();
}

export async function fetchConversationHistory(conversationId: string): Promise<{
  conversation_id: string;
  status: string;
  escalation_reason?: string | null;
  messages: MessageItem[];
}> {
  const res = await fetch(`${API_BASE}/api/conversations/${conversationId}/history`);
  if (!res.ok) throw new Error("Failed to fetch conversation history");
  return res.json();
}

export async function fetchConversationActions(conversationId: string): Promise<ActionLedgerItem[]> {
  const res = await fetch(`${API_BASE}/api/conversations/${conversationId}/actions`);
  if (!res.ok) throw new Error("Failed to fetch conversation actions");
  return res.json();
}

export async function resetConversation(conversationId: string): Promise<void> {
  await fetch(`${API_BASE}/api/conversations/${conversationId}/reset`, {
    method: "POST",
  });
}

export async function streamChatMessage({
  customerId,
  message,
  conversationId,
  onTrace,
  onComplete,
  onError,
}: {
  customerId: number;
  message: string;
  conversationId?: string;
  onTrace: (trace: AgentTraceItem) => void;
  onComplete: (data: {
    message: string;
    conversation_id: string;
    escalated: boolean;
    escalation_reason?: string | null;
    actions: ActionLedgerItem[];
  }) => void;
  onError: (err: any) => void;
}) {
  try {
    const res = await fetch(`${API_BASE}/api/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        customer_id: customerId,
        message,
        conversation_id: conversationId,
      }),
    });

    if (!res.ok) {
      throw new Error(`Server returned ${res.status}: ${res.statusText}`);
    }

    const reader = res.body?.getReader();
    if (!reader) {
      throw new Error("No readable stream received from server");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith("data: ")) {
          try {
            const rawJson = trimmed.replace("data: ", "");
            const event: StreamEvent = JSON.parse(rawJson);

            if (event.type === "trace" && event.agent) {
              onTrace({
                agent: event.agent,
                status: (event.status as any) || "COMPLETED",
                summary: event.summary || "",
                details: event.details,
                rule_cited: event.rule_cited,
                timestamp: event.timestamp || new Date().toISOString(),
              });
            } else if (event.type === "complete") {
              onComplete({
                message: event.message || "",
                conversation_id: event.conversation_id || "",
                escalated: !!event.escalated,
                escalation_reason: event.escalation_reason,
                actions: event.actions || [],
              });
            }
          } catch (parseErr) {
            console.warn("Failed to parse SSE line:", trimmed, parseErr);
          }
        }
      }
    }
  } catch (err) {
    console.error("Streaming error, trying fallback endpoint:", err);
    try {
      const fallbackRes = await fetch(`${API_BASE}/api/chat/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: customerId,
          message,
          conversation_id: conversationId,
        }),
      });
      if (!fallbackRes.ok) throw new Error("Fallback failed");
      const fallbackData = await fallbackRes.json();
      for (const tr of fallbackData.traces || []) {
        onTrace(tr);
      }
      onComplete({
        message: fallbackData.message,
        conversation_id: fallbackData.conversation_id,
        escalated: fallbackData.escalated,
        escalation_reason: fallbackData.escalation_reason,
        actions: fallbackData.actions,
      });
    } catch (finalErr) {
      onError(finalErr);
    }
  }
}
