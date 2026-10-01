"""Generates the Cymbal Energy source documents for the CX Agent Studio demo pack.

Outputs (relative to the pack root):
  01-start-with-ai/Cymbal Energy - Customer Care Requirements.pdf
  01-start-with-ai/Cymbal Energy - Sample Call Transcripts.txt
  04-knowledge/policies/*.pdf           (three policy PDFs for the Cloud Storage data store)
  04-knowledge/faq/cymbal_energy_faq.csv
  04-knowledge/metadata/policies_metadata.jsonl  (show-and-tell for the JSONL slide; BUCKET placeholder)

Everything about Cymbal Energy is fictional. Run: python3 src/make_docs.py  (from the pack root)
"""
import csv, io, json, os
from reportlab import rl_config
rl_config.invariant = 1  # byte-identical PDFs on every build (no timestamps), so git only sees real changes
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)
NAVY = colors.HexColor("#1F4E79")
ss = getSampleStyleSheet()
H1 = ParagraphStyle("h1", parent=ss["Heading1"], textColor=NAVY, fontSize=17, spaceAfter=4)
SUB = ParagraphStyle("sub", parent=ss["Normal"], textColor=colors.HexColor("#555555"), fontSize=9, spaceAfter=10)
H2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=NAVY, fontSize=12.5, spaceBefore=10, spaceAfter=4)
BODY = ParagraphStyle("b", parent=ss["Normal"], fontSize=10, leading=13.5, spaceAfter=5)


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawString(0.75 * inch, 0.5 * inch, "Cymbal Energy is a fictional company. Training material for Build Agents with CX Agent Studio.")
    canvas.drawRightString(7.75 * inch, 0.5 * inch, "Page %d" % doc.page)
    canvas.restoreState()


def bullets(items):
    return ListFlowable([ListItem(Paragraph(t, BODY), leftIndent=12) for t in items], bulletType="bullet", start="•", leftIndent=14)


def tbl(rows, widths):
    t = Table(rows, colWidths=widths)
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9), ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#999999")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF3F8")]),
    ]))
    return t


def P(t): return Paragraph(t, BODY)


def cell(t): return Paragraph(t, ParagraphStyle("c", parent=BODY, fontSize=9, leading=11.5, spaceAfter=0))


def build(path, title, subtitle, story):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.8 * inch, title=title, author="Cymbal Energy (fictional)")
    doc.build([Paragraph(title, H1), Paragraph(subtitle, SUB)] + story, onFirstPage=footer, onLaterPages=footer)
    print("wrote", os.path.relpath(path, ROOT))


# ------------------------------------------------------------------ Stage 1: requirements for "Start with AI"
build(D("01-start-with-ai", "Cymbal Energy - Customer Care Requirements.pdf"),
      "Digital Customer Care Agent: Business Requirements",
      "Cymbal Energy · Customer Operations · Draft v0.9 for the CX agent pilot",
      [
          Paragraph("1. Background", H2),
          P("Cymbal Energy delivers electricity and natural gas to about 212,000 homes and businesses along the Mississippi Gulf Coast, "
            "including Pascagoula, Moss Point, Gautier and Ocean Springs. Our contact center handles about 90,000 contacts a month. "
            "During tropical storms, contact volume rises up to eight times in a single day, hold times pass 40 minutes, and most "
            "callers only want to know whether we know about their outage and when their power will be back."),
          Paragraph("2. Goal", H2),
          P("Launch a customer care agent on the web and on the phone that resolves the two highest-volume contact types, outages "
            "and billing, without a human representative, and hands everything else to a representative with context."),
          Paragraph("3. In-scope customer journeys", H2),
          tbl([["#", "Journey", "What the agent must do"],
               ["1", cell("Check outage status"), cell("Look up the outage by the ZIP code of the service address. Give status, cause, crew status and estimated restoration time exactly as the outage system returns them.")],
               ["2", cell("Report a problem"), cell("Create a trouble ticket for no power, flickering lights or partial power. A downed or sparking line is always an emergency: tell the caller to stay 35 feet away.")],
               ["3", cell("Balance and due date"), cell("Verify the customer, then give the balance, due date and last payment.")],
               ["4", cell("Payment arrangement"), cell("For customers who cannot pay in full, set up an installment plan if the billing system approves it.")],
               ["5", cell("Gas odor or leak"), cell("Read the approved gas safety script word for word and transfer immediately to emergency dispatch. No troubleshooting.")]],
              [0.35 * inch, 1.6 * inch, 5.0 * inch]),
          Paragraph("4. Business rules", H2),
          bullets([
              "Verify identity with the 6-digit account number and the service ZIP code before sharing any account information.",
              "Never estimate or round restoration times, balances or dates. Only the systems of record are allowed to state them.",
              "Never take payment card or bank details in the conversation. Payments go to cymbalenergy.example/pay or 1-800-555-0142.",
              "Customers can ask for a person at any time. The representative must receive the customer's name and reason for contact.",
              "Tone: warm, calm, plain-spoken, short. Many customers are stressed, in the dark, or worried about money.",
          ]),
          Paragraph("5. Systems the agent can call (tool catalog)", H2),
          tbl([["System", "Operation", "Input", "Returns"],
               [cell("Customer Information System"), cell("verify_customer"), cell("account number, ZIP"), cell("verified yes/no, customer name, service address")],
               [cell("Outage Management System"), cell("check_outage"), cell("ZIP code"), cell("status, cause, customers affected, crew status, estimated restoration")],
               [cell("Work Management"), cell("report_outage"), cell("ZIP code, description"), cell("ticket number, priority")],
               [cell("Billing"), cell("get_bill_summary"), cell("(verified customer)"), cell("balance, due date, days past due, last payment")],
               [cell("Billing"), cell("create_payment_arrangement"), cell("number of installments"), cell("approved yes/no, reason, monthly amount")]],
              [1.8 * inch, 1.7 * inch, 1.4 * inch, 2.05 * inch]),
          Paragraph("5a. Test data for the pilot build (use these in mock responses)", H2),
          P("Until the systems above are connected, each operation should return realistic mock data built from this test set:"),
          tbl([["Operation", "Mock behavior"],
               [cell("verify_customer"), cell("Verified only when account number <b>123456</b> and ZIP <b>39562</b> are both given: customer Patrick Haggerty, 3702 Magnolia St, Moss Point, MS 39562. Anything else: not verified, ask the customer to check the bill.")],
               [cell("check_outage"), cell("ZIP <b>39562</b>: active outage OUT-58840, tree limb on a distribution line, 310 customers affected, crew en route, estimated restoration 4:30 PM today. Any other ZIP: no known outage.")],
               [cell("report_outage"), cell("Returns a ticket such as <b>TKT-204817</b>, priority Standard (Emergency when the description mentions a downed or sparking line), and a one-sentence confirmation for the customer.")],
               [cell("get_bill_summary"), cell("Balance $238.45, due October 8, not past due, last payment $212.10 on September 8.")],
               [cell("create_payment_arrangement"), cell("Returns an arrangement ID such as PA-123456-4 and the monthly amount (balance divided by the installments).")]],
              [1.8 * inch, 5.15 * inch]),
          Paragraph("6. Out of scope for the pilot", H2),
          bullets(["Starting, stopping or transferring service (phase 2).", "Taking payments in the conversation.",
                   "Commercial and industrial accounts."]),
          Paragraph("7. Success measures", H2),
          bullets(["Containment of 60% for outage and billing contacts within 90 days.", "Customer satisfaction of 4.3 out of 5 or higher.",
                   "Zero incorrect restoration times or balances quoted by the agent.", "Every gas odor contact transferred in under 30 seconds."]),
      ])

TRANSCRIPTS = """Cymbal Energy - Sample Call Transcripts (edited, customer details changed)
Fictional company. Training material for Build Agents with CX Agent Studio.

=== Call 1: outage status (storm day) ===
REP: Thank you for calling Cymbal Energy, this is Dana. How can I help?
CUSTOMER: My power's been out since the storm came through. Do y'all even know about it?
REP: I'm sorry, let me check. What's the ZIP code where you have service?
CUSTOMER: 39567.
REP: Yes, we have an active outage in that area. A main feeder line was damaged, a crew is on site, and the estimated restoration is 11 tonight.
CUSTOMER: Tonight? It's been three days.
REP: I understand, it's been a long one. That time comes straight from the crew on site. Can I help with anything else?
CUSTOMER: No, that's it.

=== Call 2: payment arrangement ===
REP: Cymbal Energy, this is Luis.
CUSTOMER: My bill is way past due and I can't pay it all right now.
REP: I can look at options. Can I have your account number and the ZIP code at the service address?
CUSTOMER: 100871, and 39564.
REP: Thank you, Mr. Bell. Your balance is $412.37 and it was due September 9th. I can set up a payment arrangement over a few months if you're eligible. How many months would help?
CUSTOMER: As many as I can get.
REP: The most I can do is six months. That's $68.73 a month added to your next bills, and your current charges still need to be paid each month.
CUSTOMER: OK, let's do that.

=== Call 3: gas odor ===
REP: Cymbal Energy, this is Priya.
CUSTOMER: I think I smell gas in my kitchen. It smells like rotten eggs.
REP: Please leave the house right now and take everyone with you. Don't use light switches or your phone inside. Once you're outside and away from the house, call 911 and our gas emergency line at 1-800-555-0199. I'm transferring you to emergency dispatch now.
"""
with open(D("01-start-with-ai", "Cymbal Energy - Sample Call Transcripts.txt"), "w") as f:
    f.write(TRANSCRIPTS)
print("wrote 01-start-with-ai/Cymbal Energy - Sample Call Transcripts.txt")

# ------------------------------------------------------------------ Stage 4: policy PDFs
build(D("04-knowledge", "policies", "OP-110-Storm-Restoration-and-Outage-Credit-Policy.pdf"),
      "Storm Restoration and Outage Credit Policy",
      "Policy OP-110 · Cymbal Energy Customer Operations · Effective June 1, 2026",
      [
          Paragraph("1. Purpose", H2),
          P("This policy explains how Cymbal Energy restores power after outages, how estimated restoration times are set, and which credits "
            "residential customers can receive after a long outage during a major storm."),
          Paragraph("2. Restoration priorities", H2),
          P("After a major storm, crews restore service in this order:"),
          bullets(["Public safety hazards, including downed and energized lines.",
                   "Critical facilities: hospitals, 911 centers, water and wastewater plants, and emergency shelters.",
                   "Transmission lines and substations, which restore the largest number of customers at once.",
                   "Main distribution feeders, then neighborhood lines, then individual service lines."]),
          P("Customers on the Medical Priority Registry receive outage alerts and welfare checks, but restoration is not guaranteed to be faster "
            "during a Major Storm Event. Customers who rely on powered medical equipment should keep a backup power plan."),
          Paragraph("3. Estimated restoration times", H2),
          P("Estimated restoration times come only from the Outage Management System and are updated as crews assess damage. "
            "Representatives and digital agents must quote them exactly and must not estimate their own."),
          Paragraph("4. Major Storm Events", H2),
          P("Cymbal Energy declares a Major Storm Event (MSE) when more than 10% of customers are out of service at the same time, or when the "
            "National Weather Service issues a tropical storm or hurricane warning for our service area and outages follow. Each event receives "
            "an MSE number, for example MSE-2026-04."),
          Paragraph("5. Storm Hardship Credit", H2),
          P("A residential customer whose service is out for <b>more than 72 consecutive hours</b> during a declared Major Storm Event may receive a "
            "<b>one-time $25 Storm Hardship Credit</b> on their next bill."),
          bullets(["The credit is not automatic. The customer must request it within <b>30 days</b> after service is restored, at "
                   "cymbalenergy.example/storm-credit or by calling 1-800-555-0142.",
                   "One credit per account per Major Storm Event.",
                   "Outages that are not part of a declared Major Storm Event do not qualify.",
                   "Commercial accounts are not eligible."]),
          Paragraph("6. Food, medication and property losses", H2),
          P("Cymbal Energy <b>does not reimburse food, medication or other spoilage</b> caused by weather-related outages, including Major Storm Events. "
            "Customers may be covered by their homeowner's or renter's insurance."),
          P("When an outage is caused by a failure of Cymbal Energy equipment on a clear-weather day, a customer may file a claim with the Claims "
            "Department within 60 days. Claims for food spoilage are limited to $300 per household and require photos or receipts."),
          Paragraph("7. Reconnection fees during storms", H2),
          P("Reconnection fees are waived for any account restored during a declared Major Storm Event."),
      ])

build(D("04-knowledge", "policies", "BP-210-Payment-Arrangement-and-Disconnection-Policy.pdf"),
      "Payment Arrangement and Disconnection Policy",
      "Policy BP-210 · Cymbal Energy Billing Operations · Effective January 1, 2026",
      [
          Paragraph("1. Payment arrangements", H2),
          P("A payment arrangement spreads a past-due or current balance over equal monthly installments that are added to future bills."),
          bullets(["Eligibility: a balance of at least <b>$100.00</b>, and <b>no payment arrangement on the account in the previous 12 months</b>.",
                   "Length: <b>2 to 6 monthly installments</b>. Arrangements longer than 6 months require a Billing supervisor and are not available through self-service or the digital agent.",
                   "Current charges must still be paid in full by their due date each month.",
                   "Missing an installment cancels the arrangement, and the remaining balance becomes due immediately.",
                   "While an arrangement is kept current (every installment and current charge paid on time), the arranged balance is not past due, and service will not be disconnected for it.",
                   "Eligibility is decided by the billing system. Representatives and digital agents must not promise approval."]),
          Paragraph("2. Budget Billing", H2),
          P("Budget Billing averages the last 12 months of usage into a level monthly amount, reviewed every six months. Accounts must have no "
            "past-due balance to enroll."),
          Paragraph("3. Disconnection for nonpayment", H2),
          P("Before disconnection, Cymbal Energy mails a written notice at least 10 days in advance and makes a courtesy call or text 48 hours in advance. "
            "Cymbal Energy never asks for payment by gift card, prepaid card or cryptocurrency, and never threatens same-day disconnection by phone."),
          Paragraph("4. When service will not be disconnected", H2),
          bullets(["On Fridays, weekends, holidays, or the day before a holiday.",
                   "When the National Weather Service forecasts a heat index of 98°F or higher, or a temperature of 32°F or lower, in the next 24 hours.",
                   "For <b>30 days</b> after Cymbal Energy receives a <b>medical certificate</b> from a licensed physician stating that disconnection would "
                   "endanger the health of someone in the home. The certificate can be renewed once for another 30 days.",
                   "During a declared Major Storm Event in the customer's area."]),
          Paragraph("5. Reconnection", H2),
          P("After payment, service is normally reconnected within 24 hours. A $35 reconnection fee applies, except during a declared Major Storm Event."),
          Paragraph("6. Assistance programs", H2),
          P("Customers who are struggling to pay can be referred to the Low Income Home Energy Assistance Program (LIHEAP) through their county "
            "community action agency, and to the Cymbal Cares fund, which offers up to $300 once every 12 months."),
      ])

build(D("04-knowledge", "policies", "GS-001-Natural-Gas-Safety-Guide.pdf"),
      "Natural Gas Safety Guide",
      "Guide GS-001 · Cymbal Energy Gas Operations · For customers",
      [
          Paragraph("Know the signs of a gas leak", H2),
          bullets(["A smell like rotten eggs or sulfur. Natural gas has no smell, so we add one called mercaptan.",
                   "A hissing, whistling or roaring sound near a gas line or appliance.",
                   "Dead or dying plants over a gas line, bubbles in standing water, or dirt blowing into the air."]),
          Paragraph("If you suspect a leak", H2),
          bullets(["Leave the building immediately and take everyone with you. Leave doors open behind you.",
                   "Do not use light switches, phones, garage door openers, or anything that could make a spark inside.",
                   "Do not try to find the leak or shut off appliances.",
                   "From a safe distance, call 911 and the Cymbal Energy gas emergency line at <b>1-800-555-0199</b>. It is answered 24 hours a day.",
                   "There is never a charge for a leak investigation."]),
          Paragraph("Carbon monoxide", H2),
          P("Carbon monoxide is odorless. Install CO alarms on every level of the home and near sleeping areas. If an alarm sounds or people feel "
            "dizzy or nauseated, get everyone outside and call 911."),
          Paragraph("Portable generators after a storm", H2),
          bullets(["Never run a generator indoors, in a garage, or on a porch. Keep it at least 20 feet from the house with the exhaust pointed away.",
                   "Never plug a generator into a wall outlet. Backfeeding can kill line workers restoring your power."]),
          Paragraph("Before you dig", H2),
          P("Call 811 at least three working days before any digging project so buried gas and electric lines can be marked at no cost."),
      ])

# ------------------------------------------------------------------ FAQ CSV (strict format: header row, no space after commas, no blank lines)
FAQ = [
    ("What are your customer service hours?", "Our customer service representatives are available Monday through Friday from 7 AM to 7 PM Central. Outage reporting and the gas emergency line (1-800-555-0199) are available 24 hours a day.", "Customer service hours", "https://cymbalenergy.example/contact"),
    ("How do I report a streetlight that is out?", "Report a streetlight at cymbalenergy.example/streetlights with the pole number (on a metal tag about eye level) or the nearest address. Repairs are usually completed within 5 business days.", "Streetlight repair", "https://cymbalenergy.example/streetlights"),
    ("Where can I pay my bill in person?", "You can pay in person at any Cymbal Energy payment location, including our Pascagoula and Ocean Springs offices and participating grocery and pharmacy stores. A $1.50 convenience fee may apply at retail locations.", "Payment locations", "https://cymbalenergy.example/pay/locations"),
    ("How do I start service at a new address?", "Start service online at cymbalenergy.example/start at least 3 business days before your move-in date. You will need a photo ID and the service address.", "Start service", "https://cymbalenergy.example/start"),
    ("How do I stop service when I move out?", "Stop service online at cymbalenergy.example/stop or call 1-800-555-0142 at least 3 business days before you move. Your final bill is mailed to your forwarding address.", "Stop service", "https://cymbalenergy.example/stop"),
    ("Is there a deposit to start service?", "A deposit of up to $150 may be required for new customers without a recent payment history with Cymbal Energy. It is refunded after 12 months of on-time payments.", "Deposits", "https://cymbalenergy.example/start"),
    ("What payment methods do you accept?", "We accept bank draft, debit and credit cards through our secure payment page, checks by mail, and cash at payment locations. We never accept gift cards, prepaid cards or cryptocurrency.", "Payment methods", "https://cymbalenergy.example/pay"),
    ("How do I sign up for outage text alerts?", "Text REG to 55501 from the mobile number on your account, or turn on alerts at cymbalenergy.example/alerts. You will get updates when an outage is detected, when a crew is assigned and when power is restored.", "Outage alerts", "https://cymbalenergy.example/alerts"),
    ("What is Budget Billing?", "Budget Billing averages your last 12 months of usage into a level monthly amount so your bill is predictable. The amount is reviewed every six months. Your account must be current to enroll.", "Budget Billing", "https://cymbalenergy.example/budget-billing"),
    ("What should I do if a power line is down?", "Stay at least 35 feet away from any downed or sagging line, keep others away, and report it right away at 1-800-555-0142. Always assume a downed line is energized.", "Downed lines", "https://cymbalenergy.example/safety"),
    ("Can I get a paper bill instead of a paperless bill?", "Yes. Change your bill delivery preference at cymbalenergy.example/account under Billing Preferences. Paperless customers receive an email when each bill is ready.", "Bill delivery", "https://cymbalenergy.example/account"),
    ("How do I read my electric meter?", "Most Cymbal Energy meters are smart meters that report usage automatically. The display cycles through several readings; the number labeled kWh is your total usage.", "Meters", "https://cymbalenergy.example/meters"),
    ("Why is my bill higher than last month?", "Bills are usually higher in summer and winter because heating and cooling use the most energy. Compare your kWh usage to the same month last year on your bill, and check whether the billing period was longer than usual.", "High bills", "https://cymbalenergy.example/high-bill"),
    ("Do you offer help paying my bill?", "Yes. Customers who are struggling can apply for LIHEAP through their county community action agency, apply to the Cymbal Cares fund, or ask about a payment arrangement.", "Bill assistance", "https://cymbalenergy.example/assistance"),
    ("How can I trim trees near power lines?", "Never trim trees near power lines yourself. Request a free safety trim at cymbalenergy.example/trees and a qualified line-clearance crew will schedule a visit.", "Tree trimming", "https://cymbalenergy.example/trees"),
    ("Where are your offices located?", "Customer offices are at 3300 Market Street in Pascagoula and 1010 Government Street in Ocean Springs, open Monday through Friday from 8 AM to 5 PM.", "Office locations", "https://cymbalenergy.example/contact"),
    ("How do I sign up for the Medical Priority Registry?", "Download the Medical Priority Registry form at cymbalenergy.example/medical, have your physician complete it, and return it by mail or email. You will receive outage alerts and welfare checks during extended outages.", "Medical Priority Registry", "https://cymbalenergy.example/medical"),
    ("Can I choose my bill due date?", "Yes. Residential customers can move their due date once every 12 months to any day between the 1st and the 28th at cymbalenergy.example/account.", "Due date", "https://cymbalenergy.example/account"),
]
buf = io.StringIO()
w = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\n")
w.writerow(["question", "answer", "title", "url"])
for row in FAQ:
    w.writerow(row)
os.makedirs(D("04-knowledge", "faq"), exist_ok=True)
with open(D("04-knowledge", "faq", "cymbal_energy_faq.csv"), "w", newline="") as f:
    f.write(buf.getvalue().rstrip("\n"))  # no trailing blank line: the FAQ importer rejects it
print("wrote 04-knowledge/faq/cymbal_energy_faq.csv")

# ------------------------------------------------------------------ JSONL metadata (slide 35 show-and-tell)
docs = [("op-110", "OP-110-Storm-Restoration-and-Outage-Credit-Policy.pdf", "Storm Restoration and Outage Credit Policy", "customer-operations"),
        ("bp-210", "BP-210-Payment-Arrangement-and-Disconnection-Policy.pdf", "Payment Arrangement and Disconnection Policy", "billing"),
        ("gs-001", "GS-001-Natural-Gas-Safety-Guide.pdf", "Natural Gas Safety Guide", "gas-safety")]
os.makedirs(D("04-knowledge", "metadata"), exist_ok=True)
with open(D("04-knowledge", "metadata", "policies_metadata.jsonl"), "w") as f:
    for i, fn, title, cat in docs:
        f.write(json.dumps({"id": i, "structData": {"title": title, "category": cat,
                                                     "url": "https://cymbalenergy.example/policies/" + i},
                            "content": {"mimeType": "application/pdf", "uri": "gs://BUCKET/cymbal-energy/policies/" + fn}}) + "\n")
print("wrote 04-knowledge/metadata/policies_metadata.jsonl")
