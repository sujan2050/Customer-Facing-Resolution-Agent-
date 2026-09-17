import pytest
from app.models.models import Conversation

def test_legal_threat_immediate_escalation(client, db_session):
    """Test Sample C from prompt: customer threatens legal action / formal complaint."""
    conversation_id = "test-conv-legal-001"

    # Message matching Sample C: "This is unacceptable, I'm going to file a formal complaint and consider legal action over this."
    res = client.post("/api/chat/message", json={
        "customer_id": 1,
        "message": "This is unacceptable, I'm going to file a formal complaint and consider legal action over this.",
        "conversation_id": conversation_id
    })
    assert res.status_code == 200
    data = res.json()

    # Must be escalated immediately
    assert data["escalated"] is True
    assert "legal" in data["escalation_reason"].lower() or "formal complaint" in data["escalation_reason"].lower()

    # Per Sample C: Empathetic response without attempting substantive resolution
    assert "specialist support team" in data["message"].lower() or "reach out to you directly" in data["message"].lower()

    # Check traces exist
    assert len(data["traces"]) >= 2
    tone_trace = next((t for t in data["traces"] if "Tone" in t["agent"]), None)
    assert tone_trace is not None
    assert tone_trace["status"] == "ESCALATED"

def test_traces_and_audit_completeness(client):
    """Test that all agent traces are captured in order."""
    conversation_id = "test-conv-traces-001"
    res = client.post("/api/chat/message", json={
        "customer_id": 2,
        "message": "What is the status of my flight SK-118?",
        "conversation_id": conversation_id
    })
    assert res.status_code == 200
    data = res.json()
    
    agent_names = [t["agent"] for t in data["traces"]]
    assert any("Context Agent" in name for name in agent_names)
    assert any("Tone" in name for name in agent_names)
    assert any("Router" in name for name in agent_names)
    assert any("Policy" in name for name in agent_names)
    assert any("Guardrail" in name for name in agent_names)
    assert any("Action Execution" in name for name in agent_names)
    assert any("Audit Logger" in name for name in agent_names)
