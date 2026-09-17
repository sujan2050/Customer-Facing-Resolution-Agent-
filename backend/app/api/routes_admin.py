from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Customer, Booking, PolicyRule, ActionLedgerEntry, Conversation, MessageAudit
from app.models.schemas import CustomerSchema, ActionLedgerSchema, MessageAuditSchema

router = APIRouter(prefix="/api", tags=["Admin & Context"])

@router.get("/customers", response_model=List[CustomerSchema])
def list_customers(db: Session = Depends(get_db)):
    """List all customers with their active bookings."""
    customers = db.query(Customer).all()
    return customers

@router.get("/customers/{customer_id}", response_model=CustomerSchema)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get single customer profile with bookings."""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.get("/conversations/{conversation_id}/history")
def get_conversation_history(conversation_id: str, db: Session = Depends(get_db)):
    """Fetch message history and audit traces for a conversation."""
    messages = db.query(MessageAudit).filter(
        MessageAudit.conversation_id == conversation_id
    ).order_by(MessageAudit.created_at.asc()).all()
    
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    return {
        "conversation_id": conversation_id,
        "status": conv.status if conv else "ACTIVE",
        "escalation_reason": conv.escalation_reason if conv else None,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "agent_traces": m.agent_traces_json,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ]
    }

@router.get("/conversations/{conversation_id}/actions", response_model=List[ActionLedgerSchema])
def get_conversation_actions(conversation_id: str, db: Session = Depends(get_db)):
    """Fetch action ledger entries for a conversation."""
    actions = db.query(ActionLedgerEntry).filter(
        ActionLedgerEntry.conversation_id == conversation_id
    ).order_by(ActionLedgerEntry.created_at.desc()).all()
    return actions

@router.post("/conversations/{conversation_id}/reset")
def reset_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Reset a conversation state and action ledger for clean scenario replay."""
    db.query(ActionLedgerEntry).filter(ActionLedgerEntry.conversation_id == conversation_id).delete()
    db.query(MessageAudit).filter(MessageAudit.conversation_id == conversation_id).delete()
    db.query(Conversation).filter(Conversation.id == conversation_id).delete()
    db.commit()
    return {"status": "success", "message": f"Conversation {conversation_id} reset"}
