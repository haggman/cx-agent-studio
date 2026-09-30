from typing import Any, Dict

# PLACEHOLDER built from the requirements doc's test data. Not connected to a real system yet.


def get_bill_summary() -> Dict[str, Any]:
    """Returns the verified customer's balance, due date and last payment."""
    return {"customer_name": "Patrick Haggerty", "balance": "$238.45", "due_date": "October 8",
            "past_due_days": 0, "last_payment": "$212.10 on September 8", "source": "placeholder",
            "agent_action": "Share the balance and due date. Only give them to a customer verified with verify_customer."}
