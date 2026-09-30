from typing import Any, Dict

# Current outage map for the demo (fictional). Keyed by 5-digit ZIP code.
OUTAGES = {
    "39567": {
        "outage_id": "OUT-58812",
        "status": "Active outage",
        "cause": "Tropical Storm Delphine damaged a main feeder line",
        "customers_affected": 2140,
        "hours_without_power": 76,
        "major_storm_event": "MSE-2026-04 (Tropical Storm Delphine)",
        "crew_status": "Crew on site, repairing the feeder",
        "estimated_restoration": "11:00 PM tonight",
    },
    "39562": {
        "outage_id": "OUT-58840",
        "status": "Active outage",
        "cause": "Tree limb on a distribution line",
        "customers_affected": 310,
        "hours_without_power": 2,
        "major_storm_event": None,
        "crew_status": "Crew assigned, en route",
        "estimated_restoration": "4:30 PM today",
    },
}
SERVED_ZIPS = {"39562", "39563", "39564", "39565", "39567", "39581"}


def check_outage(zip_code: str = "") -> Dict[str, Any]:
    """Checks for a known power outage at a Cymbal Energy service ZIP code and returns its status, cause,
    crew status and estimated restoration time. If zip_code is empty, the verified customer's service ZIP is used.
    Only quote restoration times exactly as returned by this tool."""
    zip5 = "".join(ch for ch in str(zip_code) if ch.isdigit())[:5] or get_variable("service_zip", "")
    if not zip5:
        return {"error": "No ZIP code provided.", "agent_action": "Ask the customer for the ZIP code of the service address."}
    if zip5 not in SERVED_ZIPS:
        return {"zip_code": zip5, "served": False,
                "message": "This ZIP code is outside the Cymbal Energy service area."}
    outage = OUTAGES.get(zip5)
    if not outage:
        return {"zip_code": zip5, "served": True, "status": "No known outage",
                "message": "No outage is reported for this ZIP code. The problem may be inside the home; offer to report it."}
    result = {"zip_code": zip5, "served": True}
    result.update(outage)
    return result
