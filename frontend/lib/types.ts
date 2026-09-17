export interface Booking {
  id: number;
  customer_id: number;
  pnr: string;
  flight_number: string;
  route: string;
  flight_date: string;
  scheduled_departure: string;
  status: string;
  delay_hours: number;
  new_departure?: string | null;
  is_cancelled: boolean;
  is_airline_caused: boolean;
}

export interface Customer {
  id: number;
  name: string;
  tier: "Gold" | "Silver" | "Platinum" | string;
  pnr: string;
  email: string;
  phone?: string | null;
  travel_history?: string | null;
  bookings: Booking[];
}

export interface ActionLedgerItem {
  id: number;
  conversation_id?: string;
  customer_id: number;
  action_type: string;
  rule_cited: string;
  status: "COMPLETED" | "ESCALATED" | "BLOCKED" | string;
  details_json?: any;
  created_at: string;
}

export interface AgentTraceItem {
  agent: string;
  status: "RUNNING" | "COMPLETED" | "WARNING" | "ESCALATED" | "BLOCKED" | string;
  summary: string;
  details?: any;
  rule_cited?: string | null;
  timestamp: string;
}

export interface MessageItem {
  id?: number | string;
  role: "user" | "assistant" | "system";
  content: string;
  agent_traces?: AgentTraceItem[];
  created_at?: string;
}

export interface StreamEvent {
  type: "trace" | "complete" | "error";
  node?: string;
  agent?: string;
  status?: string;
  summary?: string;
  details?: any;
  rule_cited?: string | null;
  timestamp?: string;
  message?: string;
  conversation_id?: string;
  escalated?: boolean;
  escalation_reason?: string | null;
  actions?: ActionLedgerItem[];
}
