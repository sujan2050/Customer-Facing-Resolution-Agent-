import pytest
from app.models.models import ActionLedgerEntry, Conversation

def test_arvind_scenario_end_to_end(client, db_session):
    conversation_id = "test-conv-arvind-001"

    # Arvind's flight SK-118 is delayed 4 hours. Asks for hotel accommodation.
    res = client.post("/api/chat/message", json={
        "customer_id": 2,
        "message": "My flight SK-118 is delayed 4 hours. I am frustrated about missing my connecting meeting. Can you arrange hotel accommodation since it has been such a long delay?",
        "conversation_id": conversation_id
    })
    assert res.status_code == 200
    data = res.json()

    # Assertions
    # 1. Delay bucket >3h recognized
    assert "meal voucher" in data["message"].lower()
    assert "lounge" in data["message"].lower()

    # 2. Hotel accommodation declined with rule cited
    assert "hotel" in data["message"].lower()
    assert "5 hours" in data["message"].lower() or "exceeding 5 hours" in data["message"].lower()

    # 3. No escalation needed (Arvind is just asking, agent explains politely)
    assert data["escalated"] is False

    # 4. Action ledger verification
    actions = db_session.query(ActionLedgerEntry).filter(
        ActionLedgerEntry.conversation_id == conversation_id
    ).all()
    action_types = [a.action_type for a in actions]

    assert "voucher_issued" in action_types
    assert "lounge_granted" in action_types
    # Hotel must NOT be arranged
    assert "hotel_arranged" not in action_types
    # No escalation
    assert "escalated_to_supervisor" not in action_types

    # Conversation status must remain ACTIVE
    conv = db_session.query(Conversation).filter(Conversation.id == conversation_id).first()
    assert conv is not None
    assert conv.status == "ACTIVE"
