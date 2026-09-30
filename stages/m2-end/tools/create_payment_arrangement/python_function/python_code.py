from typing import Any, Dict

# Business rules live here, in code, not in the agent's instructions (Payment Arrangement Policy BP-210):
#   - balance of at least $100
#   - no payment arrangement in the previous 12 months
#   - 2 to 6 monthly installments
BILLS = {
    "100234": {"balance": 142.80, "arrangement_in_last_12_months": False},
    "100871": {"balance": 412.37, "arrangement_in_last_12_months": False},
    "100455": {"balance": 86.10, "arrangement_in_last_12_months": True},
    "123456": {"balance": 238.45, "arrangement_in_last_12_months": False},
}
MIN_BALANCE = 100.00
MIN_INSTALLMENTS = 2
MAX_INSTALLMENTS = 6


def create_payment_arrangement(installments: int) -> Dict[str, Any]:
    """Creates a payment arrangement that spreads the verified customer's current balance over equal monthly
    installments added to future bills. Cymbal Energy policy decides eligibility; this tool enforces it and
    returns approved true or false with the reason. The customer must be verified first with verify_customer."""
    if not get_variable("is_authenticated", False):
        return {"approved": False, "reason": "Customer is not verified.", "agent_action": "Verify the customer with verify_customer first."}
    acct = get_variable("account_id", "")
    bill = BILLS.get(acct)
    if not bill:
        return {"approved": False, "reason": "No bill found for this account."}
    if bill["balance"] < MIN_BALANCE:
        return {"approved": False,
                "reason": "Balance of $" + format(bill["balance"], ".2f") + " is below the $100.00 minimum for a payment arrangement."}
    if bill["arrangement_in_last_12_months"]:
        return {"approved": False, "reason": "The account already had a payment arrangement in the last 12 months."}
    n = int(installments)
    if n < MIN_INSTALLMENTS or n > MAX_INSTALLMENTS:
        return {"approved": False,
                "reason": "Installments must be between 2 and 6 months. Requested: " + str(n) + "."}
    monthly = round(bill["balance"] / n, 2)
    return {
        "approved": True,
        "arrangement_id": "PA-" + acct + "-" + str(n),
        "installments": n,
        "monthly_amount": "$" + format(monthly, ".2f"),
        "total": "$" + format(bill["balance"], ".2f"),
        "first_installment": "added to the next bill",
        "note": "Current charges must still be paid by their due date each month.",
    }
