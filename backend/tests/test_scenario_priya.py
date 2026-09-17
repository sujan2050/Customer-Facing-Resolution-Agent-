import pytest
from app.models.models import ActionLedgerEntry, Conversation

def test_priya_scenario_end_to_end(client, db_session):
    conversation_id = "test-conv-priya-001"
    
    # Step 1: Priya contacts support about flight SK-204 (Delhi -> Goa)
    res1 = client.post("/api/chat/message", json={
        "customer_id": 1,
        "message": "Hi, my flight SK-204 from Delhi to Goa was cancelled. What can you do for me?",
        "conversation_id": conversation_id
    })
    assert res1.status_code == 200
    data1 = res1.json()
    
    # Assertions for Step 1
    assert data1["conversation_id"] == conversation_id
    assert "cancell" in data1["message"].lower()
    # Offer rebook-or-refund per cancellation rule
    assert "24 hours" in data1["message"].lower() or "rebook" in data1["message"].lower()
    assert "refund" in data1["message"].lower()
    # Gold priority rebooking mention
    assert "gold" in data1["message"].lower() or "priority" in data1["message"].lower()
    assert data1["escalated"] is False

    # Step 2: Mid-conversation, Priya is furious and demands cash refund + free upgrade to business class
    res2 = client.post("/api/chat/message", json={
        "customer_id": 1,
        "message": "This is terrible, I am furious! I want a full cash refund plus a free upgrade to business class on my return flight for the trouble.",
        "conversation_id": conversation_id
    })
    assert res2.status_code == 200
    data2 = res2.json()

    # Assertions for Step 2
    # Refund is offered/processed
    assert "refund" in data2["message"].lower()
    # Free business class upgrade must be declined per Loyalty Tier Rule
    assert "upgrade" in data2["message"].lower()
    # Must be escalated
    assert data2["escalated"] is True
    assert "upgrade" in data2["escalation_reason"].lower() or "policy" in data2["escalation_reason"].lower()
    
    # Interaction stays polite & empathetic
    assert "understand" in data2["message"].lower() or "sorry" in data2["message"].lower() or "appreciate" in data2["message"].lower()

    # Assert Action Ledger records in DB
    actions = db_session.query(ActionLedgerEntry).filter(
        ActionLedgerEntry.conversation_id == conversation_id
    ).all()
    action_types = [a.action_type for a in actions]
    
    # Escalation row must exist in action ledger
    assert "escalated_to_supervisor" in action_types

    # Conversation row must be flagged as ESCALATED
    conv = db_session.query(Conversation).filter(Conversation.id == conversation_id).first()
    assert conv is not None
    assert conv.status == "ESCALATED"
