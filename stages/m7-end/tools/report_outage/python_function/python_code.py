from typing import Any, Dict

KNOWN_OUTAGES = {"39567": "OUT-58812", "39562": "OUT-58840"}


def report_outage(zip_code: str, description: str) -> Dict[str, Any]:
    """Reports a new power problem for a service address, for example no power, flickering lights,
    or a downed line. Returns a ticket number. If a known outage already covers the ZIP code,
    the report is attached to that outage instead of creating a new one."""
    zip5 = "".join(ch for ch in str(zip_code) if ch.isdigit())[:5] or get_variable("service_zip", "")
    if not zip5:
        return {"error": "A ZIP code is required to report a problem.", "agent_action": "Ask the customer for the ZIP code of the service address."}
    text = str(description).lower()
    if "down" in text and ("line" in text or "wire" in text):
        return {"ticket": "EMR-" + zip5 + "-01", "priority": "Emergency",
                "message": "Downed line reported as an emergency. Tell the customer to stay at least 35 feet away and keep others away."}
    if zip5 in KNOWN_OUTAGES:
        return {"ticket": KNOWN_OUTAGES[zip5], "attached_to_existing_outage": True,
                "message": "Report added to the existing outage for this area."}
    number = sum(ord(c) for c in zip5 + text) % 9000 + 1000
    return {"ticket": "TKT-" + str(number), "attached_to_existing_outage": False,
            "message": "New trouble ticket created. A technician will be assigned."}
