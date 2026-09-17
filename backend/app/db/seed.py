from sqlalchemy.orm import Session
from app.db.session import engine, Base, SessionLocal
from app.models.models import Customer, Booking, PolicyRule, ActionLedgerEntry, Conversation, MessageAudit

def seed_database(db: Session = None):
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    close_at_end = False
    if db is None:
        db = SessionLocal()
        close_at_end = True

    try:
        # Check if already seeded
        existing_customers = db.query(Customer).count()
        if existing_customers >= 3:
            print("Database already seeded. Skipping...")
            return

        # Clear existing data in reverse foreign key order if any partial state exists
        db.query(ActionLedgerEntry).delete()
        db.query(MessageAudit).delete()
        db.query(Conversation).delete()
        db.query(Booking).delete()
        db.query(Customer).delete()
        db.query(PolicyRule).delete()
        db.commit()

        # Seed Customers
        priya = Customer(
            id=1,
            name="Priya Nair",
            tier="Gold",
            pnr="SK4821X",
            email="priya.nair@example.com",
            phone="+91-98xxxxxxx1",
            travel_history="6 flights/12mo, 1 prior complaint (delayed baggage, resolved with voucher)"
        )
        arvind = Customer(
            id=2,
            name="Arvind Kulkarni",
            tier="Silver",
            pnr="TR1190B",
            email="arvind.kulkarni@example.com",
            phone="+91-98xxxxxxx2",
            travel_history="3 flights/12mo, no prior complaints"
        )
        meher = Customer(
            id=3,
            name="Meher Kaur",
            tier="Platinum",
            pnr="WL7742",
            email="meher.kaur@example.com",
            phone="+91-98xxxxxxx3",
            travel_history="10 flights/12mo, 1 prior complaint (overbooking, resolved with a tier-status upgrade)"
        )
        db.add_all([priya, arvind, meher])
        db.commit()

        # Seed Bookings (Exercise date: Wed 23 Sep 2026)
        bookings = [
            Booking(
                customer_id=priya.id,
                pnr="SK4821X",
                flight_number="SK-204",
                route="Delhi → Goa",
                flight_date="Wed 23 Sep 2026",
                scheduled_departure="18:40",
                status="Cancelled (operational reasons)",
                delay_hours=0,
                new_departure=None,
                is_cancelled=True,
                is_airline_caused=True
            ),
            Booking(
                customer_id=priya.id,
                pnr="SK4821X",
                flight_number="Return",
                route="Goa → Delhi",
                flight_date="Fri 25 Sep 2026",
                scheduled_departure="16:20",
                status="Unaffected",
                delay_hours=0,
                new_departure=None,
                is_cancelled=False,
                is_airline_caused=True
            ),
            Booking(
                customer_id=arvind.id,
                pnr="TR1190B",
                flight_number="SK-118",
                route="Mumbai → Bengaluru",
                flight_date="Wed 23 Sep 2026",
                scheduled_departure="07:10",
                status="Delayed 4h (new departure 11:10)",
                delay_hours=4,
                new_departure="11:10",
                is_cancelled=False,
                is_airline_caused=True
            ),
            Booking(
                customer_id=meher.id,
                pnr="WL7742",
                flight_number="SK-305",
                route="Delhi → Hyderabad",
                flight_date="Wed 23 Sep 2026",
                scheduled_departure="14:00",
                status="Delayed 6h (new departure 20:00)",
                delay_hours=6,
                new_departure="20:00",
                is_cancelled=False,
                is_airline_caused=True
            )
        ]
        db.add_all(bookings)
        db.commit()

        # Seed Policy Rules
        policies = [
            PolicyRule(
                category="cancellation",
                rule_name="Cancellation Rebooking Rule",
                description="If a flight is cancelled by the airline, the customer is entitled to a free rebooking on the next available flight within 24 hours, or a full refund, customer's choice.",
                entitlement_summary="Free rebooking within 24 hours OR full refund",
                conditions_json={"is_airline_caused": True, "rebooking_window_hours": 24}
            ),
            PolicyRule(
                category="delay",
                rule_name="Delay Compensation Rule (< 3 hours)",
                description="Delay under 3 hours: ₹500 meal voucher",
                entitlement_summary="₹500 meal voucher",
                conditions_json={"min_delay_hours": 0, "max_delay_hours": 3}
            ),
            PolicyRule(
                category="delay",
                rule_name="Delay Compensation Rule (> 3 hours)",
                description="Delay more than 3 hours: meal voucher + lounge access",
                entitlement_summary="Meal voucher + lounge access",
                conditions_json={"min_delay_hours": 3, "max_delay_hours": 5}
            ),
            PolicyRule(
                category="delay",
                rule_name="Delay Compensation Rule (> 5 hours)",
                description="Delay more than 5 hours: meal voucher + hotel accommodation, covering only the delayed hours (not a full night's stay)",
                entitlement_summary="Meal voucher + hotel accommodation covering delayed hours only (not full night)",
                conditions_json={"min_delay_hours": 5, "hotel_coverage": "delayed_hours_only"}
            ),
            PolicyRule(
                category="refund",
                rule_name="Refund Processing Rule",
                description="Refunds for airline-caused cancellations are processed in full within 7 business days. Refunds are issued to the original payment method only.",
                entitlement_summary="Full refund within 7 business days to original payment method only",
                conditions_json={"processing_days": 7, "original_payment_method_only": True}
            ),
            PolicyRule(
                category="fare_difference",
                rule_name="Fare Difference Rule",
                description="If a customer voluntarily chooses to rebook on a higher-fare flight (not airline-caused), they must pay the fare difference. Agents cannot waive fare differences above ₹1,500 without supervisor approval.",
                entitlement_summary="Customer pays fare difference; agent waiver cap is ₹1,500 max without supervisor approval",
                conditions_json={"max_agent_waiver": 1500}
            ),
            PolicyRule(
                category="loyalty",
                rule_name="Loyalty Tier Rule",
                description="Gold and Platinum tier customers get priority rebooking (first access to next-available seats) but no additional compensation beyond the standard policy.",
                entitlement_summary="Priority rebooking for Gold and Platinum; no additional compensation beyond standard policy",
                conditions_json={"eligible_tiers": ["Gold", "Platinum"]}
            )
        ]
        db.add_all(policies)
        db.commit()

        print("Database seeded successfully with Section 3 Ground Truth Data.")
    finally:
        if close_at_end:
            db.close()

if __name__ == "__main__":
    seed_database()
