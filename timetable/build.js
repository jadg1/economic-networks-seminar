const pptxgen = require("pptxgenjs");
// Optional: a helper that writes THEME's colours into the .pptx theme.
// Without it the timetable still builds; only the theme colour slots stay default.
let applyTheme = async () => {};
try { ({ applyTheme } = require("./apply_theme.js")); } catch (e) { /* optional */ }

const OUT = "seminar_timetable.pptx";
const THEME = {
  name: "Black and White", headFontFace: "Calibri", bodyFontFace: "Calibri",
  colors: { dk1: "000000", lt1: "FFFFFF", dk2: "000000", lt2: "FFFFFF", accent1: "000000", accent2: "404040",
            accent3: "808080", accent4: "000000", accent5: "404040", accent6: "808080", hlink: "000000", folHlink: "404040" },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.title = "Economic Networks Fundamentals: Nodes, Influence, and Applications in Machine Learning";
pres.author = "Javier De Golferichs";
pres.theme = { headFontFace: "Calibri", bodyFontFace: "Calibri" };

const PARTS = [
  {
    time: "15:45–16:50", num: "Part 1", name: "Nodes: Network Structure and Representation",
    subs: ["1.1  Welcome and Overview", "1.2  Let's Play a Game: The Cops and Robbers Example", "1.3  Introduction to Network Notation",
           "1.4  Origins of Graph Theory: Euler and Königsberg", "1.5  Reaching the Dean: Introduction to Shortest Paths",
           "1.6  Centrality Measures", "1.7  Types of Networks"],
    outcomes: ["Describe any network using nodes, links and an adjacency matrix",
               "Find the cheapest route between two nodes with Dijkstra's algorithm",
               "Identify the most influential node using centrality measures"],
  },
  { brk: "16:50–17:00" },
  {
    time: "17:00–18:10", num: "Part 2", name: "Influence: Diffusion and Contagion in Networks",
    subs: ["2.1  Hubs and Scale-Free Networks: Barabási–Albert", "2.2  Dynamic Networks and SIR Contagion", "2.3  Information Diffusion and Spectral Graphs: Margin Call",
           "2.4  Financial Contagion: 2008, Basel III and Credit Suisse", "2.5  Counterparty Risk and Trust in Interbank Markets", "2.6  Hands-on Activity: The Bank Game",
           "2.7  Simulating the Hands-on Activity in Python"],
    outcomes: ["Explain why a few hubs dominate real networks",
               "Relate compartmental (SIR) contagion models to dynamic networks in finance and economics",
               "Analyse the 2008 and 2023 banking crises as network failures, and explain how regulation responded"],
  },
  { brk: "18:10–18:25" },
  {
    time: "18:25–19:00", num: "Part 3", name: "Applications in Machine Learning and Useful Notes",
    subs: ["3.1  Predicting Influence: Rumours in a School Network", "3.2  Knowledge Graphs for Study and Literature Review",
           "3.3  Applications in Industry, Finance and Policy", "3.4  Closing Remarks: TFM and Next Steps"],
    outcomes: ["Use real network data to find who is most influential",
               "Build a knowledge graph to organise study and literature reviews",
               "Recognise network methods in industry, finance and policy",
               "Know what to expect when writing the TFM, and how to plan for it"],
  },
];

const READINGS = [
  ["Book, introductory", "Robin J. Wilson, Introduction to Graph Theory (Pearson)"],
  ["Book, diffusion", "Shakarian et al., \"The Independent Cascade and Linear Threshold Models\", ch. 4 of Diffusion in Social Networks (Springer, 2015)"],
  ["Book, machine learning", "Vladimir N. Vapnik, The Nature of Statistical Learning Theory (Springer)"],
  ["Online course, GNNs", "Alejandro Ribeiro, Graph Neural Networks, University of Pennsylvania (gnn.seas.upenn.edu)"],
];

const FS = 11;
const NONE = { type: "none" };
const RULE = { type: "solid", pt: 0.75, color: "000000" };
const HAIR = { type: "solid", pt: 0.5, color: "000000" };
const cell = (extra = {}) => ({ fontFace: "Calibri", fontSize: FS, color: "000000", valign: "top",
                                margin: [0.04, 0.08, 0.04, 0.08], ...extra });

const lines = (arr, extra = {}) => arr.map((t, i) => ({ text: t, options: { ...extra, breakLine: i < arr.length - 1 } }));

const rows = [[
  { text: "Time", options: cell({ bold: true, border: [NONE, NONE, RULE, NONE] }) },
  { text: "Part", options: cell({ bold: true, border: [NONE, NONE, RULE, NONE] }) },
  { text: "Sessions", options: cell({ bold: true, border: [NONE, NONE, RULE, NONE] }) },
  { text: "Expected learning outcomes", options: cell({ bold: true, border: [NONE, NONE, RULE, NONE] }) },
]];
PARTS.forEach((p, i) => {
  if (p.brk) {
    rows.push([
      { text: p.brk, options: cell({ italic: true, margin: [0.02, 0.08, 0.02, 0.08], border: [NONE, NONE, NONE, NONE] }) },
      { text: "Break", options: cell({ italic: true, colspan: 3, margin: [0.02, 0.08, 0.02, 0.08], border: [NONE, NONE, NONE, NONE] }) },
    ]);
    return;
  }
  const b = { border: [i === 0 ? NONE : HAIR, NONE, NONE, NONE] };
  rows.push([
    { text: p.time, options: cell({ bold: true, ...b }) },
    { text: [{ text: p.num, options: { bold: true, breakLine: true } }, { text: p.name, options: { bold: true } }],
      options: cell(b) },
    { text: lines(p.subs), options: cell(b) },
    { text: lines(p.outcomes, { bullet: { indent: 10 } }), options: cell(b) },
  ]);
});

const slide = pres.addSlide();
slide.background = { color: "FFFFFF" };
const txt = (t, o) => slide.addText(t, { fontFace: "Calibri", color: "000000", margin: 0, isTextBox: true, ...o });

txt("Universidad Autónoma de Madrid  ·  Master in Quantitative Economic Analysis", { x: 0.6, y: 0.32, w: 7.5, h: 0.28, fontSize: 12 });
txt("Delivered by Javier De Golferichs", { x: 8.2, y: 0.32, w: 4.5, h: 0.28, fontSize: 12, italic: true, align: "right" });
txt("Friday, 13 November 2026  ·  15:45–19:00", { x: 8.2, y: 0.6, w: 4.5, h: 0.28, fontSize: 12, align: "right" });
txt("Economic Networks Fundamentals:\nNodes, Influence, and Applications in Machine Learning",
    { x: 0.6, y: 0.62, w: 12.1, h: 0.75, fontSize: 22, bold: true, valign: "top", color: "1E6B3A" });

slide.addTable(rows, { x: 0.6, y: 1.5, w: 12.1, colW: [1.1, 2.35, 3.95, 4.7], autoPage: false });

txt([{ text: "Python on Google Colab: ", options: { bold: true } },
     { text: "every demo runs in the browser, so there is nothing to install. Bring a laptop and a Google account." }],
    { x: 0.6, y: 6.05, w: 12.1, h: 0.25, fontSize: FS });
txt("Suggested readings", { x: 0.6, y: 6.4, w: 12.1, h: 0.22, fontSize: FS, bold: true });
const col = (items, x) => txt(items.flatMap(([tag, ref], i) => [
  { text: `[${tag}] `, options: { bold: true } },
  { text: ref, options: { breakLine: i < items.length - 1 } },
]), { x, y: 6.64, w: 5.9, h: 0.56, fontSize: 10, valign: "top", paraSpaceAfter: 3 });
col(READINGS.slice(0, 2), 0.6);
col(READINGS.slice(2), 6.8);

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("done");
})();
