from typing import Any, Dict

BILLS = {
    "100234": {"balance": 142.80, "due": "October 6", "past_due_days": 0,
               "last_payment": "$131.55 on September 3", "arrangement_in_last_12_months": False},
    "100871": {"balance": 412.37, "due": "September 9", "past_due_days": 18,
               "last_payment": "$95.00 on July 28", "arrangement_in_last_12_months": False},
    "100455": {"balance": 86.10, "due": "October 2", "past_due_days": 0,
               "last_payment": "$120.40 on August 30", "arrangement_in_last_12_months": True},
    "123456": {"balance": 238.45, "due": "October 8", "past_due_days": 0,
               "last_payment": "$212.10 on September 8", "arrangement_in_last_12_months": False},
}


def get_bill_summary() -> Dict[str, Any]:
    """Returns the verified customer's current balance, due date, days past due and last payment.
    The customer must be verified first with verify_customer."""
    if not get_variable("is_authenticated", False):
        return {"error": "Customer is not verified.", "agent_action": "Verify the customer with verify_customer first."}
    bill = BILLS.get(get_variable("account_id", ""))
    if not bill:
        return {"error": "No bill found for this account.", "agent_action": "Apologize and offer to connect the customer with a representative."}
    return {
        "customer_name": get_variable("customer_name", ""),
        "balance": "$" + format(bill["balance"], ".2f"),
        "due_date": bill["due"],
        "past_due_days": bill["past_due_days"],
        "last_payment": bill["last_payment"],
    }
