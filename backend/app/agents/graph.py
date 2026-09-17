from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END

from app.agents.context_agent import run_context_agent
from app.agents.tone_agent import run_tone_agent
from app.agents.router_agent import run_router_agent
from app.agents.policy_agent import run_policy_agent
from app.agents.guardrail_agent import run_guardrail_agent
from app.agents.execution_agent import run_execution_agent
from app.agents.audit_logger import run_audit_logger

class AgentState(TypedDict, total=False):
    customer_id: Optional[int]
    pnr: Optional[str]
    conversation_id: str
    user_message: str
    customer_profile: Dict[str, Any]
    bookings: List[Dict[str, Any]]
    active_booking: Dict[str, Any]
    intent: str
    entities: Dict[str, Any]
    tone: Dict[str, Any]
    policy: Dict[str, Any]
    guardrail: Dict[str, Any]
    executed_actions: List[Dict[str, Any]]
    escalation_triggered: bool
    escalation_reason: Optional[str]
    immediate_escalation: bool
    final_response_text: Optional[str]
    traces: List[Dict[str, Any]]
    db: Any

def should_skip_after_tone(state: AgentState) -> str:
    """If legal threat or formal complaint detected, immediately escalate and skip to audit."""
    if state.get("immediate_escalation"):
        return "audit_node"
    return "router_node"

def build_agent_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("context_node", run_context_agent)
    workflow.add_node("tone_node", run_tone_agent)
    workflow.add_node("router_node", run_router_agent)
    workflow.add_node("policy_node", run_policy_agent)
    workflow.add_node("guardrail_node", run_guardrail_agent)
    workflow.add_node("execution_node", run_execution_agent)
    workflow.add_node("audit_node", run_audit_logger)

    # Set Entry Point
    workflow.set_entry_point("context_node")

    # Connect Edges
    workflow.add_edge("context_node", "tone_node")
    
    # Conditional routing after Tone analysis
    workflow.add_conditional_edges(
        "tone_node",
        should_skip_after_tone,
        {
            "audit_node": "audit_node",
            "router_node": "router_node"
        }
    )

    workflow.add_edge("router_node", "policy_node")
    workflow.add_edge("policy_node", "guardrail_node")
    workflow.add_edge("guardrail_node", "execution_node")
    workflow.add_edge("execution_node", "audit_node")
    workflow.add_edge("audit_node", END)

    return workflow.compile()

# Singleton compiled graph
agent_graph = build_agent_graph()
