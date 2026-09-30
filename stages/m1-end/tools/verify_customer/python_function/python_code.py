from typing import Any, Dict

# PLACEHOLDER built from the requirements doc's test data. Not connected to a real system yet.
TEST_ACCOUNT, TEST_ZIP = "123456", "39562"


def verify_customer(account_number: str, zip_code: str) -> Dict[str, Any]:
    """Verifies the customer with their account number and service ZIP code."""
    acct = "".join(ch for ch in str(account_number) if ch.isdigit())
    zip5 = "".join(ch for ch in str(zip_code) if ch.isdigit())[:5]
    if acct == TEST_ACCOUNT and zip5 == TEST_ZIP:
        return {"verified": True, "customer_name": "Patrick Haggerty",
                "service_address": "3702 Magnolia St, Moss Point, MS 39562", "source": "placeholder"}
    return {"verified": False, "message": "The account number and ZIP code do not match our records.",
            "agent_action": "Ask the customer to check the account number on their bill and try again.", "source": "placeholder"}
