from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Customer, Booking, PolicyRule
from app.db.session import SessionLocal

def run_context_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Context Agent: Loads active customer's profile + booking record from Postgres.
    Never lets the model guess data — all facts come strictly from the DB read.
    """
    customer_id = state.get("customer_id")
    pnr = state.get("pnr")
    db: Session = state.get("db") or SessionLocal()
    close_db = state.get("db") is None

    try:
        customer = None
        if customer_id:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
        elif pnr:
            customer = db.query(Customer).filter(Customer.pnr == pnr).first()

        if not customer:
            raise ValueError(f"Customer not found for id={customer_id}, pnr={pnr}")

        bookings = db.query(Booking).filter(Booking.customer_id == customer.id).all()
        
        # Primary active booking (prioritize cancelled or delayed flights)
        active_booking = None
        for b in bookings:
            if b.is_cancelled or b.delay_hours > 0:
                active_booking = b
                break
        if not active_booking and bookings:
            active_booking = bookings[0]

        booking_data = []
        for b in bookings:
            booking_data.append({
                "id": b.id,
                "flight_number": b.flight_number,
                "route": b.route,
                "flight_date": b.flight_date,
                "scheduled_departure": b.scheduled_departure,
                "status": b.status,
                "delay_hours": b.delay_hours,
                "new_departure": b.new_departure,
                "is_cancelled": b.is_cancelled,
                "is_airline_caused": b.is_airline_caused
            })

        customer_profile = {
            "id": customer.id,
            "name": customer.name,
            "tier": customer.tier,
            "pnr": customer.pnr,
            "email": customer.email,
            "phone": customer.phone,
            "travel_history": customer.travel_history
        }

        trace = {
            "agent": "Context Agent",
            "status": "COMPLETED",
            "summary": f"Retrieved profile for {customer.name} ({customer.tier} Tier, PNR: {customer.pnr}) and {len(bookings)} booking(s).",
            "details": {
                "customer": customer_profile,
                "active_flight": active_booking.flight_number if active_booking else None,
                "active_status": active_booking.status if active_booking else None
            },
            "rule_cited": None
        }

        # Append trace
        traces = list(state.get("traces", []))
        traces.append(trace)

        return {
            "customer_profile": customer_profile,
            "bookings": booking_data,
            "active_booking": booking_data[0] if booking_data else None,
            "traces": traces
        }
    finally:
        if close_db:
            db.close()
