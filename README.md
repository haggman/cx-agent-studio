# CX Agent Studio demos: Cymbal Energy Care

One customer care agent, built live and grown one capability at a time across the seven modules of Google Cloud's **Build Agents with CX Agent Studio** course. It starts as a two-minute Start with AI draft in Module 1 and ends as a multi-agent, knowledge-grounded, evaluated, deployed, launch-ready agent in Module 7.

Everything that isn't a lesson is scripted. One command sets up a project, and one command catches the agent up to the start of any module. So you can follow the whole series in your own project, pick it up at any module, or recover from a live demo that went sideways.

*Cymbal Energy is a fictional electric and gas utility on the Mississippi Gulf Coast. This is not an official Google product, and the course slide decks are not included. Slide numbers in the docs refer to the course decks, but every demo stands on its own.*

---

## Quick start (Cloud Shell)

You need a Google Cloud project where you're **Owner**. Cloud Shell always starts in your home folder (`~`), so these commands work in anyone's Cloud Shell. The clone lands in `~/cx-agent-studio`, which is where every script and doc expects it:

```bash
cd ~ && git clone https://github.com/haggman/cx-agent-studio.git
bash ~/cx-agent-studio/setup.sh          # everything that isn't a lesson; safe to rerun
```

Then open [docs/TELEPROMPTER.md](docs/TELEPROMPTER.md) and start at block 1, or jump ahead:

```bash
bash ~/cx-agent-studio/catch_up.sh 4        # the agent as it stands at the start of Module 4
bash ~/cx-agent-studio/catch_up.sh done     # the finished agent
```

After a catch-up, refresh the CX Agent Studio console (`ces.cloud.google.com`, location **us**) and start a new preview conversation.

To pick up later changes, run `git -C ~/cx-agent-studio pull`.

**No git?** Download `cymbal-energy-demo-pack.zip` from this repo. In Cloud Shell, go to ⋮ (More) ▸ Upload, then run `unzip -o ~/cymbal-energy-demo-pack.zip -d ~/cx-agent-studio && bash ~/cx-agent-studio/setup.sh`. The zip holds exactly what Cloud Shell needs (no docs or generators), in the same place. Use either the clone or the zip, not both, because git won't clone into a folder that already has files.

---

## What's in the repo

```
cx-agent-studio/                       ~/cx-agent-studio in Cloud Shell
├── README.md                          you are here
├── setup.sh                           one-time project setup, safe to rerun
├── catch_up.sh                        catch the agent up to the start of any module
├── setup/                             APIs + bucket (called by setup.sh)
├── 01-start-with-ai/                  requirements PDF + call transcripts for Start with AI
├── 02-build/                          instructions, variables, callback, Python tools, guardrails
├── 03-programmatic/                   SCRAPI demo, Antigravity CLI + MCP setup and prompts, voice settings
├── 04-knowledge/                      policy PDFs, FAQ CSV, metadata JSONL, knowledge subtask
├── 05-evaluate/                       goldens, persona, scenarios, the billing fix
├── 06-deploy/                         outage web page for the widget, runSession API script, escalation
├── 07-launch/                         voice disclaimer, DLP redaction templates
├── stages/                            the whole app as files at the end of every module + the loader
├── docs/
│   ├── TELEPROMPTER.md                every demo, click by click (renders here on GitHub)
│   ├── TELEPROMPTER - … .docx         the same teleprompter as a Word file, one block per page
│   └── PLANNING GUIDE - … .docx       the why, talk track, two-day timing, fact sheet, setup detail
├── cymbal-energy-demo-pack.zip        the Cloud Shell files zipped, for uploading without git
├── src/                               generators for the module files, the stages and the docs (maintainers only)
├── package.json · requirements-dev.txt   dependencies for rebuilding (not needed to run the demos)
└── .gitignore
```

---

## The story

Tropical Storm Delphine has just come through. A feeder is down in Pascagoula (ZIP 39567), 2,140 customers have been out for 76 hours, and a Major Storm Event is declared. The demo follows two threads through the course:

- **The freezer question.** In Module 1, a customer asks for a credit for spoiled food and the draft agent makes up an answer. In Module 2, an after-tool callback turns outage data into a `storm_credit_eligible` flag. In Module 4, the storm policy PDF supplies the real answer: no reimbursement for spoilage, but a $25 Storm Hardship Credit that has to be requested within 30 days.
- **The planted bug.** The Billing Agent's instructions promise "up to 12 monthly installments", while the Python tool enforces 2–6. Nobody mentions it until the Module 5 evaluation catches it.

## The demos

| # | Module · slide | Demo | Saves version |
|---|---|---|---|
| 1 | M1 · 13 | Create the app and let Start with AI build a first draft | |
| 2 | M1 · 26–29 | Review the AI draft and have the first conversation | `v1-start-with-ai` |
| 3 | M2 · 3–4 | Product tour on our own draft | |
| 4 | M2 · 11 | From one agent to a team: root + Outage Agent + Billing Agent | |
| 5 | M2 · 19, 26–27 | Global instruction (brand voice) and Restructure instructions | |
| 6 | M2 · 28–30 | Variables: the agent's memory | |
| 7 | M2 · 40 | After-tool callback: turn a tool result into state | |
| 8 | M2 · 82 | Python tools replace the placeholders; business rules live in code | |
| 9 | M2 · 82 | Wire the tools to the specialists and have a real conversation | |
| 10 | M2 · 90 | Guardrails: prompt guard, a scam blocklist, a no-promises rule | `v2-multi-agent` |
| 11 | M3 · 15 | SCRAPI: the same agent, from Python | |
| 12 | M3 · 22–24 | Antigravity CLI + MCP: talk to the agent's design | |
| 13 | M3 · 26–29 | Native audio: call the agent and interrupt it | `v3-day1` |
| 14 | M4 · 2–3 | Cooking show: build a data store tool, then pull the finished one out of the oven | |
| 15 | M4 · 35, 39 | Show the real files behind the slides *(optional)* | |
| 16 | M4 · 41 | Attach the knowledge and ask yesterday's question again | `v4-knowledge` |
| 17 | M4 · 69, 74 | No-match and ungrounded answers *(optional)* | |
| 18 | M5 · 9–10 | Goldens from real conversations | |
| 19 | M5 · 25–27 | A frustrated persona, two scenarios, and start the run | |
| 20 | M5 · 31 | Read the failure, fix it, run again (quality hill climbing) | `v5-evaluated` |
| 21 | M6 · 12–13 | Put the agent on the Cymbal Energy outage page | |
| 22 | M6 · 17–18 | The same agent over the API | |
| 23 | M6 · 39–41 | Hand off to a human with context | `v6-escalation` |
| 24 | M7 · 19–20 | A recording disclaimer the caller can't talk over *(optional)* | |
| 25 | M7 · 29–30 | Redact card numbers, SSNs and phone numbers from the logs | `v7-launch-ready` |
| 26 | M7 · 31 | The whole journey in one list | |

The course runs over two days, with blocks 1–13 on day 1 and 14–26 on day 2. Each block in [the teleprompter](docs/TELEPROMPTER.md) lists its start state, the files it uses, every click, the exact text to type or paste, and what a good result looks like.

---

## How the scripts work

### `setup.sh`: everything that isn't a lesson

Run it once per project. It's also safe to run again at any time, because every step checks first and only creates what's missing. Each line starts with ✓ (already there) or + (created now).

| Step | What it makes |
|---|---|
| 1 | Enables `ces`, `discoveryengine` and `dlp`; creates `gs://PROJECT_ID-cymbal-energy` (US) and loads the policy PDFs, FAQ CSV and metadata |
| 2 | Installs [SCRAPI](https://github.com/GoogleCloudPlatform/cxas-scrapi) (`cxas-scrapi==1.9.1`) |
| 3 | Creates the two Module 4 data stores, `cymbal-policies` (unstructured) and `cymbal-faq` (FAQ CSV), in the `us` multi-region, and imports each one once. Indexing then runs for about 15 minutes on its own. |
| 4 | Creates the Module 7 DLP inspect and de-identify templates in `us` and `global` |
| 5 | Antigravity CLI: adds the CX Agent Studio MCP server (`https://ces.googleapis.com/mcp`) and the CXAS agent skills (skipped if `agy` isn't installed) |
| 6 | Reports whether the "Cymbal Energy Care" app exists |

The only manual setup step is signing in to Antigravity the first time you run `agy` (Module 3, optional).

### `catch_up.sh`: start any module from a known state

```bash
bash ~/cx-agent-studio/catch_up.sh <module you are about to teach, 2-7>     # or: done
```

It loads the agent as it stands at the **end of the previous module** over the app named exactly "Cymbal Energy Care" (creating the app if there isn't one), then saves that module's version.

| Before | Command | Loads | What the app has |
|---|---|---|---|
| M2 | `catch_up.sh 2` | `v1-start-with-ai` | One agent + five placeholder tools that answer from the requirements doc's test data |
| M3 | `catch_up.sh 3` | `v2-multi-agent` | Root + outage + billing agents, global instruction, 8 variables, after-tool callback, 5 Python tools, 3 guardrails |
| M4 | `catch_up.sh 4` | `v3-day1` | The same, plus the pre-built data store tools sitting in Tools, not yet attached |
| M5 | `catch_up.sh 5` | `v4-knowledge` | Data store tools attached by journey (root: policies + FAQ; outage and billing: policies), plus a knowledge subtask |
| M6 | `catch_up.sh 6` | `v5-evaluated` | Billing fixed, a persona, three scenario evaluations |
| M7 | `catch_up.sh 7` | `v6-escalation` | Escalation to a human; a web widget channel on the version |
| — | `catch_up.sh done` | `v7-launch-ready` | Voice disclaimer and log redaction: the finished agent |

**What it does, so nothing surprises you**

- It works in a brand-new Cloud Shell. It enables the APIs and installs SCRAPI itself, and from Module 4 on it runs the same bucket and data store checks as `setup.sh`.
- It pushes `stages/m<N>-end/` with `cxas push --overwrite`. That replaces every agent, tool and guardrail in the app, so anything built live is gone. Version history stays.
- It saves one version per name and stage content. Running it again skips the version, a version it saved from older stage files is replaced, and a version you saved yourself is kept.
- Loaded agents are named `cymbal_care`, `outage_agent` and `billing_agent`. The importer resolves agent references by display name, and names with spaces fail with `400 Reference not found`, so the teleprompter's "Outage Agent" is `outage_agent` after a catch-up.
- If it stops, it prints the line it stopped on.

`stages/load_stage.sh N` does the same thing, addressed by the module that just ended (`catch_up.sh M` = `load_stage.sh M-1`). `stages/build_all_stages.sh` saves every version, v1 through v7, in order. See [stages/README.md](stages/README.md).

---

## Test data

Everything is fictional. Phone numbers use 555-01xx, and web addresses use `cymbalenergy.example`.

| Account | Customer | ZIP | Bill | Payment arrangement |
|---|---|---|---|---|
| 100234 | Renee Thibodeaux | 39567 (Pascagoula) | $142.80 due Oct 6 | Eligible |
| 100871 | Marcus Bell | 39564 (Ocean Springs) | $412.37, 18 days past due | Eligible: 2–6 months; 6 = $68.73/mo |
| 100455 | Linh Nguyen | 39563 (Moss Point) | $86.10 due Oct 2 | Not eligible (under $100, and one in the last 12 months) |
| 123456 | Patrick Haggerty | 39562 (Moss Point) | $238.45 due Oct 8 | Eligible; also the Module 1 test customer |

| ZIP | Outage |
|---|---|
| 39567 | OUT-58812: Tropical Storm Delphine, 2,140 customers, 76 hours, Major Storm Event MSE-2026-04, restoration 11:00 PM tonight |
| 39562 | OUT-58840: tree limb on a line, 310 customers, 2 hours, restoration 4:30 PM today |
| other served ZIPs | No outage: offer `report_outage` (a "line down" description returns an emergency ticket) |

---

## Requirements, cost and cleanup

- **Project:** Owner on a Google Cloud project with billing. CX Agent Studio runs in the `us` location, and the data stores are in `us` too. The data store console lists `global` by default, so switch it to `us` to see them.
- **Cost:** small for a two-day class: Discovery Engine indexing and queries for 3 PDFs and 18 FAQ rows, a few DLP calls, one Cloud Storage bucket and the agent's model calls. Clean up when you're done.
- **Cleanup** (Cloud Shell):

```bash
P=$(gcloud config get-value project); T=$(gcloud auth print-access-token)
cxas delete --display-name "Cymbal Energy Care" --project-id "$P" --location us --force
for DS in cymbal-policies cymbal-faq; do
  curl -s -X DELETE -H "Authorization: Bearer $T" -H "x-goog-user-project: $P" \
    "https://us-discoveryengine.googleapis.com/v1/projects/$P/locations/us/collections/default_collection/dataStores/$DS"; done
for L in us global; do for K in inspectTemplates/cymbal-inspect deidentifyTemplates/cymbal-deidentify; do
  curl -s -X DELETE -H "Authorization: Bearer $T" -H "x-goog-user-project: $P" "https://dlp.googleapis.com/v2/projects/$P/locations/$L/$K"; done; done
gcloud storage rm -r "gs://$P-cymbal-energy"
```

---

## Lessons from real runs

These are baked into the scripts, and worth knowing if you build your own:

- **Agent names in imported apps must be snake_case** (folder = `name` = `displayName`). Display names with spaces fail with `400 Reference not found`.
- **Every guardrail needs an action.** A guardrail without one makes *every* turn fail with `Trigger action type ACTION_NOT_SET is not supported`. The console fills one in for you; the import format does not.
- **A CSV (FAQ) data store import needs `autoGenerateIds`.** Without it, every row fails with `Custom Document Id (_id) was not found`.
- **Start with AI varies from run to run.** The requirements PDF includes a test-data section so its mock tools come out usable, and `catch_up.sh 2` loads a known-good draft if yours doesn't.

## Rebuilding (maintainers)

Everything generated comes from `src/`: the module folders' PDFs and CSV (`make_docs.py`), the stage folders (`make_stages.py`), the Word and Markdown teleprompters and the planning guide (`content.js` + `teleprompter.js` / `teleprompter_md.js` / `guide.js`), and the zip. Edit the source, then:

```bash
pip install -r requirements-dev.txt && npm install
bash src/build.sh
cxas lint --app-dir stages/m7-end     # optional: SCRAPI's linter on any stage
```
