from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import Conversation, MessageAudit
from app.db.session import SessionLocal

def format_customer_response(state: Dict[str, Any]) -> str:
    # If immediate escalation was already generated (e.g. legal threat from tone agent), use it
    if state.get("final_response_text"):
        return state.get("final_response_text")

    customer = state.get("customer_profile", {})
    tier = customer.get("tier", "Standard")
    booking = state.get("active_booking", {})
    tone = state.get("tone", {})
    policy = state.get("policy", {})
    guardrail = state.get("guardrail", {})
    entities = state.get("entities", {})
    is_escalated = state.get("escalation_triggered", False)
    escalation_reason = state.get("escalation_reason", "")

    paragraphs: List[str] = []

    # 1. Empathy / Greeting opening
    if tone.get("is_angry_or_frustrated"):
        paragraphs.append("I completely understand how frustrating and disruptive flight changes can be, and I appreciate your patience.")
    else:
        paragraphs.append(f"Hello {customer.get('name', 'there')}, thank you for reaching out to SkyRoute Support.")

    # 2. Main Flight Disruption Context & Allowed Policy Entitlements
    if booking.get("is_cancelled"):
        flight_num = booking.get("flight_number", "your flight")
        route = booking.get("route", "")
        if tier in ["Gold", "Platinum"]:
            paragraphs.append(
                f"I can confirm that flight {flight_num} ({route}) was cancelled due to operational reasons. "
                f"Under our Cancellation Rebooking Rule and Loyalty Tier Rule, as a valued {tier} member, you are entitled to "
                "priority rebooking on the next available flight within 24 hours (with first access to open seats), "
                "OR a full refund processed to your original payment method within 7 business days."
            )
        else:
            paragraphs.append(
                f"I can confirm that flight {flight_num} ({route}) was cancelled due to operational reasons. "
                "Under our Cancellation Rebooking Rule, you are entitled to a free rebooking on the next available flight "
                "within 24 hours, OR a full refund processed to your original payment method within 7 business days."
            )

    elif booking.get("delay_hours", 0) > 0:
        delay = booking.get("delay_hours")
        flight_num = booking.get("flight_number", "your flight")
        new_dep = booking.get("new_departure", "")
        time_info = f" with new estimated departure at {new_dep}" if new_dep else ""
        
        if delay < 3:
            paragraphs.append(
                f"Flight {flight_num} is currently delayed by {delay} hours{time_info}. "
                "Under our Delay Compensation Rule, you qualify for a ₹500 meal voucher."
            )
        elif 3 <= delay <= 5:
            paragraphs.append(
                f"Flight {flight_num} is currently delayed by {delay} hours{time_info}. "
                "Per our Delay Compensation Rule (delays exceeding 3 hours), you are entitled to a meal voucher "
                "and complimentary lounge access, both of which have been activated for you."
            )
        else:  # delay > 5
            paragraphs.append(
                f"Flight {flight_num} is currently delayed by {delay} hours{time_info}. "
                "Under our Delay Compensation Rule (delays exceeding 5 hours), you are entitled to a meal voucher "
                "and hotel accommodation covering only the delayed hours (please note this covers the waiting hours, not a full night's stay)."
            )

    # 3. Address Specific Requests & Policy Enforcements
    # Hotel request for Arvind (delay <= 5h)
    if entities.get("hotel_requested") and booking.get("delay_hours", 0) <= 5:
        paragraphs.append(
            "Regarding your request for hotel accommodation: our policy provides hotel accommodation only when delays exceed 5 hours. "
            f"Because your delay is {booking.get('delay_hours', 0)} hours, hotel accommodation cannot be arranged; "
            "however, your meal voucher and lounge access are available immediately at the terminal."
        )

    # Full night hotel clarification for Meher
    if entities.get("hotel_requested") and entities.get("hotel_stay_type") == "full_night":
        paragraphs.append(
            "Regarding the hotel stay duration: our policy specifically covers hotel accommodation for the delayed-hours portion only, "
            "rather than a full night's stay. We have arranged your day-room accommodation accordingly."
        )

    # Business class upgrade decline & escalation for Priya
    if entities.get("upgrade_requested"):
        paragraphs.append(
            "Regarding your request for a complimentary upgrade to business class on your return flight: "
            "under SkyRoute's Loyalty Tier Rule, Gold tier status grants priority access for rebooking on scheduled flights, "
            "but agents cannot approve complimentary cabin upgrades or extra compensation beyond our standard policy. "
            "Because this request falls outside standard agent authority, I have transferred this request to our senior supervisor team for formal review."
        )

    # Fare difference waiver cap for Meher (> 1500)
    fare_diff = entities.get("fare_difference_amount")
    if fare_diff and fare_diff > 1500:
        paragraphs.append(
            f"Regarding moving you to an alternate flight with a ₹{fare_diff:,.0f} fare difference: "
            f"under our Fare Difference Rule, agents can only waive fare differences up to ₹1,500. "
            f"Since the ₹{fare_diff:,.0f} difference exceeds my authorization threshold, I have escalated this rebooking request "
            "to our supervisory team to review a fare waiver."
        )
    elif fare_diff and fare_diff <= 1500:
        paragraphs.append(
            f"Regarding moving you to an alternate flight with a ₹{fare_diff:,.0f} fare difference: "
            f"this amount is within our authorized ₹1,500 agent waiver threshold under the Fare Difference Rule."
        )

    # Refund request to a different payment method
    if entities.get("refund_payment_method") == "different":
        paragraphs.append(
            "Regarding your request to process a refund to a different bank account or card: "
            "under SkyRoute's Refund Processing Rule, refunds can strictly be issued to the original payment method only. "
            "Processing refunds to an alternate payment method or account is prohibited under agent authority. "
            "Because we cannot process this change directly, this request has been escalated to our specialist team for review."
        )
    elif entities.get("refund_requested") and not booking.get("is_cancelled"):
        flight_num = booking.get("flight_number", "your flight")
        paragraphs.append(
            f"Regarding your inquiry about a refund: under SkyRoute service rules, full refunds are provided for airline-caused cancellations. "
            f"Because flight {flight_num} is currently delayed rather than cancelled, the flight remains scheduled to depart, "
            "and compensation is provided via our Delay Compensation Rule (meal voucher and lounge access)."
        )

    # Non-airline caused disruption
    if entities.get("non_airline_caused"):
        paragraphs.append(
            "Regarding non-airline-caused disruptions (such as personal delays or missed flights): "
            "under our policy, complimentary rebooking or compensation cannot be authorized without supervisor review."
        )

    # 4. Closing / Escalation Banner
    if is_escalated:
        paragraphs.append(
            f"A senior customer care specialist has been assigned to your case (Reason: {escalation_reason}). "
            "They will follow up with you directly to assist with the escalated request."
        )
    else:
        paragraphs.append("Please let me know how you would like to proceed, and I will be glad to assist you further.")

    return "\n\n".join(paragraphs)

def run_audit_logger(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Audit Logger Agent:
    Appends every message, agent decision, rule cited, and action taken to a per-conversation log.
    Saves to the database and formats the final state.
    """
    db: Session = state.get("db") or SessionLocal()
    close_db = state.get("db") is None

    try:
        now_utc = datetime.now(timezone.utc)
        conversation_id = state.get("conversation_id", f"conv-{now_utc.strftime('%Y%m%d%H%M%S')}")
        customer_profile = state.get("customer_profile", {})
        customer_id = customer_profile.get("id", 1)
        pnr = customer_profile.get("pnr", "UNKNOWN")
        user_message = state.get("user_message", "")
        traces = state.get("traces", [])
        is_escalated = state.get("escalation_triggered", False)
        escalation_reason = state.get("escalation_reason")

        # Synthesize final response if not already set
        final_response = state.get("final_response_text") or format_customer_response(state)

        # Upsert Conversation
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conv:
            conv = Conversation(
                id=conversation_id,
                customer_id=customer_id,
                pnr=pnr,
                status="ESCALATED" if is_escalated else "ACTIVE",
                escalation_reason=escalation_reason,
                created_at=now_utc,
                updated_at=now_utc
            )
            db.add(conv)
        else:
            if is_escalated:
                conv.status = "ESCALATED"
                conv.escalation_reason = escalation_reason
            conv.updated_at = now_utc

        # Record User Message
        user_audit = MessageAudit(
            conversation_id=conversation_id,
            role="user",
            content=user_message,
            agent_traces_json=None,
            created_at=now_utc
        )
        db.add(user_audit)

        # Record Audit Logger Trace
        audit_trace = {
            "agent": "Audit Logger",
            "status": "COMPLETED",
            "summary": f"Audit trail logged with {len(traces)} agent event(s). Status: {'ESCALATED' if is_escalated else 'ACTIVE'}",
            "details": {
                "conversation_id": conversation_id,
                "timestamp": now_utc.isoformat(),
                "escalated": is_escalated,
                "escalation_reason": escalation_reason
            },
            "rule_cited": None
        }
        all_traces = list(traces) + [audit_trace]

        # Record Assistant Message with traces
        assistant_audit = MessageAudit(
            conversation_id=conversation_id,
            role="assistant",
            content=final_response,
            agent_traces_json=all_traces
        )
        db.add(assistant_audit)

        db.commit()

        return {
            "conversation_id": conversation_id,
            "final_response_text": final_response,
            "traces": all_traces,
            "escalation_triggered": is_escalated,
            "escalation_reason": escalation_reason
        }
    finally:
        if close_db:
            db.close()
