from typing import Dict, Any, List
from app.models.schemas import GuardrailOutput

MAX_FARE_WAIVER = 1500.0

def run_guardrail_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Guardrail Agent:
    Deterministic code with VETO power.
    Validates proposed actions against allowed vs prohibited policies.
    Overrides downstream execution and forces escalation whenever policy boundaries are violated.
    """
    customer_profile = state.get("customer_profile", {})
    active_booking = state.get("active_booking", {})
    entities = state.get("entities", {})
    policy = state.get("policy", {})
    tone = state.get("tone", {})

    proposed_entitlements = policy.get("entitlements", [])
    violated_rules = []
    blocked_actions = []
    cleared_actions = []
    escalation_reasons = []

    # Check 1: Legal threat or formal complaint (from Tone agent or direct keywords)
    if tone.get("is_legal_threat_or_formal_complaint"):
        violated_rules.append("Prohibited Action: Handling threats of legal action or formal complaints")
        escalation_reasons.append("Immediate escalation required due to legal action or formal complaint threat.")

    # Check 2: Fare difference waiver exceeding cap (₹1,500)
    fare_diff = entities.get("fare_difference_amount")
    if fare_diff is not None and fare_diff > MAX_FARE_WAIVER:
        violated = f"Prohibited Action: Waiving a fare difference of ₹{fare_diff:,.0f} (exceeds agent cap of ₹{MAX_FARE_WAIVER:,.0f})"
        violated_rules.append(violated)
        blocked_actions.append({
            "type": "fare_waiver_above_cap",
            "amount": fare_diff,
            "rule": "Fare Difference Rule",
            "reason": f"Fare difference waiver of ₹{fare_diff:,.0f} exceeds ₹{MAX_FARE_WAIVER:,.0f} limit and requires supervisor approval."
        })
        escalation_reasons.append(f"Fare waiver request (₹{fare_diff:,.0f}) exceeds the ₹{MAX_FARE_WAIVER:,.0f} agent authorization cap.")

    # Check 3: Free upgrade or extra compensation beyond policy (e.g., cash refund + free upgrade combo)
    if entities.get("upgrade_requested"):
        violated = "Prohibited Action: Approving compensation/upgrades beyond stated policy amounts"
        violated_rules.append(violated)
        blocked_actions.append({
            "type": "complimentary_upgrade",
            "rule": "Loyalty Tier Rule & Prohibited Actions",
            "reason": "Agents are prohibited from offering complimentary business-class upgrades or compensation beyond standard policy."
        })
        escalation_reasons.append("Customer requested complimentary business-class upgrade / compensation beyond policy.")

    # Check 4: Hotel duration conversion (full night instead of delayed hours)
    if entities.get("hotel_requested"):
        delay_hours = active_booking.get("delay_hours", 0)
        if delay_hours < 5:
            # Arvind case: 4h delay does not qualify for hotel at all
            blocked_actions.append({
                "type": "hotel_accommodation",
                "rule": "Delay Compensation Rule (< 5 hours)",
                "reason": f"Hotel accommodation requires delay > 5 hours (current delay: {delay_hours}h)."
            })
        elif entities.get("hotel_stay_type") == "full_night":
            # Meher case: >5h delay qualifies only for delayed hours, not full night
            violated = "Prohibited Action: Converting delayed-hours hotel coverage into a full night's stay"
            violated_rules.append(violated)
            blocked_actions.append({
                "type": "full_night_hotel",
                "rule": "Delay Compensation Rule (> 5 hours)",
                "reason": "Delay compensation covers hotel accommodation for delayed hours only, not a full night's stay."
            })
            # Note: Do not escalate merely for asking, but block full night and restrict to delayed hours

    # Check 5: Non-airline-caused disruption exception ask
    if entities.get("non_airline_caused") or active_booking.get("is_airline_caused") is False:
        violated_rules.append("Prohibited Action: Making exceptions for non-airline-caused disruptions")
        escalation_reasons.append("Exceptions for non-airline-caused disruptions require supervisor escalation.")
        blocked_actions.append({
            "type": "non_airline_exception",
            "rule": "Allowed vs Prohibited Actions",
            "reason": "Agents cannot approve compensation or waivers for non-airline-caused disruptions."
        })

    # Check 6: Refund to a different payment method
    if entities.get("refund_payment_method") == "different":
        violated_rules.append("Prohibited Action: Processing refunds to a different payment method than original")
        escalation_reasons.append("Refunds to different payment methods are strictly prohibited and require supervisor escalation.")
        blocked_actions.append({
            "type": "refund_different_payment_method",
            "rule": "Refund Processing Rule",
            "reason": "Refunds can only be processed to the original payment method."
        })

    # Determine which proposed entitlements are cleared
    for ent in proposed_entitlements:
        ent_type = ent.get("type")
        
        # Priority rebooking or standard rebooking
        if ent_type in ["priority_rebooking", "standard_rebooking"]:
            cleared_actions.append(ent)
            
        # Refund (to original payment method)
        elif ent_type == "refund":
            if entities.get("refund_payment_method") != "different":
                cleared_actions.append(ent)
                
        # Meal voucher
        elif ent_type == "meal_voucher":
            cleared_actions.append(ent)
            
        # Lounge access
        elif ent_type == "lounge_access":
            cleared_actions.append(ent)
            
        # Hotel accommodation (strictly delayed hours only)
        elif ent_type == "hotel_accommodation":
            # Allowed strictly for delayed hours
            cleared_actions.append({
                "type": "hotel_accommodation",
                "rule": ent.get("rule"),
                "description": "Hotel accommodation covering delayed hours only (not full night)"
            })

    is_escalation_forced = len(escalation_reasons) > 0
    passed = not is_escalation_forced and len(violated_rules) == 0

    if is_escalation_forced:
        status = "ESCALATED"
        summary = f"VETO TRIGGERED: {len(violated_rules)} violation(s). Overriding execution for: {'; '.join(escalation_reasons)}"
    elif len(blocked_actions) > 0:
        status = "WARNING"
        summary = f"Guardrail enforced limits: {len(blocked_actions)} unentitled action(s) blocked. {len(cleared_actions)} action(s) cleared."
    else:
        status = "COMPLETED"
        summary = f"Guardrails passed clean. {len(cleared_actions)} action(s) approved for execution."

    trace = {
        "agent": "Guardrail Agent",
        "status": status,
        "summary": summary,
        "details": {
            "passed": passed,
            "is_escalation_forced": is_escalation_forced,
            "violated_rules": violated_rules,
            "escalation_reasons": escalation_reasons,
            "cleared_actions": cleared_actions,
            "blocked_actions": blocked_actions
        },
        "rule_cited": violated_rules[0] if violated_rules else "Allowed vs Prohibited Agent Actions"
    }

    traces = list(state.get("traces", []))
    traces.append(trace)

    return {
        "guardrail": {
            "passed": passed,
            "is_escalation_forced": is_escalation_forced,
            "violated_rules": violated_rules,
            "escalation_reason": " | ".join(escalation_reasons) if escalation_reasons else None,
            "cleared_actions": cleared_actions,
            "blocked_actions": blocked_actions,
            "explanation": summary
        },
        "escalation_triggered": is_escalation_forced or state.get("escalation_triggered", False),
        "escalation_reason": " | ".join(escalation_reasons) if escalation_reasons else state.get("escalation_reason"),
        "traces": traces
    }
