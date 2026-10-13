// node bin/build-architecture-drawing.mjs
// Writes layouts/partials/sf-architecture.svg (wide) and sf-architecture-narrow.svg:
// the talk deck's one-row architecture (profile · agent in its sandbox · egress proxy ·
// what lies behind it, with the runtime authorization service beneath and the
// tamper-evident record under everything), redrawn for /reference-architecture.
// The page's own drawing, not one of the paper's figures: the paper's stay in
// software-factory/figures/ and the PDF. Labels are the paper's words.
// The agent proposes, the runtime authorization service decides, and the egress proxy
// enforces. The service is drawn as a decision, not a container: trusted context (who's
// asking, who it acts for, the task, policy, any delegation) and the profile's bounds
// flow into it, with the agent's proposal for each task and each delegation, which it
// doesn't take at face value; this task's scope (to the proxy, which enforces it),
// approval and the record flow out, and anything else is denied or sent to a person. Task and delegation are
// what the decision weighs, never boxes inside it: delegation only narrows a task, and
// only a new decision widens one. The profile appears once, with its two jobs: it
// configures the sandbox at launch and bounds every decision.
// The core path (agent to proxy, the proposal, trusted context into the decision, this
// task's scope) is drawn heavier than the rest (.sfa-main).
// Colours come from classes the page styles with its own tokens (.sfa-* in
// layouts/reference-architecture.html), so the drawing follows the theme.
// Its text is never smaller than the paper's figures' beside it, at any width: they
// share the figures' slot and switch point, and the smallest text here is at least
// theirs in proportion (wide: 12.25 of 736 units, so 14.65 of 880; narrow: 12.5 of 376).
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const icon = n => fs.readFileSync(`${REPO}/layouts/partials/icons/${n}.svg`, 'utf8').match(/ d="([^"]+)"/)[1];
const SEAL = icon('seal-check'), HAND = icon('hand-palm');
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/'/g, '’');
const f1 = n => +(+n).toFixed(1);

function kit(id, T) {
  // T: { title, gloss, lab, cap, num, lead, badge, pad, mk }
  const r = b => b.x + b.w, btm = b => b.y + b.h, cx = b => b.x + b.w / 2, cy = b => b.y + b.h / 2;
  const gl = (x, y, t) => `<text class="sfa-g" x="${f1(x)}" y="${f1(y)}" font-size="${T.gloss}">${esc(t)}</text>`;
  // a title and gloss lines, set in the middle of a box (or from its top, with o.top)
  function lines(b, title, sub = [], o = {}) {
    sub = [].concat(sub);
    const cap = T.title * 0.72, desc = T.gloss * 0.22, lead = o.lead ?? T.lead;
    const block = cap + sub.length * lead + desc * (sub.length ? 1 : 0);
    const y0 = o.top != null ? b.y + o.top + cap : b.y + (b.h - block) / 2 + cap;
    const x = b.x + (o.dx ?? T.pad);
    let s = `<text class="sfa-t" x="${f1(x)}" y="${f1(y0)}" font-size="${T.title}">${esc(title)}</text>`;
    sub.forEach((l, i) => { s += gl(x, y0 + (i + 1) * lead, l); });
    return s;
  }
  const rect = (b, cls, rx = 6, extra = '') => `<rect class="${cls}" x="${b.x + .5}" y="${b.y + .5}" width="${b.w - 1}" height="${b.h - 1}" rx="${rx}"${extra}/>`;
  const card = (b, title, sub, o = {}) => `<g data-card="${esc(title)}">${rect(b, o.cls || 'sfa-box', 6, o.b ? ` pathLength="1" data-k="${o.b}"` : '')}${lines(b, title, sub, o)}${o.after || ''}</g>`;
  // the profile is a document, not a step in the request path: a folded corner
  function doc(b, title, sub) {
    const E = 13, X = r(b) - .5, Y = b.y + .5;
    return `<g data-card="${esc(title)}"><path class="sfa-doc" d="M${b.x + .5 + 6} ${Y} H${X - E} L${X} ${Y + E} V${btm(b) - .5 - 6} Q${X} ${btm(b) - .5} ${X - 6} ${btm(b) - .5} H${b.x + .5 + 6} Q${b.x + .5} ${btm(b) - .5} ${b.x + .5} ${btm(b) - .5 - 6} V${Y + 6} Q${b.x + .5} ${Y} ${b.x + .5 + 6} ${Y} Z"/>`
      + `<path class="sfa-ear" d="M${X - E} ${Y} V${Y + E} H${X} Z"/>` + lines(b, title, sub) + `</g>`;
  }
  const badge = (x, y, n) => `<g class="sfa-badge" aria-hidden="true"><circle cx="${x}" cy="${y}" r="${T.badge}"/><text x="${x}" y="${f1(y + T.num * 0.36)}" font-size="${T.num}" text-anchor="middle">${n}</text></g>`;
  // a wire; o.main draws it as part of the core path, heavier, with its own arrowhead
  const wire = (pts, o = {}) => `<path class="sfa-wire${o.main ? ' sfa-main' : ''}${o.dash ? ' sfa-dash' : ''}" d="M${pts.map(p => p.map(f1).join(' ')).join(' L')}"${o.head === false ? '' : ` marker-end="url(#${id}-${o.main ? 'm' : 'a'})"`}/>`;
  // where one wire joins another
  const dot = (x, y) => `<circle class="sfa-dot" cx="${f1(x)}" cy="${f1(y)}" r="3.2"/>`;
  const lbl = (x, y, t, o = {}) => `<text class="sfa-l" x="${f1(x)}" y="${f1(y)}" font-size="${T.lab}"${o.end ? ' text-anchor="end"' : o.mid ? ' text-anchor="middle"' : ''}>${esc(t)}</text>`;
  const capt = (x, y, t) => `<text class="sfa-cap" x="${x}" y="${y}" font-size="${T.cap}">${esc(t)}</text>`;
  const glyph = (d, x, y, s, cls) => `<path class="${cls}" transform="translate(${f1(x)} ${f1(y)}) scale(${s / 256})" d="${d}"/>`;
  // over time: a small loop on the proposal wire, centred on (x, y), the wire running
  // through it (a paper disc hides the wire inside): task after task, delegation after
  // delegation, each proposed and checked
  const cycle = (x, y, R) => {
    const a0 = -60 * Math.PI / 180, a1 = 230 * Math.PI / 180;
    const p = a => [x + R * Math.cos(a), y + R * Math.sin(a)].map(f1);
    const [ex, ey] = p(a1), h = R * 0.62;
    // the arrowhead at the arc's end, pointing along it (clockwise)
    const tx = -Math.sin(a1), ty = Math.cos(a1), nx = Math.cos(a1), ny = Math.sin(a1);
    const tip = [ex + tx * h, ey + ty * h], b1 = [ex + nx * h * 0.7, ey + ny * h * 0.7], b2 = [ex - nx * h * 0.7, ey - ny * h * 0.7];
    return `<g aria-hidden="true"><circle class="sfa-disc" cx="${f1(x)}" cy="${f1(y)}" r="${f1(R + 2.5)}"/><path class="sfa-cyc" d="M${p(a0).join(' ')} A${R} ${R} 0 1 1 ${ex} ${ey}"/>`
      + `<path class="sfa-cyc-h" d="M${tip.map(f1).join(' ')} L${b1.map(f1).join(' ')} L${b2.map(f1).join(' ')} Z"/></g>`;
  };
  // the sandbox: untrusted execution, one per task, built from verified components
  const sandbox = (b, k, capW, line2Y) => `<g data-zone="sandbox">${rect(b, 'sfa-zone sfa-b', 8, ` pathLength="1" data-k="${k}"`)}`
    + capt(b.x + T.pad + 2, f1(b.y + T.title * 0.72 + 12), 'SANDBOX')
    + gl(b.x + T.pad + 2 + capW, b.y + T.title * 0.72 + 12, 'one per task')
    + gl(b.x + T.pad + 2, line2Y, 'built from verified components') + `</g>`;
  // what the proxy denies: a dashed card, its wire ending on a stop bar. With
  // o.inline its one word sits on the title's line.
  const deny = (b, trunkX, title, sub, o = {}) => {
    const by = cy(b), ex = b.x - 8;
    const body = o.inline
      ? `<text class="sfa-t" x="${f1(b.x + T.pad)}" y="${f1(by + T.title * 0.34)}" font-size="${T.title}">${esc(title)}</text>${gl(b.x + T.pad + o.inline, by + T.title * 0.34, sub)}`
      : lines(b, title, [sub]);
    return `<g data-card="${esc(title)}">${rect(b, 'sfa-box sfa-deny')}${body}</g>`
      + `<path class="sfa-wire sfa-dash" d="M${trunkX} ${by} H${ex}"/><path class="sfa-wire sfa-stop" d="M${ex} ${by - 7} V${by + 7}"/>`;
  };
  // two arrowheads: the same shape, the core path's in its heavier ink (sized down so
  // the heavier stroke doesn't blow it up, since markers scale with the stroke)
  const mk = (k, cls, s) => `<marker id="${id}-${k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="${s}" markerHeight="${s}" orient="auto-start-reverse"><path class="${cls}" d="M0 0 L10 5 L0 10 z"/></marker>`;
  const defs = `<defs>${mk('a', 'sfa-mk', T.mk)}${mk('m', 'sfa-mk sfa-mk-main', f1(T.mk * 0.82))}</defs>`;
  return { r, btm, cx, cy, gl, lines, rect, card, doc, badge, wire, dot, lbl, capt, glyph, cycle, sandbox, deny, defs };
}

const ALT = 'The agent proposes, the runtime authorization service decides, and the egress proxy enforces. Trusted context (who’s asking, who it acts for, the task, policy, any delegation and the profile’s bounds) flows into each decision. For each task and each delegation, the agent, untrusted and holding no credentials, proposes the scope it needs, which the service doesn’t take at face value; delegation only narrows a task, and only a new decision widens it. The proxy enforces this task’s scope and attaches the credentials. High-impact actions go to approval the agent can’t give; anything else is denied or sent to a person. The profile also configures each sandbox at launch. Every grant is recorded, and every boundary keeps a tamper-evident record. Badges number the boundaries: 1 identity and access, 2 supply chain (the admission point), 3 sandbox, 4 network.';
const svgOf = (W, H, L, defs) => `<svg xmlns="http://www.w3.org/2000/svg" class="sfa-d" viewBox="0 0 ${W} ${H}" role="img" aria-label="${ALT}">\n${defs}\n${L.flat().join('\n')}\n</svg>`;

// ── wide: the deck's row, set for an 880-unit canvas ─────────────────────────
// Smallest text 14.75 units, above the paper's figures' 14.65 (12.25 of 736): 10.8px
// in the 644px slot a 700px screen gives it, where theirs is 10.7px.
function wide() {
  const W = 880, T = { title: 16, gloss: 14.75, lab: 14.75, cap: 14.75, num: 14.75, lead: 19, badge: 11, pad: 12, mk: 7 };
  const K = kit('sfa-w', T);
  // row: profile · gap for "configures at launch" · sandbox · proxy · trunk · what lies behind it
  const SB = { x: 264, y: 14, w: 242, h: 150 };
  const AG = { x: SB.x + 14, y: SB.y + 60, w: SB.w - 28, h: 76 };
  const RY = K.cy(AG);
  const PROF = { x: 14, y: RY - 38, w: 176, h: 76 };
  const PX = { x: 540, y: RY - 47, w: 114, h: 94 };
  const TRUNK = 670, COL = { x: 686, w: 186 };
  const DN = { ...COL, y: RY - 37, h: 74 };
  const ADM = { ...COL, y: K.btm(DN) + 12, h: 92 };
  const BLK = { ...COL, y: K.btm(ADM) + 10, h: 40 };
  // beneath: the decision, clear of the proxy's column (its top below what the proxy
  // denies, so that denial doesn't read as the service's), what flows into it on the
  // left and its outcomes beneath it, approval out of the proxy's column
  const AU = { x: 254, y: K.btm(BLK) + 10, w: K.r(PX) - 254, h: 114 };
  const TC = { x: 14, y: K.cy(AU) - 55, w: 150, h: 110 };
  const APR = { x: K.r(AU) - 186, y: K.btm(AU) + 38, w: 186, h: 92 };
  const REC = { x: 14, y: K.btm(APR) + 18, w: 858, h: 52 };
  const H = REC.y + REC.h + 4;
  // the proposal and the record leave the service on different lines, so nothing reads
  // as passing straight through it
  const PROPX = 300, AUTHX = K.cx(PX), BNX = 177, RECX = 380, APRX = APR.x + 30;
  const L = [[], [], [], []]; // 0 zones, 1 cards, 2 wires, 3 labels and badges
  L[0].push(K.sandbox(SB, 3, 87, SB.y + 47));
  L[1].push(K.doc(PROF, 'Profile', ['for one kind of agent,', 'the most it can ever do']));
  L[1].push(K.card(AG, 'Agent', ['untrusted, and holds', 'no credentials'], { cls: 'sfa-box sfa-plate' }));
  L[1].push(K.card(PX, 'Egress proxy', ['enforces it,', 'attaches', 'credentials'], { cls: 'sfa-box sfa-b', b: 4 }));
  L[1].push(K.card(DN, 'Downstream', ['only authorized', 'operations reach it']));
  L[1].push(K.card(ADM, 'Admission point', ['approved versions', 'the profile allows;', 'hides unsafe ones'], { cls: 'sfa-box sfa-b', b: 2 }));
  L[1].push(K.deny(BLK, TRUNK, 'Everything else', 'denied', { inline: 119 }));
  L[1].push(K.card(TC, 'Trusted context', ['who’s asking,', 'who it acts for,', 'the task, policy,', 'and any delegation'], { cls: 'sfa-box sfa-ctx' }));
  L[1].push(K.card(AU, 'Runtime authorization service', ['decides what access each task gets;', 'delegation only narrows;', 'only a new decision widens a task;', 'anything else: denied, or sent to a person'], { cls: 'sfa-box sfa-b', b: 1, dx: T.pad + 2 }));
  L[1].push(K.card(APR, 'Approval', ['the agent can’t give it:', 'a person, or automatic', 'within approval policy'], { after: K.glyph(HAND, APR.x + 86, APR.y + 10, 18, 'sfa-ico') }));
  // the record, under everything: every boundary keeps one
  L[1].push(`<g data-card="Tamper-evident record">${K.rect(REC, 'sfa-rec', 6)}`
    + K.glyph(SEAL, REC.x + 14, REC.y + REC.h / 2 - 13, 26, 'sfa-ico sfa-ico-rec')
    + `<text class="sfa-t" x="${REC.x + 50}" y="${f1(REC.y + REC.h / 2 + 6)}" font-size="${T.title + 2}">Tamper-evident record</text>`
    + K.gl(REC.x + 262, REC.y + REC.h / 2 + 5, 'every boundary keeps its own, linked by run, out of any agent’s reach') + `</g>`);
  // the row's wires
  L[2].push(K.wire([[K.r(PROF), RY], [SB.x, RY]]));
  L[3].push(K.lbl((K.r(PROF) + SB.x) / 2, RY - 24, 'configures', { mid: 1 }), K.lbl((K.r(PROF) + SB.x) / 2, RY - 8, 'at launch', { mid: 1 }));
  L[2].push(K.wire([[K.r(AG), RY], [PX.x, RY]], { main: 1 }));
  L[2].push(K.wire([[K.r(PX), RY], [DN.x, RY]]));
  L[2].push(K.wire([[TRUNK, RY], [TRUNK, K.cy(ADM)], [ADM.x, K.cy(ADM)]]));
  L[2].push(`<path class="sfa-wire sfa-dash" d="M${TRUNK} ${K.cy(ADM)} V${K.cy(BLK)}"/>`);
  // into the decision: trusted context, joined by the profile's bounds, in one arrow;
  // and the agent's proposal, task after task, which it doesn't take at face value
  L[2].push(K.wire([[K.r(TC), K.cy(AU)], [AU.x, K.cy(AU)]], { main: 1 }));
  L[2].push(K.wire([[BNX, K.btm(PROF)], [BNX, K.cy(AU)]], { head: false }), K.dot(BNX, K.cy(AU)));
  L[3].push(K.lbl(BNX - 9, K.btm(SB) + 62, 'bounds every decision', { end: 1 }));
  L[2].push(K.wire([[PROPX, K.btm(AG)], [PROPX, AU.y]], { main: 1 }));
  L[3].push(K.cycle(PROPX, K.btm(SB) + 22, 8), K.lbl(PROPX + 16, K.btm(SB) + 27, 'each task, each delegation:'));
  L[3].push(K.lbl(PROPX + 16, K.btm(SB) + 46, 'proposes scope,'), K.lbl(PROPX + 16, K.btm(SB) + 62, 'not taken at face value'));
  // out of it: this task's scope up to the proxy, which enforces it; high-impact
  // actions down to approval; every grant to the record
  L[2].push(K.wire([[AUTHX, AU.y], [AUTHX, K.btm(PX)]], { main: 1 }));
  L[3].push(K.lbl(AUTHX - 9, K.btm(SB) + 46, 'this task’s scope', { end: 1 }));
  const outY = K.btm(AU) + 24;
  L[2].push(K.wire([[APRX, K.btm(AU)], [APRX, APR.y]]));
  L[3].push(K.lbl(APRX + 9, outY, 'high-impact actions'));
  L[2].push(K.wire([[RECX, K.btm(AU)], [RECX, REC.y]]));
  L[3].push(K.lbl(RECX - 9, outY, 'every grant recorded', { end: 1 }));
  // the four boundaries, numbered as the page's list numbers them
  L[3].push(K.badge(AU.x, AU.y, 1), K.badge(ADM.x, ADM.y, 2), K.badge(SB.x, SB.y, 3), K.badge(PX.x, PX.y, 4));
  return { W, H, svg: svgOf(W, H, L, K.defs) };
}

// ── narrow: the same parts and relationships, top to bottom, for phones ─────
// Read down the column: the profile, the sandbox, what flows into the decision, the
// decision, approval, then the proxy that enforces it; no wire runs back up. Smallest
// text 11.75 units: 10.3px at 320, where the drawing is 304px wide and the paper's
// narrow figures' is 10.1px.
function narrow() {
  const W = 348, T = { title: 13, gloss: 11.75, lab: 11.75, cap: 11.75, num: 11.75, lead: 16, badge: 9, pad: 12, mk: 6.5 };
  const K = kit('sfa-n', T);
  const LL = 34, RL = 332, X0 = 56, X1 = 312;
  const PROF = { x: 16, y: 12, w: X1 - 16, h: 48 };
  const SB = { x: X0, y: 96, w: X1 - X0, h: 112 };
  const AG = { x: X0 + 14, y: SB.y + 52, w: X1 - X0 - 28, h: 46 };
  // trusted context sits right of the profile's own wire, which runs past it into the decision
  const TC = { x: 48, y: K.btm(SB) + 26, w: 136, h: 92 };
  const AU = { x: 16, y: K.btm(TC) + 26, w: X1 - 16, h: 110 };
  const APR = { x: 152, y: K.btm(AU) + 26, w: X1 - 152, h: 78 };
  const PX = { x: X0, y: K.btm(APR) + 40, w: X1 - X0, h: 46 };
  const DN = { x: X0, y: K.btm(PX) + 18, w: X1 - X0, h: 46 };
  const ADM = { x: X0, y: K.btm(DN) + 12, w: X1 - X0, h: 62 };
  const BLK = { x: X0, y: K.btm(ADM) + 12, w: X1 - X0, h: 40 };
  const REC = { x: 16, y: K.btm(BLK) + 18, w: RL - 16, h: 72 };
  const H = REC.y + REC.h + 4;
  const CFX = 170, PROPX = 196, AUTHX = 132, APRX = APR.x + 20;
  const L = [[], [], [], []];
  L[0].push(K.sandbox(SB, 3, 74, SB.y + 39));
  L[1].push(K.doc(PROF, 'Profile', ['for one kind of agent, the most it can ever do']));
  L[1].push(K.card(AG, 'Agent', ['untrusted, and holds no credentials'], { cls: 'sfa-box sfa-plate' }));
  L[1].push(K.card(TC, 'Trusted context', ['who’s asking,', 'who it acts for,', 'the task, policy,', 'and any delegation'], { cls: 'sfa-box sfa-ctx' }));
  L[1].push(K.card(AU, 'Runtime authorization service', ['decides what access each task gets', 'and records every grant;', 'delegation only narrows;', 'only a new decision widens a task;', 'anything else: denied, or sent to a person'], { cls: 'sfa-box sfa-b', b: 1, dx: 14 }));
  L[1].push(K.card(APR, 'Approval', ['the agent can’t give it:', 'a person, or automatic', 'within approval policy'], { lead: 15, after: K.glyph(HAND, APR.x + 78, APR.y + 9, 15, 'sfa-ico') }));
  L[1].push(K.card(PX, 'Egress proxy', ['enforces it, attaches credentials'], { cls: 'sfa-box sfa-b', b: 4 }));
  L[1].push(K.card(DN, 'Downstream', ['only authorized operations reach it']));
  L[1].push(K.card(ADM, 'Admission point', ['approved versions the profile allows;', 'hides unsafe ones'], { cls: 'sfa-box sfa-b', b: 2 }));
  L[1].push(K.deny(BLK, LL, 'Everything else', 'denied'));
  L[1].push(`<g data-card="Tamper-evident record">${K.rect(REC, 'sfa-rec', 6)}`
    + K.glyph(SEAL, REC.x + 12, REC.y + 12, 24, 'sfa-ico sfa-ico-rec')
    + `<text class="sfa-t" x="${REC.x + 44}" y="${REC.y + 30}" font-size="${T.title + 2}">Tamper-evident record</text>`
    + K.gl(REC.x + 12, REC.y + 50, 'every boundary keeps its own, linked by run,')
    + K.gl(REC.x + 12, REC.y + 65, 'out of any agent’s reach') + `</g>`);
  // the profile's two jobs, labelled side by side under it: it bounds the decision
  // itself (its wire runs down the left edge, past trusted context, into the service)
  // and configures the sandbox at launch
  L[2].push(K.wire([[LL, K.btm(PROF)], [LL, AU.y]]));
  L[3].push(K.lbl(LL + 8, 83, 'bounds every decision'));
  L[2].push(K.wire([[CFX, K.btm(PROF)], [CFX, SB.y]]));
  L[3].push(K.lbl(CFX + 8, 83, 'configures at launch'));
  // into the decision: trusted context, and the agent's proposal, task after task
  L[2].push(K.wire([[K.cx(TC), K.btm(TC)], [K.cx(TC), AU.y]], { main: 1 }));
  L[2].push(K.wire([[PROPX, K.btm(AG)], [PROPX, AU.y]], { main: 1 }));
  L[3].push(K.cycle(PROPX, K.btm(SB) + 20, 6.5), K.lbl(PROPX + 13, K.btm(SB) + 24, 'each task,'), K.lbl(PROPX + 13, K.btm(SB) + 39, 'each delegation:'));
  L[3].push(K.lbl(PROPX + 13, K.btm(SB) + 57, 'proposes scope,'), K.lbl(PROPX + 13, K.btm(SB) + 72, 'not taken at face value'));
  // the agent's requests reach the proxy down the right-hand edge
  L[2].push(K.wire([[K.r(AG), K.cy(AG)], [RL, K.cy(AG)], [RL, K.cy(PX)], [K.r(PX), K.cy(PX)]], { main: 1 }));
  // out of the decision: high-impact actions to approval, this task's scope on to the proxy
  L[2].push(K.wire([[APRX, K.btm(AU)], [APRX, APR.y]]));
  L[3].push(K.lbl(APRX + 8, K.btm(AU) + 17, 'high-impact actions'));
  L[2].push(K.wire([[AUTHX, K.btm(AU)], [AUTHX, PX.y]], { main: 1 }));
  L[3].push(K.lbl(AUTHX - 8, K.cy(APR) + 4, 'this task’s scope', { end: 1 }));
  // what leaves the proxy, down a trunk on the left
  L[2].push(K.wire([[PX.x, K.cy(PX)], [LL, K.cy(PX)], [LL, K.cy(DN)], [DN.x, K.cy(DN)]]));
  L[2].push(K.wire([[LL, K.cy(DN)], [LL, K.cy(ADM)], [ADM.x, K.cy(ADM)]]));
  L[2].push(`<path class="sfa-wire sfa-dash" d="M${LL} ${K.cy(ADM)} V${K.cy(BLK)}"/>`);
  L[3].push(K.badge(AU.x, AU.y, 1), K.badge(ADM.x, ADM.y, 2), K.badge(SB.x, SB.y, 3), K.badge(PX.x, PX.y, 4));
  return { W, H, svg: svgOf(W, H, L, K.defs) };
}

for (const [name, fn] of [['sf-architecture', wide], ['sf-architecture-narrow', narrow]]) {
  const { W, H, svg } = fn();
  fs.writeFileSync(`${REPO}/layouts/partials/${name}.svg`, svg + '\n');
  console.log(`wrote layouts/partials/${name}.svg ${W}×${H}`);
}
