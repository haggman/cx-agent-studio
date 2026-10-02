from typing import Any
import json


def _payload(tool_response: Any) -> dict:
    """The runtime may hand the callback the tool's dict as-is, or wrapped (for example {"result": {...}} or
    {"output": {...}}, sometimes as a JSON string). Return the tool's own dict either way."""
    data = tool_response
    for _ in range(3):  # unwrap at most a few layers
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except ValueError:
                return {}
        if not isinstance(data, dict):
            return {}
        if "outage_id" in data or "served" in data or "zip_code" in data:
            return data  # check_outage's own fields: this is the payload
        inner = next((data[k] for k in ("result", "output", "response") if k in data), None)
        if inner is None:
            return data
        data = inner
    return data if isinstance(data, dict) else {}


def after_tool_callback(tool: Tool, input: dict[str, Any], callback_context: CallbackContext, tool_response: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Runs after every tool call on the outage_agent. When check_outage returns an active outage,
    copy the outage facts into session variables and work out storm-credit eligibility in code:
    more than 72 hours out during a declared Major Storm Event (policy OP-110).
    Returns None, so the tool's own response reaches the model unchanged."""
    if getattr(tool, "name", "") != "check_outage":
        return None  # every other tool passes straight through

    result = _payload(tool_response)
    if not result.get("outage_id"):  # no active outage for this ZIP
        callback_context.variables["storm_credit_eligible"] = False
        print(f"[after_tool] check_outage: no active outage, storm_credit_eligible=False (response keys: {list(result) or type(tool_response).__name__})")
        return None

    hours = int(result.get("hours_without_power") or 0)
    storm = result.get("major_storm_event")
    eligible = bool(storm) and hours > 72

    callback_context.variables["outage_id"] = result["outage_id"]
    callback_context.variables["estimated_restoration"] = result.get("estimated_restoration", "")
    callback_context.variables["hours_without_power"] = hours
    callback_context.variables["storm_credit_eligible"] = eligible

    print(f"[after_tool] {result['outage_id']}: {hours}h out, storm={storm}, storm_credit_eligible={eligible}")
    return None
