from typing import Any, Dict

# PLACEHOLDER built from the requirements doc's test data. Not connected to a real system yet.


def report_outage(zip_code: str, description: str) -> Dict[str, Any]:
    """Creates a trouble ticket for a power problem."""
    zip5 = "".join(ch for ch in str(zip_code) if ch.isdigit())[:5]
    if not zip5:
        return {"error": "No ZIP code provided.", "agent_action": "Ask the customer for the ZIP code of the service address."}
    text = str(description).lower()
    emergency = any(w in text for w in ("down", "spark", "fallen"))
    ticket = ("EMR-" if emergency else "TKT-") + str(sum(ord(c) for c in zip5 + text) % 900000 + 100000)
    if emergency:
        message = ("Emergency ticket " + ticket + " has been created for ZIP " + zip5 + ". A crew is being dispatched now. "
                   "Stay at least 35 feet away from the line and keep others away.")
    else:
        message = ("Ticket " + ticket + " has been created for ZIP " + zip5 + ". A technician will be assigned and "
                   "you will get a text when the crew is on the way.")
    return {"ticket": ticket, "priority": "Emergency" if emergency else "Standard", "message": message, "source": "placeholder"}
