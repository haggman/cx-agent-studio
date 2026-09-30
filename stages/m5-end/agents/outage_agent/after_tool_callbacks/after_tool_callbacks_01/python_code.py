from typing import Any


def after_tool_callback(tool: Tool, input: dict[str, Any], callback_context: CallbackContext, tool_response: dict[str, Any]) -> Optional[dict[str, Any]]:
    """Runs after every tool call on the Outage Agent. When check_outage returns an active outage,
    copy the outage facts into session variables and work out storm-credit eligibility in code:
    more than 72 hours out during a declared Major Storm Event (policy OP-110).
    Returns None, so the tool's own response reaches the model unchanged."""
    if getattr(tool, "name", "") != "check_outage" or not isinstance(tool_response, dict):
        return None  # every other tool passes straight through

    if not tool_response.get("outage_id"):  # no active outage for this ZIP
        callback_context.set_variable("storm_credit_eligible", False)
        print("[after_tool] check_outage: no active outage, storm_credit_eligible=False")
        return None

    hours = int(tool_response.get("hours_without_power") or 0)
    storm = tool_response.get("major_storm_event")
    eligible = bool(storm) and hours > 72

    callback_context.set_variable("outage_id", tool_response["outage_id"])
    callback_context.set_variable("estimated_restoration", tool_response.get("estimated_restoration", ""))
    callback_context.set_variable("hours_without_power", hours)
    callback_context.set_variable("storm_credit_eligible", eligible)

    print(f"[after_tool] {tool_response['outage_id']}: {hours}h out, storm={storm}, storm_credit_eligible={eligible}")
    return None
