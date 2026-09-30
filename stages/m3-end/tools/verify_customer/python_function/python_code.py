from typing import Any, Dict

# Demo accounts (fictional). Account number + service ZIP is the identity check.
ACCOUNTS = {
    "100234": {"name": "Renee Thibodeaux", "zip": "39567", "address": "1418 Beach Blvd, Pascagoula, MS 39567"},
    "100871": {"name": "Marcus Bell", "zip": "39564", "address": "22 Porter Ave, Ocean Springs, MS 39564"},
    "100455": {"name": "Linh Nguyen", "zip": "39563", "address": "5107 Main St, Moss Point, MS 39563"},
    "123456": {"name": "Patrick Haggerty", "zip": "39562", "address": "3702 Magnolia St, Moss Point, MS 39562"},
}


def verify_customer(account_number: str, zip_code: str) -> Dict[str, Any]:
    """Verifies a Cymbal Energy customer using their 6-digit account number and the ZIP code of the service address.
    Call this before sharing any account-specific information such as balances, bills, or payment arrangements.
    On success it remembers the customer for the rest of the conversation."""
    acct = "".join(ch for ch in str(account_number) if ch.isdigit())
    zip5 = "".join(ch for ch in str(zip_code) if ch.isdigit())[:5]
    record = ACCOUNTS.get(acct)
    if not record or record["zip"] != zip5:
        set_variable("is_authenticated", False)
        return {"verified": False,
                "message": "The account number and ZIP code do not match our records.",
                "agent_action": "Ask the customer to check the account number on their bill and try again."}
    set_variable("is_authenticated", True)
    set_variable("account_id", acct)
    set_variable("customer_name", record["name"])
    set_variable("service_zip", record["zip"])
    return {"verified": True, "customer_name": record["name"], "service_address": record["address"]}
