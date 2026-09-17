import re
from typing import Dict, Any, List
from app.models.schemas import ToneOutput
from app.core.llm import extract_structured_data

LEGAL_THREAT_KEYWORDS = [
    r"legal action",
    r"file a formal complaint",
    r"formal complaint",
    r"lawyer",
    r"attorney",
    r"sue\b",
    r"suing",
    r"court",
    r"consumer court",
    r"dgca",
    r"take legal",
    r"take this to court"
]

FRUSTRATION_KEYWORDS = [
    r"furious",
    r"unacceptable",
    r"ridiculous",
    r"ruined my whole day",
    r"terrible",
    r"horrible",
    r"angry",
    r"outrageous",
    r"disaster",
    r"pathetic"
]

def analyze_tone_deterministic(message: str) -> ToneOutput:
    msg_lower = message.lower()
    
    # Check legal threat
    is_legal = any(re.search(pattern, msg_lower) for pattern in LEGAL_THREAT_KEYWORDS)
    is_frustrated = any(re.search(pattern, msg_lower) for pattern in FRUSTRATION_KEYWORDS)
    
    detected = []
    for pattern in LEGAL_THREAT_KEYWORDS:
        match = re.search(pattern, msg_lower)
        if match:
            detected.append(match.group(0))
            
    for pattern in FRUSTRATION_KEYWORDS:
        match = re.search(pattern, msg_lower)
        if match:
            detected.append(match.group(0))

    sentiment = "neutral"
    if is_legal:
        sentiment = "angry"
    elif is_frustrated:
        sentiment = "frustrated"

    prefix = None
    if is_frustrated:
        prefix = "I hear you, and I completely understand how frustrating this disruption is."
    if is_legal:
        prefix = "I hear you, and I'm sorry this has been such a frustrating experience. I want to make sure this gets the right attention — I'm escalating this to our specialist support team right now, and they'll reach out to you directly."

    return ToneOutput(
        sentiment=sentiment,
        is_angry_or_frustrated=is_frustrated or is_legal,
        is_legal_threat_or_formal_complaint=is_legal,
        detected_phrases=detected,
        empathetic_response_prefix=prefix
    )

def run_tone_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tone/De-escalation Agent:
    Evaluates tone and detects legal threats or formal complaints.
    If a legal threat is detected, forces immediate escalation per Sample C.
    """
    user_message = state.get("user_message", "")
    
    # Run deterministic pattern match first
    deterministic_result = analyze_tone_deterministic(user_message)
    
    prompt = f"""
    Analyze the tone of the following customer message:
    Message: "{user_message}"
    Determine sentiment (positive, neutral, frustrated, angry), whether customer is angry or frustrated,
    and whether there are threats of legal action or filing a formal complaint.
    """
    
    tone_result = extract_structured_data(
        prompt=prompt,
        schema_cls=ToneOutput,
        default_factory=lambda: deterministic_result
    )
    
    # Ensure legal threat is flagged if deterministic detected it (security guardrail)
    if deterministic_result.is_legal_threat_or_formal_complaint:
        tone_result.is_legal_threat_or_formal_complaint = True
        tone_result.sentiment = "angry"
        if not tone_result.empathetic_response_prefix:
            tone_result.empathetic_response_prefix = deterministic_result.empathetic_response_prefix

    traces = list(state.get("traces", []))
    
    if tone_result.is_legal_threat_or_formal_complaint:
        status = "ESCALATED"
        summary = "CRITICAL: Legal threat / formal complaint detected. Forcing immediate human escalation without substantive resolution."
        escalation_triggered = True
        escalation_reason = "Threat of legal action or formal complaint detected."
    elif tone_result.is_angry_or_frustrated:
        status = "WARNING"
        summary = f"Customer sentiment is {tone_result.sentiment} ({', '.join(tone_result.detected_phrases) or 'frustration detected'}). Applying de-escalation tone."
        escalation_triggered = False
        escalation_reason = None
    else:
        status = "COMPLETED"
        summary = f"Customer sentiment analyzed as {tone_result.sentiment}."
        escalation_triggered = False
        escalation_reason = None

    trace = {
        "agent": "Tone / De-escalation Agent",
        "status": status,
        "summary": summary,
        "details": {
            "sentiment": tone_result.sentiment,
            "is_legal_threat": tone_result.is_legal_threat_or_formal_complaint,
            "detected_phrases": tone_result.detected_phrases
        },
        "rule_cited": "Prohibited Actions: Handling threats of legal action or formal complaints — must be escalated immediately" if tone_result.is_legal_threat_or_formal_complaint else None
    }
    traces.append(trace)

    updates = {
        "tone": tone_result.model_dump(),
        "traces": traces
    }
    
    if escalation_triggered:
        updates["escalation_triggered"] = True
        updates["escalation_reason"] = escalation_reason
        updates["immediate_escalation"] = True
        updates["final_response_text"] = "I hear you, and I'm sorry this has been such a frustrating experience. I want to make sure this gets the right attention — I'm escalating this to our specialist support team right now, and they'll reach out to you directly."

    return updates
