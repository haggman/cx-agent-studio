// Shared rendering helpers. Palette: mid-tone accents that read on black and on white (Word in dark mode).
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, BorderStyle, HeadingLevel, PageBreak, LevelFormat } = require("docx");
const C = { blue: "3D8BFF", orange: "F28C28", green: "2ECC71", red: "FF5C5C", purple: "B07CFF", gray: "9AA4B2", teal: "2BB3B1" };
const FONT = "Calibri", MONO = "Consolas";
const border = (color, size = 8) => ({ style: BorderStyle.SINGLE, size, color });

const run = (text, o = {}) => new TextRun({ text, font: o.mono ? MONO : FONT, size: o.size || 22, bold: !!o.bold, italics: !!o.italic, color: o.color });
const P = (children, o = {}) => new Paragraph({ children: typeof children === "string" ? [run(children, o)] : children,
  spacing: { before: o.before ?? 40, after: o.after ?? 80, line: 264 }, keepNext: o.keepNext, pageBreakBefore: o.pageBreak, heading: o.heading });

function box(paras, color, width, left = 36) {
  return new Table({ width: { size: width, type: WidthType.DXA }, columnWidths: [width],
    rows: [new TableRow({ cantSplit: true, children: [new TableCell({ width: { size: width, type: WidthType.DXA },
      borders: { top: border(color, 12), bottom: border(color, 12), left: border(color, left), right: border(color, 12) },
      margins: { top: 80, bottom: 80, left: 160, right: 160 }, children: paras })] })] });
}

const TAGS = {
  DO:      { label: "DO", color: C.purple, mono: false },
  TYPE:    { label: "TYPE in Preview", color: C.orange, mono: true },
  PASTE:   { label: "PASTE file ▸ where", color: C.teal, mono: false },
  SHELL:   { label: "CLOUD SHELL", color: C.teal, mono: true },
  MAC:     { label: "LOCAL TERMINAL", color: C.teal, mono: true },
  CLI:     { label: "TYPE in Antigravity CLI", color: C.orange, mono: true },
  VERSION: { label: "SAVE VERSION", color: C.green, mono: false },
  OPTIONAL:{ label: "OPTIONAL", color: C.gray, mono: false },
};

function stepBox(s, width, size = 22) {
  const t = TAGS[s.tag];
  const paras = [P([run(s.label || t.label, { bold: true, color: t.color, size: 18 })], { before: 0, after: 40 })];
  s.text.split("\n").forEach(l => paras.push(P([run(l, { mono: t.mono, size: t.mono ? size - 1 : size, bold: s.tag === "VERSION" })], { before: 0, after: 0 })));
  if (s.expect) paras.push(P([run("→ ", { color: C.green, size: 19, bold: true }), run(s.expect, { size: 19, color: C.gray })], { before: 60, after: 0 }));
  return box(paras, t.color, width, s.tag === "DO" || s.tag === "VERSION" ? 12 : 36);
}
function resetBox(lines, width) {
  const paras = [P([run("RESET TO START STATE", { bold: true, color: C.purple, size: 18 })], { before: 0, after: 40 })];
  lines.forEach(l => paras.push(P([run(l, { size: 21 })], { before: 0, after: 20 })));
  return box(paras, C.purple, width, 12);
}
function table(headers, rows, widths, o = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (t, w, hdr) => new TableCell({ width: { size: w, type: WidthType.DXA },
    borders: { top: border(C.gray, 4), bottom: border(C.gray, 4), left: border(C.gray, 4), right: border(C.gray, 4) },
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    children: (Array.isArray(t) ? t : [t]).map(x => typeof x === "string"
      ? new Paragraph({ children: [run(x, { bold: hdr, color: hdr ? C.blue : undefined, size: o.size || 19, mono: o.monoCols && o.monoCols.includes(widths.indexOf(w)) })], spacing: { before: 0, after: 0 } })
      : x) });
  return new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, widths[i], true)) }),
      ...rows.map(r => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, widths[i], false)) }))] });
}
const slideLabel = (b) => b.module + " · SLIDE" + (/[–,]/.test(b.slides) ? "S " : " ") + b.slides;
function save(doc, path) { return Packer.toBuffer(doc).then(buf => { require("fs").writeFileSync(path, buf); console.log("wrote", path, buf.length); }); }
module.exports = { C, FONT, MONO, run, P, box, stepBox, resetBox, table, slideLabel, save, border, Document, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, HeadingLevel, PageBreak, LevelFormat };
