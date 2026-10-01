"""Builds stages/m1-end ... m7-end: the whole Cymbal Energy Care app as it should look at the end of each module,
in the folder format `cxas push` imports (cxas-scrapi 1.9.1, the CX Agent Studio app export layout).

Single source of truth: the instruction / tool / callback files already in 02-build ... 07-launch.
Placeholders filled in at load time by stages/load_stage.sh:
    __PROJECT_ID__   __POLICIES_DATASTORE__   __FAQ_DATASTORE__

Run from the pack root:  python3 src/make_stages.py
"""
import json, os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)
OUT = D("stages")
read = lambda *p: open(D(*p)).read()

# ---------------------------------------------------------------- shared pieces
GLOBAL_M2 = read("02-build", "instructions", "global_instruction.txt").rstrip("\n") + \
    "\n- Once the customer is verified, call them by first name: {customer_name}\n"
ESCALATION_LINES = "".join(l + "\n" for l in read("06-deploy", "global_instruction_ADD_escalation.txt").splitlines() if l.startswith("- "))
ROOT_M2 = read("02-build", "instructions", "root_agent.txt")
KNOWLEDGE = read("04-knowledge", "root_agent_ADD_knowledge.txt")
KNOWLEDGE_SUBTASK = KNOWLEDGE[KNOWLEDGE.index("  <subtask"):].rstrip("\n") + "\n"
ROOT_M4 = ROOT_M2.replace("</taskflow>", KNOWLEDGE_SUBTASK + "</taskflow>")
SPEC = read("04-knowledge", "specialists_ADD_policies.txt")
SPECIALIST_POLICY_STEP = SPEC[SPEC.index('    <step name="Policy questions">'):].rstrip("\n") + "\n"
VOICE = read("07-launch", "root_agent_ADD_voice_disclaimer.txt")
VOICE_BLOCK = VOICE[VOICE.index("{@startModalityVOICE}"):VOICE.index("{@endModalityVOICE}") + len("{@endModalityVOICE}")] + "\n\n"
OUTAGE = read("02-build", "instructions", "outage_agent.txt")
BILLING_BUG = read("02-build", "instructions", "billing_agent.txt")
BILLING_FIXED = read("05-evaluate", "billing_agent_FIXED.txt")
CALLBACK = read("02-build", "callbacks", "outage_state_after_tool.py")
TOOL_FILES = ["verify_customer", "check_outage", "report_outage", "get_bill_summary", "create_payment_arrangement"]

VARIABLES = [
    ("is_authenticated", "BOOLEAN", False, "True once verify_customer succeeds"),
    ("account_id", "STRING", "", "6-digit Cymbal Energy account number"),
    ("customer_name", "STRING", "", "Verified customer's name"),
    ("service_zip", "STRING", "", "ZIP code of the verified service address"),
    ("outage_id", "STRING", "", "Outage the customer is affected by (after-tool callback)"),
    ("estimated_restoration", "STRING", "", "ETR exactly as the outage system returned it (after-tool callback)"),
    ("hours_without_power", "NUMBER", 0, "Hours the outage has lasted (after-tool callback)"),
    ("storm_credit_eligible", "BOOLEAN", False, "More than 72 hours during a declared Major Storm Event (after-tool callback)"),
]

GUARDRAILS = {
    "prompt_guard": {
        "displayName": "prompt_guard", "description": "Blocks jailbreak and prompt-injection attempts.", "enabled": True,
        "llmPromptSecurity": {"defaultSettings": {}},
        # Every guardrail needs an action: without one each turn fails with
        # "Trigger action type ACTION_NOT_SET is not supported for prompt_guard" (found Sep 30 in class).
        "action": {"respondImmediately": {"responses": [{"text": (
            "I can only help with Cymbal Energy outages, billing and payment arrangements. What can I help you with today?")}]}},
    },
    "payment_scam_warning": {
        "displayName": "payment_scam_warning", "description": "Warns customers about gift-card and crypto payment scams.", "enabled": True,
        "contentFilter": {
            "bannedContentsInUserInput": ["gift card", "gift cards", "bitcoin", "crypto", "cryptocurrency", "prepaid card", "cash app"],
            "matchType": "SIMPLE_STRING_MATCH",
        },
        "action": {"respondImmediately": {"responses": [{"text": (
            "Cymbal Energy will never ask you to pay with gift cards, prepaid cards or cryptocurrency, and we never threaten "
            "same-day disconnection by phone. If someone contacted you asking for that, it is a scam: please hang up and call "
            "us at the number on your bill.")}]}},
    },
    "no_unauthorized_promises": {
        "displayName": "no_unauthorized_promises", "description": "No credits, refunds, waivers or restoration times that did not come from a tool, variable or policy.", "enabled": True,
        "llmPolicy": {
            "prompt": ("The agent must not promise bill credits, refunds, fee waivers, or restoration times unless they came "
                       "from a tool result, a session variable, or a Cymbal Energy policy document."),
            "policyScope": "AGENT_RESPONSE",
            "maxConversationMessages": 10,
        },
        "action": {"generativeAnswer": {"prompt": "Politely explain that you cannot promise that, and offer what you can do instead."}},
    },
}

PERSONA = {
    "name": "frustrated_after_the_storm", "displayName": "Frustrated after the storm",
    "personality": ("Impatient and frustrated. Has been without power for days and on hold for an hour. Gives short answers, "
                    "pushes for more than is offered, and asks for \"as long as possible\" whenever there is a choice."),
    "description": "Calling from a car on a cell phone on the Mississippi Gulf Coast. Has the bill in hand.",
}

# App-level yes/no checks (Evaluate ▸ scenario ▸ Add expectations ▸ Create expectation): the evaluator answers the question
# about the whole transcript and the scenario passes only on "Yes". This is how a scenario says "must NOT happen".
EVAL_EXPECTATIONS = {
    "max-6-installments": ("Did the agent keep every payment arrangement it offered or agreed to at 6 monthly installments or fewer?",
                           "Billing policy"),
    "ineligible-not-approved": ("Did the agent tell the customer the account is not eligible for a payment arrangement, without "
                                "saying an arrangement was approved or set up?", "Billing policy"),
}

SCENARIOS = {
    "arrangement-marcus-max-months": {
        "task": ("You are Marcus Bell, account 100871, service ZIP 39564. You cannot pay your past-due bill this month. Get a "
                 "payment arrangement with as many monthly installments as the agent will allow, and find out the monthly amount."),
        "facts": {"account_number": "100871", "zip_code": "39564"},
        "rubrics": ["The agent never offers or agrees to more than 6 monthly installments."],
        "checks": ["max-6-installments"],
        # the mock is exactly what the real tool returns for this account (the API requires one with a tool expectation)
        "tool": ("create_payment_arrangement", {"installments": 6},
                 {"approved": True, "arrangement_id": "PA-100871-6", "installments": 6, "monthly_amount": "$68.73", "total": "$412.37",
                  "fees_and_interest": "None: Cymbal Energy charges no fees or interest on payment arrangements."}),
    },
    "arrangement-linh-not-eligible": {
        "task": "You are Linh Nguyen, account 100455, service ZIP 39563. Ask to split your bill into 3 payments.",
        "facts": {"account_number": "100455", "zip_code": "39563"},
        "goal": "USER_GOAL_REJECTED",
        "rubrics": ["The agent explains the account is not eligible and never says an arrangement was approved."],
        "checks": ["ineligible-not-approved"],
        "tool": ("create_payment_arrangement", {"installments": 3},
                 {"approved": False, "reason": "Balance of $86.10 is below the $100.00 minimum for a payment arrangement."}),
    },
    "storm-credit-renee": {
        "task": ("You are Renee Thibodeaux, ZIP 39567. Your power has been out since the storm. Find out whether you can get any "
                 "credit for the outage and for the food you lost."),
        "facts": {"zip_code": "39567"},
        "rubrics": ["The agent mentions the $25 Storm Hardship Credit and that it must be requested."],
        "expect": ["Food spoilage from a storm outage isn't reimbursed, but you may qualify for a $25 Storm Hardship Credit, which you need to request within 30 days."],
    },
}

# ---------------------------------------------------------------- stage 1 (Start with AI-style single agent)
STAGE1_INSTRUCTION = """<role>
You are the Cymbal Energy customer care agent. You help customers of Cymbal Energy, an electric and natural gas utility on the Mississippi Gulf Coast, with power outages, billing questions and payment arrangements.
</role>
<persona>
Warm, calm and empathetic. Keep answers short.
</persona>
<taskflow>
  <subtask name="Outages">
    <step name="Check">Ask for the ZIP code of the service address and call {@TOOL: check_outage}. Share the status and estimated restoration time.</step>
    <step name="Report">If there is no known outage, offer to report the problem with {@TOOL: report_outage}.</step>
  </subtask>
  <subtask name="Billing">
    <step name="Verify">Ask for the account number and ZIP code and call {@TOOL: verify_customer}.</step>
    <step name="Balance">Call {@TOOL: get_bill_summary} and share the balance and due date.</step>
    <step name="Arrangement">If the customer cannot pay, offer a payment arrangement with {@TOOL: create_payment_arrangement}.</step>
  </subtask>
  <subtask name="Gas odor">
    <step name="Safety">If the customer smells gas, tell them to leave the building and call the gas emergency line, then transfer them to a human.</step>
  </subtask>
</taskflow>
"""
# Placeholder tools as Start with AI drafts them from the requirements doc's test data (section 5a): canned answers
# for one test customer, no business rules and no memory between calls. M2 replaces them with the real mock tools.
PH_HEAD = "from typing import Any, Dict\n\n# PLACEHOLDER built from the requirements doc's test data. Not connected to a real system yet.\n"
STAGE1_TOOLS = {
    "verify_customer": PH_HEAD + '''TEST_ACCOUNT, TEST_ZIP = "123456", "39562"


def verify_customer(account_number: str, zip_code: str) -> Dict[str, Any]:
    """Verifies the customer with their account number and service ZIP code."""
    acct = "".join(ch for ch in str(account_number) if ch.isdigit())
    zip5 = "".join(ch for ch in str(zip_code) if ch.isdigit())[:5]
    if acct == TEST_ACCOUNT and zip5 == TEST_ZIP:
        return {"verified": True, "customer_name": "Patrick Haggerty",
                "service_address": "3702 Magnolia St, Moss Point, MS 39562", "source": "placeholder"}
    return {"verified": False, "message": "The account number and ZIP code do not match our records.",
            "agent_action": "Ask the customer to check the account number on their bill and try again.", "source": "placeholder"}
''',
    "check_outage": PH_HEAD + '''

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
''',
    "report_outage": PH_HEAD + '''

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
''',
    "get_bill_summary": PH_HEAD + '''

def get_bill_summary() -> Dict[str, Any]:
    """Returns the verified customer's balance, due date and last payment."""
    return {"customer_name": "Patrick Haggerty", "balance": "$238.45", "due_date": "October 8",
            "past_due_days": 0, "last_payment": "$212.10 on September 8", "source": "placeholder",
            "agent_action": "Share the balance and due date. Only give them to a customer verified with verify_customer."}
''',
    "create_payment_arrangement": PH_HEAD + '''

def create_payment_arrangement(installments: int) -> Dict[str, Any]:
    """Creates a payment arrangement for the verified customer."""
    n = int(installments)
    if n < 1:
        return {"approved": False, "error": "Number of installments is missing.",
                "agent_action": "Ask how many monthly installments the customer wants."}
    return {"approved": True, "arrangement_id": "PA-123456-" + str(n), "installments": n,
            "monthly_amount": "$" + format(238.45 / n, ".2f"), "source": "placeholder"}
''',
}


# ---------------------------------------------------------------- writers
def wjson(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")


def wtext(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def docstring(code):
    m = re.search(r'"""(.*?)"""', code, re.S)
    return " ".join(m.group(1).split()) if m else ""


def python_tool(stage_dir, name, code):
    wtext(os.path.join(stage_dir, "tools", name, "python_function", "python_code.py"), code)
    wjson(os.path.join(stage_dir, "tools", name, f"{name}.json"), {
        "name": name, "displayName": name, "executionType": "SYNCHRONOUS",
        "pythonFunction": {"name": name, "pythonCode": f"tools/{name}/python_function/python_code.py",
                           "description": docstring(code)},
    })


def datastore_tool(stage_dir, name, placeholder, ds_type, description):
    wjson(os.path.join(stage_dir, "tools", name, f"{name}.json"), {
        "name": name, "displayName": name, "executionType": "SYNCHRONOUS",
        "dataStoreTool": {"name": name, "description": description,
                          "dataStoreSource": {"dataStore": {"name": placeholder, "type": ds_type}}},
    })


# The importer resolves rootAgent / childAgents / {@AGENT: ...} by displayName, and the export layout names each
# folder after it. Spaces break that ("400 Reference not found"), so every agent is snake_case: folder = name = displayName.
# The live build uses the same names, so the source instructions already say {@AGENT: cymbal_care}; this map only guards
# against an old friendly name creeping back in.
AGENT_REFS = {"Cymbal Care": "cymbal_care", "Outage Agent": "outage_agent", "Billing Agent": "billing_agent"}


def agent(stage_dir, name, description, instruction, tools, children=(), after_tool=None):
    base = os.path.join(stage_dir, "agents", name)
    for shown, ref in AGENT_REFS.items():
        instruction = instruction.replace("{@AGENT: " + shown + "}", "{@AGENT: " + ref + "}")
    assert "{@AGENT: " not in re.sub(r"\{@AGENT: [a-z_]+\}", "", instruction), f"unmapped agent reference in {name}"
    wtext(os.path.join(base, "instruction.txt"), instruction)
    cfg = {"name": name, "displayName": name, "description": description,
           "instruction": f"agents/{name}/instruction.txt", "tools": list(tools)}
    if children:
        cfg["childAgents"] = list(children)
    if after_tool:
        wtext(os.path.join(base, "after_tool_callbacks", "after_tool_callbacks_01", "python_code.py"), after_tool)
        cfg["afterToolCallbacks"] = [{"pythonCode": f"agents/{name}/after_tool_callbacks/after_tool_callbacks_01/python_code.py",
                                      "description": "Outage facts and storm-credit flag into session variables"}]
    wjson(os.path.join(base, f"{name}.json"), cfg)


def app_json(stage_dir, root, tools, stage, guardrails=(), variables=True, global_instruction=True, extra=None):
    cfg = {
        "name": "cymbal_energy_care", "displayName": "Cymbal Energy Care",
        "description": f"Cymbal Energy customer care demo agent: end of module {stage} (loaded with cxas push).",
        "rootAgent": root,
        "languageSettings": {"defaultLanguageCode": "en-US"},
        "timeZoneSettings": {"timeZone": "America/Chicago"},
        "toolExecutionMode": "PARALLEL",
    }
    if global_instruction:
        cfg["globalInstruction"] = "global_instruction.txt"
    if variables:
        cfg["variableDeclarations"] = [
            {"name": n, "description": d, "schema": {"type": t, "default": v, "required": []}} for n, t, v, d in VARIABLES]
    if guardrails:
        cfg["guardrails"] = list(guardrails)
    if extra:
        cfg.update(extra)
    wjson(os.path.join(stage_dir, "app.json"), cfg)


# ---------------------------------------------------------------- stages
def stage1(sd):
    for name, code in STAGE1_TOOLS.items():
        python_tool(sd, name, code)
    agent(sd, "cymbal_energy_care_agent",
          "Assists Cymbal Energy customers with power outages, billing inquiries and payment arrangements.",
          STAGE1_INSTRUCTION, list(STAGE1_TOOLS) + ["end_session"])
    app_json(sd, "cymbal_energy_care_agent", list(STAGE1_TOOLS), 1, variables=False, global_instruction=False)


def multi_agent(sd, stage, root_instruction, global_text, billing, knowledge=False, voice=False, extra=None, pantry=False):
    """knowledge: data store tools exist AND are attached to the agents (end of M4 on).
    pantry: data store tools exist but aren't attached yet (end of M3: pre-built for the M4 cooking-show demo)."""
    for name in TOOL_FILES:
        python_tool(sd, name, read("02-build", "tools", f"{name}.py"))
    ds = []
    if knowledge or pantry:
        datastore_tool(sd, "cymbal_policies", "__POLICIES_DATASTORE__", "UNSTRUCTURED",
                       "Cymbal Energy policies: storm restoration and outage credits, payment arrangements and disconnection, natural gas safety.")
        datastore_tool(sd, "cymbal_faq", "__FAQ_DATASTORE__", "FAQ",
                       "Short answers to common Cymbal Energy customer questions.")
        ds = ["cymbal_policies", "cymbal_faq"] if knowledge else []
    # Scoped by journey: the root gets both (general questions arrive there); each specialist gets the policies only,
    # plus a "Policy questions" step, because policy questions come up mid-conversation and tools belong to agents.
    spec = ["cymbal_policies"] if knowledge else []
    outage_text, billing_text = OUTAGE, billing
    if knowledge:
        # (billing_agent_FIXED.txt already carries the step: M5 pastes it over the whole billing_agent)
        outage_text, billing_text = (t if SPECIALIST_POLICY_STEP in t else
                                     t.replace('    <step name="Wrap up">', SPECIALIST_POLICY_STEP + '    <step name="Wrap up">', 1)
                                     for t in (OUTAGE, billing))
        assert SPECIALIST_POLICY_STEP in outage_text and SPECIALIST_POLICY_STEP in billing_text
    root_tools = ["end_session"] + ds + (["customize_response"] if voice else [])
    agent(sd, "cymbal_care", "Front door of Cymbal Energy customer care; greets and routes.",
          (VOICE_BLOCK if voice else "") + root_instruction, root_tools, children=["outage_agent", "billing_agent"])
    agent(sd, "outage_agent", "Handles power outages, downed lines, and outage status by ZIP code.",
          outage_text, ["check_outage", "report_outage", "end_session"] + spec, after_tool=CALLBACK)
    agent(sd, "billing_agent", "Handles bills, balances, payments and payment arrangements.",
          billing_text, ["verify_customer", "get_bill_summary", "create_payment_arrangement", "end_session"] + spec)
    wtext(os.path.join(sd, "global_instruction.txt"), global_text)
    for gname, gcfg in GUARDRAILS.items():
        assert gcfg.get("action"), f"guardrail {gname} has no action (the runtime rejects every turn)"
        wjson(os.path.join(sd, "guardrails", gname, f"{gname}.json"), gcfg)
    app_json(sd, "cymbal_care", TOOL_FILES + ds, stage, guardrails=list(GUARDRAILS), extra=extra)


def evaluations(sd):
    """Same shape as the UI (Evaluate ▸ + Add test case ▸ Scenario): a user goal with its expected outcome, positive
    expectations (a tool call with its expected input, or an agent response), and rubrics for anything that must NOT happen."""
    for name, (question, category) in EVAL_EXPECTATIONS.items():
        wjson(os.path.join(sd, "evaluationExpectations", name, f"{name}.json"),
              {"displayName": name, "llmCriteria": {"prompt": question}, "tags": [category]})
    for name, s in SCENARIOS.items():
        if "tool" in s:
            tool, args, mock = s["tool"]
            expectations = [{"toolExpectation": {"expectedToolCall": {"tool": tool, "args": args},
                                                 "mockToolResponse": {"tool": tool, "response": mock}}}]
        else:
            expectations = [{"agentResponse": {"role": "agent", "chunks": [{"text": r}]}} for r in s["expect"]]
        wjson(os.path.join(sd, "evaluations", name, f"{name}.json"), {
            "displayName": name,
            "scenario": {"task": s["task"], "userFacts": [{"name": k, "value": v} for k, v in s["facts"].items()],
                         "maxTurns": 15, "rubrics": s["rubrics"], "scenarioExpectations": expectations,
                         "userGoalBehavior": s.get("goal", "USER_GOAL_SATISFIED"),
                         **({"evaluationExpectations": s["checks"]} if s.get("checks") else {})},
        })


EVAL_EXTRA = {"evaluationPersonas": [PERSONA], "evaluationSettings": {"scenarioConversationInitiator": "USER"}}
REDACTION = {"loggingSettings": {"redactionConfig": {
    "enableRedaction": True,
    "inspectTemplate": "projects/__PROJECT_ID__/locations/us/inspectTemplates/cymbal-inspect",
    "deidentifyTemplate": "projects/__PROJECT_ID__/locations/us/deidentifyTemplates/cymbal-deidentify"}}}

STAGES = {
    1: lambda sd: stage1(sd),
    2: lambda sd: multi_agent(sd, 2, ROOT_M2, GLOBAL_M2, BILLING_BUG),
    3: lambda sd: multi_agent(sd, 3, ROOT_M2, GLOBAL_M2, BILLING_BUG, pantry=True),
    4: lambda sd: multi_agent(sd, 4, ROOT_M4, GLOBAL_M2, BILLING_BUG, knowledge=True),
    5: lambda sd: (multi_agent(sd, 5, ROOT_M4, GLOBAL_M2, BILLING_FIXED, knowledge=True, extra=EVAL_EXTRA), evaluations(sd)),
    6: lambda sd: (multi_agent(sd, 6, ROOT_M4, GLOBAL_M2 + ESCALATION_LINES, BILLING_FIXED, knowledge=True, extra=EVAL_EXTRA), evaluations(sd)),
    7: lambda sd: (multi_agent(sd, 7, ROOT_M4, GLOBAL_M2 + ESCALATION_LINES, BILLING_FIXED, knowledge=True, voice=True,
                               extra={**EVAL_EXTRA, **REDACTION}), evaluations(sd)),
}

if __name__ == "__main__":
    for n, build in STAGES.items():
        sd = os.path.join(OUT, f"m{n}-end")
        shutil.rmtree(sd, ignore_errors=True)
        build(sd)
        print("built", os.path.relpath(sd, ROOT))
