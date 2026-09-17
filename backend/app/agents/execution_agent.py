from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import ActionLedgerEntry, Conversation
from app.db.session import SessionLocal

def run_execution_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Action Execution Agent:
    Only commits actions cleared by the Guardrail Agent.
    Writes rows to the action_ledger database table:
    - rebooked
    - voucher_issued
    - lounge_granted
    - hotel_arranged
    - refund_initiated
    - escalated_to_supervisor (for escalated requests)
    """
    db: Session = state.get("db") or SessionLocal()
    close_db = state.get("db") is None
    
    customer_profile = state.get("customer_profile", {})
    customer_id = customer_profile.get("id")
    conversation_id = state.get("conversation_id", "conv-default")
    guardrail = state.get("guardrail", {})
    cleared_actions = guardrail.get("cleared_actions", [])
    blocked_actions = guardrail.get("blocked_actions", [])
    is_escalation_forced = guardrail.get("is_escalation_forced", False)
    escalation_reason = guardrail.get("escalation_reason")

    executed_records = []
    
    try:
        # Ensure parent Conversation row exists to satisfy Foreign Key constraint
        if conversation_id and customer_id:
            conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not conv:
                conv = Conversation(
                    id=conversation_id,
                    customer_id=customer_id,
                    pnr=customer_profile.get("pnr", "UNKNOWN"),
                    status="ESCALATED" if is_escalation_forced else "ACTIVE",
                    escalation_reason=escalation_reason if is_escalation_forced else None
                )
                db.add(conv)
                db.commit()

        # Execute cleared actions
        for act in cleared_actions:
            act_type = act.get("type")
            rule = act.get("rule", "Service Rules")
            
            mapped_type = "generic_action"
            if "voucher" in act_type:
                mapped_type = "voucher_issued"
            elif "lounge" in act_type:
                mapped_type = "lounge_granted"
            elif "hotel" in act_type:
                mapped_type = "hotel_arranged"
            elif "refund" in act_type:
                mapped_type = "refund_initiated"
            elif "rebook" in act_type:
                mapped_type = "rebooked"
            elif "waiver" in act_type:
                mapped_type = "fare_waived"

            db_entry = ActionLedgerEntry(
                conversation_id=conversation_id,
                customer_id=customer_id,
                action_type=mapped_type,
                rule_cited=rule,
                status="COMPLETED",
                details_json=act
            )
            db.add(db_entry)
            db.commit()
            db.refresh(db_entry)
            
            executed_records.append({
                "id": db_entry.id,
                "action_type": db_entry.action_type,
                "rule_cited": db_entry.rule_cited,
                "status": db_entry.status,
                "details": act
            })

        # Record escalation entries if any
        if is_escalation_forced and blocked_actions:
            for blk in blocked_actions:
                db_entry = ActionLedgerEntry(
                    conversation_id=conversation_id,
                    customer_id=customer_id,
                    action_type="escalated_to_supervisor",
                    rule_cited=blk.get("rule", "Prohibited Actions"),
                    status="ESCALATED",
                    details_json=blk
                )
                db.add(db_entry)
                db.commit()
                db.refresh(db_entry)

                executed_records.append({
                    "id": db_entry.id,
                    "action_type": db_entry.action_type,
                    "rule_cited": db_entry.rule_cited,
                    "status": db_entry.status,
                    "details": blk
                })

        traces = list(state.get("traces", []))
        summary = f"Executed {len(cleared_actions)} database action(s)."
        if is_escalation_forced:
            summary += f" Logged escalation record in ledger."

        trace = {
            "agent": "Action Execution Agent",
            "status": "COMPLETED",
            "summary": summary,
            "details": {
                "executed_actions": executed_records
            },
            "rule_cited": None
        }
        traces.append(trace)

        return {
            "executed_actions": executed_records,
            "traces": traces
        }
    finally:
        if close_db:
            db.close()
