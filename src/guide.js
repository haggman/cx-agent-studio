// Planning guide: the story, the map, setup, per-block talk track and detail, fact sheet, things to confirm.
const K = require("./content");
const H = require("./helpers");
const { C, run, P, box, stepBox, resetBox, table, slideLabel, save, Document, Paragraph, PageBreak, HeadingLevel, LevelFormat } = H;
const PAGE_W = 12240, MARGIN = 1080, W = PAGE_W - 2 * MARGIN;

const doc = [];
const add = (...x) => doc.push(...x);
const H1 = (t, pb = true) => new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: pb, children: [run(t, { bold: true, size: 32, color: C.blue })], spacing: { before: 200, after: 120 } });
const H2 = (t, color = C.blue) => new Paragraph({ heading: HeadingLevel.HEADING_2, keepNext: true, children: [run(t, { bold: true, size: 26, color })], spacing: { before: 260, after: 80 } });
const H3 = (t, color = C.teal) => new Paragraph({ heading: HeadingLevel.HEADING_3, keepNext: true, children: [run(t, { bold: true, size: 22, color })], spacing: { before: 160, after: 40 } });
const bullet = (children) => new Paragraph({ children: typeof children === "string" ? [run(children)] : children, numbering: { reference: "bul", level: 0 }, spacing: { before: 20, after: 40, line: 264 } });
const say = (t) => P([run("SAY  ", { bold: true, color: C.teal, size: 20 }), run(t, { italic: true })]);
const gap = () => P("", { before: 0, after: 60 });
const mono = (t) => run(t, { mono: true, size: 20 });

// ------------------------------------------------------------------ title
add(P([run("Planning Guide — Build Agents with CX Agent Studio", { bold: true, size: 40, color: C.blue })], { after: 40 }));
add(P([run("One evolving demo across both days: ", { size: 22 }), run("Cymbal Energy Care", { bold: true, size: 22 }), run(", a customer care agent for a fictional Gulf Coast electric and gas utility. First delivery: Mon–Tue, September 28–29, 2026.", { size: 22 })]));
add(P([run("This is the prep document. On the day, use the ", { size: 20, color: C.gray }), run("TELEPROMPTER", { bold: true, size: 20, color: C.orange }),
  run(" file: one block per page, slide first, nothing else. Both are generated from src/content.js. Colour key: ", { size: 20, color: C.gray }),
  run("slides / text to type", { bold: true, size: 20, color: C.orange }), run("  ·  ", { size: 20, color: C.gray }),
  run("clicks and reset states", { bold: true, size: 20, color: C.purple }), run("  ·  ", { size: 20, color: C.gray }),
  run("files and commands", { bold: true, size: 20, color: C.teal }), run("  ·  ", { size: 20, color: C.gray }),
  run("versions / good results", { bold: true, size: 20, color: C.green }), run("  ·  ", { size: 20, color: C.gray }),
  run("gotchas", { bold: true, size: 20, color: C.red })]));

add(box([
  P([run("How this demo works", { bold: true, color: C.blue })], { after: 40 }),
  bullet("One app, built live in front of the room, that gains one capability per module. Nothing is pre-built except the data files."),
  bullet([run("Every stage ends with a saved version (v1 … v7). The reset at the start of any block is \"Versions ▸ restore the previous one\". Last night's dry-run app, renamed "), run("Cymbal Energy Care (dry run)", { bold: true }), run(", is the backup for every stage.")]),
  bullet("The main thread is the storm credit: in M1 the agent guesses at the freezer-credit question; in M2 an after-tool callback turns the outage data into a storm_credit_eligible flag; in M4 the policy PDF supplies the details ($25, request within 30 days). Gas safety is a global-instruction behavior, guarded by a golden in M5."),
  bullet("One planted bug: the billing_agent's instructions say \"up to 12 monthly installments\" while the tool enforces 6. Nobody mentions it until the M5 evaluation catches it."),
  bullet("M1 is live. At each module break one command catches the app up to the end of the previous module (section 3.2): bash ~/cx-agent-studio/catch_up.sh <module you are about to teach>. Use it every break for a guaranteed start state, or only when a live build went sideways."),
  bullet("Slow things are started early and revisited: Start with AI (slide 13 → 26) and evaluation runs (M5 slide 27 → 31). Data store indexing (about 15 minutes) is a cooking show: setup.sh builds both stores ahead of time, in class you walk the create dialog under another name and cancel, then open the ones made earlier."),
], C.blue, W, 12));

// ------------------------------------------------------------------ 1. story
add(H1("1. The story in one page"));
add(P("Cymbal Energy delivers electricity and natural gas to about 212,000 customers on the Mississippi Gulf Coast (Pascagoula, Moss Point, Gautier, Ocean Springs). Tropical Storm Delphine has just come through: a feeder is down in Pascagoula (ZIP 39567), 2,140 customers have been out for 76 hours, and a declared Major Storm Event (MSE-2026-04) is in effect. On storm days contact volume rises eight times, and most people just want to know whether we know."));
add(P("Why a utility: it exercises every module naturally. Identity and lookups (tools and variables), rules that must not be left to a prompt (payment arrangements in code), tool results that should become state (the storm-credit callback), a safety behavior every agent must share (gas leaks, in the global instruction), policies nobody can guess (storm credit, data stores), a voice channel people really use, card numbers to redact, and a human hand-off."));
add(table(["Stage", "Module", "The agent gains", "Version"], [
  ["1", "M1", "Start with AI draft from a requirements PDF + call transcripts; first conversation; the planted storm question", "v1-start-with-ai"],
  ["2", "M2", "Root + outage_agent + billing_agent; global instruction (incl. gas safety); Restructure instructions; 8 variables; after-tool callback that writes outage state and the storm-credit flag; 5 Python tools; Prompt Guard, scam blocklist, no-promises rule", "v2-multi-agent"],
  ["3", "M3", "SCRAPI from Cloud Shell; Antigravity CLI + MCP creates a version; native audio call with an interruption", "v3-cli-checkpoint, v3-day1"],
  ["4", "M4", "cymbal_policies (3 PDFs) and cymbal_faq (CSV) data store tools; the storm question answered with a citation", "v4-knowledge"],
  ["5", "M5", "Two goldens, a frustrated persona, a scenario; the eval catches the 12-installment bug; fix and re-run", "v5-evaluated"],
  ["6", "M6", "Web widget on a mock outage page; runSession over curl; escalation with end_session", "v6-escalation"],
  ["7", "M7", "Voice-only recording disclaimer (no barge-in); DLP redaction of cards, SSNs, phones in logs; the version list as the course recap", "v7-launch-ready"],
], [700, 800, 6180, 2400]));

// ------------------------------------------------------------------ 2. map
add(H1("2. Two-day demo map"));
add(P([run("Slide numbers are PDF pages of the delivery-copy decks in the 2026-09-28 folder. Where the printed footer differs (M2 after slide 13, M4 after slide 43, M7 slide 31) the footer is in brackets. ", { color: C.gray, size: 20 })]));
[1, 2].forEach(day => {
  add(H2("Day " + day, C.orange));
  add(table(["#", "Module · slide", "Min", "Block", "Core?"], K.blocks.filter(b => b.day === day).map(b => [
    String(b.n), b.module + " " + b.slides + (b.footer ? " [" + b.footer + "]" : ""), String(b.mins), b.title, b.optional ? "optional" : "core"]),
    [500, 2000, 600, 5880, 1100]));
  const core = K.blocks.filter(b => b.day === day && !b.optional).reduce((a, b) => a + b.mins, 0);
  const all = K.blocks.filter(b => b.day === day).reduce((a, b) => a + b.mins, 0);
  add(P([run(`Day ${day}: about ${core} minutes of core demo, ${all} with the optional blocks. Demos replace the slides' own demo time; they are not all extra.`, { color: C.gray, size: 20 })]));
});
add(H3("Running long? Cut in this order", C.red));
add(bullet("Day 1: the product tour (block 3: do it in 2 minutes while talking), then Antigravity CLI (block 12: keep SCRAPI), then native audio (block 13: the M3 lab covers voice in depth)."));
add(bullet("Day 2: the optional blocks (15, 17, 24), then the API block (22: show the curl on the slide instead). Never cut block 16 (yesterday's question answered) or block 20 (the eval catching the bug): they are the payoff of the two threads."));
add(bullet("If Day 1 slips and M3 moves to Day 2 morning, blocks 11–13 move with it; the Day 2 reset becomes v2-multi-agent."));

// ------------------------------------------------------------------ 3. setup
add(H1("3. Setup"));
add(H2("3.1 Tonight: load the project and do one full dry run"));
add(P("Any Google Cloud project where you are Owner works (the class uses a long-running Qwiklabs project, good for a week). Everything below happens in that project, in Cloud Shell. Everything the demos run lives in the repo, which the scripts expect at ~/cx-agent-studio (Cloud Shell always starts in ~, so this works in anyone's Cloud Shell). Paste these one box at a time:"));
const shellSteps = [
  ["Step 1 · Point Cloud Shell at the class project", "gcloud config get-value project",
   "Prints your project ID. If it's empty or wrong: gcloud config set project YOUR_PROJECT_ID, then run it again."],
  ["Step 2 · Put the pack at ~/cx-agent-studio (clone the repo, or upload the zip)", "cd ~ && git clone https://github.com/haggman/cx-agent-studio.git\nls ~/cx-agent-studio/",
   "Shows 01-start-with-ai … 07-launch, setup, stages, setup.sh and catch_up.sh. Later updates: git -C ~/cx-agent-studio pull. No git? Cloud Shell ▸ ⋮ (More) ▸ Upload ▸ cymbal-energy-demo-pack.zip, then unzip -o ~/cymbal-energy-demo-pack.zip -d ~/cx-agent-studio (same folder, same paths; use one way or the other, since git won't clone into a folder that already has files)."],
  ["Step 3 · One command for everything that isn't a lesson (safe to rerun)", "bash ~/cx-agent-studio/setup.sh",
   "Six numbered steps; each line starts with ✓ (already there) or + (created now). 1 APIs and bucket (3 policy PDFs, FAQ CSV, metadata JSONL). 2 SCRAPI 1.9.1. 3 the two M4 data stores, cymbal-policies and cymbal-faq, created through the Discovery Engine API and imported once (indexing then runs about 15 minutes on its own). 4 the M7 DLP templates in us and global. 5 Antigravity: the CX Agent Studio MCP server in ~/.gemini/config/mcp_config.json, Cloud Shell's broken Vertex plugin parked, CXAS skills in ~/cx-agent-studio-skills. 6 whether the app exists. Run it again in the morning: every line should be ✓, and both data stores should say \"already has documents\"."],
  ["Step 4 · Sign in to Antigravity once (the only interactive step)", "cd ~/cx-agent-studio/03-programmatic && agy     (open the sign-in URL, paste the code back, type /mcp, check Connected, /quit)",
   "The CX Agent Studio server shows Connected. No MCP enable command is needed: the endpoint comes with the ces API."],
];
shellSteps.forEach(([title, cmd, expectText]) => { add(stepBox({ tag: "SHELL", label: "CLOUD SHELL · " + title, text: cmd, expect: expectText }, W, 20)); add(P("", { before: 0, after: 40 })); });
add(P([run("If setup.sh stops, it prints the line it stopped on. The likeliest cause is the API enable hitting a permissions limit on your user: check that it is Owner on the project, or enable the three APIs from Console ▸ APIs & Services ▸ Library, then rerun setup.sh (finished steps are skipped). Terraform was considered and skipped: it can create the data stores but not import their documents, and its state file would fight every change you make in the UI during class.", { size: 20, color: C.gray })]));
add(P([run("Then:", { bold: true })], { before: 120 }));
const setupSteps = [
  [run("Do the whole teleprompter once, blocks 1–26, in the same project. Note anything that differs from the click paths (section 6 lists the ones I could not confirm from the docs).")],
  [run("When it's done, rename the app "), run("Cymbal Energy Care (dry run)", { bold: true }), run(". Its versions v1…v7 are your backup for every stage tomorrow and Tuesday. The SCRAPI script and the CLI prompts look for the exact name \"Cymbal Energy Care\", so the live app must have that name and the dry run must not.")],
  [run("In the dry run, do M4 block 14 exactly as written (Cancel at the end). If you do click Create, the extra store is named cymbal_policies_live and the scripts ignore it.")],
];
setupSteps.forEach((c, i) => add(P([run((i + 1) + ".  ", { bold: true, color: C.blue })].concat(c))));
add(H2("3.2 Catch-up between modules (the stage loader)"));
add(P("Run of show: do the M1 demos live. At each break after that, run one Cloud Shell command that loads the app as it should look at the end of the previous module and saves that version, then refresh the console. Every module then starts from exactly the state the teleprompter expects, whatever happened live. The teleprompter has a CATCH-UP page before M2, M3, M5, M6 and M7 (for M4 it's the first line of the Day 2 morning list)."));
add(stepBox({ tag: "SHELL", label: "CLOUD SHELL · before teaching module N", text: "bash ~/cx-agent-studio/catch_up.sh N          # N = the module you are about to teach: 2 … 7\nbash ~/cx-agent-studio/catch_up.sh done       # the finished app (end of M7)", expect: "About 1–2 minutes. Then console ▸ refresh ▸ Preview agent ▸ Start new conversation." }, W, 20));
add(P("", { before: 0, after: 40 }));
add(table(["Before", "Command", "Loads", "What the app has afterwards"], K.CATCH_UP.map(c => [c.module === "done" ? "Finished" : c.module,
  "catch_up.sh " + (c.module === "done" ? "done" : c.module.slice(1)), c.version, c.has]), [900, 1700, 1900, 5580], { size: 18 }));
add(H3("What it does, so nothing surprises you"));
[
  "Safe in a brand-new Cloud Shell: the only prerequisite is the pack unzipped in ~/cx-agent-studio (3.1, step 2). It enables the three APIs, installs cxas-scrapi 1.9.1 if it's missing or a different version, and puts ~/.local/bin on the PATH itself.",
  "Before M4 onward it runs the same checks as setup.sh for the bucket and the two data stores (creating only what's missing) and fills their names into the data store tools: before M4 the tools are there but not attached (the cooking-show dish), before M5 onward they're attached. Before M7 it checks the DLP templates, and from M7 on it points the cymbal-web widget channel at the new version.",
  "It pushes stages/m<N-1>-end over the app named exactly \"Cymbal Energy Care\" with cxas push --overwrite (creating the app if there isn't one), then saves the version, but only if no version with that name exists yet, so a second run doesn't pile up duplicates (it keeps the one you saved live, if any). --overwrite replaces every agent, tool and guardrail in the app, so anything built live is gone; the version history stays, so live versions can still be restored.",
  "Loaded agents are snake_case: cymbal_care, outage_agent, billing_agent (and cymbal_energy_care_agent for the M1 draft). The importer resolves the root agent, sub-agents and {@AGENT: …} references by display name, and names with spaces fail with 400 Reference not found (that was the first push error). The live build uses the same names (block 4 creates them), so a catch-up looks exactly like what you built by hand.",
  "If it stops, it prints the line it stopped at. Copy the whole output. The folders are generated by src/make_stages.py from the same files the live demo pastes; bash ~/cx-agent-studio/stages/load_stage.sh N does the same thing addressed by the module that just ended.",
].forEach(t => add(bullet(t)));
add(stepBox({ tag: "SHELL", label: "CLOUD SHELL · optional tonight: build every restore point in order", text: "bash ~/cx-agent-studio/stages/build_all_stages.sh", expect: "Saves v1 … v7 (skips names that already exist). Uses the data stores setup.sh built." }, W, 20));
add(H2("3.3 Morning of day 1 (5 minutes)"));
["bash ~/cx-agent-studio/setup.sh: every line ✓",
 "No app named exactly \"Cymbal Energy Care\" exists (only the dry run)",
 "ces.cloud.google.com open on the class project; Cloud Shell in a second tab",
 "Your file browser open on 01-start-with-ai in your local clone (the two files for the Start with AI upload)",
 "Browser microphone permission granted for ces.cloud.google.com; headset or speakers connected"].forEach(t => add(bullet(t)));
add(H2("3.4 Morning of day 2 (5 minutes)"));
["bash ~/cx-agent-studio/setup.sh (both data stores say \"already has documents\"), then bash ~/cx-agent-studio/catch_up.sh 4 (end-of-M3 agent plus cymbal_policies and cymbal_faq in Tools, not attached: block 14 needs them there)",
 "Cloud Shell ▸ Open Editor: ~/cx-agent-studio/06-deploy/cymbal-energy-outage-center.html opens (the PASTE markers are at the bottom); block 21 serves it with python3 -m http.server 8080 and Web Preview",
 "Cloud Shell still has ~/cx-agent-studio (Cloud Shell home persists; clone again or re-upload the zip if the project was reset)"].forEach(t => add(bullet(t)));

// ------------------------------------------------------------------ 4. blocks
add(H1("4. Block by block: why, talk track, steps, expected results"));
add(P([run("Each block is the teleprompter block plus the reasoning behind it. The \"why\" line is the answer to \"why should I care on Monday\".", { color: C.gray, size: 20 })]));
let lastModule = "";
K.blocks.forEach(b => {
  if (b.module !== lastModule) {
    add(H2(b.module + " — " + K.DECKS[b.module].replace(/^0\d_/, ""), C.orange));
    lastModule = b.module;
  }
  add(H3(`${b.n}. ${b.title}   ·   ${slideLabel(b)}${b.footer ? " [footer " + b.footer + "]" : ""}   ·   ~${b.mins} min${b.optional ? "   ·   optional" : ""}`, C.blue));
  add(P([run("WHY  ", { bold: true, color: C.green, size: 20 }), run(b.why)]));
  (b.say || []).forEach(s => add(say(s)));
  add(resetBox(b.reset, W));
  add(gap());
  if (b.files.length) add(P([run("FILES  ", { bold: true, color: C.purple, size: 20 }), run(b.files.join("   ·   "), { size: 20, color: C.purple })]));
  b.steps.forEach(s => { add(stepBox(s, W, 20)); add(P("", { before: 0, after: 20 })); });
  if (b.gotcha) add(P([run("GOTCHA  ", { bold: true, color: C.red, size: 20 }), run(b.gotcha, { size: 20 })], { before: 40 }));
});

// ------------------------------------------------------------------ 5. fact sheet
add(H1("5. Fact sheet — keep on the second screen"));
add(H2("Customers (all fictional)"));
add(table(["Account", "Name", "ZIP", "Address", "Bill", "Arrangement?"], [
  ["100234", "Renee Thibodeaux", "39567", "1418 Beach Blvd, Pascagoula", "$142.80 due Oct 6", "Eligible (not past due)"],
  ["100871", "Marcus Bell", "39564", "22 Porter Ave, Ocean Springs", "$412.37, 18 days past due (due Sep 9)", "Eligible: 2–6 months; 6 = $68.73/mo"],
  ["100455", "Linh Nguyen", "39563", "5107 Main St, Moss Point", "$86.10 due Oct 2", "Not eligible: under $100 (and had one in the last 12 months)"],
  ["123456", "Patrick Haggerty (the presenter)", "39562", "3702 Magnolia St, Moss Point", "$238.45 due Oct 8", "Eligible: 2–6 months; 4 = $59.61/mo. Also the M1 test customer (placeholder tools)"],
], [900, 1600, 700, 2300, 2300, 2280]));
add(H2("Outages (check_outage)"));
add(table(["ZIP", "Area", "Status", "Detail"], [
  ["39567", "Pascagoula", "Active, OUT-58812", "Tropical Storm Delphine damaged a main feeder; 2,140 customers; 76 hours; MSE-2026-04; crew on site; ETR 11:00 PM tonight"],
  ["39562", "Moss Point", "Active, OUT-58840", "Tree limb on a line; 310 customers; 2 hours; crew en route; ETR 4:30 PM today"],
  ["39563, 39564, 39565, 39581", "Moss Point (39563), Ocean Springs, …", "No outage", "Offer report_outage; \"line down\" in the description returns an Emergency ticket (EMR-…)"],
  ["anything else", "", "Not served", "Outside the service area"],
], [1300, 1700, 1800, 5280]));
add(H2("Policies in the data store"));
add(table(["Doc", "The facts the demo relies on"], [
  ["OP-110 Storm Restoration and Outage Credit Policy", "No reimbursement for storm spoilage. $25 Storm Hardship Credit: residential, out >72 consecutive hours in a declared Major Storm Event, one per event, must be requested within 30 days of restoration (cymbalenergy.example/storm-credit or 1-800-555-0142). Clear-weather equipment failure: claims up to $300 within 60 days. Restoration priority order. Reconnection fees waived during an MSE."],
  ["BP-210 Payment Arrangement and Disconnection Policy", "Arrangements: balance ≥ $100, none in the prior 12 months, 2–6 installments, longer needs a supervisor. No disconnection on Fridays/weekends/holidays, in extreme heat (heat index ≥ 98°F) or cold (≤ 32°F), for 30 days after a medical certificate (renewable once), or during an MSE. $35 reconnection fee. Never asks for gift cards or crypto. LIHEAP; Cymbal Cares fund up to $300."],
  ["GS-001 Natural Gas Safety Guide", "Rotten-egg smell (mercaptan), hissing; leave, no switches or phones, call 911 and 1-800-555-0199 from outside; no charge for leak checks; generators 20 feet from the house; call 811 before digging."],
  ["cymbal_energy_faq.csv (18 rows)", "Hours, streetlights (pole number, 5 business days), payment locations, start/stop service, deposits (up to $150), payment methods, outage text alerts (REG to 55501), Budget Billing, downed lines, tree trimming, offices, Medical Priority Registry, due-date change."],
], [3000, 7080]));
add(H2("Building blocks"));
add(table(["Kind", "Name", "Where", "Notes"], [
  ["Agent", "cymbal_care (root)", "—", "Greets, routes; later the knowledge subtask and the voice block"],
  ["Agent", "outage_agent", "sub-agent", "check_outage, report_outage (+ both data stores)"],
  ["Agent", "billing_agent", "sub-agent", "verify_customer, get_bill_summary, create_payment_arrangement (+ both data stores)"],
  ["Variable", "is_authenticated · account_id · customer_name · service_zip", "app", "Written by verify_customer; read by every agent"],
  ["Variable", "outage_id · estimated_restoration · hours_without_power · storm_credit_eligible", "app", "Written by the after-tool callback"],
  ["Callback", "after_tool_callback (outage state)", "outage_agent", "After check_outage: writes outage_id, estimated_restoration, hours_without_power, storm_credit_eligible (>72 h in a declared storm); returns None so the tool response is unchanged"],
  ["Guardrails", "Prompt Guard · Payment scam warning (blocklist) · No unauthorized promises (rule)", "app", "Safety filter left at Balanced"],
  ["Data stores", "cymbal_policies (Unstructured) · cymbal_faq (FAQ)", "tools", "gs://PROJECT_ID-cymbal-energy/cymbal-energy/policies/ and …/faq/cymbal_energy_faq.csv"],
  ["System tools", "end_session · customize_response", "all agents / root", "end_session attached by default; customize_response added in M7"],
], [1300, 3900, 1500, 3380]));
add(H2("Versions"));
add(table(["Version", "Made in", "Contents"], K.VERSIONS.map(v => [v[0], v[1], v[2]]), [2300, 900, 6880]));

// ------------------------------------------------------------------ 5b. what's new
add(H1("What changed since the decks were written"));
add(P("Checked against the CX Agent Studio release notes and docs on September 27, 2026 (release notes last updated September 24). The decks are dated April–May 2026."));
add(table(["Date", "Change", "Where it touches the course and this demo"], [
  ["Sep 24", "Supervisor agents: Audio Quality Supervisor and Missed Tool Call Supervisor, as a new guardrail type (Blocking or Non-Blocking; outcomes Say exactly / Handoff / Generate)", "M2 guardrails (slides 84–90) list four types; there are now five. Optional step in block 10: a Missed Tool Call Supervisor, which fits our rule that restoration times must come from a tool."],
  ["Sep 24", "composite-v1 voice model (GA): listener, thinking and speaker models in one, tuned for strict instruction following and tool execution", "M3 audio slides 26–29 show three generations; composite-v1 is a fourth option and is a cascade, not audio-to-audio. Block 13 still demos gemini-3.1-flash-live (the slide's native audio); block 24 uses composite-v1 for the disclaimer because it follows customize_response instructions strictly."],
  ["Sep 24", "Agent as a tool is GA (added Apr 17)", "M2 slide 116 links \"sub-agents versus agents as tools\". Talking point for block 4: a sub-agent takes over the conversation; an agent-as-tool does a job and hands back the result."],
  ["Sep 24", "Agent-to-agent (A2A) protocol tools", "M2 tools slides 73–81 list seven custom tool types; A2A is new. Mention on slide 73."],
  ["Sep 24", "WhatsApp, Instagram and SecureCo deployment options", "M6 slides 11–16 show web widget, Twilio/telephony, API. Point at the longer channel list in block 21."],
  ["Apr 17", "gemini-3.1-flash-live replaced gemini-3-flash-native-audio", "If a lab or slide says native-audio, it's this model now."],
  ["Apr 13", "Static and dynamic variables ({{name}} vs {name})", "M2 variables slides 28–30 predate it; our instructions use dynamic {name}."],
  ["Apr 20", "Fallback behavior for error handling in app settings", "M7 slide 24 (error handling): show Settings ▸ Basic ▸ Behavior ▸ Fallback behavior."],
  ["Jun 18", "Gemini CLI stopped serving free and Google AI Pro/Ultra users; Google moved it to Antigravity CLI (agy). Extensions become plugins (agy plugin import gemini); MCP config moves to ~/.gemini/config/mcp_config.json with serverUrl; workspace skills live in .agents/skills", "M1 slide 28 and M3 slides 19–24 show Gemini CLI. Block 12 uses Antigravity CLI against the same CX Agent Studio MCP server (checked Sep 27: endpoint, scope and tool names unchanged; there is no list_variables tool)."],
  ["—", "Workflows agents: still not released (no docs, no API type, no release note)", "M2 slides 57–66 say \"Skip or include based on release of Workflows\": skip them."],
], [900, 3900, 5280]));

// ------------------------------------------------------------------ 6. confirm
add(H1("6. Confirm in tonight's dry run"));
add(P("CX Agent Studio docs changed as recently as September 24. These click paths and behaviors come from the docs, but I could not see the live console, so check them once and correct the teleprompter by hand if a label differs:"));
[
  "Start with AI: which file types the Upload accepts (PDF and TXT are in the pack; up to 5 files, 8 MB total), and the name of the button that applies the preview to the app.",
  "Whether pasted {@AGENT: …} / {@TOOL: …} text becomes a live reference, or has to be re-inserted with the @ menu.",
  "The Restructure instructions button label (the quickstart calls it Structure).",
  "Callback (confirmed: agent title bar ▸ Add callback): the After tool type, tool.name == \"check_outage\" inside the callback, callback_context.set_variable, and that print() lines show in the trace.",
  "Python tools: set_variable/get_variable as globals (documented), and module-level constants (ACCOUNTS, BILLS) outside the function.",
  "Voice: the Global model list shows gemini-3.1-flash-live and composite-v1, and Voice / Ambient sounds / interruptions live under Settings ▸ Basic ▸ Behavior.",
  "Data store tool: the Cloud Storage option names (Unstructured data / FAQ, One time sync), and whether the FAQ CSV imports cleanly.",
  "Evaluations: persona selection at run time, the Find issues with AI checkbox (needs 3+ runs), and how scenario expectations are entered.",
  "Web widget: which snippet the console generates (<chat-messenger> in the current docs, <ces-messenger> on the slide), whether the Cloud Shell Web Preview page works with public access on and origin check off.",
  "api_demo.sh: runSession on /v1/ with the widget's deployment; your user needs Owner or roles/ces.client.",
  "Antigravity CLI: the CX Agent Studio server shows Connected in /mcp; MCP calls prompt for approval; the optional skills appear as / commands when agy starts in ~/cx-agent-studio-skills (hooks from cxas init are registered for Claude Code and Gemini CLI only, not Antigravity).",
  "Data stores built by API (setup.sh) live in the us multi-region, next to the app (the AI Applications console lists global by default: switch the location to us). Sep 29 dry run: cymbal-policies indexed 3 documents; the first cymbal-faq import failed on every row (\"Custom Document Id (_id) was not found\") and is fixed with autoGenerateIds; rerun setup.sh to retry it. After catch_up.sh 4, cymbal_policies and cymbal_faq appear in Tools pointing at the indexed stores, and cymbal_faq answers verbatim like a UI-made FAQ store (created as NO_CONTENT + CSV import). If the FAQ one misbehaves, delete that tool and create it in the UI from the same CSV.",
  "Redaction: whether the template fields appear under Settings ▸ Advanced ▸ Logging, and which location (us or global) the templates must be in. The script creates both.",
  "SCRAPI: scrapi_demo.py was rewritten against the installed cxas-scrapi 1.9.1 API (Agents and Tools take app_name, not project/location); pinned in requirements.txt. Listing apps in location us confirmed working on Sep 27.",
].forEach(t => add(bullet(t)));

// ------------------------------------------------------------------ appendix
add(H1("Appendix — files in the pack"));
add(table(["Path (repo root)", "Used in", "What it is"], [
  ["setup.sh", "Setup", "Everything that isn't a lesson, safe to rerun: APIs, bucket, SCRAPI, both data stores, DLP templates, Antigravity MCP + skills"],
  ["catch_up.sh · stages/", "Between modules", "catch_up.sh N loads the end of module N−1 (stage folders m1-end … m7-end, loader, helpers)"],
  ["setup/cloudshell_setup.sh", "Setup", "APIs + bucket (called by setup.sh)"],
  ["01-start-with-ai/Cymbal Energy - Customer Care Requirements.pdf", "Block 1", "2-page requirements doc with the tool catalog (what Start with AI builds from)"],
  ["01-start-with-ai/Cymbal Energy - Sample Call Transcripts.txt", "Block 1", "Three short calls: outage, payment arrangement, gas odor"],
  ["01-start-with-ai/start-with-ai-goal.txt", "Block 1", "The goal sentence"],
  ["02-build/instructions/*.txt", "Blocks 4, 5, 9", "root_agent, outage_agent_prose (for Restructure), outage_agent (final), billing_agent (with the planted 12), global_instruction"],
  ["02-build/variables.txt · guardrails.txt", "Blocks 6, 10", "What to enter in the Variables and Guardrails panels (incl. the optional supervisor agent)"],
  ["02-build/callbacks/outage_state_after_tool.py", "Block 7", "After-tool callback: outage facts and storm-credit flag into variables"],
  ["02-build/tools/*.py", "Block 8", "Five Python tools with mock data and the arrangement rules in code"],
  ["03-programmatic/*", "Blocks 11–13", "scrapi_demo.py, requirements.txt, scrapi_commands.sh, antigravity_setup.sh, antigravity_prompts.txt, voice_settings.txt"],
  ["04-knowledge/policies/*.pdf · faq/*.csv · metadata/*.jsonl", "Blocks 14–17", "Data store content (also in the bucket)"],
  ["04-knowledge/root_agent_ADD_knowledge.txt · specialists_ADD_policies.txt", "Block 16", "Knowledge subtask for the root; the policy step for Outage and Billing agents (tools scoped by journey)"],
  ["05-evaluate/test_cases.txt · billing_agent_FIXED.txt", "Blocks 18–20", "Goldens, persona, scenarios; the fix"],
  ["06-deploy/cymbal-energy-outage-center.html", "Block 21", "Mock outage page with the widget paste markers"],
  ["06-deploy/api_demo.sh · global_instruction_ADD_escalation.txt · conversation_profile_OPTIONAL.json", "Blocks 22–23", "runSession script; escalation lines; Agent Assist profile body"],
  ["07-launch/root_agent_ADD_voice_disclaimer.txt · dlp_templates.sh", "Blocks 24–25", "Voice-only block; DLP template creation"],
  ["cymbal-energy-demo-pack.zip", "Setup", "The data folder zipped for the Cloud Shell upload (if you don't clone the repo)"],
  ["docs/TELEPROMPTER.md · docs/*.docx", "Everywhere", "The teleprompter as Markdown (renders on GitHub, copy buttons on every command) and as Word; this planning guide"],
  ["src/", "—", "build.sh rebuilds everything: make_docs.py (PDFs, CSV, JSONL), make_stages.py (stages), content.js + teleprompter.js + teleprompter_md.js + guide.js (these documents)"],
], [4300, 1300, 4480]));
add(P([run("Everything about Cymbal Energy is fictional. Phone numbers use the 555-01xx range and web addresses use cymbalenergy.example.", { color: C.gray, size: 20 })], { before: 120 }));

const document = new Document({
  creator: "Patrick Haggerty / Claude", title: "Planning Guide — Build Agents with CX Agent Studio (Cymbal Energy)",
  styles: { default: { document: { run: { font: H.FONT, size: 22 } } } },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", style: { paragraph: { indent: { left: 460, hanging: 260 } } } }] }] },
  sections: [{ properties: { page: { size: { width: PAGE_W, height: 15840 }, margin: { top: 1000, bottom: 1000, left: MARGIN, right: MARGIN } } }, children: doc }],
});
save(document, process.argv[2]);
