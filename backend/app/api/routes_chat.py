import json
import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db, SessionLocal
from app.models.schemas import ChatRequest, ChatResponse, AgentTrace, ActionLedgerSchema
from app.models.models import Customer, Conversation, ActionLedgerEntry
from app.agents.graph import build_agent_graph

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/message", response_model=ChatResponse)
def handle_chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    """Standard synchronous chat endpoint."""
    customer = db.query(Customer).filter(Customer.id == request.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    conversation_id = request.conversation_id or f"conv-{customer.pnr}-{int(datetime.utcnow().timestamp())}"

    initial_state = {
        "customer_id": customer.id,
        "pnr": customer.pnr,
        "conversation_id": conversation_id,
        "user_message": request.message,
        "traces": [],
        "db": db
    }

    graph = build_agent_graph()
    final_state = graph.invoke(initial_state)

    # Fetch actions created for this conversation
    actions = db.query(ActionLedgerEntry).filter(
        ActionLedgerEntry.conversation_id == conversation_id
    ).all()

    action_schemas = [
        ActionLedgerSchema(
            id=a.id,
            conversation_id=a.conversation_id,
            customer_id=a.customer_id,
            action_type=a.action_type,
            rule_cited=a.rule_cited,
            status=a.status,
            details_json=a.details_json,
            created_at=a.created_at
        )
        for a in actions
    ]

    traces = [
        AgentTrace(
            agent=t.get("agent", "Agent"),
            status=t.get("status", "COMPLETED"),
            summary=t.get("summary", ""),
            details=t.get("details"),
            rule_cited=t.get("rule_cited"),
            timestamp=datetime.utcnow().isoformat()
        )
        for t in final_state.get("traces", [])
    ]

    return ChatResponse(
        conversation_id=conversation_id,
        message=final_state.get("final_response_text", ""),
        escalated=final_state.get("escalation_triggered", False),
        escalation_reason=final_state.get("escalation_reason"),
        traces=traces,
        actions=action_schemas
    )

@router.post("/stream")
async def handle_chat_stream(request: ChatRequest):
    """Server-Sent Events (SSE) streaming endpoint."""
    db = SessionLocal()
    customer = db.query(Customer).filter(Customer.id == request.customer_id).first()
    if not customer:
        db.close()
        raise HTTPException(status_code=404, detail="Customer not found")

    conversation_id = request.conversation_id or f"conv-{customer.pnr}-{int(datetime.utcnow().timestamp())}"

    async def event_generator():
        try:
            initial_state = {
                "customer_id": customer.id,
                "pnr": customer.pnr,
                "conversation_id": conversation_id,
                "user_message": request.message,
                "traces": [],
                "db": db
            }

            graph = build_agent_graph()
            
            # Stream node transitions
            last_trace_count = 0
            for output in graph.stream(initial_state):
                for node_name, node_state in output.items():
                    traces = node_state.get("traces", [])
                    if len(traces) > last_trace_count:
                        new_traces = traces[last_trace_count:]
                        last_trace_count = len(traces)
                        for tr in new_traces:
                            event_data = {
                                "type": "trace",
                                "node": node_name,
                                "agent": tr.get("agent"),
                                "status": tr.get("status"),
                                "summary": tr.get("summary"),
                                "details": tr.get("details"),
                                "rule_cited": tr.get("rule_cited"),
                                "timestamp": datetime.utcnow().isoformat()
                            }
                            yield f"data: {json.dumps(event_data)}\n\n"
                            await asyncio.sleep(0.05)

            # Query actions taken
            actions = db.query(ActionLedgerEntry).filter(
                ActionLedgerEntry.conversation_id == conversation_id
            ).all()

            action_data = [
                {
                    "id": a.id,
                    "action_type": a.action_type,
                    "rule_cited": a.rule_cited,
                    "status": a.status,
                    "details_json": a.details_json,
                    "created_at": a.created_at.isoformat()
                }
                for a in actions
            ]

            # Fetch conversation status
            conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            is_escalated = conv.status == "ESCALATED" if conv else False
            escalation_reason = conv.escalation_reason if conv else None

            final_state = node_state
            payload = {
                "type": "complete",
                "conversation_id": conversation_id,
                "message": final_state.get("final_response_text", ""),
                "escalated": is_escalated,
                "escalation_reason": escalation_reason,
                "actions": action_data
            }
            yield f"data: {json.dumps(payload)}\n\n"

        finally:
            db.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
