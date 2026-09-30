// Teleprompter as Markdown (renders on GitHub): same source as the Word teleprompter (content.js).
// Run from the repo root:  node src/teleprompter_md.js docs/TELEPROMPTER.md
const fs = require("fs");
const K = require("./content");

const LABEL = {
  DO: "DO", TYPE: "TYPE in Preview", PASTE: "PASTE file ▸ where", SHELL: "CLOUD SHELL", MAC: "LOCAL TERMINAL",
  CLI: "TYPE in Antigravity CLI", VERSION: "SAVE VERSION", OPTIONAL: "OPTIONAL",
};
const CODE = new Set(["TYPE", "SHELL", "MAC", "CLI"]);   // copy button on GitHub
const esc = (t) => t.replace(/\|/g, "\\|");
const slides = (b) => "slide" + (/[–,]/.test(b.slides) ? "s " : " ") + b.slides;
const version = (b) => { const v = b.steps.find(s => s.tag === "VERSION"); return v ? v.text.split("▸").pop().trim() : ""; };
const out = [];
const add = (...l) => out.push(...l);

add("# Teleprompter · Build Agents with CX Agent Studio · Cymbal Energy Care", "",
  "One agent that grows through both days. One section per demo block: slide first, then the start state, the files, and every click and line to type. " +
  "Code boxes have a copy button. Slide numbers are PDF page numbers of the course decks (the printed footer number follows when it differs). " +
  "Files are in this repo (cloned to `~/cx-agent-studio` in Cloud Shell). The Word version with the same content is `TELEPROMPTER - CX Agent Studio - Cymbal Energy.docx`.", "",
  "→ marks what a good result looks like.", "");

[1, 2].forEach(day => {
  add(`## Day ${day}`, "", "| # | Module · slide | Min | Block | Saves version |", "|---|---|---|---|---|");
  K.blocks.filter(b => b.day === day).forEach(b =>
    add(`| ${b.n} | ${b.module} · ${b.slides} | ${b.mins} | [${esc(b.title)}](#b${b.n})${b.optional ? " *(optional)*" : ""} | ${version(b)} |`));
  add("");
});

add("## Catch-up between modules", "",
  "M1 is live. At each module break, one Cloud Shell command loads the end of the previous module over \"Cymbal Energy Care\" and saves its version, " +
  "so every module starts from the state this script expects. It works in a fresh Cloud Shell; the only prerequisite is the pack at `~/cx-agent-studio`.", "",
  "| Before | Cloud Shell | Loads |", "|---|---|---|");
K.CATCH_UP.forEach(c => add(`| ${c.module === "done" ? "Finished app" : c.module} | \`bash ~/cx-agent-studio/catch_up.sh ${c.module === "done" ? "done" : c.module.slice(1)}\` | ${c.version} |`));
add("");

const stepMd = (s) => {
  add(`**${s.label || LABEL[s.tag]}**`, "");
  if (CODE.has(s.tag)) add("```text", s.text, "```");
  else add(s.text.split("\n").map(l => l.replace(/^ +/, m => "&nbsp;".repeat(m.length))).join("  \n"));
  if (s.expect) add("", `→ *${s.expect}*`);
  add("");
};

K.blocks.forEach((b, i) => {
  const prev = K.blocks[i - 1];
  if (i === 0 || b.day !== prev.day) {
    add("---", "", `## Before day ${b.day}`, "");
    K.MORNING[b.day].forEach(l => add(`- [ ] ${l}`));
    add("");
  }
  if (i > 0 && b.module !== prev.module && b.day === prev.day) {
    const c = K.CATCH_UP.find(x => x.module === b.module);
    add("---", "", `## Before ${b.module} · catch-up (at the break)`, "",
      "**CLOUD SHELL · 1–2 minutes · skip it if the live build is on track**", "",
      "```text", `bash ~/cx-agent-studio/catch_up.sh ${b.module.slice(1)}`, "```", "", `→ *Loads ${c.version}. ${c.has}*`, "",
      "Then: console ▸ refresh the page ▸ Preview agent ▸ Start new conversation.", "",
      "It replaces everything in the app with that stage (version history stays). Agent names match the live build " +
      "(cymbal_care, outage_agent, billing_agent).", "");
  }
  add("---", "", `<a name="b${b.n}"></a>`, "",
    `## ${b.n} · ${b.module} · ${slides(b)}${b.footer ? ` (footer ${b.footer})` : ""}`, "",
    `### ${b.title}`, "",
    `Stop on ${b.stop} · ~${b.mins} min · Stage ${b.stage}${b.optional ? " · **optional**" : ""}`, "",
    "**RESET TO START STATE**", "");
  b.reset.forEach(l => add(`- ${l}`));
  add("");
  if (b.files.length) { add("**FILES**", ""); b.files.forEach(f => add(`- \`${f}\``)); add(""); }
  b.steps.forEach(stepMd);
  if (b.gotcha) add(`> **If it goes wrong:** ${b.gotcha}`, "");
});

add("---", "", "*Cymbal Energy is fictional. Generated from `src/content.js` by `src/teleprompter_md.js`: edit the source, not this file.*", "");
fs.writeFileSync(process.argv[2] || "TELEPROMPTER.md", out.join("\n"));
console.log("wrote", process.argv[2] || "TELEPROMPTER.md", out.length, "lines");
