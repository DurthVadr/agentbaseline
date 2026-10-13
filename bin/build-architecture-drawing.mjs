// node bin/build-architecture-drawing.mjs
// Writes layouts/partials/sf-architecture.svg (wide) and sf-architecture-narrow.svg:
// the talk deck's one-row architecture (profile · agent in its sandbox · egress proxy ·
// what lies behind it, between two trusted controls: supply chain scanning above,
// the runtime authorization service beneath, and the tamper-evident record under
// everything), redrawn for /reference-architecture.
// The page's own drawing, not one of the paper's figures: the paper's stay in
// software-factory/figures/ and the PDF. It is drawn as they are, so the page and the
// paper read as one system, and its labels are the paper's words.
// The agent proposes, the runtime authorization service decides, and the egress proxy
// enforces. The service is drawn as a decision, not a container: trusted context and the
// profile's bounds flow into it with the agent's proposal; the scope it authorizes goes
// up to the proxy and high-impact actions out to approval. The profile configures the
// sandbox at launch through scanning, which checks the components it is built from,
// and the proxy checks every package it fetches with it.
// A box is its name and at most one short line, a wire a verb or two: the drawing names
// things, and the caption, the alt text and the paper explain them.
// The core path (agent to proxy, the proposal, trusted context into the decision, the
// authorized scope) is drawn heavier than the rest (.sfa-main).
// The boundaries' numbers are the paper's, read at build time (boundaryNumbers), as
// software-factory/figures/build-figures.py reads them for the figures.
// Colours come from classes the page styles with its own tokens (.sfa-* in
// layouts/reference-architecture.html), so the drawing follows the theme.
// Its text is never smaller than the paper's figures' beside it, at any width: they
// share the figures' slot and switch point, and the smallest text here is at least
// theirs in proportion (wide: 12.25 of 736 units, so 14.65 of 880; narrow: 12.5 of 376).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const icon = n => fs.readFileSync(`${REPO}/layouts/partials/icons/${n}.svg`, 'utf8').match(/ d="([^"]+)"/)[1];
const SEAL = icon('seal-check'), HAND = icon('hand-palm');
// Text and attribute values: escape what XML needs, and set a straight apostrophe curly.
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;')
  .replace(/'/g, '’');
const f1 = n => +(+n).toFixed(1);

// A boundary's number is its place among the "## Name: ..." sections under "# The four
// security boundaries" in the paper, so reordering the paper renumbers this drawing on
// its next build, as it does the figures and the page's list of boundaries.
const BOUNDARIES = { sandbox: 'Sandbox', network: 'Network', supply: 'Supply chain',
  identity: 'Identity and access' };
function boundaryNumbers() {
  const file = `${REPO}/software-factory/software-factory.md`;
  const sec = fs.readFileSync(file, 'utf8').split(/^# /m)
    .find(s => s.startsWith('The four security boundaries\n'));
  const order = sec ? [...sec.matchAll(/^## ([^:\n]+):/gm)].map(m => m[1].trim()) : [];
  const want = Object.values(BOUNDARIES);
  if (order.length !== want.length || want.some(b => !order.includes(b))) {
    console.error(`${path.relative(REPO, file)}: "The four security boundaries" has the sections `
      + `${JSON.stringify(order)}; the drawing numbers ${JSON.stringify(want)}`);
    process.exit(1);
  }
  return Object.fromEntries(Object.entries(BOUNDARIES).map(([k, b]) => [k, order.indexOf(b) + 1]));
}
const N = boundaryNumbers();

function kit(id, T) {
  // T: { title, gloss, lab, cap, num, lead, badge, pad, mk }
  const r = b => b.x + b.w, btm = b => b.y + b.h, cx = b => b.x + b.w / 2, cy = b => b.y + b.h / 2;
  const gl = (x, y, t) => `<text class="sfa-g" x="${f1(x)}" y="${f1(y)}" font-size="${T.gloss}">${esc(t)}</text>`;
  // a title and gloss lines, set in the middle of a box
  function lines(b, title, sub = [], o = {}) {
    sub = [].concat(sub);
    const cap = T.title * 0.72, desc = T.gloss * 0.22, lead = o.lead ?? T.lead;
    const block = cap + sub.length * lead + desc * (sub.length ? 1 : 0);
    const y0 = b.y + (b.h - block) / 2 + cap;
    const x = b.x + (o.dx ?? T.pad);
    let s = `<text class="sfa-t" x="${f1(x)}" y="${f1(y0)}" font-size="${T.title}">${esc(title)}</text>`;
    sub.forEach((l, i) => { s += gl(x, y0 + (i + 1) * lead, l); });
    return s;
  }
  const rect = (b, cls, rx = 6, extra = '') => `<rect class="${cls}" x="${b.x + .5}" y="${b.y + .5}" width="${b.w - 1}" height="${b.h - 1}" rx="${rx}"${extra}/>`;
  // o.k: the number of the boundary the card enforces, by which static/js/draw.js and the
  // page's sheet draw its outline in
  const card = (b, title, sub, o = {}) => `<g data-card="${esc(title)}">${rect(b, o.cls || 'sfa-box', 6, o.k ? ` pathLength="1" data-k="${o.k}"` : '')}${lines(b, title, sub, o)}${o.after || ''}</g>`;
  // the profile is a document, not a step in the request path: a folded corner
  function doc(b, title, sub) {
    const E = 13, X = r(b) - .5, Y = b.y + .5;
    return `<g data-card="${esc(title)}"><path class="sfa-doc" d="M${b.x + .5 + 6} ${Y} H${X - E} L${X} ${Y + E} V${btm(b) - .5 - 6} Q${X} ${btm(b) - .5} ${X - 6} ${btm(b) - .5} H${b.x + .5 + 6} Q${b.x + .5} ${btm(b) - .5} ${b.x + .5} ${btm(b) - .5 - 6} V${Y + 6} Q${b.x + .5} ${Y} ${b.x + .5 + 6} ${Y} Z"/>`
      + `<path class="sfa-ear" d="M${X - E} ${Y} V${Y + E} H${X} Z"/>` + lines(b, title, sub) + `</g>`;
  }
  // a boundary's number on the corner of what enforces it; o.ring draws it as a ring, for
  // a part that enforces another boundary's decision (the proxy, the service's), set on
  // that part's foot beside where the decision comes in
  const badge = (x, y, n, o = {}) => `<g class="sfa-badge${o.ring ? ' sfa-ring' : ''}" aria-hidden="true"><circle cx="${x}" cy="${y}" r="${o.ring ? T.badge - .75 : T.badge}"/><text x="${x}" y="${f1(y + T.num * 0.36)}" font-size="${T.num}" text-anchor="middle">${n}</text></g>`;
  // a wire; o.main draws it as part of the core path, heavier, with its own arrowhead;
  // o.both heads both ends, for a check that goes and comes back
  const wire = (pts, o = {}) => {
    const m = `url(#${id}-${o.main ? 'm' : 'a'})`;
    return `<path class="sfa-wire${o.main ? ' sfa-main' : ''}${o.dash ? ' sfa-dash' : ''}" d="M${pts.map(p => p.map(f1).join(' ')).join(' L')}"`
      + `${o.head === false ? '' : ` marker-end="${m}"`}${o.both ? ` marker-start="${m}"` : ''}/>`;
  };
  // where one wire joins another
  const dot = (x, y) => `<circle class="sfa-dot" cx="${f1(x)}" cy="${f1(y)}" r="3.2"/>`;
  const lbl = (x, y, t, o = {}) => `<text class="sfa-l" x="${f1(x)}" y="${f1(y)}" font-size="${T.lab}"${o.end ? ' text-anchor="end"' : o.mid ? ' text-anchor="middle"' : ''}>${esc(t)}</text>`;
  const capt = (x, y, t) => `<text class="sfa-cap" x="${x}" y="${y}" font-size="${T.cap}">${esc(t)}</text>`;
  const glyph = (d, x, y, s, cls) => `<path class="${cls}" transform="translate(${f1(x)} ${f1(y)}) scale(${s / 256})" d="${d}"/>`;
  // the sandbox: where untrusted agent code runs
  const sandbox = b => `<g data-zone="sandbox">${rect(b, 'sfa-zone sfa-b', 8, ` pathLength="1" data-k="${N.sandbox}"`)}`
    + capt(b.x + T.pad + 2, f1(b.y + T.title * 0.72 + 12), 'SANDBOX') + `</g>`;
  // what the proxy denies: a dashed card, its wire from the trunk ending on a stop bar on
  // the trunk's side of it. With o.inline its one word sits on the title's line.
  const deny = (b, trunkX, title, sub, o = {}) => {
    const by = cy(b), ex = trunkX > b.x ? r(b) + 8 : b.x - 8;
    const body = o.inline
      ? `<text class="sfa-t" x="${f1(b.x + T.pad)}" y="${f1(by + T.title * 0.34)}" font-size="${T.title}">${esc(title)}</text>${gl(b.x + T.pad + o.inline, by + T.title * 0.34, sub)}`
      : lines(b, title, [sub]);
    return `<g data-card="${esc(title)}">${rect(b, 'sfa-box sfa-deny')}${body}</g>`
      + `<path class="sfa-wire sfa-dash" d="M${trunkX} ${by} H${ex}"/><path class="sfa-wire sfa-stop" d="M${ex} ${by - 7} V${by + 7}"/>`;
  };
  // the record, under everything, its seal beside its name: t is the name's size, baseline
  // and inset, g where its lines start
  const record = (b, t, g) => `<g data-card="Tamper-evident record">${rect(b, 'sfa-rec', 6)}`
    + glyph(SEAL, b.x + 12, t.y - t.s - 1, t.s + 8, 'sfa-ico sfa-ico-rec')
    + `<text class="sfa-t" x="${f1(b.x + t.dx)}" y="${f1(t.y)}" font-size="${t.s}">Tamper-evident record</text>`
    + g.lines.map((l, i) => gl(g.x, g.y + i * T.lead, l)).join('') + `</g>`;
  // two arrowheads: the same shape, the core path's in its heavier ink (sized down so
  // the heavier stroke doesn't blow it up, since markers scale with the stroke)
  const mk = (k, cls, s) => `<marker id="${id}-${k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="${s}" markerHeight="${s}" orient="auto-start-reverse"><path class="${cls}" d="M0 0 L10 5 L0 10 z"/></marker>`;
  const defs = `<defs>${mk('a', 'sfa-mk', T.mk)}${mk('m', 'sfa-mk sfa-mk-main', f1(T.mk * 0.82))}</defs>`;
  return { r, btm, cx, cy, gl, lines, rect, card, doc, badge, wire, dot, lbl, capt, glyph, sandbox, deny, record, defs };
}

// What the boxes say, wide and narrow alike, in the words the paper's Figure 2 uses. The
// record names one event of each boundary's, as the paper's observability checklist does.
const SAYS = {
  profile: 'the most it can ever do',
  scanning: 'approved versions the profile allows',
  auth: 'authorizes each task’s scope',
  approval: 'automatic or a person',
  record: ['grants, admissions, process starts,', 'requests, linked by run'],
};
const SCANNING = 'Supply chain scanning';
const ALT =
  'The agent proposes, the runtime authorization service decides, and the egress proxy '
  + 'enforces. The agent runs in a sandbox, untrusted and holding no credentials, and proposes '
  + 'the scope it needs; the service authorizes each task’s scope within the bounds of the '
  + 'profile, using trusted context (identity, the task, any delegation and policy), and the '
  + 'proxy enforces it and attaches the credentials. Delegation only narrows a task, and only '
  + 'a new decision widens it. High-impact actions go to approval the agent can’t give; '
  + 'anything else is denied or sent to a person. The profile configures the sandbox at '
  + 'launch through supply chain scanning, which checks the components it is built from, '
  + 'and the proxy checks every package it fetches with it, so only approved versions the '
  + 'profile allows get in and new versions wait out a cooldown. Every grant, '
  + 'admission, process start and request goes into a tamper-evident record, linked by run. '
  + 'Badges number the boundaries as the paper does: '
  + Object.keys(BOUNDARIES).sort((a, b) => N[a] - N[b])
    .map(k => `${N[k]} ${BOUNDARIES[k].toLowerCase()}`).join(', ')
  + `; the proxy also carries ${N.identity}, as a ring where the authorized scope comes in, `
  + 'because it enforces the service’s decisions.';
const svgOf = (W, H, L, defs) =>
  `<svg xmlns="http://www.w3.org/2000/svg" class="sfa-d" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(ALT)}">`
  + `\n${defs}\n${L.flat().join('\n')}\n</svg>`;

// ── wide: the deck's row, set for an 880-unit canvas ─────────────────────────
// Smallest text 14.75 units, above the paper's figures' 14.65 (12.25 of 736): 10.8px
// in the 644px slot a 700px screen gives it, where theirs is 10.7px.
function wide() {
  const W = 880, T = { title: 16, gloss: 14.75, lab: 14.75, cap: 14.75, num: 14.75, lead: 19, badge: 11, pad: 12, mk: 7 };
  const K = kit('sfa-w', T);
  // above the row: the profile, and beside it supply chain scanning, across the
  // sandbox and the proxy, on the profile's launch path
  const PROF = { x: 14, y: 14, w: 184, h: 62 };
  const SC = { x: 300, y: 14, w: 360, h: 62 };
  // the row: sandbox · proxy · trunk · what lies behind it
  const SB = { x: 214, y: 112, w: 236, h: 130 };
  const AG = { x: SB.x + 14, y: SB.y + 44, w: SB.w - 28, h: 62 };
  const RY = K.cy(AG);
  const PX = { x: 484, y: RY - 40, w: 176, h: 80 };
  const TRUNK = 672, COL = { x: 686, w: 186 };
  const DN = { ...COL, y: RY - 40, h: 80 };
  const BLK = { ...COL, y: K.btm(DN) + 12, h: 40 };
  // beneath the row: the decision, under the sandbox and the proxy, what flows into it
  // on its left and approval under its right-hand end
  const AU = { x: SB.x, y: 300, w: K.r(PX) - SB.x, h: 62 };
  const TC = { x: 14, y: K.cy(AU) - 40, w: 150, h: 80 };
  const APR = { x: K.r(AU) - 186, y: K.btm(AU) + 38, w: 186, h: 62 };
  const REC = { x: 14, y: K.btm(APR) + 18, w: 858, h: 52 };
  const H = REC.y + REC.h + 4;
  const LY = 52, INTO = 400, CHK = 600;
  const PROPX = 300, AUTHX = K.cx(PX), BNX = 181, APRX = APR.x + 30;
  const L = [[], [], [], []]; // 0 zones, 1 cards, 2 wires, 3 labels and badges
  L[0].push(K.sandbox(SB));
  L[1].push(K.card(SC, SCANNING, [SAYS.scanning], { cls: 'sfa-box sfa-b', k: N.supply }));
  L[1].push(K.doc(PROF, 'Profile', [SAYS.profile]));
  L[1].push(K.card(AG, 'Agent', ['untrusted, no credentials'], { cls: 'sfa-box sfa-plate' }));
  L[1].push(K.card(PX, 'Egress proxy', ['default-deny,', 'attaches credentials'], { cls: 'sfa-box sfa-b', k: N.network }));
  L[1].push(K.card(DN, 'Downstream', ['only authorized', 'operations']));
  L[1].push(K.deny(BLK, TRUNK, 'Everything else', 'denied', { inline: 119 }));
  L[1].push(K.card(TC, 'Trusted context', ['identity, task,', 'delegation, policy'], { cls: 'sfa-box sfa-ctx' }));
  L[1].push(K.card(AU, 'Runtime authorization service', [SAYS.auth], { cls: 'sfa-box sfa-b', k: N.identity, dx: T.pad + 2 }));
  L[1].push(K.card(APR, 'Approval', [SAYS.approval], { after: K.glyph(HAND, APR.x + 90, APR.y + 12, 18, 'sfa-ico') }));
  L[1].push(K.record(REC, { s: T.title + 2, y: K.cy(REC) + 6, dx: 50 },
    { x: REC.x + 262, y: K.cy(REC) + 5, lines: [SAYS.record.join(' ')] }));
  // the launch path, straight across from the profile and through scanning into the
  // sandbox, and the proxy's package check
  L[2].push(K.wire([[K.r(PROF), LY], [SC.x, LY]]));
  L[3].push(K.lbl(K.r(PROF) + 9, LY - 25, 'configures'), K.lbl(K.r(PROF) + 9, LY - 8, 'at launch'));
  L[2].push(K.wire([[INTO, K.btm(SC)], [INTO, SB.y]]));
  L[3].push(K.lbl(INTO + 9, K.btm(SC) + 22, 'checks components'));
  L[2].push(K.wire([[CHK, K.btm(SC)], [CHK, PX.y]], { both: 1 }));
  L[3].push(K.lbl(CHK + 9, K.btm(SC) + 22, 'checks packages'));
  // the row's wires
  L[2].push(K.wire([[K.r(AG), RY], [PX.x, RY]], { main: 1 }));
  L[2].push(K.wire([[K.r(PX), RY], [DN.x, RY]]));
  L[2].push(`<path class="sfa-wire sfa-dash" d="M${TRUNK} ${RY} V${K.cy(BLK)}"/>`);
  // into the decision: trusted context, joined by the profile's bounds, in one arrow;
  // and the agent's proposal
  L[2].push(K.wire([[K.r(TC), K.cy(AU)], [AU.x, K.cy(AU)]], { main: 1 }));
  L[2].push(K.wire([[BNX, K.btm(PROF)], [BNX, K.cy(AU)]], { head: false }), K.dot(BNX, K.cy(AU)));
  L[3].push(K.lbl(BNX - 9, RY + 5, 'bounds every decision', { end: 1 }));
  L[2].push(K.wire([[PROPX, K.btm(AG)], [PROPX, AU.y]], { main: 1 }));
  L[3].push(K.lbl(PROPX + 9, K.btm(SB) + 34, 'proposes scope'));
  // out of it: the authorized scope up to the proxy, which enforces it; high-impact
  // actions down to approval
  L[2].push(K.wire([[AUTHX, AU.y], [AUTHX, K.btm(PX)]], { main: 1 }));
  L[3].push(K.lbl(AUTHX - 9, K.btm(SB) + 34, 'authorized scope', { end: 1 }));
  L[2].push(K.wire([[APRX, K.btm(AU)], [APRX, APR.y]]));
  L[3].push(K.lbl(APRX + 9, K.btm(AU) + 24, 'high-impact actions'));
  // the four boundaries, numbered as the paper numbers them; the proxy enforces the
  // service's decisions as well as the network's, so it carries the service's mark too,
  // as a ring where the authorized scope comes in
  L[3].push(K.badge(SB.x, SB.y, N.sandbox), K.badge(PX.x, PX.y, N.network),
    K.badge(AUTHX + 20, K.btm(PX), N.identity, { ring: 1 }), K.badge(SC.x, SC.y, N.supply),
    K.badge(AU.x, AU.y, N.identity));
  return { W, H, svg: svgOf(W, H, L, K.defs) };
}

// ── narrow: the same parts and relationships for phones, as the paper's Figure 2 sets
// them on a phone: the profile, scanning on its launch path, the sandbox beside the
// proxy, the decision beneath both with trusted context and approval under it, and
// what the proxy lets through fed down the right-hand edge past them. Smallest text
// 11.75 units: 10.3px at 320, where the drawing is 304px wide and the paper's narrow
// figures' is 10.1px.
function narrow() {
  const W = 348, T = { title: 13, gloss: 11.75, lab: 11.75, cap: 11.75, num: 11.75, lead: 16, badge: 9, pad: 12, mk: 6.5 };
  const K = kit('sfa-n', T);
  const LL = 30, RL = 340, CFX = 200;
  const PROF = { x: 16, y: 12, w: 316, h: 50 };
  const SC = { x: 44, y: 96, w: 288, h: 50 };
  const SB = { x: 44, y: 180, w: 136, h: 116 };
  const AG = { x: SB.x + 12, y: SB.y + 36, w: SB.w - 24, h: 66 };
  const RY = K.cy(AG);
  const PX = { x: 192, y: RY - 33, w: 140, h: 66 };
  const AU = { x: 16, y: K.btm(SB) + 34, w: 316, h: 50 };
  const TC = { x: 16, y: K.btm(AU) + 30, w: 144, h: 66 };
  const APR = { x: 176, y: K.btm(AU) + 30, w: 142, h: 50 };
  const DN = { x: 56, y: K.btm(TC) + 24, w: 262, h: 50 };
  const BLK = { x: 56, y: K.btm(DN) + 12, w: 262, h: 40 };
  const REC = { x: 16, y: K.btm(BLK) + 24, w: RL - 16, h: 82 };
  const H = REC.y + REC.h + 4;
  const INTO = 165, CHK = 300, PROPX = 100, AUTHX = 300, TCX = K.cx(TC), APRX = APR.x + 24;
  const L = [[], [], [], []];
  L[0].push(K.sandbox(SB));
  L[1].push(K.doc(PROF, 'Profile', [SAYS.profile]));
  L[1].push(K.card(SC, SCANNING, [SAYS.scanning], { cls: 'sfa-box sfa-b', k: N.supply }));
  L[1].push(K.card(AG, 'Agent', ['untrusted,', 'no credentials'], { cls: 'sfa-box sfa-plate' }));
  L[1].push(K.card(PX, 'Egress proxy', ['default-deny,', 'attaches credentials'], { cls: 'sfa-box sfa-b', k: N.network }));
  L[1].push(K.card(AU, 'Runtime authorization service', [SAYS.auth], { cls: 'sfa-box sfa-b', k: N.identity, dx: 14 }));
  L[1].push(K.card(TC, 'Trusted context', ['identity, task,', 'delegation, policy'], { cls: 'sfa-box sfa-ctx' }));
  L[1].push(K.card(APR, 'Approval', [SAYS.approval], { after: K.glyph(HAND, APR.x + 76, APR.y + 9, 15, 'sfa-ico') }));
  L[1].push(K.card(DN, 'Downstream', ['only authorized operations']));
  L[1].push(K.deny(BLK, RL, 'Everything else', 'denied', { inline: 104 }));
  L[1].push(K.record(REC, { s: T.title + 2, y: REC.y + 28, dx: 44 },
    { x: REC.x + 12, y: REC.y + 50, lines: SAYS.record }));
  // the profile's two jobs, labelled side by side under it: it bounds the decision (its
  // wire runs down the left edge into the service) and configures the sandbox at launch,
  // through scanning
  L[2].push(K.wire([[LL, K.btm(PROF)], [LL, AU.y]]));
  L[3].push(K.lbl(LL + 8, 83, 'bounds every decision'));
  L[2].push(K.wire([[CFX, K.btm(PROF)], [CFX, SC.y]]));
  L[3].push(K.lbl(CFX + 8, 83, 'configures at launch'));
  // scanning's two checks, each labelled left of its own wire
  L[2].push(K.wire([[INTO, K.btm(SC)], [INTO, SB.y]]));
  L[3].push(K.lbl(INTO - 8, K.btm(SC) + 22, 'checks components', { end: 1 }));
  L[2].push(K.wire([[CHK, K.btm(SC)], [CHK, PX.y]], { both: 1 }));
  L[3].push(K.lbl(CHK - 8, K.btm(SC) + 22, 'checks packages', { end: 1 }));
  // the agent's requests to the proxy; between the row and the decision, its proposal
  // going down and the authorized scope coming up
  L[2].push(K.wire([[K.r(AG), RY], [PX.x, RY]], { main: 1 }));
  L[2].push(K.wire([[PROPX, K.btm(AG)], [PROPX, AU.y]], { main: 1 }));
  L[3].push(K.lbl(PROPX + 8, K.btm(SB) + 21, 'proposes scope'));
  L[2].push(K.wire([[AUTHX, AU.y], [AUTHX, K.btm(PX)]], { main: 1 }));
  L[3].push(K.lbl(AUTHX - 8, K.btm(SB) + 21, 'authorized scope', { end: 1 }));
  // under the decision: trusted context into it, high-impact actions out to approval
  L[2].push(K.wire([[TCX, TC.y], [TCX, K.btm(AU)]], { main: 1 }));
  L[2].push(K.wire([[APRX, K.btm(AU)], [APRX, APR.y]]));
  L[3].push(K.lbl(APRX + 8, K.btm(AU) + 19, 'high-impact actions'));
  // what leaves the proxy, down a trunk on the right
  L[2].push(K.wire([[K.r(PX), RY], [RL, RY], [RL, K.cy(DN)], [K.r(DN), K.cy(DN)]]));
  L[2].push(`<path class="sfa-wire sfa-dash" d="M${RL} ${K.cy(DN)} V${K.cy(BLK)}"/>`);
  L[3].push(K.badge(SB.x, SB.y, N.sandbox), K.badge(PX.x, PX.y, N.network),
    K.badge(AUTHX + 18, K.btm(PX), N.identity, { ring: 1 }), K.badge(SC.x, SC.y, N.supply),
    K.badge(AU.x, AU.y, N.identity));
  return { W, H, svg: svgOf(W, H, L, K.defs) };
}

for (const [name, fn] of [['sf-architecture', wide], ['sf-architecture-narrow', narrow]]) {
  const { W, H, svg } = fn();
  fs.writeFileSync(`${REPO}/layouts/partials/${name}.svg`, svg + '\n');
  console.log(`wrote layouts/partials/${name}.svg ${W}×${H}`);
}
