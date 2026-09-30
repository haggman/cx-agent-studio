from typing import Any, Dict

# PLACEHOLDER built from the requirements doc's test data. Not connected to a real system yet.


def check_outage(zip_code: str) -> Dict[str, Any]:
    """Looks up the outage status and estimated restoration time for a ZIP code."""
    zip5 = "".join(ch for ch in str(zip_code) if ch.isdigit())[:5]
    if not zip5:
        return {"error": "No ZIP code provided.", "agent_action": "Ask the customer for the ZIP code of the service address."}
    if zip5 == "39562":
        return {"zip_code": zip5, "outage_id": "OUT-58840", "status": "Active outage",
                "cause": "Tree limb on a distribution line", "customers_affected": 310,
                "crew_status": "Crew assigned, en route", "estimated_restoration": "4:30 PM today", "source": "placeholder"}
    return {"zip_code": zip5, "status": "No known outage",
            "message": "No outage is reported for this ZIP code. Offer to report the problem.", "source": "placeholder"}
