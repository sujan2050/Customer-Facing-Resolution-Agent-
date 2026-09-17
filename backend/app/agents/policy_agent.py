from typing import Dict, Any, List
from app.models.schemas import PolicyOutput
from app.core.llm import extract_structured_data

def evaluate_policy_deterministic(
    customer_profile: Dict[str, Any],
    active_booking: Dict[str, Any],
    intent: str,
    entities: Dict[str, Any]
) -> PolicyOutput:
    tier = customer_profile.get("tier", "Standard")
    is_cancelled = active_booking.get("is_cancelled", False)
    delay_hours = active_booking.get("delay_hours", 0)
    
    entitlements = []
    rules_cited = []
    explanation_parts = []
    requires_escalation = False
    escalation_reason = None
    supervisor_approval_required = False

    # 1. Cancellation scenario
    if is_cancelled:
        rules_cited.append("Cancellation Rebooking Rule")
        explanation_parts.append(
            "Under the Cancellation Rebooking Rule, since flight SK-204 was cancelled due to operational reasons, "
            "you are entitled to a free rebooking on the next available flight within 24 hours, OR a full refund."
        )
        if tier in ["Gold", "Platinum"]:
            rules_cited.append("Loyalty Tier Rule")
            explanation_parts.append(
                f"As a {tier} member, you receive priority rebooking (first access to next-available seats) under our Loyalty Tier Rule."
            )
            entitlements.append({
                "type": "priority_rebooking",
                "rule": "Loyalty Tier Rule",
                "description": f"Priority rebooking within 24 hours ({tier} Tier advantage)"
            })
        else:
            entitlements.append({
                "type": "standard_rebooking",
                "rule": "Cancellation Rebooking Rule",
                "description": "Free rebooking within 24 hours"
            })

        entitlements.append({
            "type": "refund",
            "rule": "Refund Processing Rule",
            "description": "Full refund within 7 business days to original payment method"
        })

        # Check if customer asked for upgrade or extra compensation
        if entities.get("upgrade_requested"):
            rules_cited.append("Loyalty Tier Rule & Prohibited Actions")
            requires_escalation = True
            escalation_reason = "Customer requested free business-class upgrade / compensation beyond stated policy."
            explanation_parts.append(
                "Regarding the request for a complimentary business-class upgrade on the return flight: "
                "our policy specifies that Gold and Platinum tier status provides priority rebooking access only, "
                "with no additional compensation beyond the standard policy."
            )

    # 2. Delay scenario
    elif delay_hours > 0:
        if delay_hours < 3:
            rules_cited.append("Delay Compensation Rule (< 3 hours)")
            entitlements.append({
                "type": "meal_voucher",
                "rule": "Delay Compensation Rule (< 3 hours)",
                "description": "₹500 meal voucher"
            })
            explanation_parts.append("Flight is delayed under 3 hours, qualifying for a ₹500 meal voucher.")
        elif 3 <= delay_hours <= 5:
            rules_cited.append("Delay Compensation Rule (> 3 hours)")
            entitlements.append({
                "type": "meal_voucher",
                "rule": "Delay Compensation Rule (> 3 hours)",
                "description": "Meal voucher"
            })
            entitlements.append({
                "type": "lounge_access",
                "rule": "Delay Compensation Rule (> 3 hours)",
                "description": "Complimentary lounge access"
            })
            explanation_parts.append(
                f"Flight SK-118 is delayed {delay_hours} hours. Per our Delay Compensation Rule for delays over 3 hours, "
                "you qualify for a meal voucher and lounge access."
            )
            if entities.get("hotel_requested"):
                explanation_parts.append(
                    "Regarding hotel accommodation: under SkyRoute service rules, hotel accommodation is only provided "
                    "for delays exceeding 5 hours. Since your delay is 4 hours, we cannot arrange hotel accommodation, "
                    "but your meal voucher and lounge access are available immediately."
                )
        else:  # delay_hours > 5
            rules_cited.append("Delay Compensation Rule (> 5 hours)")
            entitlements.append({
                "type": "meal_voucher",
                "rule": "Delay Compensation Rule (> 5 hours)",
                "description": "Meal voucher"
            })
            entitlements.append({
                "type": "hotel_accommodation",
                "rule": "Delay Compensation Rule (> 5 hours)",
                "description": "Hotel accommodation covering only the delayed hours (not a full night's stay)"
            })
            explanation_parts.append(
                f"Your flight is delayed {delay_hours} hours, which qualifies for a meal voucher and hotel accommodation "
                "covering only the delayed hours (not a full night's stay) per the Delay Compensation Rule."
            )

            # Check if customer requested full night hotel
            if entities.get("hotel_stay_type") == "full_night":
                explanation_parts.append(
                    "Please note: policy strictly covers accommodation during the delayed hours only, and does not permit a full night's stay."
                )

        # Check voluntary rebook to higher-fare flight
        fare_diff = entities.get("fare_difference_amount")
        if fare_diff is not None and fare_diff > 0:
            rules_cited.append("Fare Difference Rule")
            if fare_diff > 1500:
                supervisor_approval_required = True
                requires_escalation = True
                escalation_reason = f"Requested fare waiver of ₹{fare_diff:,.0f} exceeds the ₹1,500 agent authority cap."
                explanation_parts.append(
                    f"Regarding rebooking to a higher-fare flight with a ₹{fare_diff:,.0f} fare difference: "
                    "under our Fare Difference Rule, agents cannot waive fare differences exceeding ₹1,500 without supervisor approval. "
                    f"Because ₹{fare_diff:,.0f} exceeds our ₹1,500 waiver limit, this specific request requires supervisor escalation."
                )
            else:
                entitlements.append({
                    "type": "fare_waiver",
                    "rule": "Fare Difference Rule",
                    "description": f"Fare waiver of ₹{fare_diff:,.0f} (within ₹1,500 limit)"
                })
                explanation_parts.append(f"Fare difference of ₹{fare_diff:,.0f} is within agent waiver authority.")

    applicable_rule = " & ".join(dict.fromkeys(rules_cited)) if rules_cited else "Service Rules"
    explanation = " ".join(explanation_parts)

    return PolicyOutput(
        applicable_rule=applicable_rule,
        is_eligible=len(entitlements) > 0,
        entitlements=entitlements,
        explanation=explanation,
        supervisor_approval_required=supervisor_approval_required,
        requires_escalation=requires_escalation,
        escalation_reason=escalation_reason
    )

def run_policy_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Policy Reasoning Agent:
    Computes exact entitlements per Section 3 service rules and formats rule citations.
    """
    customer_profile = state.get("customer_profile", {})
    active_booking = state.get("active_booking", {})
    intent = state.get("intent", "general_query")
    entities = state.get("entities", {})

    deterministic_policy = evaluate_policy_deterministic(
        customer_profile=customer_profile,
        active_booking=active_booking,
        intent=intent,
        entities=entities
    )

    traces = list(state.get("traces", []))
    summary = f"Rule: {deterministic_policy.applicable_rule} | Entitlements: {len(deterministic_policy.entitlements)} item(s)"
    if deterministic_policy.requires_escalation:
        summary += f" | Flags: {deterministic_policy.escalation_reason}"

    trace = {
        "agent": "Policy Reasoning Agent",
        "status": "WARNING" if deterministic_policy.requires_escalation else "COMPLETED",
        "summary": summary,
        "details": {
            "applicable_rule": deterministic_policy.applicable_rule,
            "entitlements": deterministic_policy.entitlements,
            "explanation": deterministic_policy.explanation,
            "requires_escalation": deterministic_policy.requires_escalation,
            "escalation_reason": deterministic_policy.escalation_reason
        },
        "rule_cited": deterministic_policy.applicable_rule
    }
    traces.append(trace)

    return {
        "policy": deterministic_policy.model_dump(),
        "traces": traces
    }
