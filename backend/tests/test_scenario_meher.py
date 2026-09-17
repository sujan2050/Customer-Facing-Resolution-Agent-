import pytest
from app.models.models import ActionLedgerEntry, Conversation

def test_meher_scenario_end_to_end(client, db_session):
    conversation_id = "test-conv-meher-001"

    # Meher asks for a full night's hotel stay and rebooking to higher-fare flight with ₹2,000 fare difference
    res = client.post("/api/chat/message", json={
        "customer_id": 3,
        "message": "My flight SK-305 is delayed 6 hours. I want a full night's hotel stay rather than just waiting at the airport, and I want to be moved onto a different, higher-fare flight instead with a ₹2,000 fare difference.",
        "conversation_id": conversation_id
    })
    assert res.status_code == 200
    data = res.json()

    # Assertions
    # 1. >5h delay bucket entitles to meal voucher + delayed-hours hotel
    assert "meal voucher" in data["message"].lower()
    assert "hotel" in data["message"].lower()
    # Explicit distinction that hotel covers delayed hours only (not full night)
    assert "delayed" in data["message"].lower() or "not a full night" in data["message"].lower()

    # 2. ₹2,000 fare waiver exceeds ₹1,500 limit -> Escalation triggered
    assert "1,500" in data["message"] or "1500" in data["message"]
    assert "2,000" in data["message"] or "2000" in data["message"]
    assert data["escalated"] is True
    assert "1,500" in data["escalation_reason"] or "cap" in data["escalation_reason"].lower() or "waiver" in data["escalation_reason"].lower()

    # 3. Action ledger verification
    actions = db_session.query(ActionLedgerEntry).filter(
        ActionLedgerEntry.conversation_id == conversation_id
    ).all()
    action_types = [a.action_type for a in actions]

    # Allowed parts processed
    assert "voucher_issued" in action_types
    assert "hotel_arranged" in action_types

    # Exceeded part escalated
    assert "escalated_to_supervisor" in action_types

    # Verify hotel details specify delayed hours only
    hotel_action = next(a for a in actions if a.action_type == "hotel_arranged")
    assert "delayed hours" in str(hotel_action.details_json).lower()

    # Verify conversation is escalated
    conv = db_session.query(Conversation).filter(Conversation.id == conversation_id).first()
    assert conv is not None
    assert conv.status == "ESCALATED"
