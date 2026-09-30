// Teleprompter: one block per page, slide number first, nothing but what to do and type.
const K = require("./content");
const H = require("./helpers");
const { C, run, P, stepBox, resetBox, table, slideLabel, save, Document, Paragraph, PageBreak } = H;
const PAGE_W = 12240, MARGIN = 900, W = PAGE_W - 2 * MARGIN;

const doc = [];
const add = (...x) => doc.push(...x);
const versionMade = (b) => { const v = b.steps.find(s => s.tag === "VERSION"); return v ? v.text.split("▸").pop().trim() : ""; };

add(P([run("TELEPROMPTER · Build Agents with CX Agent Studio · Cymbal Energy Care", { bold: true, size: 34, color: C.blue })], { after: 40 }));
add(P([run("One agent that grows through both days. One block per page. The slide number is the first thing on each page (PDF page of the delivery deck; the printed footer number follows when it differs).", { size: 20, color: C.gray })], { after: 40 }));
add(P([
  run("Key:  ", { size: 20, color: C.gray }), run("SLIDE", { bold: true, size: 20, color: C.orange }), run(" stop here and demo  ·  ", { size: 20, color: C.gray }),
  run("RESET", { bold: true, size: 20, color: C.purple }), run(" start state  ·  ", { size: 20, color: C.gray }),
  run("DO", { bold: true, size: 20, color: C.purple }), run(" clicks  ·  ", { size: 20, color: C.gray }),
  run("TYPE", { bold: true, size: 20, color: C.orange }), run(" verbatim  ·  ", { size: 20, color: C.gray }),
  run("PASTE / SHELL", { bold: true, size: 20, color: C.teal }), run(" files and commands  ·  ", { size: 20, color: C.gray }),
  run("SAVE VERSION", { bold: true, size: 20, color: C.green }), run("  ·  grey → what a good result looks like. Files are in the repo (cloned to ~/cx-agent-studio in Cloud Shell).", { size: 20, color: C.gray }),
], { after: 80 }));

[1, 2].forEach(day => {
  add(P([run("DAY " + day, { bold: true, size: 26, color: C.orange })], { before: 120, after: 40 }));
  add(table(["#", "Slide", "Min", "Block", "Version"], K.blocks.filter(b => b.day === day).map(b => [
    String(b.n), b.module + " " + b.slides.split(/[ ,]/)[0], String(b.mins), b.title + (b.optional ? "  (optional)" : ""), versionMade(b)]),
    [500, 1500, 600, 5540, 2300], { size: 19 }));
});

add(new Paragraph({ children: [new PageBreak()] }));
add(P([run("CATCH-UP BETWEEN MODULES", { bold: true, size: 26, color: C.teal })], { before: 0, after: 20 }));
add(P([run("M1 is live. At each module break, one Cloud Shell command loads the end of the previous module over \"Cymbal Energy Care\" and saves its version, so every module starts from the state this script expects. Works in a fresh Cloud Shell: it enables the APIs and installs SCRAPI itself. The only prerequisite is the pack unzipped in ~/cx-agent-studio.", { size: 20, color: C.gray })], { after: 60 }));
add(table(["Before", "Cloud Shell", "Loads"], K.CATCH_UP.map(c => [c.module === "done" ? "Finished app" : c.module,
  "bash ~/cx-agent-studio/catch_up.sh " + (c.module === "done" ? "done" : c.module.slice(1)), c.version]), [1300, 5040, 3700], { size: 19 }));

const morning = K.MORNING;

K.blocks.forEach((b, i) => {
  if (i === 0 || b.day !== K.blocks[i - 1].day) {
    add(new Paragraph({ children: [new PageBreak()] }));
    add(P([run("BEFORE DAY " + b.day, { bold: true, size: 40, color: C.orange })], { before: 0, after: 80 }));
    add(resetBox(morning[b.day], W));
  }
  if (i > 0 && b.module !== K.blocks[i - 1].module && b.day === K.blocks[i - 1].day) {  // day 2 morning list covers M4
    const c = K.CATCH_UP.find(x => x.module === b.module);
    add(new Paragraph({ children: [new PageBreak()] }));
    add(P([run("BEFORE " + b.module + " · CATCH-UP (at the break)", { bold: true, size: 40, color: C.teal })], { before: 0, after: 80 }));
    add(stepBox({ tag: "SHELL", label: "CLOUD SHELL · 1–2 minutes · skip it if the live build is on track", text: "bash ~/cx-agent-studio/catch_up.sh " + b.module.slice(1),
      expect: "Loads " + c.version + ". " + c.has }, W, 24));
    add(P("", { before: 0, after: 40 }));
    add(stepBox({ tag: "DO", text: "Console: refresh the page ▸ Preview agent ▸ Start new conversation" }, W, 22));
    add(P("", { before: 0, after: 40 }));
    add(P([run("NOTE  ", { bold: true, color: C.teal, size: 18 }), run("It replaces everything in the app with that stage (version history stays). Loaded agents are named cymbal_care, outage_agent and billing_agent: the importer needs snake_case names, so read \"Outage Agent\" in the script as outage_agent. If it stops with an error, the last lines say where; copy the whole output.", { size: 18, color: C.gray })]));
  }
  add(new Paragraph({ children: [new PageBreak()] }));
  const head = [run(slideLabel(b), { bold: true, size: 48, color: C.orange })];
  if (b.footer) head.push(run("   (footer " + b.footer + ")", { size: 24, color: C.gray }));
  add(P(head, { before: 0, after: 0 }));
  add(P([run("stop on " + b.stop, { size: 21, color: C.orange })], { before: 0, after: 60 }));
  const t = [run(b.n + ". " + b.title, { bold: true, size: 30, color: C.blue }), run("   ~" + b.mins + " min · Stage " + b.stage, { size: 21, color: C.gray })];
  if (b.optional) t.push(run("   OPTIONAL", { bold: true, size: 21, color: C.gray }));
  add(P(t, { before: 0, after: 80 }));
  add(resetBox(b.reset, W));
  add(P("", { before: 0, after: 40 }));
  if (b.files.length) {
    add(P([run("FILES", { bold: true, size: 18, color: C.purple })], { before: 0, after: 10 }));
    b.files.forEach(f => add(P([run(f, { size: 19, color: C.purple })], { before: 0, after: 0 })));
    add(P("", { before: 0, after: 60 }));
  }
  b.steps.forEach(s => { add(stepBox(s, W, 22)); add(P("", { before: 0, after: 20 })); });
  if (b.gotcha) add(P([run("IF IT GOES WRONG  ", { bold: true, color: C.red, size: 18 }), run(b.gotcha, { size: 18, color: C.gray })], { before: 40, after: 0 }));
});

const document = new Document({
  creator: "Patrick Haggerty / Claude", title: "Teleprompter — Build Agents with CX Agent Studio (Cymbal Energy)",
  styles: { default: { document: { run: { font: H.FONT, size: 22 } } } },
  sections: [{ properties: { page: { size: { width: PAGE_W, height: 15840 }, margin: { top: 800, bottom: 800, left: MARGIN, right: MARGIN } } }, children: doc }],
});
save(document, process.argv[2]);
