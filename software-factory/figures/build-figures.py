#!/usr/bin/env python3
"""The Secure Software Factory — its six figures, generated.

Drawn with the first paper's kit (whitepaper/figures/figkit.py): the same plate,
the same four voices (Figtree names, Plex Serif glosses, Chakra Petch labels,
Plex Mono numerals) and the same hairline cards. Structure comes from position,
whitespace and hairlines. Colour encodes exactly one thing, the paper's own
central distinction:

  * GUARD (the site's accent) marks what is enforced outside the agent's loop —
    the four boundaries, the enforcement infrastructure and the record. Each
    boundary carries its number on the corner of the part that enforces it, and
    the numbers are the paper's: each boundary's place among the sections of
    "The four security boundaries", read when the figures are built
    (boundary_numbers), so reordering the paper renumbers every drawing. The
    egress proxy enforces two boundaries' decisions (the glossary's "both the
    network boundary and the identity and access boundary's authorization
    decisions"), so it carries the network's mark on its corner and, as a ring
    on the edge where the authorized scope comes in (its foot in Figure 2, its
    top in the levels and Figure 6), identity and access's.
  * WASH marks untrusted agent execution: the inside of a sandbox, and any
    agent that plans or watches from outside one.

Everything else is ink on the plate. The levels (Figures 3–5) are each drawn
complete, and what a level adds is marked by weight and a pale tint (NEWT),
which survive a greyscale print and leave the accent its one meaning:

  new card       tint fill (a wash card keeps its wash) and a heavier outline
  new connector  ink, heavier
  new words      outside a card, set on the tint
  carried over   drawn as the level before drew it

Figure 2 is one row — the profile, the agent in its sandbox, the egress proxy,
and what lies behind it — between two trusted controls: the supply chain
firewall above it, which checks the components a sandbox is built from and
every package the proxy fetches, and the runtime authorization service beneath
it. The levels (Figures 3–5) share one skeleton drawn to the lead author's
composition (LV): whoever orchestrates across the top; beneath it the durable
execution layer, a separate card, and beside that the service, above the
column of what the proxies reach (the firewall and the model gateway,
trusted, then what lies downstream); the frame where agents run, the record
inside it; the outputs along the foot. Figure 6, one incident at Level 3, is
drawn on the same skeleton. Wherever it is drawn the service is a decision,
not a container: what the agent (at Level 3, the orchestrator) proposes comes
into it, and the scope it authorizes goes to the proxy.
Figure 1 is the process the boundaries serve, so it has its own composition.

The drawing names things; the paper and the caption explain them. A box is
its name and at most one short phrase, an arrow a verb or two.

Every label is the paper's vocabulary (final draft, 13 October 2026), with the
lead author's wording from his redrawn figures where it is the plainer one.
Sizes are set for the PDF column: at 150 mm (425.2 pt) a 736-unit canvas prints
at 0.578 pt per unit, so the smallest run here (12.25 units) prints at 7.08 pt.

Writes figure-N.svg and figure-N-narrow.svg for N = 1…6, each with the box
manifest bin/check-figure reads and a geometry manifest for the checks that
only boxed figures need (containment, connectors that land, nothing drawn
through text).
"""
import contextlib, json, math, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "whitepaper" / "figures"))
from figkit import Fig, C  # noqa: E402

# ── the one colour, and the wash ─────────────────────────────────────────────
# figkit's accent (#1A4D8F) is the first paper's identifier blue and never
# appears in a drawing; on the web every accent becomes --fig-accent, the
# site's olive. These figures are mostly accent, so they carry the olive in
# their fixed ink too: the PNG, the PDF and the light page then agree.
GUARD = "#5A7A00"
WASH = "#F1F2EC"
# Card outlines. figkit's rule (#CBCDC8) is 1.6:1 on white, too faint for
# outlines that carry meaning, such as the cards of the trusted context Figure 2
# feeds into its decision. These figures use the reference-architecture page's own --fig-rule,
# 3.45:1 on white (WCAG 1.4.11's 3:1), and the partials map it back to that
# token. The first paper keeps figkit's rule.
RULE = "#8F8A7C"

# ── type, sized for the PDF column ───────────────────────────────────────────
# Every figure is drawn on a 720-unit content width (360 for phones) and set on
# a canvas MARGIN wider on every side, so no stroke meets the canvas edge. The
# PDF prints the 736-unit canvas 425.2 pt wide (measured; see bin/check-figure),
# 0.578 pt a unit, so the smallest run here (12.25) prints at 7.08 pt and a name
# (12.5) at 7.22 pt. On the page the same 12.25 is never under 11 px.
W = 720
MARGIN = 8
NAME, GLOSS, LAB, NUM = 12.5, 12.25, 12.25, 12.25
# Narrow (phone) compositions are shown as small as 304 px (a 320 px phone with
# 8 px gutters), where 12.25 units would render at 9.9 px; their smallest run is
# 12.5 units, 10.1 px there. bin/check-figure holds both.
NARROW_TYPE = 12.5
PAD = 10                              # card inset
# Cards that carry a boundary badge on their corner stack this far apart: the
# badge's radius (8) plus the 2 units bin/check-figure keeps it clear of the
# card above, plus 2 of air.
STACK = 12

# ── what each figure says, in words ──────────────────────────────────────────
# CAPTION is the paper's, verbatim; it is each drawing's <title>. ALT is the
# alt text: what the drawing shows and the point it makes, in one or two plain
# sentences. It is each drawing's <desc>, wide and narrow alike, and the text
# the paper source carries for the figure, so the page, the PDF and a screen
# reader say the same thing.
CAPTION = {
    1: "Work loops until it passes, and problems feed back to design",
    2: "The agent proposes, policy authorizes, and infrastructure enforces",
    3: "Level 1, where a developer gives an agent room to work without giving it everything "
       "the developer can reach",
    4: "Level 2, where a workflow orchestrates",
    5: "Level 3, where an agent orchestrates but can't grant itself access",
    6: "Only a new authorization decision can widen a task",
}
ALT = {
    1: "Work arrives as a prompt, a requirements document or a ticket, design sets its "
       "limits, and an inner loop "
       "assembles, builds in a sandbox and verifies the change until it passes. After review "
       "and a deploy under approval policy, an outer loop carries review, evals and "
       "production feedback back to design, and production signals start new work.",
    # Figure 2's describes the redrawn figure. bin/check-copy holds every one
    # to the alt text the paper carries.
    2: "An agent in a sandbox, holding no credentials, proposes the scope it needs; the "
       "runtime authorization service decides within the bounds of the agent's profile, using "
       "trusted context: the agent and whoever it acts for, its task, any delegation and "
       "policy. The egress proxy enforces that decision and attaches the credentials, so only "
       "authorized operations reach anything downstream and packages come only through an "
       "admission point. High-impact actions go to an approval the agent can't give, anything "
       "outside policy is denied or sent to a person, and every grant is recorded. The profile "
       "also configures the sandbox at launch, and each boundary keeps a tamper-evident record.",
    3: "A developer kicks off each run of one coding agent, an agent harness built from "
       "skills, tools, hooks and context files and configured by its profile, in a sandbox "
       "on their machine or a remote environment. The agent proposes the scope it needs, "
       "and a default-deny egress proxy enforces the authorization service's decision on "
       "every request it makes to the supply chain firewall, a model gateway, source "
       "control, APIs and MCP servers; its pull request goes back to the developer, who "
       "drives the next run.",
    4: "A request, event, schedule or ticket starts a workflow, which schedules each run "
       "on a durable execution layer, CI/CD or a step runner, that starts the same agent "
       "harness in a fresh sandbox behind its own proxy. The pull request goes through "
       "approval to merge, review feedback drives the next run, and the authorization "
       "service, supply chain firewall, model gateway and downstream are the same as at "
       "Level 1.",
    5: "An orchestrator agent takes in requests, context and signals, divides the work "
       "into tasks and schedules them on the durable execution layer beneath it, a "
       "separate system that starts each agent in its own sandbox behind its own proxy; it "
       "proposes each task's profile and scope to the authorization service, which alone "
       "grants access. Monitoring agents watch the work from outside, changes go through "
       "approval and deploy to production, and incidents, scanner findings, monitoring and "
       "evals come back as signals that start new work.",
    6: "A production alert leads the orchestrator to schedule a task for an incident agent on "
       "the durable execution layer, which starts the agent in its sandbox, and to propose the "
       "task's scope, one service's logs for the last hour and one pull request, which the "
       "authorization service checks against policy and the alert's source. When the agent "
       "reaches for another "
       "service's logs, the proxy blocks the call, because only a new authorization decision "
       "could widen the task; the fix ships through approval and a small first deploy, and the "
       "error rate afterward confirms it or starts the next run.",
}
LS = 0.04                             # label tracking (em)

# ── the four boundaries, numbered by the paper ───────────────────────────────
# A boundary's number is its place among the "## Name: ..." sections under
# "# The four security boundaries" in the paper, read here at build time, so a
# reorder there renumbers every badge and key on the next build. The page's
# own drawing (bin/build-architecture-drawing.mjs) and its boundary list read
# the same sections.
PAPER = ROOT / "software-factory" / "software-factory.md"
SANDBOX, NETWORK, SUPPLY, IAM = "Sandbox", "Network", "Supply chain", "Identity and access"


def boundary_numbers(paper=PAPER):
    """{boundary: its number}, from the order of the paper's sections. Stops
    the build when the section has other boundaries than the four drawn."""
    src = paper.read_text(encoding="utf-8")
    sec = re.search(r"^# The four security boundaries\n(.*?)(?=^# |\Z)", src, re.M | re.S)
    order = [h.split(":", 1)[0].strip()
             for h in re.findall(r"^## (.+?)(?:\s*\{#[^}]*\})?$", sec.group(1), re.M)] if sec else []
    want = (SANDBOX, NETWORK, SUPPLY, IAM)
    if sorted(order) != sorted(want):
        raise SystemExit(f"{paper.name}: \"The four security boundaries\" has the sections "
                         f"{order}; the figures number {list(want)}")
    return {b: order.index(b) + 1 for b in want}


BN = boundary_numbers()


class SF(Fig):
    """figkit's Fig plus boxes, badges and connectors, all recorded so the
    checker can see them: a card the text escapes, an arrow that ends in
    mid-air or a line drawn through a label are errors, not taste."""

    def __init__(self, key, w, h, title, desc, narrow=False):
        super().__init__(w, h, title, desc)
        self.key = key
        # figkit names title/desc "ft"/"fd"; several figures share a page, so
        # each gets its own ids.
        self.parts[0] = self.parts[0].replace('aria-labelledby="ft fd"',
                                              f'aria-labelledby="{key}-t {key}-d"')
        self.parts[1] = self.parts[1].replace('id="ft"', f'id="{key}-t"')
        self.parts[2] = self.parts[2].replace('id="fd"', f'id="{key}-d"')
        self.shapes, self.links = [], []
        self.narrow = narrow
        for k, col in (("a", C["faint"]), ("g", GUARD), ("s", C["soft"])):
            self._def(f"m{k}", f'<marker id="{key}-{k}" viewBox="0 0 10 10" refX="9" refY="5" '
                               f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
                               f'<path d="M0 0 L10 5 L0 10 z" fill="{col}"/></marker>')

    # canvas height is known only once a column has been laid out
    def set_height(self, h):
        h = int(math.ceil(h))
        self.parts[0] = self.parts[0].replace(f'0 0 {self.W} {self.H}"', f'0 0 {self.W} {h}"') \
                                     .replace(f'height="{self.H}"', f'height="{h}"')
        self.parts[3] = f'<rect width="{self.W}" height="{h}" fill="{C["plate"]}"/>'
        self.H = h

    def rule(self, y, x1, x2, colour=None):
        """figkit's fading rule, its gradient id prefixed with this figure's
        key. figkit names it by colour and span alone, so two figures on one
        page that draw a rule over the same span would share an id, url(#…)
        would resolve to the first copy, and when that copy sat in a hidden
        variant or tab the rule would vanish. The first paper's figures keep
        figkit's ids; only these figures are renamed."""
        c = colour or C["hair"]
        old = f'fade{c.lstrip("#")}{int(x1)}x{int(x2)}'
        new = f"{self.key}-{old}"
        super().rule(y, x1, x2, colour)
        self.parts[-1] = self.parts[-1].replace(f"url(#{old})", f"url(#{new})")
        if old in self._defs:
            markup = self._defs.pop(old).replace(f'id="{old}"', f'id="{new}"')
            self._defs.setdefault(new, markup)

    # ── text in the page's four voices ──
    def name(self, x, y, s, tag, size=NAME):
        return self.text(x, y, s, size, C["ink"], "600", tag=tag, face="head")

    # sizes per figure: a narrow composition sets its small runs larger
    @property
    def gs(self):
        return NARROW_TYPE if self.narrow else GLOSS

    @property
    def ls(self):
        return NARROW_TYPE if self.narrow else LAB

    @property
    def ns(self):
        return NARROW_TYPE if self.narrow else NUM

    def gloss(self, x, y, s, tag, size=None, fill=None):
        return self.text(x, y, s, size or self.gs, fill or C["soft"], tag=tag)

    def lab(self, x, y, s, tag, fill=None, size=None):
        size = size or self.ls
        return self.text(x, y, s.upper(), size, fill or C["soft"], "500", False, LS,
                         tag=tag, face="label")

    def width(self, s, kind):
        if kind == "name":
            return len(s) * self._adv(NAME, False, "600", "head")
        if kind == "label":
            return len(s) * (self._adv(self.ls, False, "500", "label") + LS * self.ls)
        return len(s) * self._adv(self.gs, False)

    # ── shapes ──
    STYLE = {
        "card":    ('fill="none"', RULE, 1, ""),
        "guard":   ('fill="none"', GUARD, 1.25, ""),
        # a guard drawn in front of its own stack: opaque, so the cards behind
        # show only their right and bottom edges, as the sandbox stack does
        "guardfill": (f'fill="{C["plate"]}"', GUARD, 1.25, ""),
        "sandbox": (f'fill="{WASH}"', GUARD, 1.25, ""),
        "agent":   (f'fill="{WASH}"', RULE, 1, ""),
        "ghost":   (f'fill="{C["plate"]}"', GUARD, 0.75, ""),
        "zone":    ('fill="none"', C["faint"], 1, ' stroke-dasharray="4 3"'),
        "blocked": ('fill="none"', RULE, 1, ' stroke-dasharray="3 3"'),
        "floor":   ('fill="none"', RULE, 1, ""),
    }
    SOLID = {"card", "guard", "guardfill", "sandbox", "agent", "blocked", "floor"}

    def box(self, x, y, w, h, kind, tag):
        """Drawn half a unit inside its box, so a hairline on the canvas edge is
        not clipped and every edge lands on the pixel grid; recorded at its box."""
        fill, stroke, sw, dash = self.STYLE[kind]
        self.parts.append(f'<rect x="{x + .5:g}" y="{y + .5:g}" width="{w - 1:g}" '
                          f'height="{h - 1:g}" rx="4" {fill} '
                          f'stroke="{stroke}" stroke-width="{sw}"{dash}/>')
        self.shapes.append({"tag": tag, "kind": kind, "x": x, "y": y, "w": w, "h": h,
                            "solid": kind in self.SOLID, "sw": sw})

    def badge(self, cx, cy, n, tag, light=False):
        """A boundary number: an accent disc with the numeral knocked out. It
        sits on the corner of the part that enforces the boundary, so it reads
        as a mark on that part rather than as a word in its name. `light`: a
        ring the same size with the numeral in the accent, for a part that
        enforces another boundary's decision (the proxy, identity and access's)."""
        if light:
            self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="7.4" fill="{C["plate"]}" '
                              f'stroke="{GUARD}" stroke-width="1.2"/>')
            self.text(cx - 3.3, cy + 3.9, str(n), self.ns, GUARD, "600", True, tag=f"#{tag}")
        else:
            self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="{GUARD}"/>')
            self.text(cx - 3.3, cy + 3.9, str(n), self.ns, C["plate"], "600", True,
                      tag=f"#{tag}")
        self.shapes.append({"tag": f"badge{tag}", "kind": "badge", "x": cx - 8, "y": cy - 8,
                            "w": 16, "h": 16, "solid": True})

    def node(self, x, y, w, h, name, gloss=(), kind="card", num=None, tag="", lh=14.5):
        """A card: name, then up to a few gloss lines, left-aligned at the inset
        the first paper's cards use. Returns the card's box."""
        self.box(x, y, w, h, kind, tag)
        if num:
            self.badge(x, y, num, tag)
        names = name if isinstance(name, (list, tuple)) else [name]
        by = y + 21
        for i, n in enumerate(names):
            self.name(x + PAD, by + i * 15, n, f"{tag}.n{i}")
        gy = by + (len(names) - 1) * 15 + 16
        for i, g in enumerate(gloss):
            self.gloss(x + PAD, gy + i * lh, g, f"{tag}.g{i}")
        return (x, y, w, h)

    # ── connectors ──
    def link(self, pts, kind="flow", head=True, tag="", group=None, bar=False, free=False):
        """An orthogonal connector. flow: a request or traffic (faint, solid).
        grant: an authorization decision (accent, dashed). loop: the outer loop
        (soft, dashed). bar: ends in a stop instead of a head — blocked."""
        col, sw, dash, m = {"flow": (C["faint"], 1.1, "", "a"),
                            "grant": (GUARD, 1.25, ' stroke-dasharray="5 3"', "g"),
                            "loop": (C["soft"], 1.1, ' stroke-dasharray="4 3"', "s")}[kind]
        d = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
        mk = f' marker-end="url(#{self.key}-{m})"' if head and not bar else ""
        self.parts.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}"'
                          f'{dash}{mk}/>')
        if bar:  # the stop is the proxy enforcing, so it takes the accent
            (x1, y1), (x2, y2) = pts[-2], pts[-1]
            if y1 == y2:
                self.parts.append(f'<path d="M{x2 - 1.5:g} {y2-7:g} L{x2 - 1.5:g} {y2+7:g}" '
                                  f'stroke="{GUARD}" stroke-width="2"/>')
            else:
                self.parts.append(f'<path d="M{x2-7:g} {y2 - 1.5:g} L{x2+7:g} {y2 - 1.5:g}" '
                                  f'stroke="{GUARD}" stroke-width="2"/>')
        self.links.append({"tag": tag, "kind": kind, "pts": pts, "head": head and not bar,
                           "group": group, "free": free})

    def dot(self, x, y, tag, colour=None, r=2.6):
        """Where one connector joins another: a small disc, so a line that
        runs into a path reads as joining it rather than branching off it.
        Recorded as a mark, so no text may sit on it."""
        self.parts.append(f'<circle cx="{x:g}" cy="{y:g}" r="{r}" fill="{colour or C["faint"]}"/>')
        self.shapes.append({"tag": tag, "kind": "glyph", "x": x - r, "y": y - r, "w": 2 * r,
                            "h": 2 * r, "solid": False})

    def loop_glyph(self, cx, cy, tag, r=6.5):
        """The inner loop as a mark: an open circle that comes back round on
        itself, its head drawn along the arc's tangent rather than by a marker,
        so it reads as a loop and not as a reload button."""
        a0, a1 = math.radians(-40), math.radians(250)
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        col = C["faint"]
        self.parts.append(f'<path d="M{x0:.2f} {y0:.2f} A{r} {r} 0 1 1 {x1:.2f} {y1:.2f}" '
                          f'fill="none" stroke="{col}" stroke-width="1.2"/>')
        tx, ty = -math.sin(a1), math.cos(a1)          # clockwise tangent at the end
        nx, ny = -ty, tx
        tip = (x1 + tx * 3.6, y1 + ty * 3.6)
        b1 = (x1 + nx * 2.6, y1 + ny * 2.6)
        b2 = (x1 - nx * 2.6, y1 - ny * 2.6)
        self.parts.append(f'<path d="M{tip[0]:.2f} {tip[1]:.2f} L{b1[0]:.2f} {b1[1]:.2f} '
                          f'L{b2[0]:.2f} {b2[1]:.2f} z" fill="{col}"/>')
        self.shapes.append({"tag": tag, "kind": "glyph", "x": cx - r - 3, "y": cy - r - 3,
                            "w": 2 * r + 6, "h": 2 * r + 6, "solid": False})

    def write(self, name):
        """Set the drawing on its canvas: MARGIN of air on every side, the
        content translated into it, and every manifest coordinate moved with
        it so the checker sees the canvas the reader does."""
        m = MARGIN
        cw, ch = self.W + 2 * m, int(math.ceil(self.H)) + 2 * m
        self.parts[0] = re.sub(r'viewBox="0 0 [\d.]+ [\d.]+" width="[\d.]+" height="[\d.]+"',
                               f'viewBox="0 0 {cw} {ch}" width="{cw}" height="{ch}"',
                               self.parts[0])
        self.parts[3] = f'<rect width="{cw}" height="{ch}" fill="{C["plate"]}"/>'
        self.parts.insert(4, f'<g transform="translate({m} {m})">')
        self.parts.append("</g>")
        for b in self.boxes:
            b["x"] += m
            b["y"] += m
        for sh in self.shapes:
            sh["x"] += m
            sh["y"] += m
        for l in self.links:
            l["pts"] = [(x + m, y + m) for x, y in l["pts"]]
        self.W, self.H = cw, ch
        # where the figure is shown, and how small that makes its text, is
        # bin/check-figure's to decide (rule 9), not this manifest's
        meta = {"W": self.W, "H": self.H, "shapes": self.shapes, "links": self.links,
                "margin": m}
        super().write(name, out_dir=HERE)
        (HERE / f".{name}.geom.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")



def mid(a):
    return (a[0] + a[1]) / 2


# a destination card's height, when it has a name and no more
DEST_H = 44


def card_h(gloss, name=""):
    """A card's height: one name line and one gloss line is 44; each further
    line adds its leading."""
    names = len(name) if isinstance(name, (list, tuple)) else 1
    # each further line at its leading (15 for names, 14.5 for glosses),
    # rounded up to even units so every fan branch lands on a whole unit
    return 44 + 16 * (names - 1) + 16 * max(len(gloss) - 1, 0)


# ── the supply chain firewall, and the proxy that checks with it ─────────────
# The supply chain boundary's trusted control, named as the paper names it
# (the glossary's Supply Chain Firewall, the trust table's "supply chain
# firewall"). It has the card the runtime authorization service has, with the
# supply chain mark. It checks the components a sandbox is built from, on the
# path that launches the agent, and the proxy checks every package it fetches
# with it, both ways. Its line is the checklist's ("approved versions allowed
# by the agent's profile"). The levels and Figure 6 draw it at the head of
# the column of what the proxies reach (lv_column).
SC_NAME = "Supply chain firewall"
SC_G = "approved versions the profile allows"
SC_LAUNCH, SC_PKG = "checks components", "checks packages"


def sc_card(f, x0, y0, x1, lines=(SC_G,), tag="sc"):
    """The supply chain firewall as a card, its line set in `lines`; returns
    its bottom."""
    h = card_h(lines)
    f.node(x0, y0, x1 - x0, h, SC_NAME, lines, kind="guard", num=BN[SUPPLY], tag=tag)
    return y0 + h


def proxy_card(f, x0, y0, x1, y1, gloss, grant_x, kind="guard", tag="proxy"):
    """The egress proxy: the network's mark on its corner and, as a ring on
    its foot just right of where the authorized scope (at grant_x) comes in,
    the identity and access mark of the decision it enforces. The card keeps
    its gloss clear of the ring."""
    f.node(x0, y0, x1 - x0, y1 - y0, "Egress proxy", gloss, kind=kind, num=BN[NETWORK], tag=tag)
    f.badge(grant_x + 14, y1, BN[IAM], tag, light=True)


# The key's own text, measured: Chrome, the site's IBM Plex Serif 400 at 12.25
# units (GLOSS), getComputedTextLength (12 Oct 2026). The key is spaced by these,
# with one constant gap. Spaced by the checker's deliberately pessimistic
# estimate, which overstates long phrases (+24 units on "Identity and access")
# and slightly understates short capitalised words, evenly meant items came out
# about three times further apart in one place than another.
KEY_W = {"Enforced outside the agent’s loop:": 194.34, "Identity and access": 110.31,
         "Supply chain": 75.2, "Sandbox": 50.2, "Network": 49.3}
KEY_GAP = 14


# the key, in the paper's order
ALL_MARKS = tuple(sorted((n, b) for b, n in BN.items()))


def legend(f, x, y, width, marks=ALL_MARKS):
    """The key, once, for the one thing a reader can't read off the drawing:
    the numbered marks are boundaries, enforced outside the agent's loop. It
    keys only the boundaries the figure draws. The arrows that matter carry
    their own labels, and the shaded fill is named where it is drawn ("the
    agent, untrusted"), so neither needs a key. One line wide, two narrow,
    each item placed by its measured width and one gap."""
    def measured(s_):
        if s_ not in KEY_W:
            raise SystemExit(f"legend: measure {s_!r} (KEY_W) before keying it")
        w = KEY_W[s_] * f.gs / GLOSS             # measured at GLOSS; scales with size
        f.boxes[-1]["w"] = w + 1                 # the run as drawn, plus a unit
        return w

    f.rule(y - 18, x, x + width)
    head = "Enforced outside the agent’s loop:"
    f.text(x, y, head, f.gs, C["ink"], tag="lg.h")
    bx, by = x + measured(head) + KEY_GAP, y
    need = sum(22 + KEY_W[s_] * f.gs / GLOSS for _, s_ in marks) + KEY_GAP * (len(marks) - 1)
    if bx + need > x + width:
        bx, by = x, y + 24
    for n, s_ in marks:
        f.badge(bx + 8, by - 4, n, f"lg{n}")
        f.gloss(bx + 22, by, s_, f"lg{n}.t")
        bx += 22 + measured(s_) + KEY_GAP
    return by + 6


def key_grid(f, x, y, marks=ALL_MARKS, cols=2):
    """The key in a block: its heading, then the marks in a grid, each column
    as wide as its widest measured name, one gap between. For a figure whose
    free space is a corner rather than a line."""
    k = f.gs / GLOSS
    head = "Enforced outside the agent’s loop:"
    f.text(x, y, head, f.gs, C["ink"], tag="lg.h")
    f.boxes[-1]["w"] = KEY_W[head] * k + 1
    colw = [max(22 + KEY_W[s_] * k for _, s_ in marks[c::cols]) for c in range(cols)]
    for i, (n, s_) in enumerate(marks):
        r, c = divmod(i, cols)
        bx = x + sum(colw[:c]) + KEY_GAP * c
        by = y + 24 * (r + 1)
        f.badge(bx + 8, by - 4, n, f"lg{n}")
        f.gloss(bx + 22, by, s_, f"lg{n}.t")
        f.boxes[-1]["w"] = KEY_W[s_] * k + 1
    return y + 24 * ((len(marks) + cols - 1) // cols) + 6


# ═════════════════════════════════════════════════════════════════════════════
# Figures 2–6. What a level adds is marked by weight and a pale tint; the
# accent keeps its one meaning (enforced outside the agent's loop).
# ═════════════════════════════════════════════════════════════════════════════
INK, SOFT, FAINT, PLATE = C["ink"], C["soft"], C["faint"], C["plate"]
# New at this level: a pale accent tint (--fig-new on the page), dark enough
# (luma ≈ 221) to stay apart from the sandbox's wash (≈ 241) in a greyscale print.
NEWT = "#DCE4BE"
KEY_W.update({"new at Level 1": 81.19, "new at Level 2": 81.19, "new at Level 3": 81.19,
              "as in Figure 2": 77.7, "as at Level 1": 69.94, "as at Level 2": 69.94})
# The same words wherever the same part is drawn. Approval is the glossary's
# approval policy ("approved automatically or waits for a person"); the
# service's line is the lead author's ("authorizes each task's scope"); the
# proxy's is the paper's default-deny, and in Figure 2, where who holds the
# credentials is the point, where they are attached. The execution layer's
# says what it is and what it does that the orchestrator doesn't: the paper's
# "agents start and stop only through the execution layer".
APPROVAL_G = ["automatic or a person"]
AUTH_G = "authorizes each task’s scope"
F2_PROXY_G = ["default-deny,", "attaches credentials"]
EXEC_G = ["CI/CD or a step runner", "that starts each agent"]

# Runs measured: Chrome, the site's fonts at the size each is set,
# getComputedTextLength, without letter-spacing (12–13 Oct 2026). Words set on
# the tint are tinted to the measured width; figkit's estimate overstates long
# runs by up to a tenth, which would leave a ragged tail of tint. A label set
# right against its own line is placed by its measured width for the same
# reason (gloss_to): placed by the estimate, it drifts off its line toward the
# next one over. A run that isn't here stops the build rather than guessing.
TINT_W = {
    "label|500|12.25|DEVELOPER’S MACHINE": 133.72,
    "label|500|12.25|OUTER LOOP": 73.09,
    "label|500|12.25|THE FACTORY": 77.53,
    "label|500|12.5|DEVELOPER’S MACHINE": 136.44,
    "label|500|12.5|OUTER LOOP": 74.58,
    "label|500|12.5|THE FACTORY": 79.11,
    "serif|400|12.25|a shared service": 93.75,
    "serif|400|12.25|all four boundaries’ records, linked by run": 242.52,
    "serif|400|12.25|and task scope": 85.08,
    "serif|400|12.25|and updates the configuration": 172.98,
    "serif|400|12.25|checks policy and the alert’s source": 203.81,
    "serif|400|12.25|decision": 48.78,
    "serif|400|12.25|drives the next run": 109.31,
    "serif|400|12.25|each part to its own agent,": 150.66,
    "serif|400|12.25|inner loop, until it passes": 145.13,
    "serif|400|12.25|last hour; one pull request": 150.59,
    "serif|400|12.25|needs a new": 70.80,
    "serif|400|12.25|new work": 55.69,
    "serif|400|12.25|opens": 34.92,
    "serif|400|12.25|or a remote environment": 144.22,
    "serif|400|12.25|proposes payments logs,": 141.97,
    "serif|400|12.25|proposes profile": 93.53,
    "serif|400|12.25|proposes scope": 89.05,
    "serif|400|12.25|review feedback": 93.75,
    "serif|400|12.25|schedules runs": 87.80,
    "serif|400|12.25|schedules tasks": 90.86,
    "serif|400|12.25|telemetry and evals across all runs": 199.83,
    "serif|400|12.25|the developer drives the next run": 190.73,
    "serif|400|12.25|with narrowed authority": 140.03,
    "serif|400|12.5|a shared service": 95.67,
    "serif|400|12.5|all four boundaries’ records, by run": 207.36,
    "serif|400|12.5|and task scope": 86.81,
    "serif|400|12.5|and updates the configuration": 176.50,
    "serif|400|12.5|decision": 49.77,
    "serif|400|12.5|each part to its own agent,": 153.73,
    "serif|400|12.5|inner loop,": 63.67,
    "serif|400|12.5|logs, last hour;": 85.33,
    "serif|400|12.5|needs a new": 72.25,
    "serif|400|12.5|new work": 56.81,
    "serif|400|12.5|one pull request": 95.14,
    "serif|400|12.5|opens": 35.63,
    "serif|400|12.5|or a remote environment": 147.16,
    "serif|400|12.5|proposes": 54.00,
    "serif|400|12.5|proposes payments": 115.17,
    "serif|400|12.5|proposes profile": 95.44,
    "serif|400|12.5|review feedback drives the next run": 210.11,
    "serif|400|12.5|schedules runs": 89.58,
    "serif|400|12.5|schedules tasks": 92.70,
    "serif|400|12.5|scope": 33.97,
    "serif|400|12.5|telemetry and evals across all runs": 203.91,
    "serif|400|12.5|the developer drives the next run": 194.63,
    "serif|400|12.5|until it passes": 81.52,
    "serif|400|12.5|with narrowed authority": 142.89,
}


def measured(f, s, face="serif", weight="400"):
    """A run's measured width (TINT_W), at the size this figure sets it."""
    key = f"{face}|{weight}|{(f.gs if face == 'serif' else f.ls):g}|{s}"
    if key not in TINT_W:
        raise SystemExit(f"measure {key!r} (TINT_W) before setting it against a line")
    return TINT_W[key]


def gloss_to(f, x, y, s, tag):
    """A gloss right-aligned to end at x, by its measured width, and recorded
    at that width, so the checker holds the run as drawn. On the tint, the
    tint is already recorded."""
    w = measured(f, s)
    f.gloss(x - w, y, s, tag)
    if f.state != "newtext":
        f.boxes[-1]["w"] = w + 1


class CF(SF):
    """SF plus the levels' states. `at("new")` draws what a level adds (tint
    and weight); `at("newtext")` sets words outside a card on the tint."""
    STYLE = {**SF.STYLE, "record": ('fill="none"', GUARD, 1.25, "")}
    SOLID = SF.SOLID | {"record"}

    def __init__(self, key, w, h, title, desc, narrow=False, level=0):
        super().__init__(key, w, h, title, desc, narrow)
        self.level, self.state = level, "old"
        for k, col, mw in (("n", INK, 4.4), ("H", INK, 3.0), ("G", GUARD, 3.8)):
            self._def(f"m{k}", f'<marker id="{key}-{k}" viewBox="0 0 10 10" refX="9" refY="5" '
                               f'markerWidth="{mw}" markerHeight="{mw}" orient="auto-start-reverse">'
                               f'<path d="M0 0 L10 5 L0 10 z" fill="{col}"/></marker>')

    @contextlib.contextmanager
    def at(self, state):
        before, self.state = self.state, state
        try:
            yield
        finally:
            self.state = before

    def text(self, x, y, s, size=13, fill=None, weight="400", mono=False, ls=0.0, tag="",
             href="", face=None):
        if self.state == "newtext":
            fill = INK
            key = f"{face or 'serif'}|{weight}|{size:g}|{s}"
            if key not in TINT_W:
                raise SystemExit(f"tint: measure {key!r} (TINT_W) before setting it on the tint")
            wd = TINT_W[key] + len(s) * ls * size
            self.parts.append(f'<rect x="{x - 3:g}" y="{y - size * 0.84:.2f}" width="{wd + 6:.2f}" '
                              f'height="{size * 1.14:.2f}" rx="2" fill="{NEWT}"/>')
            w = super().text(x, y, s, size, fill, weight, mono, ls, tag, href, face)
            # the run as drawn: its tint, which is measured, not figkit's estimate
            self.boxes[-1].update(x=x - 3, w=wd + 6)
            return w
        return super().text(x, y, s, size, fill, weight, mono, ls, tag, href, face)

    def box(self, x, y, w, h, kind, tag, fill=None):
        f_, stroke, sw, dash = self.STYLE[kind]
        if self.state == "new":
            if kind in ("guard", "guardfill", "record"):
                f_, sw = f'fill="{NEWT}"', 2.0
            elif kind == "sandbox":
                sw = 2.0
            elif kind in ("card", "blocked"):
                f_, stroke, sw = f'fill="{NEWT}"', SOFT, 1.75
            elif kind == "agent":
                stroke, sw = SOFT, 1.75
        if fill:
            f_ = f'fill="{fill}"'
        self.parts.append(f'<rect x="{x + .5:g}" y="{y + .5:g}" width="{w - 1:g}" '
                          f'height="{h - 1:g}" rx="4" {f_} '
                          f'stroke="{stroke}" stroke-width="{sw}"{dash}/>')
        self.shapes.append({"tag": tag, "kind": kind, "x": x, "y": y, "w": w, "h": h,
                            "solid": kind in self.SOLID, "sw": sw})

    def ghost(self, x, y, w, h, tag, front):
        """A card stacked behind another, in the front card's own treatment."""
        new = self.state == "new"
        if front == "sandbox":
            fill, sw = WASH, (1.25 if new else 0.75)
        else:
            fill, sw = (NEWT if new else PLATE), (1.25 if new else 0.75)
        self.parts.append(f'<rect x="{x + .5:g}" y="{y + .5:g}" width="{w - 1:g}" '
                          f'height="{h - 1:g}" rx="4" fill="{fill}" stroke="{GUARD}" '
                          f'stroke-width="{sw}"/>')
        self.shapes.append({"tag": tag, "kind": "ghost", "x": x, "y": y, "w": w, "h": h,
                            "solid": False, "sw": sw})

    def link(self, pts, kind="flow", head=True, tag="", group=None, bar=False, free=False,
             heavy=False, stop=False, both=False, dot=False):
        """SF's connectors, plus watch (dotted, no head: watching, not acting)
        and heavy (the orchestrator's proposal, the line that matters most). A
        grant, the decision going out, is solid accent and heavier than any
        flow but that proposal: dashes already mean the frames, the outer loop
        and a stop. `both`
        heads both ends: a check that goes and comes back (the proxy's
        packages, through the supply chain firewall). `dot` marks where a
        headless connector ends on another, joining it."""
        new = self.state in ("new", "newtext")
        dash = ""
        if kind == "grant":
            col, sw, m = GUARD, 1.75, "G"
        elif kind == "watch":
            col, sw, m, head = (INK, 1.5, None, False) if new else (FAINT, 1.1, None, False)
            dash = ' stroke-dasharray="0.1 3.2" stroke-linecap="round"'
            sw = sw + 0.6
        elif kind == "loop":
            col, sw, m = (INK, 1.5, "n") if new else (SOFT, 1.1, "s")
            dash = ' stroke-dasharray="4 3"'
        else:
            col, sw, m = (INK, 1.5, "n") if new else (FAINT, 1.1, "a")
        if heavy:
            col, sw, m = INK, 2.25, "H"
        d = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
        mk = f' marker-end="url(#{self.key}-{m})"' if head and not bar and m else ""
        if both and mk:
            mk += f' marker-start="url(#{self.key}-{m})"'
        self.parts.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}"'
                          f'{dash}{mk}/>')
        if bar:  # the stop is enforcement outside the agent's loop, so it takes the accent
            (x1, y1), (x2, y2) = pts[-2], pts[-1]
            if y1 == y2:
                d = 1.5 if x2 > x1 else -1.5
                self.parts.append(f'<path d="M{x2 - d:g} {y2 - 7:g} L{x2 - d:g} {y2 + 7:g}" '
                                  f'stroke="{GUARD}" stroke-width="2"/>')
                mark = (min(x2, x2 - 2 * d), y2 - 7, 2, 14)
            else:
                d = 1.5 if y2 > y1 else -1.5
                self.parts.append(f'<path d="M{x2 - 7:g} {y2 - d:g} L{x2 + 7:g} {y2 - d:g}" '
                                  f'stroke="{GUARD}" stroke-width="2"/>')
                mark = (x2 - 7, min(y2, y2 - 2 * d), 14, 2)
            if stop:
                # a stop that ends in the open (no card behind it: the service
                # denying, not the proxy blocking a call to somewhere): the bar
                # is drawn, so it is recorded, and the connector ends on it
                self.shapes.append({"tag": f"{tag}.stop", "kind": "stop", "x": mark[0],
                                    "y": mark[1], "w": mark[2], "h": mark[3], "solid": False})
        self.links.append({"tag": tag, "kind": "flow" if kind == "watch" else kind, "pts": pts,
                           "head": bool(head and not bar and m), "group": group, "free": free})
        if dot:
            self.dot(*pts[-1], f"{tag}.dot", col)


# ── shared pieces ────────────────────────────────────────────────────────────
def record(f, x0, y0, x1, y1, tag="obs", two=False):
    """The record every boundary keeps: an accent outline with a heavier top
    rule (no heavier than a grant, so the eye lands on the decision, not the
    footer) and an accent title, Observability, as the paper names it. Returns where
    its gloss starts (beside the title, or under it when `two`)."""
    f.box(x0, y0, x1 - x0, y1 - y0, "record", tag)
    f.parts.append(f'<path d="M{x0 + 4:g} {y0 + 1.5:g} L{x1 - 4:g} {y0 + 1.5:g}" '
                   f'stroke="{GUARD}" stroke-width="1.75"/>')
    if two:
        f.text(x0 + PAD, y0 + 23, "Observability", NAME, GUARD, "600", tag=f"{tag}.n", face="head")
        return y0 + 23
    f.text(x0 + PAD, y0 + 28, "Observability", NAME, GUARD, "600", tag=f"{tag}.n", face="head")
    return x0 + PAD + f.width("Observability", "name") + 14


def delta_key(f, x, y, prev, gap=19):
    """Two marks, the tint and the plain card: new at this level, as before."""
    k = f.gs / GLOSS
    for i, (st, s) in enumerate((("new", f"new at Level {f.level}"), ("old", prev))):
        yy = y + i * gap
        with f.at(st):
            f.box(x, yy - 10, 18, 12, "card", f"dk{i}")
        f.text(x + 24, yy, s, f.gs, SOFT, tag=f"dk{i}.t")
        f.boxes[-1]["w"] = KEY_W[s] * k + 1


# ═════════════════════════════════════════════════════════════════════════════
# The levels (Figures 3–5), on one skeleton drawn to the lead author's
# composition (his redrawn Levels 1 and 3, 13 Oct 2026). Across the top, in
# one place at every level, whoever orchestrates: the developer, a workflow,
# then an orchestrator agent, with what starts the work coming in from the
# left. Beneath it, a separate and plainer card, the durable execution layer
# (Levels 2 and 3; at Level 1 the developer works through the agent harness)
# and, beside that, the runtime authorization service, above the column on the
# right of what the proxies reach: the supply chain firewall and the model
# gateway, trusted, then what lies downstream. Below them the frame where agents
# run, with the record inside it; the outputs along the foot, right to left;
# the outer loop up the left-hand side, back into the orchestrator's place.
#
# The service is a decision, never a container: what the agent proposes (at
# Level 3, the orchestrator) comes into it, and the authorized scope goes down
# to the proxy that enforces it. At Level 3 it goes into one proxy, the
# nearer: with the service and the proxies' traffic both to the right and the
# line that splits the work above them, every route into the other proxy
# crosses a line, so that proxy's ring alone carries the mark, as in the lead
# author's drawing.
# ═════════════════════════════════════════════════════════════════════════════
class LV:
    # the top band
    REQ = (0, 4, 120, 48)                  # Level 3's requests
    REQ2 = (0, 0, 120, 76)                 # Level 2's request, event, schedule or ticket
    IN_Y = 26                              # where they come in
    ORCH = (150, 0, 452, 52)               # whoever orchestrates
    TX = 301                               # its centre, and the execution layer's
    CTX = (610, 0, 720, 60)
    CTX_Y, PROP_Y, ORCH_IN = 20, 40, 44    # context in, the proposal out, the outer loop in
    EXEC = (191, 88, 411, 148)
    AUTH = (460, 88, 720, 132)
    PROP_X = 576                           # the orchestrator's proposal drops into the service
    AGENT_PX, AGENT_PY = 430, 110          # the agent's own proposal, Levels 1 and 2
    LOOP_X, LOOP_Y, LOOP_RISE = 8, 100, 130
    # the frame, and its label in its top left-hand corner
    FRAME = (104, 164, 546, 516)
    LAB = (114, 182)
    # Level 3: one line splits the work; each task is a sandbox, beside it its
    # proxy, beneath it the monitoring agent that watches it
    ARM_Y = 192
    TOP, SH = 238, 114
    S = ((116, 230), (334, 448))
    LEG = 74                               # where the split lands, right of "Task n"
    PY, PH = 250, 76                       # the proxies, centred on the sandboxes
    P = ((248, 316), (466, 534))
    GRANT_DX, RING_DX = 26, 48             # on a proxy's top: the scope in, its ring
    M_Y = (370, 430)
    M = ((116, 246), (334, 464))
    EGRESS_Y = 444                         # the left-hand proxy's traffic, out to the bus
    # Levels 1 and 2: one sandbox where the tasks are, the agent harness in it
    SB = (116, 442, 238, 430)
    HARNESS = (121, 437, 268, 372)
    OBS = (116, 458, 530, 502)
    SIG = (0, 418, 92, 516)
    BUS = 566
    COL = (584, 720)
    COL_Y = (164, 236, 308)                # the firewall, the gateway, downstream
    OUT = (540, 600)
    PROD, DEPLOY, APPR, PR = (16, 142), (162, 272), (292, 458), (478, 596)
    KEY = (590, 392)
    LOOPB = 616                            # Levels 1 and 2: the outer loop's run home
    LEGEND_Y = 648


# The same words wherever the same part is drawn, set for the levels' narrower
# cards: the proxy's default-deny broken at its hyphen, the firewall's name in
# two lines and its line shortened from the lead author's ("approved, scanned
# components only") to what the column holds.
LV_PROXY_G = ["default-", "deny"]
SC_LINES = SC_NAME.rsplit(" ", 1)
SC_COL_G = ["approved, scanned"]
MG_G = ["approved models", "and budgets"]
DOWN_COL_G = ["source control,", "APIs, MCP servers"]
HARNESS_G = "the coding agent, configured by its profile"
HARNESS_PARTS = ["Skills", "Tools", "Hooks", "Context files"]   # the lead author's
# each task's own identity, and the profile and task scope the orchestrator
# proposed for it: what its heaviest line carries lands in every task
TASK_G = ["own identity,", "profile and", "task scope"]
TASK_NG = ["own identity, profile", "and task scope"]          # the phone's wider card
MON_G = ["watches work", "in progress"]


def lv_frame(f, label, gloss=(), s="old"):
    x0, y0, x1, y1 = LV.FRAME
    f.box(x0, y0, x1 - x0, y1 - y0, "zone", "frame")
    with f.at("newtext" if s == "new" else "old"):
        f.lab(*LV.LAB, label, "frame.l")
        for i, g in enumerate(gloss):
            f.gloss(LV.LAB[0], LV.LAB[1] + 14.5 * (i + 1), g, f"frame.g{i}")


def lv_service(f):
    """The runtime authorization service, beside the execution layer, and the
    scope it authorizes, down into the proxy beneath it; its label sits just
    under the service, against its own line."""
    ax0, ay0, ax1, ay1 = LV.AUTH
    f.node(ax0, ay0, ax1 - ax0, ay1 - ay0, "Runtime authorization service", [AUTH_G],
           kind="guard", num=BN[IAM], tag="auth")
    gx = LV.P[1][0] + LV.GRANT_DX
    f.link([(gx, ay1), (gx, LV.PY)], "grant", tag="grant")
    f.gloss(gx + 8, ay1 + 14, "authorized scope", "grant.l")


def lv_proxy(f, i, s="old", stack=False):
    """A proxy: the network's mark on its corner and, on its top, where the
    authorized scope comes in, identity and access's ring. Behind it, at
    Level 2, a stack: one per run."""
    px0, px1 = LV.P[i]
    with f.at(s):
        if stack:
            for d in (6, 3):
                f.ghost(px0 + d, LV.PY + d, px1 - px0, LV.PH, f"pghost{d}", "proxy")
        f.node(px0, LV.PY, px1 - px0, LV.PH, ["Egress", "proxy"], LV_PROXY_G,
               kind="guardfill" if stack else "guard", num=BN[NETWORK], tag=f"proxy{i}")
    f.badge(px0 + LV.RING_DX, LV.PY, BN[IAM], f"proxy{i}", light=True)


def lv_column(f, s_gateway="old", s_pr="old"):
    """What the proxies reach, under the service: the supply chain firewall
    and the model gateway, trusted, then what lies downstream, fed by one bus
    that also carries the pull request the agent opens down to the outputs.
    Returns where each branch leaves the bus."""
    cx0, cx1 = LV.COL
    hs = (card_h(SC_COL_G, SC_LINES), card_h(MG_G), card_h(DOWN_COL_G))
    f.node(cx0, LV.COL_Y[0], cx1 - cx0, hs[0], SC_LINES, SC_COL_G, kind="guard",
           num=BN[SUPPLY], tag="sc")
    with f.at(s_gateway):
        f.node(cx0, LV.COL_Y[1], cx1 - cx0, hs[1], "Model gateway", MG_G, kind="guard", tag="mg")
    f.node(cx0, LV.COL_Y[2], cx1 - cx0, hs[2], "Downstream", DOWN_COL_G, tag="down")
    ys = [y + h / 2 for y, h in zip(LV.COL_Y, hs)]
    pm = LV.PY + LV.PH / 2
    f.link([(LV.P[1][1], pm), (LV.BUS, pm)], head=False, tag="bus.in1", group="bus")
    f.link([(LV.BUS, ys[0]), (LV.BUS, ys[-1])], head=False, tag="bus", group="bus")
    for i, y in enumerate(ys):
        f.link([(LV.BUS, y), (cx0, y)], tag=f"bus.{i}", group="bus")
    with f.at(s_pr):
        f.link([(LV.BUS, ys[-1]), (LV.BUS, LV.OUT[0])], tag="bus.pr", group="bus")
    # its verb, the lead author's: the agent opens it, through the proxy
    with f.at("newtext" if s_pr == "new" else "old"):
        f.gloss(LV.BUS + 8, LV.OUT[0] - 10, "opens", "bus.pr.l")
    return ys


def lv_out(f, slot, name, gloss, tag):
    o0, o1 = LV.OUT
    f.node(slot[0], o0, slot[1] - slot[0], o1 - o0, name, gloss, tag=tag)


def lv_then(f, a, b, tag):
    """Outputs run right to left: from a's left edge to b's right."""
    om = mid(LV.OUT)
    f.link([(a[0], om), (b[1], om)], tag=tag)


def lv_home(f, start):
    """The outer loop: from `start` (points to the left-hand rail) up the
    rail, under what starts the work, and into the orchestrator's place."""
    f.link(start + [(LV.LOOP_X, LV.LOOP_Y), (LV.LOOP_RISE, LV.LOOP_Y),
                    (LV.LOOP_RISE, LV.ORCH_IN), (LV.ORCH[0], LV.ORCH_IN)], "loop", tag="outer")


def lv_home_from_pr(f, s="old"):
    """Levels 1 and 2: the outer loop leaves the pull request's foot and runs
    home under the outputs. At Level 1 nothing comes in beside it, so it
    turns straight into the developer's side."""
    x = mid(LV.PR)
    pts = [(x, LV.OUT[1]), (x, LV.LOOPB), (LV.LOOP_X, LV.LOOPB)]
    with f.at(s):
        if f.level == 1:
            f.link(pts + [(LV.LOOP_X, LV.ORCH_IN), (LV.ORCH[0], LV.ORCH_IN)], "loop",
                   tag="outer")
        else:
            lv_home(f, pts)


def lv_loop_labels(f, lines, s_label="old", s_gloss="new"):
    """Levels 1 and 2: the outer loop's label in the corner its rail and run
    make, where Level 3 draws production."""
    y = LV.OUT[0] + 22
    with f.at("newtext" if s_label == "new" else "old"):
        f.lab(LV.PROD[0] + 2, y, "outer loop", "outer.l")
    with f.at("newtext" if s_gloss == "new" else "old"):
        for i, s_ in enumerate(lines):
            f.gloss(LV.PROD[0] + 2, y + 16 + 14.5 * i, s_, f"outer.g{i}")


def lv_record(f, gloss, s="old"):
    x0, y0, x1, y1 = LV.OBS
    gx = record(f, x0, y0, x1, y1)
    with f.at("newtext" if s == "new" else "old"):
        f.gloss(gx, y0 + 28, gloss, "obs.g")


def lv_sandbox(f, label, s="old", stack=False, s_harness="old", s_loop="old"):
    """Levels 1 and 2: one sandbox where Level 3's tasks are, holding the agent
    harness and what it is built from, its inner loop under it. At Level 2 it
    is a stack, a fresh one per run."""
    x0, x1, y0, y1 = LV.SB
    with f.at(s):
        if stack:
            for d in (6, 3):
                f.ghost(x0 + d, y0 + d, x1 - x0, y1 - y0, f"ghost{d}", "sandbox")
        f.box(x0, y0, x1 - x0, y1 - y0, "sandbox", "sbx")
        f.badge(x0, y0, BN[SANDBOX], "sbx")
    f.lab(x0 + PAD + 5, y0 + 20, label, "sbx.l")
    hx0, hx1, hy0, hy1 = LV.HARNESS
    with f.at(s_harness):
        f.node(hx0, hy0, hx1 - hx0, hy1 - hy0, "Agent harness", [HARNESS_G], kind="agent",
               tag="harness")
    # what the harness is built from, as the lead author draws it: four parts,
    # each named, set on the plate so they read as parts, not as more agents,
    # and new where the harness is
    cw = (hx1 - hx0 - 2 * PAD - 10) / 2
    with f.at(s_harness):
        for i, n_ in enumerate(HARNESS_PARTS):
            r, c = divmod(i, 2)
            cx, cy = hx0 + PAD + c * (cw + 10), hy0 + 46 + r * 28
            f.box(cx, cy, cw, 22, "card", f"part{i}", fill=PLATE)
            f.name(cx + PAD, cy + 15.5, n_, f"part{i}.n")
    gy = y1 - 28
    f.loop_glyph(x0 + PAD + 11, gy - 4, "sbx.loop")
    with f.at("newtext" if s_loop == "new" else "old"):
        f.gloss(x0 + PAD + 26, gy, "inner loop, until it passes", "sbx.lp")


def lv_agent_proposes(f):
    """Levels 1 and 2: the agent proposes the scope it needs, as in Figure 2,
    from its sandbox up into the service's side, its label set against its
    own line, well clear of the line that starts the agent: here only the
    agent proposes."""
    x, y = LV.AGENT_PX, LV.AGENT_PY
    f.link([(x, LV.SB[2]), (x, y), (LV.AUTH[0], y)], tag="propose")
    gloss_to(f, x - 8, LV.LAB[1] + 22, "proposes scope", "propose.l")


def lv_traffic(f, x0):
    """The sandbox's requests, out to the proxy beside it."""
    pm = LV.PY + LV.PH / 2
    f.link([(x0, pm), (LV.P[1][0], pm)], tag="traffic")


# ── Level 1 ──────────────────────────────────────────────────────────────────
# The developer orchestrates and, through the agent harness, is the execution
# layer too, so the execution layer's place is empty: the developer's line
# runs straight down into the sandbox. The sandbox shows what is in the box.
# Against Figure 2, the machine it runs on and the inner loop are new too.
def lv_level1(f):
    lv_frame(f, "Developer’s machine", ["or a remote environment"], s="new")
    ox0, oy0, ox1, oy1 = LV.ORCH
    with f.at("new"):
        f.node(ox0, oy0, ox1 - ox0, oy1 - oy0, "Developer", ["kicks off each run"], tag="dev")
        f.link([(LV.TX, oy1), (LV.TX, LV.SB[2])], tag="directs")
    lv_service(f)
    lv_sandbox(f, "Sandbox", s_harness="new", s_loop="new")
    lv_agent_proposes(f)
    lv_proxy(f, 1)
    lv_traffic(f, LV.SB[1])
    lv_column(f, s_gateway="new", s_pr="new")
    with f.at("new"):
        lv_out(f, LV.PR, "Pull request", ["reviewed by", "the developer"], "pr")
    lv_home_from_pr(f, "new")
    # both halves of the outer loop: the next run, and the configuration the
    # harness is built from
    lv_loop_labels(f, ["the developer drives the next run", "and updates the configuration"],
                   "new")
    lv_record(f, "harness logs, identity and proxy records")


# ── Level 2 ──────────────────────────────────────────────────────────────────
# A workflow takes the developer's place, on a durable execution layer that
# takes the developer's line: a fresh sandbox per run, the same harness in it.
def lv_level2(f):
    lv_frame(f, "The factory", ["a shared service"], s="new")
    ox0, oy0, ox1, oy1 = LV.ORCH
    rx0, ry0, rx1, ry1 = LV.REQ2
    ex0, ey0, ex1, ey1 = LV.EXEC
    with f.at("new"):
        f.node(rx0, ry0, rx1 - rx0, ry1 - ry0, "Request", ["or an event,", "a schedule",
                                                           "or a ticket"], tag="req")
        f.link([(rx1, LV.IN_Y), (ox0, LV.IN_Y)], tag="req.in")
        f.node(ox0, oy0, ox1 - ox0, oy1 - oy0, "Workflow", ["predefined steps for each request"],
               tag="wf")
        f.link([(LV.TX, oy1), (LV.TX, ey0)], tag="schedule")
    with f.at("newtext"):
        f.gloss(LV.TX + 8, ey0 - 14, "schedules runs", "schedule.l")
    with f.at("new"):
        f.node(ex0, ey0, ex1 - ex0, ey1 - ey0, "Durable execution layer", EXEC_G, tag="exec")
    f.link([(LV.TX, ey1), (LV.TX, LV.SB[2])], tag="directs")
    lv_service(f)
    lv_sandbox(f, "Sandbox per run", s="new", stack=True)
    lv_agent_proposes(f)
    lv_proxy(f, 1, s="new", stack=True)
    lv_traffic(f, LV.SB[1])
    lv_column(f)
    # the pull request is Level 1's, its words changed; what follows it is new
    lv_out(f, LV.PR, "Pull request", ["reviewed", "until ready"], "pr")
    with f.at("new"):
        lv_out(f, LV.APPR, "Approval", APPROVAL_G, "appr")
        lv_out(f, LV.DEPLOY, "Merge", ["approved", "changes"], "merge")
        lv_then(f, LV.PR, LV.APPR, "out.pr")
        lv_then(f, LV.APPR, LV.DEPLOY, "out.appr")
    lv_home_from_pr(f)
    lv_loop_labels(f, ["review feedback", "drives the next run"])
    lv_record(f, "all four boundaries’ records, linked by run", "new")


# ── Level 3 ──────────────────────────────────────────────────────────────────
# What Level 3 adds is who runs the show. The orchestrator agent takes the
# workflow's place, fed by requests, by context and, round the outer loop, by
# signals, and everything it does leaves it as a line: it schedules the tasks
# it divides the work into, down to the durable execution layer, and proposes
# each task's profile and scope to the authorization service, the heaviest line
# in the figure. The execution layer's one line splits in the factory, each
# part to its own agent in its own sandbox, behind its own proxy, watched by a
# monitoring agent; the outputs run on to production, whose incidents come back
# as signals.
def lv_level3(f):
    lv_frame(f, "The factory")
    ox0, oy0, ox1, oy1 = LV.ORCH
    rx0, ry0, rx1, ry1 = LV.REQ
    cx0, cy0, cx1, cy1 = LV.CTX
    ex0, ey0, ex1, ey1 = LV.EXEC
    ax0, ay0 = LV.AUTH[:2]
    f.node(rx0, ry0, rx1 - rx0, ry1 - ry0, "Requests", ["people, tickets"], tag="req")
    f.link([(rx1, LV.IN_Y), (ox0, LV.IN_Y)], tag="req.in")
    with f.at("new"):
        f.node(ox0, oy0, ox1 - ox0, oy1 - oy0, "Orchestrator agent",
               ["plans the work and divides it into tasks"], kind="agent", tag="orch")
        f.node(cx0, cy0, cx1 - cx0, cy1 - cy0, "Context", ["tickets, code,", "conversations"],
               tag="ctx")
        f.link([(cx0, LV.CTX_Y), (ox1, LV.CTX_Y)], tag="ctx.in")
        # it schedules the tasks, down to the execution layer, a card of its own
        f.link([(LV.TX, oy1), (LV.TX, ey0)], tag="schedule")
        # and proposes each one's profile and scope, which only the service
        # authorizes
        f.link([(ox1, LV.PROP_Y), (LV.PROP_X, LV.PROP_Y), (LV.PROP_X, ay0)], tag="propose",
               heavy=True)
    with f.at("newtext"):
        f.gloss(LV.TX + 8, ey0 - 14, "schedules tasks", "schedule.l")
        for i, s_ in enumerate(("proposes profile", "and task scope")):
            gloss_to(f, LV.PROP_X - 8, ay0 - 22 + 14.5 * i, s_, f"propose.l{i}")
    f.node(ex0, ey0, ex1 - ex0, ey1 - ey0, "Durable execution layer", EXEC_G, tag="exec")
    lv_service(f)

    # ── the factory: one line splits the work, each part to its own agent ──
    legs = [s[0] + LV.LEG for s in LV.S]
    with f.at("new"):
        f.link([(LV.TX, ey1), (LV.TX, LV.ARM_Y)], head=False, tag="split", group="split",
               dot=True)
        for i, lx in enumerate(legs):
            f.link([(LV.TX, LV.ARM_Y), (lx, LV.ARM_Y), (lx, LV.TOP)], tag=f"split{i}",
                   group="split")
    with f.at("newtext"):
        c = mid(legs)
        for i, s_ in enumerate(("each part to its own agent,", "with narrowed authority")):
            f.gloss(c - TINT_W[f"serif|400|{f.gs:g}|{s_}"] / 2, LV.ARM_Y + 18 + 14.5 * i, s_,
                    f"split.l{i}")
    for i, (sx0, sx1) in enumerate(LV.S):
        f.box(sx0, LV.TOP, sx1 - sx0, LV.SH, "sandbox", f"sbx{i}")
        f.badge(sx0, LV.TOP, BN[SANDBOX], f"sbx{i}")
        tx0 = sx0 + PAD + 4
        f.lab(tx0, LV.TOP + 20, f"Task {i + 1}", f"sbx{i}.l")
        f.name(tx0, LV.TOP + 39, "Coding agent", f"sbx{i}.n")
        for j, g in enumerate(TASK_G):
            f.gloss(tx0, LV.TOP + 55 + 14.5 * j, g, f"sbx{i}.g{j}")
        f.loop_glyph(sx0 + PAD + 11, LV.TOP + 100, f"sbx{i}.loop")
        f.gloss(sx0 + PAD + 26, LV.TOP + 104, "inner loop", f"sbx{i}.lp")
        lv_proxy(f, i)
    pm = LV.PY + LV.PH / 2
    f.link([(LV.S[0][1], pm), (LV.P[0][0], pm)], tag="traffic0")
    lv_traffic(f, LV.S[1][1])
    with f.at("new"):
        for i, (mx0, mx1) in enumerate(LV.M):
            f.node(mx0, LV.M_Y[0], mx1 - mx0, LV.M_Y[1] - LV.M_Y[0], "Monitoring agent", MON_G,
                   kind="agent", tag=f"mon{i}")
            wx = mid(LV.S[i])
            f.link([(wx, LV.M_Y[0]), (wx, LV.TOP + LV.SH)], "watch", tag=f"watch{i}")
    lv_record(f, "telemetry and evals across all runs", "new")
    lv_column(f)
    # the left-hand proxy's traffic: down between the monitoring agents and
    # along over the record, joining the same bus (every route in above the
    # Downstream branch crosses the other task)
    dx = mid(LV.P[0])
    f.link([(dx, LV.PY + LV.PH), (dx, LV.EGRESS_Y), (LV.BUS, LV.EGRESS_Y)], head=False,
           tag="bus.in0", group="bus", dot=True)

    # ── what leaves, right to left, and the outer loop back to the orchestrator ──
    lv_out(f, LV.PR, "Pull request", ["reviewed", "until ready"], "pr")
    lv_out(f, LV.APPR, "Approval", APPROVAL_G, "appr")
    lv_then(f, LV.PR, LV.APPR, "out.pr")
    sx0, sy0, sx1, sy1 = LV.SIG
    ob = LV.OBS
    with f.at("new"):
        lv_out(f, LV.DEPLOY, "Deploy", ["merged, can be", "rolled back"], "deploy")
        lv_out(f, LV.PROD, "Production", ["emits incidents", "and metrics"], "prod")
        lv_then(f, LV.APPR, LV.DEPLOY, "out.appr")
        lv_then(f, LV.DEPLOY, LV.PROD, "out.deploy")
        f.node(sx0, sy0, sx1 - sx0, sy1 - sy0, "Signals",
               ["incidents,", "scanners,", "monitoring,", "evals"], tag="sig")
        ix = mid((LV.PROD[0], sx1))
        f.link([(ix, LV.OUT[0]), (ix, sy1)], "loop", tag="incidents")
        f.link([(ob[0], mid((ob[1], ob[3]))), (sx1, mid((ob[1], ob[3])))], "loop", tag="evals")
        lv_home(f, [(LV.LOOP_X, sy0)])
    f.lab(LV.LOOP_X + 10, LV.LOOP_Y + 24, "outer loop", "outer.l")
    with f.at("newtext"):
        f.gloss(LV.LOOP_X + 10, LV.LOOP_Y + 38.5, "new work", "outer.g")


PREV = {1: "as in Figure 2", 2: "as at Level 1", 3: "as at Level 2"}


def build_level(n):
    f = CF(f"sf{n + 2}", W, 800, CAPTION[n + 2], ALT[n + 2], level=n)
    {1: lv_level1, 2: lv_level2, 3: lv_level3}[n](f)
    delta_key(f, LV.KEY[0], LV.KEY[1], PREV[n])
    legend(f, 0, LV.LEGEND_Y, W)
    f.set_height(LV.LEGEND_Y + 8)
    f.write(f"figure-{n + 2}")


# ── the phones' drawings, on a 360-unit content width ─────────────────────────
NW = 360


# ── the levels on a phone: the same story in one column ──────────────────────
class NV:
    """The levels on a phone: the wide skeleton's story in one column. The
    orchestrator's place across the top; beneath it, side by side as wide,
    the execution layer's place and the authorization service; then the
    frame, the agents' sandboxes on the left with each one's proxy beside
    it; then what the proxies reach, the outputs, and the outer loop up the
    left-hand edge."""
    RAIL = 4                               # the outer loop
    X0, X1 = 24, 352
    HALF = 146                             # a card in the top band's left half
    EXEC = (24, 176)
    AUTH = (188, 352)
    IN_X = 60                              # lines down the left-hand side: in, schedules
    CTX_X = 270
    DROP_X = 36                            # the execution layer's line, down into the frame
    PROP_X = 330                           # the orchestrator's proposal
    AGENT_PX = 220                         # the agent's own, Levels 1 and 2
    FRAME = (14, 334)
    S = (54, 238)
    P = (256, 324)
    GRANT_X = 282
    BUS = 352
    DEST = (24, 332)


def narrow_task_sandbox(f, y, i):
    """Level 3's task on a phone: its sandbox, its proxy beside it; returns
    the sandbox's height."""
    sx0, sx1 = NV.S
    h = 116
    f.box(sx0, y, sx1 - sx0, h, "sandbox", f"sbx{i}")
    f.badge(sx0, y, BN[SANDBOX], f"sbx{i}")
    tx = sx0 + PAD + 4
    f.lab(tx, y + 20, f"Task {i + 1} sandbox", f"sbx{i}.l")
    f.name(tx, y + 40, "Coding agent", f"sbx{i}.n")
    for j, g in enumerate(TASK_NG):
        f.gloss(tx, y + 56 + 14.5 * j, g, f"sbx{i}.g{j}")
    f.loop_glyph(sx0 + PAD + 11, y + 88, f"sbx{i}.loop")
    f.gloss(sx0 + PAD + 26, y + 92, "inner loop,", f"sbx{i}.lp0")
    f.gloss(sx0 + PAD + 26, y + 106.5, "until it passes", f"sbx{i}.lp1")
    return h


def narrow_harness_sandbox(f, y, label, s="old", stack=False, s_harness="old", s_loop="old"):
    """Levels 1 and 2 on a phone: the sandbox and the agent harness in it,
    its parts in a column; returns the sandbox's height."""
    sx0, sx1 = NV.S
    h = 268
    with f.at(s):
        if stack:
            for d in (6, 3):
                f.ghost(sx0 + d, y + d, sx1 - sx0, h, f"ghost{d}", "sandbox")
        f.box(sx0, y, sx1 - sx0, h, "sandbox", "sbx")
        f.badge(sx0, y, BN[SANDBOX], "sbx")
    f.lab(sx0 + PAD + 4, y + 20, label, "sbx.l")
    hx0, hx1, hy0 = sx0 + 6, sx1 - 6, y + 30
    with f.at(s_harness):
        f.node(hx0, hy0, hx1 - hx0, 190, "Agent harness",
               ["the coding agent,", "configured by", "its profile"], kind="agent", tag="harness")
        for i, n_ in enumerate(HARNESS_PARTS):
            cy = hy0 + 76 + 28 * i
            f.box(hx0 + PAD, cy, hx1 - hx0 - 2 * PAD, 22, "card", f"part{i}", fill=PLATE)
            f.name(hx0 + 2 * PAD, cy + 15.5, n_, f"part{i}.n")
    f.loop_glyph(sx0 + PAD + 11, y + 236, "sbx.loop")
    with f.at("newtext" if s_loop == "new" else "old"):
        f.gloss(sx0 + PAD + 26, y + 240, "inner loop,", "sbx.lp0")
        f.gloss(sx0 + PAD + 26, y + 254.5, "until it passes", "sbx.lp1")
    return h


def narrow_proxy(f, y, i, s="old", stack=False):
    """A proxy on a phone, beside its sandbox, centred on `y`; returns its top."""
    px0, px1 = NV.P
    py = y - LV.PH / 2
    with f.at(s):
        if stack:
            for d in (6, 3):
                f.ghost(px0 + d, py + d, px1 - px0, LV.PH, f"pghost{d}", "proxy")
        f.node(px0, py, px1 - px0, LV.PH, ["Egress", "proxy"], LV_PROXY_G,
               kind="guardfill" if stack else "guard", num=BN[NETWORK], tag=f"proxy{i}")
    f.badge(px0 + LV.RING_DX, py, BN[IAM], f"proxy{i}", light=True)
    f.link([(NV.S[1], y), (px0, y)], tag=f"traffic{i}")
    f.link([(px1, y), (NV.BUS, y)], head=False, tag=f"bus.in{i}", group="bus")
    return py


def narrow_level(n):
    f = CF(f"sf{n + 2}n", NW, 2400, CAPTION[n + 2], ALT[n + 2], narrow=True, level=n)
    X0, X1 = NV.X0, NV.X1
    y = 10
    # ── the orchestrator's place, and what comes into it ──
    if n == 1:
        with f.at("new"):
            f.node(X0, y, X1 - X0, 44, "Developer", ["kicks off each run"], tag="dev")
        oy = y
    elif n == 2:
        with f.at("new"):
            f.node(X0, y, X1 - X0, 44, "Request", ["or an event, a schedule or a ticket"],
                   tag="req")
            f.link([(NV.IN_X, y + 44), (NV.IN_X, y + 84)], tag="req.in")
            f.node(X0, y + 84, X1 - X0, 44, "Workflow", ["predefined steps for each request"],
                   tag="wf")
        oy = y + 84
    else:
        f.node(X0, y, NV.HALF, 44, "Requests", ["people, tickets"], tag="req")
        f.link([(NV.IN_X, y + 44), (NV.IN_X, y + 84)], tag="req.in")
        with f.at("new"):
            f.node(NV.AUTH[0], y, X1 - NV.AUTH[0], 60, "Context", ["tickets, code,", "conversations"],
                   tag="ctx")
            f.link([(NV.CTX_X, y + 60), (NV.CTX_X, y + 84)], tag="ctx.in")
            f.node(X0, y + 84, X1 - X0, 44, "Orchestrator agent",
                   ["plans the work and divides it into tasks"], kind="agent", tag="orch")
        oy = y + 84
    o_mid, ob = oy + 22, oy + 44
    # ── beneath it, side by side: the execution layer and the service ──
    ey = ob + 44
    if n > 1:
        with f.at("new"):
            f.link([(NV.IN_X, ob), (NV.IN_X, ey)], tag="schedule")
        with f.at("newtext"):
            f.gloss(NV.IN_X + 8, ob + 26, "schedules runs" if n == 2 else "schedules tasks",
                    "schedule.l")
        with f.at("new" if n == 2 else "old"):
            f.node(NV.EXEC[0], ey, NV.EXEC[1] - NV.EXEC[0], 92, ["Durable execution", "layer"],
                   ["CI/CD or a step", "runner that starts", "each agent"], tag="exec")
        drop_from = ey + 92
    else:
        drop_from = ob
    if n == 3:
        with f.at("new"):
            f.link([(NV.PROP_X, ob), (NV.PROP_X, ey)], tag="propose", heavy=True)
        with f.at("newtext"):
            for i, s_ in enumerate(("proposes profile", "and task scope")):
                f.gloss(NV.PROP_X - 8 - TINT_W[f"serif|400|{f.gs:g}|{s_}"], ob + 18 + 14.5 * i, s_,
                        f"propose.l{i}")
    bh = 76
    f.node(NV.AUTH[0], ey, NV.AUTH[1] - NV.AUTH[0], bh, ["Runtime authorization", "service"],
           ["authorizes each", "task’s scope"], kind="guard", num=BN[IAM], tag="auth")
    sb = ey + bh
    for i, s_ in enumerate(("authorized", "scope")):
        f.gloss(NV.GRANT_X + 8, sb + 18 + 14.5 * i, s_, f"grant.l{i}")
    # ── the frame ──
    # at Levels 1 and 2, room above it for the agent's proposal's label,
    # clear of the execution layer's foot
    fy0 = sb + (66 if n < 3 else 40)
    fx0, fx1 = NV.FRAME
    lx = NV.S[0]
    if n == 1:
        with f.at("newtext"):
            f.lab(lx, fy0 + 22, "Developer’s machine", "frame.l")
            f.gloss(lx, fy0 + 36.5, "or a remote environment", "frame.g0")
    else:
        with f.at("newtext" if n == 2 else "old"):
            f.lab(lx, fy0 + 22, "The factory", "frame.l")
            if n == 2:
                f.gloss(lx, fy0 + 36.5, "a shared service", "frame.g0")
    if n < 3:
        sy = fy0 + 50
        with f.at("new" if n == 1 else "old"):
            f.link([(NV.DROP_X, drop_from), (NV.DROP_X, sy + 40), (NV.S[0], sy + 40)],
                   tag="directs")
        sh = narrow_harness_sandbox(f, sy, "Sandbox" if n == 1 else "Sandbox per run",
                                    s="new" if n == 2 else "old", stack=n == 2,
                                    s_harness="new" if n == 1 else "old",
                                    s_loop="new" if n == 1 else "old")
        # the agent proposes the scope it needs, up into the service; its
        # label hugs its own line, under the execution layer's foot
        f.link([(NV.AGENT_PX, sy), (NV.AGENT_PX, sb)], tag="propose")
        for i, s_ in enumerate(("proposes", "scope")):
            gloss_to(f, NV.AGENT_PX - 8, sb + 40 + 14.5 * i, s_, f"propose.l{i}")
        mids = [sy + sh / 2]
        py = narrow_proxy(f, mids[0], 0, s="new" if n == 2 else "old", stack=n == 2)
        grant_to = py
        y = sy + sh + (6 if n == 2 else 0) + 18
    else:
        with f.at("newtext"):
            for i, s_ in enumerate(("each part to its own agent,", "with narrowed authority")):
                f.gloss(lx, fy0 + 40 + 14.5 * i, s_, f"split.l{i}")
        y = fy0 + 70
        mids, branch = [], []
        for i in range(2):
            sh = narrow_task_sandbox(f, y, i)
            mids.append(y + sh / 2)
            branch.append(y + 40)
            py = narrow_proxy(f, mids[-1], i)
            if i == 0:
                grant_to = py
            my = y + sh + 20
            with f.at("new"):
                f.node(NV.S[0], my, NV.S[1] - NV.S[0], 44, "Monitoring agent",
                       ["watches work in progress"], kind="agent", tag=f"mon{i}")
                wx = mid(NV.S)
                f.link([(wx, my), (wx, y + sh)], "watch", tag=f"watch{i}")
            y = my + 44 + 24
        y -= 6
        with f.at("new"):
            f.link([(NV.DROP_X, drop_from), (NV.DROP_X, branch[-1])], head=False, tag="split",
                   group="split")
            for i, by in enumerate(branch):
                f.link([(NV.DROP_X, by), (NV.S[0], by)], tag=f"split{i}", group="split")
    f.link([(NV.GRANT_X, sb), (NV.GRANT_X, grant_to)], "grant", tag="grant")
    # the record, inside the frame
    obs = {1: "harness logs, identity and proxy records",
           2: "all four boundaries’ records, by run",
           3: "telemetry and evals across all runs"}[n]
    record(f, X0, y, fx1 - 10, y + 48, two=True)
    with f.at("newtext" if n > 1 else "old"):
        f.gloss(X0 + PAD, y + 39, obs, "obs.g")
    if n == 3:
        # evals come back too: the record's dashed line joins the outer loop
        with f.at("new"):
            f.link([(X0, y + 24), (NV.RAIL, y + 24)], "loop", head=False, tag="evals", dot=True)
    fy1 = y + 48 + 12
    f.box(fx0, fy0, fx1 - fx0, fy1 - fy0, "zone", "frame")
    # ── what the proxies reach, and the pull request, down the bus ──
    y = fy1 + 24
    ys = []
    for i, (nm, g, kind, tag) in enumerate([(SC_NAME, SC_COL_G, "guard", "sc"),
                                            ("Model gateway", [" ".join(MG_G)], "guard", "mg"),
                                            ("Downstream", [" ".join(DOWN_COL_G)], "card", "down")]):
        with f.at("new" if (n == 1 and tag == "mg") else "old"):
            f.node(NV.DEST[0], y, NV.DEST[1] - NV.DEST[0], 44, nm, g, kind=kind,
                   num=BN[SUPPLY] if tag == "sc" else None, tag=tag)
        ys.append(y + 22)
        y += 44 + STACK
    # the gap above the pull request: at Levels 1 and 2 the outer loop
    # leaves through it, with its label
    y += (64 if n < 3 else 30) - STACK
    pr_mid = y + 23
    f.link([(NV.BUS, mids[0]), (NV.BUS, ys[-1])], head=False, tag="bus", group="bus")
    for i, yy in enumerate(ys):
        f.link([(NV.BUS, yy), (NV.DEST[1], yy)], tag=f"bus.{i}", group="bus")
    with f.at("new" if n == 1 else "old"):
        f.link([(NV.BUS, ys[-1]), (NV.BUS, pr_mid), (NV.DEST[1], pr_mid)], tag="bus.pr",
               group="bus")
    with f.at("newtext" if n == 1 else "old"):
        gloss_to(f, NV.BUS - 10, pr_mid - 23 - 8, "opens", "bus.pr.l")
    # ── the outputs, top to bottom, and the outer loop home ──
    outs = {1: [("Pull request", ["reviewed by the developer"], 1)],
            2: [("Pull request", ["reviewed until ready"], 1),
                ("Approval", APPROVAL_G, 2),
                ("Merge", ["approved changes"], 2)],
            3: [("Pull request", ["reviewed until ready"], 2),
                ("Approval", APPROVAL_G, 2),
                ("Deploy", ["merged, can be rolled back"], 3),
                ("Production", ["emits incidents and metrics"], 3)]}[n]
    for i, (nm, g, since) in enumerate(outs):
        with f.at("new" if since == n else "old"):
            f.node(X0, y, NV.DEST[1] - X0, 46, nm, g, tag=f"out{i}")
        y += 46
        if i < len(outs) - 1:
            with f.at("new" if outs[i + 1][2] == n else "old"):
                f.link([(NV.IN_X, y), (NV.IN_X, y + 22)], tag=f"o{i}")
            y += 22
    if n < 3:
        # the loop leaves the pull request's top and turns for the rail in
        # the gap above it; its label sits beside it, as at Level 3
        pt = pr_mid - 23
        with f.at("new" if n == 1 else "old"):
            f.link([(NV.IN_X, pt), (NV.IN_X, pt - 54), (NV.RAIL, pt - 54), (NV.RAIL, o_mid),
                    (X0, o_mid)], "loop", tag="outer")
        with f.at("newtext" if n == 1 else "old"):
            f.lab(NV.IN_X + 10, pt - 38, "outer loop", "outer.l")
        lines = {1: ["the developer drives the next run", "and updates the configuration"],
                 2: ["review feedback drives the next run"]}[n]
        with f.at("newtext"):
            for i, s_ in enumerate(lines):
                f.gloss(NV.IN_X + 10, pt - 23.5 + 14.5 * i, s_, f"outer.g{i}")
    else:
        # production's signals, and from them the loop home
        sy0 = y + 40
        with f.at("new"):
            f.link([(NV.IN_X, y), (NV.IN_X, sy0)], "loop", tag="incidents")
            f.node(X0, sy0, NV.DEST[1] - X0, 44, "Signals",
                   ["incidents, scanners, monitoring, evals"], tag="sig")
            f.link([(X0, sy0 + 22), (NV.RAIL, sy0 + 22), (NV.RAIL, o_mid), (X0, o_mid)], "loop",
                   tag="outer")
        f.lab(NV.IN_X + 10, y + 18, "outer loop", "outer.l")
        with f.at("newtext"):
            f.gloss(NV.IN_X + 10, y + 32.5, "new work", "outer.g")
        y = sy0 + 44
    # ── the keys ──
    f.rule(y + 14, X0, X1)
    y = key_grid(f, X0, y + 36)
    delta_key(f, X0, y + 14, PREV[n])
    f.set_height(y + 14 + 19 + 6)
    f.write(f"figure-{n + 2}-narrow")


# ═════════════════════════════════════════════════════════════════════════════
# Figure 1 — work loops until it passes, and problems feed back to design
# ═════════════════════════════════════════════════════════════════════════════


def figure1():
    f = SF("sf1", W, 340, CAPTION[1], ALT[1])
    y0, h = 40, 64
    ym = y0 + h / 2
    f.node(28, y0, 96, h, "Inputs", ["prompt, PRD", "or ticket"], tag="in")
    f.node(148, y0, 114, h, "Design", ["sets limits", "in advance"], tag="design")
    f.link([(124, ym), (148, ym)], tag="a1")
    gx0, gx1 = 288, W
    f.box(gx0, 10, gx1 - gx0, 152, "zone", "inner")
    f.lab(gx0 + 12, 28, "Inner loop", "inner.l")
    f.gloss(gx0 + 12 + f.width("Inner loop", "label") + 8, 28, "repeats until the work passes",
            "inner.g")
    gap = 28
    cw = (gx1 - gx0 - 24 - 2 * gap) / 3
    xs = [gx0 + 12 + i * (cw + gap) for i in range(3)]
    for x, (n, g) in zip(xs, [("Assemble", ["what the task", "needs"]),
                              ("Build", ["the change, in", "a sandbox"]),
                              ("Verify", ["against the", "standards"])]):
        f.node(x, y0, cw, h, n, g, tag=n.lower())
    f.link([(262, ym), (xs[0], ym)], tag="a2")
    for a, b in zip(xs, xs[1:]):
        f.link([(a + cw, ym), (b, ym)], tag=f"s{int(a)}")
    ly = y0 + h + 24
    f.link([(mid((xs[2], xs[2] + cw)), y0 + h), (mid((xs[2], xs[2] + cw)), ly),
            (mid((xs[0], xs[0] + cw)), ly), (mid((xs[0], xs[0] + cw)), y0 + h)], tag="again")
    f.gloss(xs[0], 186, "Assembled from agents and harnesses, models, skills,", "blocks1")
    f.gloss(xs[0], 200.5, "tools and MCP servers, dependencies and blueprints", "blocks2")
    # out of the loop, right to left: review → deploy → production
    b0, rw, bg = 256, 140, 36
    rx = [W - rw, W - 2 * rw - bg, W - 3 * rw - 2 * bg]
    bm = b0 + h / 2
    f.node(rx[0], b0, rw, h, "Review", ["of the change"], tag="review")
    f.node(rx[1], b0, rw, h, "Deploy", ["under approval", "policy"], tag="deploy")
    f.node(rx[2], b0, rw, h, "Production", ["sends back signals", "such as incidents"],
           tag="prod")
    vx = mid((rx[0], rx[0] + rw)) + 20
    f.link([(vx, 162), (vx, b0)], tag="passes")
    f.gloss(vx + 8, 214, "passes", "passes.l")
    f.link([(rx[0], bm), (rx[1] + rw, bm)], tag="b1")
    f.link([(rx[1], bm), (rx[2] + rw, bm)], tag="b2")
    # the outer loop collects what review and production learn and carries it
    # back to design; production's signals go round the left to start new work
    cy = 232
    dx = mid((148, 262))
    rvx = rx[0] + 24
    f.link([(rvx, b0), (rvx, cy), (dx, cy), (dx, y0 + h)], "loop", tag="outer", group="outer")
    f.link([(rx[2] + 50, b0), (rx[2] + 50, cy)], "loop", head=False, tag="outer.p",
           group="outer")
    w = f.lab(dx + 12, cy - 8, "outer loop", "outer.l")
    f.gloss(dx + 12 + w + 8, cy - 8, "review, evals and production feedback", "outer.g")
    f.link([(rx[2], bm + 12), (8, bm + 12), (8, ym), (28, ym)], "loop", tag="signals")
    f.gloss(20, bm + 6, "signals start new work", "signals.l")
    f.set_height(b0 + h + 4)
    f.write("figure-1")


# Figure 1 on a phone. Not the wide drawing scaled down: the same
# relationships in one column.
def figure1_narrow():
    f = SF("sf1n", NW, 1000, CAPTION[1], ALT[1], narrow=True)
    x0, x1 = 40, NW
    ax = x0 + 40
    y = 10
    f.node(x0, y, x1 - x0, 46, "Inputs", ["a prompt, a PRD or a ticket"], tag="in")
    in_mid = y + 23
    y += 46 + 22
    f.link([(ax, y - 22), (ax, y)], tag="a0")
    f.node(x0, y, x1 - x0, 46, "Design", ["sets the limits, in advance"], tag="design")
    d_mid = y + 23
    y += 46 + 22
    f.link([(ax, y - 22), (ax, y)], tag="a1")
    gy0 = y
    f.lab(x0 + 12, y + 22, "Inner loop", "inner.l")
    y += 36
    cx0, cx1 = x0 + 12, x1 - 34
    mids = []
    for i, (nm, g) in enumerate([("Assemble", "what the task needs"),
                                 ("Build", "the change, in a sandbox"),
                                 ("Verify", "against the standards")]):
        f.node(cx0, y, cx1 - cx0, 46, nm, [g], tag=nm.lower())
        if i:
            f.link([(ax + 12, y - 22), (ax + 12, y)], tag=f"s{i}")
        mids.append(y + 23)
        y += 46 + 22
    y -= 22
    f.link([(cx1, mids[2]), (x1 - 14, mids[2]), (x1 - 14, mids[0]), (cx1, mids[0])], tag="again")
    f.gloss(cx0, y + 20, "repeats until the work passes", "inner.g")
    y += 32
    f.box(x0, gy0, x1 - x0, y - gy0, "zone", "inner")
    y += 22
    f.link([(ax, y - 22), (ax, y)], tag="a2")
    outs = [("Review", "and evals"), ("Deploy", "under approval policy"),
            ("Production", "sends back signals")]
    for i, (nm, g) in enumerate(outs):
        f.node(x0, y, x1 - x0, 46, nm, [g], tag=nm.lower())
        if i:
            f.link([(ax, y - 22), (ax, y)], tag=f"b{i}")
        last = y
        y += 46 + 22
    y -= 22
    # the outer loop, up the left margin, back to design; signals back to inputs
    f.link([(x0, last + 16), (22, last + 16), (22, d_mid), (x0, d_mid)], "loop", tag="outer")
    f.link([(x0, last + 32), (6, last + 32), (6, in_mid), (x0, in_mid)], "loop", tag="signals")
    f.set_height(y + 4)
    f.write("figure-1-narrow")


# ═════════════════════════════════════════════════════════════════════════════
# Figure 2 — the agent proposes, policy authorizes, infrastructure enforces.
# One row: the profile, the agent in its sandbox, the egress proxy, and what
# lies behind it. Above it, the supply chain firewall, on the profile's launch
# path: the profile configures the sandbox at launch through it, and the proxy
# checks every package with it. Beneath it, the runtime authorization service,
# drawn as a decision rather than a container. Into it come the profile's
# bounds and the agent's proposal from above, and the rest of the trusted
# context from below, as one box and one arrow; out of it go the scope the
# proxy enforces, high-impact actions to approval and, ending in a stop,
# anything outside policy. The words are names; the caption, the alt text and
# the paper say what each part does.
# ═════════════════════════════════════════════════════════════════════════════
PROFILE_G = ["the most it can ever do"]
AGENT_G = ["untrusted,", "no credentials"]
DOWN_G = ["only authorized", "operations"]
F2_DENY = "outside policy"
# the record: one event of each boundary's, as the observability checklist
# names them, so no boundary reads as unrecorded
REC2 = "every grant, admission, process start and request"
# the trusted context besides the profile, by name: the agent and whoever it
# acts for, its task, any delegation, policy (the alt text says which is which)
CONTEXT = ["Identity", "Task", "Delegation", "Policy"]


def f2_sandbox(f, x0, x1, y0, h):
    f.box(x0, y0, x1 - x0, h, "sandbox", "sbx")
    f.badge(x0, y0, BN[SANDBOX], "sbx")
    f.lab(x0 + PAD + 4, y0 + 24, "Sandbox", "sbx.l")
    f.name(x0 + PAD + 4, y0 + 50, "Agent", "sbx.n")
    for i, g in enumerate(AGENT_G):
        f.gloss(x0 + PAD + 4, y0 + 66 + i * 14.5, g, f"sbx.g{i}")


def context_box(f, x0, y0, x1, cols):
    """The trusted context as one input, not four more components: one card,
    each part named, in `cols` columns with hairlines between them, each
    column as wide as its name and the slack shared. Returns the card's
    bottom."""
    rows = [CONTEXT[i:i + cols] for i in range(0, len(CONTEXT), cols)]
    rh = DEST_H
    h = rh * len(rows)
    f.box(x0, y0, x1 - x0, h, "card", "ctx")
    need = [max(f.width(n_, "name") for n_ in CONTEXT[c::cols]) + 2 * PAD for c in range(cols)]
    slack = (x1 - x0 - sum(need)) / cols
    xs = [x0]
    for w_ in need[:-1]:
        xs.append(round(xs[-1] + w_ + slack))
    for r, row in enumerate(rows):
        for c, n_ in enumerate(row):
            f.name(xs[c] + PAD, y0 + r * rh + rh / 2 + 4.5, n_, f"ctx{r * cols + c}.n0")
    for x in xs[1:]:
        f.parts.append(f'<path d="M{x + .5:g} {y0 + 9:g} L{x + .5:g} {y0 + h - 9:g}" '
                       f'stroke="{RULE}" stroke-width="0.75"/>')
    for r in range(1, len(rows)):
        yy = y0 + r * rh
        f.parts.append(f'<path d="M{x0 + 9:g} {yy + .5:g} L{x1 - 9:g} {yy + .5:g}" '
                       f'stroke="{RULE}" stroke-width="0.75"/>')
    return y0 + h


def figure2():
    f = CF("sf2", W, 600, CAPTION[2], ALT[2])
    PR_, SB, PX, DN = (6, 178), (198, 356), (376, 530), (562, 720)
    y0, y1 = 84, 176                       # the sandbox
    ym = mid((y0, y1))
    # the profile, the proxy, downstream; tall enough that the proxy's two
    # lines clear the ring on its foot
    c0, c1 = ym - 33, ym + 33
    # the supply chain firewall, above the row: the profile configures the
    # sandbox at launch through it, and the proxy checks packages with it
    sx0 = 262
    sb_ = sc_card(f, sx0, 6, PX[1])
    f.node(PR_[0], c0, PR_[1] - PR_[0], c1 - c0, "Profile", PROFILE_G, tag="prof")
    lx, ly = 92, mid((6, sb_))
    f.link([(lx, c0), (lx, ly), (sx0, ly)], tag="launch")
    f.gloss(lx + 8, ly - 8, "configures at launch", "launch.l")
    f.link([(300, sb_), (300, y0)], tag="sc.launch")
    f.gloss(308, 73, SC_LAUNCH, "sc.launch.l")
    f2_sandbox(f, SB[0], SB[1], y0, y1 - y0)
    bx, ux, gx = 40, 330, 420
    proxy_card(f, PX[0], c0, PX[1], c1, F2_PROXY_G, gx)
    f.link([(470, sb_), (470, c0)], tag="sc.pkg", both=True)
    f.gloss(478, 73, SC_PKG, "sc.pkg.l")
    f.link([(SB[1], ym), (PX[0], ym)], tag="request")
    f.node(DN[0], c0, DN[1] - DN[0], c1 - c0, "Downstream", DOWN_G, tag="down")
    f.link([(PX[1], ym), (DN[0], ym)], tag="out")
    # the decision, beneath the row from the profile's edge to the proxy's
    s0, s1 = 226, 270
    f.node(PR_[0], s0, PX[1] - PR_[0], s1 - s0, "Runtime authorization service", [AUTH_G],
           kind="guard", num=BN[IAM], tag="auth")
    # from above: the profile's bounds, and the agent's proposal; up to the
    # proxy, the scope it authorizes
    f.link([(bx, c1), (bx, s0)], tag="bounds")
    for i, s in enumerate(("bounds every", "decision")):
        f.gloss(bx + 8, 192 + i * 14.5, s, f"bounds.l{i}")
    f.link([(ux, y1), (ux, s0)], tag="propose")
    f.gloss(ux - 8 - f.width("proposes scope", "gloss"), 206.5, "proposes scope", "propose.l")
    f.link([(gx, s0), (gx, c1)], "grant", tag="grant")
    for i, s in enumerate(("authorized", "scope")):
        f.gloss(gx - 8 - f.width(s, "gloss"), 192 + i * 14.5, s, f"grant.l{i}")
    # from below: the rest of the trusted context, one card, one arrow
    cx, cy0 = 190, s1 + 30
    end = context_box(f, PR_[0], cy0, PX[1], 4)
    f.link([(cx, cy0), (cx, s1)], tag="ctx.in")
    f.lab(cx + 8, s1 + 19, "Trusted context", "ctx.l")
    # out to the right: high-impact actions to approval, and anything outside
    # policy stopped there
    ay0 = 206
    f.node(DN[0], ay0, DN[1] - DN[0], 44, "Approval", APPROVAL_G, tag="appr")
    f.link([(PX[1], ay0 + 30), (DN[0], ay0 + 30)], tag="route")
    f.gloss(DN[0], ay0 - 8, "high-impact actions", "route.l")
    dy, dx = s1 - 8, PX[1] + 20
    f.link([(PX[1], dy), (dx, dy)], tag="deny", bar=True, stop=True)
    f.gloss(dx + 8, dy + 4, F2_DENY, "deny.l")
    # the record, its own band
    r0 = end + 22
    gx2 = record(f, 0, r0, W, r0 + 48, tag="rec")
    f.gloss(gx2, r0 + 28, REC2, "rec.g")
    end = legend(f, 0, r0 + 48 + 38, W, marks=ALL_MARKS)
    f.set_height(end)
    f.write("figure-2")


def figure2_narrow():
    """Figure 2 on a phone: the profile, the supply chain firewall on its
    launch path, the sandbox beside the proxy, what the proxy lets through under the
    proxy, the decision beneath both, its trusted context in one card under
    it, and what it routes elsewhere down the right edge: approval, then a
    stop for anything outside policy."""
    f = CF("sf2n", NW, 1400, CAPTION[2], ALT[2], narrow=True)
    X, R1 = 8, 352
    y = 10
    f.node(X, y, R1 - X, 44, "Profile", PROFILE_G, tag="prof")
    pb = y + 44
    # the supply chain firewall, on the profile's launch path; the profile's
    # bounds run down the left edge, past it and the sandbox, into the service
    s0 = pb + 42
    sb_ = sc_card(f, 60, s0, R1)
    lx, bx = 200, 22
    f.link([(lx, pb), (lx, s0)], tag="launch")
    f.gloss(lx + 8, pb + 24, "configures at launch", "launch.l")
    f.gloss(bx + 8, pb + 24, "bounds every decision", "bounds.l")
    SB, PX, BUS = (38, 176), (194, 348), 360
    sy0, sh = sb_ + 36, 98
    f2_sandbox(f, SB[0], SB[1], sy0, sh)
    ux, gx = 60, 206
    ph = card_h(F2_PROXY_G) + 6            # its two lines clear the ring on its foot
    proxy_card(f, PX[0], sy0, PX[1], sy0 + ph, F2_PROXY_G, gx)
    f.link([(120, sb_), (120, sy0)], tag="sc.launch")
    f.gloss(128, sb_ + 22, SC_LAUNCH, "sc.launch.l")
    f.link([(280, sb_), (280, sy0)], tag="sc.pkg", both=True)
    for i, s in enumerate(("checks", "packages")):
        f.gloss(288, sb_ + 15 + i * 14.5, s, f"sc.pkg.l{i}")
    rm = sy0 + ph / 2
    f.link([(SB[1], rm), (PX[0], rm)], tag="request")
    # under the proxy, what it lets through, fed down its right edge
    DC = (220, 340)
    dy0 = sy0 + ph + 18
    dh = card_h(DOWN_G)
    f.node(DC[0], dy0, DC[1] - DC[0], dh, "Downstream", DOWN_G, tag="down")
    dm = dy0 + dh / 2
    f.link([(PX[1], rm), (BUS, rm), (BUS, dm), (DC[1], dm)], tag="out")
    # the decision, beneath both columns
    b0 = max(sy0 + sh, dy0 + dh) + 24
    bh = card_h([AUTH_G])
    f.node(X, b0, R1 - X, bh, "Runtime authorization service", [AUTH_G], kind="guard",
           num=BN[IAM], tag="auth")
    # into it from above: the profile's bounds (left edge) and the proposal;
    # up into the proxy, the scope it authorizes
    f.link([(bx, pb), (bx, b0)], tag="bounds")
    f.link([(ux, sy0 + sh), (ux, b0)], tag="propose")
    f.gloss(ux + 8, sy0 + sh + 16, "proposes scope", "propose.l")
    f.link([(gx, b0), (gx, sy0 + ph)], "grant", tag="grant")
    for i, s in enumerate(("authorized", "scope")):
        f.gloss(gx - 8 - f.width(s, "gloss"), b0 - 22.5 + i * 14.5, s, f"grant.l{i}")
    # into it from below: the rest of the trusted context, one card, one arrow
    cx, c0 = 140, b0 + bh + 30
    end = context_box(f, X, c0, 326, 4)
    f.link([(cx, c0), (cx, b0 + bh)], tag="ctx.in")
    f.lab(cx + 8, b0 + bh + 19, "Trusted context", "ctx.l")
    # out of it, down the right edge: high-impact actions to approval, and
    # anything outside policy stopped there
    rx = 344
    ay0 = end + 34
    f.gloss(336 - f.width("high-impact actions", "gloss"), ay0 - 8, "high-impact actions",
            "route.l")
    f.node(X, ay0, 326 - X, 44, "Approval", APPROVAL_G, tag="appr")
    dy = ay0 + 44 + 24
    f.link([(rx, b0 + bh), (rx, dy)], tag="deny", group="route", bar=True, stop=True)
    f.link([(rx, ay0 + 22), (326, ay0 + 22)], tag="route", group="route")
    f.gloss(334 - f.width(F2_DENY, "gloss"), dy + 4, F2_DENY, "deny.l")
    r0 = dy + 24
    record(f, X, r0, R1, r0 + 62, tag="rec", two=True)
    for i, s in enumerate(("every grant, admission,", "process start and request")):
        f.gloss(X + PAD, r0 + 39 + i * 14.5, s, f"rec.g{i}")
    f.rule(r0 + 62 + 20, X, R1)
    end = key_grid(f, X, r0 + 62 + 42)
    f.set_height(end)
    f.write("figure-2-narrow")


# ═════════════════════════════════════════════════════════════════════════════
# Figure 6 — only a new authorization decision can widen a task. One incident
# on Level 3's skeleton ("A factory in action"), so the reader turning from
# Figure 5 finds every part where Figure 5 left it: the alert comes into the
# orchestrator across the top; the orchestrator schedules the task on the
# durable execution layer beneath it, which starts the incident agent, and
# proposes the task's scope, its heaviest line, into the service, which alone
# authorizes it. When the agent wants more, its request goes up the route the
# agent's proposal takes at Levels 1 and 2, and the proxy blocks the call the
# task doesn't cover.
# ═════════════════════════════════════════════════════════════════════════════
FIG6_AUTH = "checks policy and the alert’s source"
BLOCKED_G = ["blocked: not", "in the task"]   # the proxy blocking, never "outside policy"
FIG6_ORCH = ["turns the alert into a task"]
FIG6_ALERT = ["payments errors"]
# what the orchestrator proposes: two lines wide, three on a phone
FIG6_TASK = ["proposes payments logs,", "last hour; one pull request"]
FIG6_TASK_N = ["proposes payments", "logs, last hour;", "one pull request"]
FIG6_DEST = [(["Payments", "service logs"], ["last hour only"], "card"),
             (["Authentication", "service logs"], BLOCKED_G, "blocked")]
FIG6_OUT = [("Pull request", ["one, as", "granted"]), ("Approval", APPROVAL_G),
            ("Deploy", ["small share of", "traffic first"]),
            ("Production", ["error rate", "afterward"])]


class F6:
    """Where Figure 6 departs from LV: one sandbox, so a narrower frame (the
    outer loop's words sit left of it, under the rail's turn); the proposal's
    drop further right, under its longer words; the outputs higher, under
    a shorter frame."""
    ALERT = (0, 0, 120, 60)
    PROP_X = 640
    FRAME = (150, 164, 546, 354)
    SB = (170, 442, 242, 334)              # centred on the proxy, as at Level 1
    OUT = (420, 480)


def figure6():
    f = CF("sf6", W, 800, CAPTION[6], ALT[6])
    ox0, oy0, ox1, oy1 = LV.ORCH
    ex0, ey0, ex1, ey1 = LV.EXEC
    ax0, ay0, ax1, ay1 = LV.AUTH
    # ── across the top: the alert into the orchestrator ──
    x0, y0, x1, y1 = F6.ALERT
    f.node(x0, y0, x1 - x0, y1 - y0, ["Production", "alert"], FIG6_ALERT, tag="sig")
    f.link([(x1, LV.IN_Y), (ox0, LV.IN_Y)], tag="takes")
    f.node(ox0, oy0, ox1 - ox0, oy1 - oy0, "Orchestrator agent", FIG6_ORCH, kind="agent",
           tag="orch")
    # it schedules the task on the execution layer beneath it, and proposes
    # the task's scope, which only the service authorizes
    f.link([(LV.TX, oy1), (LV.TX, ey0)], tag="schedule")
    f.gloss(LV.TX + 8, ey0 - 14, "schedules the task", "schedule.l")
    f.link([(ox1, LV.PROP_Y), (F6.PROP_X, LV.PROP_Y), (F6.PROP_X, ay0)], tag="propose",
           heavy=True)
    for i, s_ in enumerate(FIG6_TASK):
        gloss_to(f, F6.PROP_X - 8, ay0 - 22 + 14.5 * i, s_, f"propose.l{i}")
    f.node(ex0, ey0, ex1 - ex0, ey1 - ey0, "Durable execution layer", EXEC_G, tag="exec")
    f.node(ax0, ay0, ax1 - ax0, ay1 - ay0, "Runtime authorization service", [FIG6_AUTH],
           kind="guard", num=BN[IAM], tag="auth")
    f.boxes[-1]["w"] = measured(f, FIG6_AUTH) + 1
    gx = LV.P[1][0] + LV.GRANT_DX
    f.link([(gx, ay1), (gx, LV.PY)], "grant", tag="grant")
    f.gloss(gx + 8, ay1 + 14, "authorized scope", "grant.l")
    # ── the factory: the execution layer starts the agent in its sandbox ──
    fx0, fy0, fx1, fy1 = F6.FRAME
    f.box(fx0, fy0, fx1 - fx0, fy1 - fy0, "zone", "frame")
    f.lab(fx0 + 10, LV.LAB[1], "The factory", "frame.l")
    sx0, sx1, sy0, sy1 = F6.SB
    f.link([(LV.TX, ey1), (LV.TX, sy0)], tag="starts")
    f.box(sx0, sy0, sx1 - sx0, sy1 - sy0, "sandbox", "sbx")
    f.badge(sx0, sy0, BN[SANDBOX], "sbx")
    tx = sx0 + PAD + 4
    f.lab(tx, sy0 + 20, "Sandbox", "sbx.l")
    f.name(tx, sy0 + 39, "Incident agent", "sbx.n")
    f.gloss(tx, sy0 + 55, "configured by its profile", "sbx.g0")
    f.loop_glyph(sx0 + PAD + 11, sy0 + 72, "sbx.loop")
    f.gloss(sx0 + PAD + 26, sy0 + 76, "inner loop, until tests pass", "sbx.lp")
    # wanting more is a request for a new decision, never a grant: up the
    # route the agent's own proposal takes at Levels 1 and 2
    wx = LV.AGENT_PX
    f.link([(wx, sy0), (wx, LV.AGENT_PY), (ax0, LV.AGENT_PY)], tag="wider")
    for i, s_ in enumerate(("needs a new", "decision")):
        gloss_to(f, wx - 8, LV.LAB[1] + 18 + 14.5 * i, s_, f"wider.l{i}")
    lv_proxy(f, 1)
    lv_traffic(f, sx1)
    # ── what the proxy reaches: the firewall, then the task's two services ──
    cx0, cx1 = LV.COL
    f.node(cx0, LV.COL_Y[0], cx1 - cx0, card_h(SC_COL_G, SC_LINES), SC_LINES, SC_COL_G,
           kind="guard", num=BN[SUPPLY], tag="sc")
    ys, y = [LV.COL_Y[0] + card_h(SC_COL_G, SC_LINES) / 2], LV.COL_Y[1]
    for i, (n_, g_, kind) in enumerate(FIG6_DEST):
        h = card_h(g_, n_)
        f.node(cx0, y, cx1 - cx0, h, n_, g_, kind=kind, tag=f"dest{i}")
        ys.append(y + h / 2)
        y += h + STACK
    pm = LV.PY + LV.PH / 2
    f.link([(LV.P[1][1], pm), (LV.BUS, pm)], head=False, tag="bus.in", group="bus")
    f.link([(LV.BUS, ys[0]), (LV.BUS, ys[-1])], head=False, tag="bus", group="bus")
    for i, yy in enumerate(ys):
        f.link([(LV.BUS, yy), (cx0, yy)], tag=f"bus.{i}", group="bus", bar=(i == len(ys) - 1))
    o0, o1 = F6.OUT
    f.link([(LV.BUS, ys[-1]), (LV.BUS, o0)], tag="bus.pr", group="bus")
    f.gloss(LV.BUS + 8, o0 - 10, "opens", "bus.pr.l")
    # ── the fix, right to left, and the error rate back to the orchestrator ──
    slots = (LV.PR, LV.APPR, LV.DEPLOY, LV.PROD)
    om = mid(F6.OUT)
    for slot, (n_, g_) in zip(slots, FIG6_OUT):
        f.node(slot[0], o0, slot[1] - slot[0], o1 - o0, n_, g_, tag=n_.split()[0].lower())
    for a, b in zip(slots, slots[1:]):
        f.link([(a[0], om), (b[1], om)], tag=f"out{a[0]}")
    lv_home(f, [(LV.PROD[0], om), (LV.LOOP_X, om)])
    f.lab(LV.LOOP_X + 10, LV.LOOP_Y + 24, "outer loop", "outer.l")
    for i, s_ in enumerate(("confirms the fix or", "starts the next run")):
        f.gloss(LV.LOOP_X + 10, LV.LOOP_Y + 38.5 + 14.5 * i, s_, f"outer.g{i}")
    f.set_height(o1 + 4)
    f.write("figure-6")


def figure6_narrow():
    """Figure 6 on a phone, on the levels' column: the alert into the
    orchestrator; beneath it, side by side, the execution layer it schedules
    the task on and the service it proposes the task's scope to; the frame,
    the sandbox the execution layer starts and its proxy; what the proxy
    reaches; the fix, and the error rate back up the rail."""
    f = CF("sf6n", NW, 1600, CAPTION[6], ALT[6], narrow=True)
    X0, X1 = NV.X0, NV.X1
    y = 10
    f.node(X0, y, X1 - X0, 44, "Production alert", FIG6_ALERT, tag="sig")
    f.link([(NV.IN_X, y + 44), (NV.IN_X, y + 84)], tag="takes")
    oy = y + 84
    f.node(X0, oy, X1 - X0, 44, "Orchestrator agent", FIG6_ORCH, kind="agent", tag="orch")
    o_mid, ob = oy + 22, oy + 44
    # room under it for the proposal's three lines
    ey = ob + 58
    f.link([(NV.IN_X, ob), (NV.IN_X, ey)], tag="schedule")
    f.gloss(NV.IN_X + 8, ob + 26, "schedules the task", "schedule.l")
    f.link([(NV.PROP_X, ob), (NV.PROP_X, ey)], tag="propose", heavy=True)
    for i, s_ in enumerate(FIG6_TASK_N):
        gloss_to(f, NV.PROP_X - 8, ob + 16 + 14.5 * i, s_, f"propose.l{i}")
    f.node(NV.EXEC[0], ey, NV.EXEC[1] - NV.EXEC[0], 92, ["Durable execution", "layer"],
           ["CI/CD or a step", "runner that starts", "each agent"], tag="exec")
    bh = 76
    f.node(NV.AUTH[0], ey, NV.AUTH[1] - NV.AUTH[0], bh, ["Runtime authorization", "service"],
           ["checks policy and", "the alert’s source"], kind="guard", num=BN[IAM], tag="auth")
    sb = ey + bh
    for i, s_ in enumerate(("authorized", "scope")):
        f.gloss(NV.GRANT_X + 8, sb + 18 + 14.5 * i, s_, f"grant.l{i}")
    # ── the frame, and the sandbox the execution layer starts ──
    fy0 = sb + 66
    lx = NV.S[0]
    f.lab(lx, fy0 + 22, "The factory", "frame.l")
    sy, sh = fy0 + 40, 116
    sx0, sx1 = NV.S
    f.link([(NV.DROP_X, ey + 92), (NV.DROP_X, sy + 40), (sx0, sy + 40)], tag="starts")
    f.box(sx0, sy, sx1 - sx0, sh, "sandbox", "sbx")
    f.badge(sx0, sy, BN[SANDBOX], "sbx")
    tx = sx0 + PAD + 4
    f.lab(tx, sy + 20, "Sandbox", "sbx.l")
    f.name(tx, sy + 40, "Incident agent", "sbx.n")
    f.gloss(tx, sy + 56, "configured by", "sbx.g0")
    f.gloss(tx, sy + 70.5, "its profile", "sbx.g1")
    f.loop_glyph(sx0 + PAD + 11, sy + 88, "sbx.loop")
    f.gloss(sx0 + PAD + 26, sy + 92, "inner loop,", "sbx.lp0")
    f.gloss(sx0 + PAD + 26, sy + 106.5, "until tests pass", "sbx.lp1")
    # wanting more: up into the service, as the agent's proposal goes at
    # Levels 1 and 2, its label under the execution layer's foot
    f.link([(NV.AGENT_PX, sy), (NV.AGENT_PX, sb)], tag="wider")
    for i, s_ in enumerate(("needs a new", "decision")):
        gloss_to(f, NV.AGENT_PX - 8, sb + 40 + 14.5 * i, s_, f"wider.l{i}")
    pmid = sy + sh / 2
    py = narrow_proxy(f, pmid, 0)
    f.link([(NV.GRANT_X, sb), (NV.GRANT_X, py)], "grant", tag="grant")
    fy1 = sy + sh + 16
    f.box(NV.FRAME[0], fy0, NV.FRAME[1] - NV.FRAME[0], fy1 - fy0, "zone", "frame")
    # ── what the proxy reaches, and the pull request, down the bus ──
    y = fy1 + 24
    ys = []
    for i, (nm, g, kind, tag) in enumerate(
            [(SC_NAME, SC_COL_G, "guard", "sc")] +
            [(" ".join(n_), [" ".join(g_)], k_, f"dest{j}")
             for j, (n_, g_, k_) in enumerate(FIG6_DEST)]):
        f.node(NV.DEST[0], y, NV.DEST[1] - NV.DEST[0], 44, nm, g, kind=kind,
               num=BN[SUPPLY] if tag == "sc" else None, tag=tag)
        ys.append(y + 22)
        y += 44 + STACK
    y += 30 - STACK
    pr_mid = y + 23
    f.link([(NV.BUS, pmid), (NV.BUS, ys[-1])], head=False, tag="bus", group="bus")
    for i, yy in enumerate(ys):
        f.link([(NV.BUS, yy), (NV.DEST[1], yy)], tag=f"bus.{i}", group="bus",
               bar=(i == len(ys) - 1))
    f.link([(NV.BUS, ys[-1]), (NV.BUS, pr_mid), (NV.DEST[1], pr_mid)], tag="bus.pr", group="bus")
    gloss_to(f, NV.BUS - 10, pr_mid - 23 - 8, "opens", "bus.pr.l")
    outs = [("Pull request", ["one, as granted"]), ("Approval", APPROVAL_G),
            ("Deploy", ["small share of traffic first"]),
            ("Production", ["error rate afterward"])]
    for i, (nm, g) in enumerate(outs):
        f.node(X0, y, NV.DEST[1] - X0, 46, nm, g, tag=f"out{i}")
        y += 46
        if i < len(outs) - 1:
            f.link([(NV.IN_X, y), (NV.IN_X, y + 22)], tag=f"o{i}")
            y += 22
    # the error rate, back up the rail into the orchestrator
    ly = y + 44
    f.link([(NV.IN_X, y), (NV.IN_X, ly), (NV.RAIL, ly), (NV.RAIL, o_mid), (X0, o_mid)], "loop",
           tag="outer")
    f.lab(NV.IN_X + 10, y + 18, "outer loop", "outer.l")
    f.gloss(NV.IN_X + 10, y + 32.5, "confirms the fix or starts the next run", "outer.g")
    f.set_height(ly + 6)
    f.write("figure-6-narrow")


if __name__ == "__main__":
    figure1()
    figure1_narrow()
    figure2()
    figure2_narrow()
    for n in (1, 2, 3):
        build_level(n)
        narrow_level(n)
    figure6()
    figure6_narrow()
