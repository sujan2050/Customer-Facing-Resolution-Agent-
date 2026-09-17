from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class BookingSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    pnr: str
    flight_number: str
    route: str
    flight_date: str
    scheduled_departure: str
    status: str
    delay_hours: int
    new_departure: Optional[str] = None
    is_cancelled: bool
    is_airline_caused: bool

class CustomerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    tier: str
    pnr: str
    email: str
    phone: Optional[str] = None
    travel_history: Optional[str] = None
    bookings: List[BookingSchema] = []

class ActionLedgerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: Optional[str] = None
    customer_id: int
    action_type: str
    rule_cited: str
    status: str
    details_json: Optional[Dict[str, Any]] = None
    created_at: datetime

class MessageAuditSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: str
    role: str
    content: str
    agent_traces_json: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

class AgentTrace(BaseModel):
    agent: str
    status: str  # RUNNING, COMPLETED, WARNING, ESCALATED, BLOCKED
    summary: str
    details: Optional[Dict[str, Any]] = None
    rule_cited: Optional[str] = None
    timestamp: str

class ChatRequest(BaseModel):
    customer_id: int
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    escalated: bool = False
    escalation_reason: Optional[str] = None
    traces: List[AgentTrace] = []
    actions: List[ActionLedgerSchema] = []

# Typed outputs for agents
class RouterOutput(BaseModel):
    intent: str = Field(
        description="One of: status_check, rebook_request, compensation_request, refund_request, escalation_trigger, general_query"
    )
    entities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extracted entities like requested_flight, upgrade_requested, hotel_requested, hotel_duration, fare_difference_amount, refund_method, etc."
    )
    raw_query: str

class ToneOutput(BaseModel):
    sentiment: str = Field(description="positive, neutral, frustrated, angry")
    is_angry_or_frustrated: bool
    is_legal_threat_or_formal_complaint: bool
    detected_phrases: List[str] = Field(default_factory=list)
    empathetic_response_prefix: Optional[str] = None

class PolicyOutput(BaseModel):
    applicable_rule: str
    is_eligible: bool
    entitlements: List[Dict[str, Any]] = Field(default_factory=list)
    explanation: str
    supervisor_approval_required: bool = False
    requires_escalation: bool = False
    escalation_reason: Optional[str] = None

class GuardrailOutput(BaseModel):
    passed: bool
    is_escalation_forced: bool
    violated_rules: List[str] = Field(default_factory=list)
    escalation_reason: Optional[str] = None
    cleared_actions: List[Dict[str, Any]] = Field(default_factory=list)
    blocked_actions: List[Dict[str, Any]] = Field(default_factory=list)
    explanation: str
