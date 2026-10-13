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
    on the edge where the authorized scope comes in (its foot, or at Level 3
    its top), identity and access's.
  * WASH marks untrusted agent execution: the inside of a sandbox, and any
    agent that plans or watches from outside one.

Everything else is ink on the plate. The levels (Figures 3–5) are each drawn
complete, and what a level adds is marked by weight and a pale tint (NEWT),
which survive a greyscale print and leave the accent its one meaning:

  new card       tint fill (a wash card keeps its wash) and a heavier outline
  new connector  ink, heavier
  new words      outside a card, set on the tint
  carried over   drawn as the level before drew it

Figures 2, 3, 4 and 6 are each one row — what starts the work, the agent in
its sandbox, the egress proxy, and what lies behind it — between two trusted
controls: the supply chain firewall above it and the runtime authorization
service beneath it. The service is a decision, not a container: what the agent
(or, at Level 3, the orchestrator) proposes comes into it, and the scope it
authorizes goes to the proxy. The firewall checks the components a sandbox
is built from, on the path that launches the agent, and every package the
proxy fetches. Figures 3, 4 and 6 share one skeleton (R) and the record is its
own band. Level 3 (Figure 5) is drawn to the lead author's composition: the
orchestrator agent across the top, fed by requests, context and signals; the
durable execution layer a separate card beneath it, splitting the work into
the factory; the runtime authorization service, the supply chain firewall,
the model gateway and what lies downstream in one column on the right; the
record inside the factory's frame (r_level3). Figure 1 is the process the
boundaries serve, so it has its own composition.

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
    3: "A developer directs one coding agent in a sandbox on their machine or a remote "
       "environment, and every request it makes goes through a default-deny egress proxy that "
       "enforces the authorization service's decision. The agent can reach source control, the "
       "services its task needs, a model gateway and approved packages, and nothing else the "
       "developer can reach; its pull request goes back to the developer.",
    4: "A request, event, schedule or ticket starts a workflow on CI/CD or a durable "
       "execution engine, which runs a coding agent in a fresh sandbox, behind its own proxy, for each "
       "run; the pull request goes through approval to merge, and review feedback starts the "
       "next run. The authorization service, proxy and destinations are the same as at "
       "Level 1.",
    5: "An orchestrator agent turns signals and requests into tasks and proposes each one's "
       "profile and scope to the authorization service, which alone grants access; the "
       "execution layer starts each agent in its own sandbox, and a monitoring agent watches "
       "from outside and flags new work. Changes go through approval and deploy to "
       "production, whose signals start the next work, inside the same boundaries as Levels 1 "
       "and 2.",
    6: "A production alert leads the orchestrator to propose a task for an incident agent, one "
       "service's logs for the last hour and one pull request, which the authorization service "
       "checks against policy and the alert's source. When the agent reaches for another "
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


# What the proxy lets through, the same four at every level, by name only.
# Packages come from the approved registries, but only through the proxy's
# check with supply chain scanning (sc_card), a trusted control, never a
# destination.
DEST = [  # (name lines, gloss lines, kind)
    (["Source control"], [], "card"),
    (["Services"], [], "card"),
    (["Model gateway"], [], "guard"),
    (["Package", "registries"], [], "card"),
]
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
# by the agent's profile"). Level 3 draws it in the column of trusted services
# the proxies reach (r_level3).
SC_NAME = "Supply chain firewall"
SC_G = "approved versions the profile allows"
SC_LAUNCH, SC_PKG = "checks components", "checks packages"


def sc_card(f, x0, y0, x1, lines=(SC_G,), tag="sc"):
    """Supply chain scanning as a card, its line set in `lines`; returns
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
# credentials is the point, where they are attached.
APPROVAL_G = ["automatic or a person"]
AUTH_G = "authorizes each task’s scope"
PROXY_G = ["default-deny"]
F2_PROXY_G = ["default-deny,", "attaches credentials"]

# Words set on the tint, measured: Chrome, the site's fonts at the size each is
# set, getComputedTextLength, without letter-spacing (12–13 Oct 2026). The tint
# is drawn to the measured width; figkit's estimate overstates long runs by up
# to a tenth, which would leave a ragged tail of tint. A run that isn't here
# stops the build rather than guessing.
TINT_W = {
    "label|500|12.25|OUTER LOOP": 73.09,
    "label|500|12.25|THE FACTORY": 77.53,
    "label|500|12.5|OUTER LOOP": 74.58,
    "label|500|12.5|THE FACTORY": 79.11,
    "serif|400|12.25|a shared service": 93.75,
    # Level 3's (13 Oct 2026)
    "serif|400|12.25|divides the work": 94.84,
    "serif|400|12.25|each part to its own agent,": 150.66,
    "serif|400|12.25|with narrowed authority": 140.03,
    "serif|400|12.25|proposes": 52.92,
    "serif|400|12.25|task scope": 60.28,
    "serif|400|12.25|new work": 55.69,
    "serif|400|12.25|all four boundaries’ records, linked by run": 242.52,
    "serif|400|12.25|and task scope": 85.08,
    "serif|400|12.25|production signals start new work": 195.89,
    "serif|400|12.25|proposes profile": 93.53,
    "serif|400|12.25|review feedback drives the next run": 205.91,
    "serif|400|12.25|telemetry and evals across all runs": 199.83,
    "serif|400|12.25|the developer drives the next run": 190.73,
    "serif|400|12.5|a shared service": 95.67,
    "serif|400|12.5|all four boundaries’ records, by run": 207.36,
    "serif|400|12.5|production signals start new work": 199.89,
    "serif|400|12.5|review feedback drives the next run": 210.11,
    "serif|400|12.5|telemetry and evals across all runs": 203.91,
    "serif|400|12.5|the developer drives the next run": 194.63,
}


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
        and heavy (Level 3's proposal, the line that matters most). A grant,
        the decision going out, is solid accent and heavier than any flow:
        dashes already mean the frames, the outer loop and a stop. `both`
        heads both ends: a check that goes and comes back (the proxy's
        packages, through supply chain scanning). `dot` marks where a
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
def node_c(f, x, y, w, h, name, kind="card", num=None, tag=""):
    """A card with its name only, centred in the box, on one line or two."""
    f.box(x, y, w, h, kind, tag)
    if num:
        f.badge(x, y, num, tag)
    names = name if isinstance(name, (list, tuple)) else [name]
    y0 = y + h / 2 + 4.5 - 7.5 * (len(names) - 1)
    for i, n in enumerate(names):
        f.name(x + PAD, y0 + 15 * i, n, f"{tag}.n{i}")


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
# The level skeleton. Columns: A who or what starts the work · B what
# orchestrates and runs it · C the sandbox(es) · D the egress proxy · E what it
# lets through. Rows: supply chain scanning above the frame, the frame where
# agents run, the runtime authorization service as a bar beneath it, the
# outputs, the outer loop, the record.
# ═════════════════════════════════════════════════════════════════════════════
class R:
    A, B, BUS_B, C, D, BUS_E, E = (0, 112), (134, 234), 246, (264, 436), (456, 560), 582, (600, 720)
    FX = (122, 572)
    # supply chain scanning, above the frame and across the sandbox and
    # proxy columns, as the service is a bar beneath them. Its component check
    # drops at BUS_B into the path that starts the agent (the developer's
    # arrow, the workflow's, the execution layer's bus), the same x at every
    # level; its package check drops into the proxy. Each is labelled between
    # the card and the frame.
    SC = (236, 6, 560, 50)
    PKG_X, SC_LY = 530, 67
    # the frame's label sits in its top left-hand corner, set in lines short
    # enough to stay left of the component check's line
    FY0, LABX, LABY = 76, 134, 96
    # the row starts 30 under the frame's label, so a label set on two lines
    # (Levels 1 and 2) clears the sandbox's mark
    ROW, MID = (126, 270), 198
    PROXY = (456, 168, 560, 228)
    LANE = (288, 348)
    FY1, FY1_SHORT = 356, 286
    # the bar reaches back to x 56; nothing is drawn at x 56–134 under the
    # frame. It sits 42 under Level 3's full frame, room for "authorized /
    # scope" in two lines set against the grant, in the same place at every
    # level.
    BAR = (56, 398, 510, 442)
    GRANT_X, GRANT_LY = 484, (372, 386.5)
    PROP_X, PROP_LY = 340, 342   # the agent proposes the scope it needs, as in Figure 2
    EXIT_X, EXIT_Y = 536, 458
    OUT = (476, 536)
    PR, APPROVAL, SLOT3, SLOT4 = (134, 238), (258, 432), (452, 548), (568, 700)
    # the outer loop's label sits above its return line, right of the pull
    # request's leg, at the same place in every level
    LOOPY, LOOP_X, LOOP_LABEL_X = 576, 36, 198
    FLOOR = (592, 638)
    H = 640
    KEY = (600, 20)


def r_frame(f, full=False, label=(), gloss=(), s_label="old"):
    """The frame and, in its corner, its label and gloss, each given as the
    lines it is set in."""
    y1 = R.FY1 if full else R.FY1_SHORT
    f.box(R.FX[0], R.FY0, R.FX[1] - R.FX[0], y1 - R.FY0, "zone", "frame")
    y = R.LABY
    with f.at("newtext" if s_label == "new" else "old"):
        for i, s in enumerate(label):
            f.lab(R.LABX, y, s, f"frame.l{i}")
            y += 14.5
        for i, s in enumerate(gloss):
            f.gloss(R.LABX, y, s, f"frame.g{i}")
            y += 14.5


def r_sc(f, launch=None):
    """Supply chain scanning above the frame. Its component check drops
    into the path that starts the agent (`launch`: the point it joins, (x,
    y)) or, where the figure draws no such path, into the sandbox's top
    (`launch` (x, None)); the proxy's package check goes and comes back. Each
    label sits right of its line, or left where it would meet the other."""
    x0, y0, x1, y1 = R.SC
    sc_card(f, x0, y0, x1)
    lx, ly = launch or (R.BUS_B, R.MID)
    f.link([(lx, y1), (lx, ly or R.ROW[0])], tag="sc.launch", head=ly is None, dot=ly is not None)
    lw = f.width(SC_LAUNCH, "gloss")
    f.gloss(lx + 8 if lx + 8 + lw < R.PKG_X - 8 else lx - 8 - lw, R.SC_LY, SC_LAUNCH,
            "sc.launch.l")
    f.link([(R.PKG_X, y1), (R.PKG_X, R.PROXY[1])], tag="sc.pkg", both=True)
    f.gloss(R.PKG_X + 8, R.SC_LY, SC_PKG, "sc.pkg.l")


def r_grant(f, x, y0, y1):
    """The scope the service authorizes, up into the proxy: the decision going
    out, labelled in two lines set right against its own line."""
    f.link([(x, y0), (x, y1)], "grant", tag="grant")
    for i, s_ in enumerate(("authorized", "scope")):
        f.gloss(x - 8 - f.width(s_, "gloss"), R.GRANT_LY[i], s_, f"grant.l{i}")


def r_bar(f, stack=False, gloss=AUTH_G):
    """The runtime authorization service: a decision, drawn as Figure 2 draws
    it — what the agent proposes comes in, the scope it authorizes goes up to
    the proxy that enforces it. Behind a stack of proxies the grant ends on the
    back card, so its head is not drawn over by the cards in front."""
    x0, y0, x1, y1 = R.BAR
    f.node(x0, y0, x1 - x0, y1 - y0, "Runtime authorization service", [gloss],
           kind="guard", num=BN[IAM], tag="auth")
    r_grant(f, R.GRANT_X, y0, R.PROXY[3] + (6 if stack else 0))


def r_proxy(f, stack=False, s="old"):
    x0, y0, x1, y1 = R.PROXY
    with f.at(s):
        if stack:
            for d in (6, 3):
                f.ghost(x0 + d, y0 + d, x1 - x0, y1 - y0, f"pghost{d}", "proxy")
        proxy_card(f, x0, y0, x1, y1, PROXY_G, R.GRANT_X, kind="guardfill" if stack else "guard")


def r_dest(f, dest=DEST):
    """What the proxy lets through, by name, fed down one bus."""
    ys, y = [], R.ROW[0]
    for i, (n, g, kind) in enumerate(dest):
        if g:
            h = card_h(g, n)
            f.node(R.E[0], y, R.E[1] - R.E[0], h, n, g, kind=kind, tag=f"dest{i}")
        else:
            h = DEST_H
            node_c(f, R.E[0], y, R.E[1] - R.E[0], h, n, kind=kind, tag=f"dest{i}")
        ys.append((y + h / 2, kind))
        y += h + STACK
    f.link([(R.PROXY[2], R.MID), (R.BUS_E, R.MID)], head=False, tag="bus.in", group="bus")
    f.link([(R.BUS_E, ys[0][0]), (R.BUS_E, ys[-1][0])], head=False, tag="bus", group="bus")
    for i, (yy, kind) in enumerate(ys):
        f.link([(R.BUS_E, yy), (R.E[0], yy)], tag=f"bus.{i}", group="bus",
               bar=(kind == "blocked"))


def r_sandbox(f, label, name, gloss, s="old", stack=False, loop=("inner loop,", "until it passes")):
    x0, x1 = R.C
    y0, y1 = R.ROW
    with f.at(s):
        if stack:
            for d in (8, 4):
                f.ghost(x0 + d, y0 + d, x1 - x0 - 8, y1 - y0 - 8, f"ghost{d}", "sandbox")
            x1, y1 = x1 - 8, y1 - 8
        f.box(x0, y0, x1 - x0, y1 - y0, "sandbox", "sbx")
        f.badge(x0, y0, BN[SANDBOX], "sbx")
    f.lab(x0 + PAD + 4, y0 + 24, label, "sbx.l")
    f.name(x0 + PAD + 4, y0 + 52, name, "sbx.n")
    for i, g in enumerate(gloss):
        f.gloss(x0 + PAD + 4, y0 + 68 + i * 14.5, g, f"sbx.g{i}")
    gy = y1 - 28
    f.loop_glyph(x0 + PAD + 11, gy - 4, "sbx.loop")
    f.gloss(x0 + PAD + 26, gy, loop[0], "sbx.lp0")
    f.gloss(x0 + PAD + 26, gy + 14.5, loop[1], "sbx.lp1")


def r_proposes(f):
    """The agent proposes the scope it needs: Figure 2's arrow, at every level
    where the agent's own request is the only proposal."""
    f.link([(R.PROP_X, R.ROW[1]), (R.PROP_X, R.BAR[1])], tag="propose")
    f.gloss(R.PROP_X - 8 - f.width("proposes scope", "gloss"), R.PROP_LY, "proposes scope",
            "propose.l")


def r_pr_exit(f):
    """Pull requests leave by the same path as everything else: the proxy."""
    f.link([(R.EXIT_X, R.PROXY[3]), (R.EXIT_X, R.EXIT_Y), (mid(R.PR), R.EXIT_Y),
            (mid(R.PR), R.OUT[0])], tag="pr.exit")


def out_card(f, slot, name, gloss, tag):
    f.node(slot[0], R.OUT[0], slot[1] - slot[0], R.OUT[1] - R.OUT[0], name, gloss, tag=tag)


def out_link(f, a, b):
    my = mid(R.OUT)
    f.link([(a[1], my), (b[0], my)], tag=f"out{a[0]}")


def r_outer(f, x, top):
    """The outer loop: down from the foot of the card it leaves, back along
    LOOPY, and up the left edge into whoever starts the next run."""
    f.link([(x, R.OUT[1]), (x, R.LOOPY), (R.LOOP_X, R.LOOPY), (R.LOOP_X, top)], "loop",
           tag="outer")


def r_outer_labels(f, gloss, s_label, s_gloss):
    with f.at("newtext" if s_label == "new" else "old"):
        f.lab(R.LOOP_LABEL_X, R.LOOPY - 24, "outer loop", "outer.l")
    with f.at("newtext" if s_gloss == "new" else "old"):
        f.gloss(R.LOOP_LABEL_X, R.LOOPY - 8, gloss, "outer.g")


def r_floor(f, gloss, s_gloss="old"):
    gx = record(f, 0, R.FLOOR[0], W, R.FLOOR[1])
    with f.at("newtext" if s_gloss == "new" else "old"):
        f.gloss(gx, R.FLOOR[0] + 28, gloss, "obs.g")


# ── Level 1 ──────────────────────────────────────────────────────────────────
def r_level1(f):
    r_frame(f, label=["Developer’s", "machine"], gloss=["or a remote", "environment"])
    r_sc(f)
    r_bar(f)
    with f.at("new"):
        f.node(R.A[0], R.MID - 36, R.A[1] - R.A[0], 72, "Developer", ["kicks off", "each run"],
               tag="dev")
        f.link([(R.A[1], R.MID), (R.C[0], R.MID)], tag="directs")
    r_sandbox(f, "Sandbox", "Coding agent", ["configured by", "its profile"])
    r_proposes(f)
    r_proxy(f)
    f.link([(R.C[1], R.MID), (R.PROXY[0], R.MID)], tag="traffic")
    r_dest(f)
    with f.at("new"):
        r_pr_exit(f)
        out_card(f, R.PR, "Pull request", ["reviewed by", "the developer"], "pr")
        r_outer(f, mid(R.PR), R.MID + 36)
    r_outer_labels(f, "the developer drives the next run", "new", "new")
    # Figure 3 is the first level to draw all four boundaries, so it keys them,
    # in the corner Levels 2 and 3 fill with approval and what follows it
    key_grid(f, 300, R.OUT[0] + 12)
    r_floor(f, "harness logs, identity and proxy records")


# ── Level 2 ──────────────────────────────────────────────────────────────────
def r_level2(f):
    r_frame(f, label=["The factory"], gloss=["a shared service"], s_label="new")
    r_sc(f)
    r_bar(f, stack=True)
    with f.at("new"):
        f.node(R.A[0], R.MID - 38, R.A[1] - R.A[0], 76, "Request",
               ["or an event,", "a schedule", "or a ticket"], tag="req")
        f.node(R.B[0], R.MID - 38, R.B[1] - R.B[0], 76, "Workflow",
               ["on CI/CD or", "durable", "execution"], tag="wf")
        f.link([(R.A[1], R.MID), (R.B[0], R.MID)], tag="starts")
        f.link([(R.B[1], R.MID), (R.C[0], R.MID)], tag="launches")
    r_sandbox(f, "Sandbox per run", "Coding agent", ["own identity,", "authenticated profile"],
              s="new", stack=True)
    r_proposes(f)
    r_proxy(f, stack=True, s="new")
    f.link([(R.C[1] - 8, R.MID), (R.PROXY[0], R.MID)], tag="traffic")
    r_dest(f)
    r_pr_exit(f)
    with f.at("new"):
        out_card(f, R.PR, "Pull request", ["reviewed", "until ready"], "pr")
        out_card(f, R.APPROVAL, "Approval", APPROVAL_G, "appr")
        out_card(f, R.SLOT3, "Merge", ["approved", "changes"], "merge")
        out_link(f, R.PR, R.APPROVAL)
        out_link(f, R.APPROVAL, R.SLOT3)
    r_outer(f, mid(R.PR), R.MID + 38)
    r_outer_labels(f, "review feedback drives the next run", "old", "new")
    r_floor(f, "all four boundaries’ records, linked by run", "new")


# ── Level 3 ──────────────────────────────────────────────────────────────────
# Drawn to the lead author's composition (his redrawn Level 3, 13 Oct 2026),
# because what Level 3 adds is who runs the show. The orchestrator agent sits
# across the top: requests come into it from the left, context from the right
# and new work from signals, round the outer loop. Everything it does leaves it
# as a line. It divides the work, handing it down to the durable execution
# layer, a separate, plainer card directly beneath it; and it proposes each
# task's scope to the runtime authorization service, the heaviest line in the
# figure. The execution layer's one line drops into the factory and splits,
# each part to its own agent in its own sandbox, behind its own egress proxy,
# with a monitoring agent watching each. The service alone authorizes, and the
# authorized scope goes down to the proxy. What the proxies let through reaches
# the factory's trusted services, the supply chain firewall and the model
# gateway, and what lies downstream, all in the service's column on the right;
# the pull request leaves the same way. The record is inside the frame, and the
# outputs run right to left along the foot, so production's incidents come
# back round to signals.
#
# The authorized scope is drawn into one proxy, the nearer one. With the
# service and the proxies' traffic both to the right and the line that splits
# the work above them, every route into the other proxy crosses a line, so its
# ring alone carries the mark.
class L3:
    REQ = (0, 4, 120, 48)
    ORCH = (160, 0, 440, 52)
    CTX = (590, 0, 720, 60)
    CTX_Y, PROP_Y = 20, 40                 # where context comes in, the proposal leaves
    EXEC = (190, 80, 410, 124)
    AUTH = (460, 80, 720, 124)
    PROP_X = 496                           # the proposal's drop into the service
    LOOP_Y, LOOP_RISE, ORCH_IN = 66, 140, 44   # the outer loop's turn, riser, way in
    LOOP_X = 8
    FRAME = (114, 140, 546, 456)
    LAB = (124, 158)
    ARM_Y = 168
    TOP, SH = 214, 96                      # the sandboxes
    S = ((126, 243), (339, 456))
    LEG = 74                               # where the split lands, right of "Task n"
    PY, PH = 238, 52                       # the proxies, centred on the sandboxes
    P = ((261, 323), (474, 536))
    GRANT_DX, RING_DX = 26, 48             # on a proxy's top: the scope in, its ring
    DROP_DX = 14                           # where the left-hand proxy's traffic leaves
    M_Y = (330, 374)                       # the monitoring agents
    M = ((126, 266), (339, 479))
    EGRESS_Y = 388
    OBS = (126, 400, 536, 444)
    SIG = (0, 300, 100, 456)
    BUS = 556
    COL = (574, 720)
    SC_Y, MG_Y, DOWN_Y = 140, 212, 268
    OUT = (480, 540)
    PROD, DEPLOY, APPR, PR = (16, 142), (162, 260), (280, 448), (468, 576)
    KEY = (590, 366)
    LEGEND_Y = 578


def r_level3(f):
    """Level 3 on its own canvas; returns its height."""
    L = L3
    fx0, fy0, fx1, fy1 = L.FRAME
    f.box(fx0, fy0, fx1 - fx0, fy1 - fy0, "zone", "frame")
    f.lab(*L.LAB, "The factory", "frame.l0")

    # ── the orchestrator, and what comes into it ──
    rx0, ry0, rx1, ry1 = L.REQ
    ox0, oy0, ox1, oy1 = L.ORCH
    f.node(rx0, ry0, rx1 - rx0, ry1 - ry0, "Requests", ["people, tickets"], tag="req")
    f.link([(rx1, mid((ry0, ry1))), (ox0, mid((ry0, ry1)))], tag="req.in")
    cx0, cy0, cx1, cy1 = L.CTX
    with f.at("new"):
        f.node(ox0, oy0, ox1 - ox0, oy1 - oy0, "Orchestrator agent",
               ["decides what happens next"], kind="agent", tag="orch")
        f.node(cx0, cy0, cx1 - cx0, cy1 - cy0, "Context", ["tickets, code,", "conversations"],
               tag="ctx")
        f.link([(cx0, L.CTX_Y), (ox1, L.CTX_Y)], tag="ctx.in")

    # it divides the work: down to the execution layer, a card of its own
    ex0, ey0, ex1, ey1 = L.EXEC
    tx = mid((ex0, ex1))
    with f.at("new"):
        f.link([(tx, oy1), (tx, ey0)], tag="divide")
    with f.at("newtext"):
        f.gloss(tx + 8, ey0 - 10, "divides the work", "divide.l")
    f.node(ex0, ey0, ex1 - ex0, ey1 - ey0, "Durable execution layer", ["CI/CD or a step runner"],
           tag="exec")

    # and it proposes each task's scope, which only the service authorizes
    ax0, ay0, ax1, ay1 = L.AUTH
    with f.at("new"):
        f.link([(ox1, L.PROP_Y), (L.PROP_X, L.PROP_Y), (L.PROP_X, ay0)], tag="propose",
               heavy=True)
    with f.at("newtext"):
        f.gloss(L.PROP_X + 8, ay0 - 22, "proposes", "propose.l0")
        f.gloss(L.PROP_X + 8, ay0 - 7.5, "task scope", "propose.l1")
    f.node(ax0, ay0, ax1 - ax0, ay1 - ay0, "Runtime authorization service", [AUTH_G],
           kind="guard", num=BN[IAM], tag="auth")

    # ── the factory: one line splits the work, each part to its own agent ──
    legs = [s[0] + L.LEG for s in L.S]
    with f.at("new"):
        f.link([(tx, ey1), (tx, L.ARM_Y)], head=False, tag="split", group="split", dot=True)
        for i, lx in enumerate(legs):
            f.link([(tx, L.ARM_Y), (lx, L.ARM_Y), (lx, L.TOP)], tag=f"split{i}", group="split")
    with f.at("newtext"):
        c = mid(legs)
        for i, s in enumerate(("each part to its own agent,", "with narrowed authority")):
            f.gloss(c - TINT_W[f"serif|400|{f.gs:g}|{s}"] / 2, L.ARM_Y + 18 + 14.5 * i, s,
                    f"split.l{i}")
    for i, (sx0, sx1) in enumerate(L.S):
        f.box(sx0, L.TOP, sx1 - sx0, L.SH, "sandbox", f"sbx{i}")
        f.badge(sx0, L.TOP, BN[SANDBOX], f"sbx{i}")
        tx0 = sx0 + PAD + 4
        f.lab(tx0, L.TOP + 20, f"Task {i + 1}", f"sbx{i}.l")
        f.name(tx0, L.TOP + 40, "Coding agent", f"sbx{i}.n")
        f.gloss(tx0, L.TOP + 56, "own identity", f"sbx{i}.g0")
        f.gloss(tx0, L.TOP + 70.5, "and task scope", f"sbx{i}.g1")
        f.loop_glyph(sx0 + PAD + 11, L.TOP + 84, f"sbx{i}.loop")
        f.gloss(sx0 + PAD + 26, L.TOP + 88, "inner loop", f"sbx{i}.lp")
    pm = L.PY + L.PH / 2
    for i, (px0, px1) in enumerate(L.P):
        # the network's mark on its corner; identity and access's ring on its
        # top, where the authorized scope comes in
        f.node(px0, L.PY, px1 - px0, L.PH, ["Egress", "proxy"], [], kind="guard",
               num=BN[NETWORK], tag=f"proxy{i}")
        f.badge(px0 + L.RING_DX, L.PY, BN[IAM], f"proxy{i}", light=True)
        f.link([(L.S[i][1], pm), (px0, pm)], tag=f"traffic{i}")
    gx = L.P[1][0] + L.GRANT_DX
    f.link([(gx, ay1), (gx, L.PY)], "grant", tag="grant")
    for i, s in enumerate(("authorized", "scope")):
        f.gloss(gx - 8 - f.width(s, "gloss"), fy0 + 16 + 14.5 * i, s, f"grant.l{i}")
    with f.at("new"):
        for i, (mx0, mx1) in enumerate(L.M):
            f.node(mx0, L.M_Y[0], mx1 - mx0, L.M_Y[1] - L.M_Y[0], "Monitoring agent",
                   ["watches for drift"], kind="agent", tag=f"mon{i}")
            wx = mid(L.S[i])
            f.link([(wx, L.M_Y[0]), (wx, L.TOP + L.SH)], "watch", tag=f"watch{i}")
    ob = L.OBS
    gx_ = record(f, *ob)
    with f.at("newtext"):
        f.gloss(gx_, ob[1] + 28, "telemetry and evals across all runs", "obs.g")

    # ── the trusted services the proxies reach, under the service ──
    cx0, cx1 = L.COL
    cw = cx1 - cx0
    f.node(cx0, L.SC_Y, cw, card_h(["x"], ["x", "x"]), ["Supply chain", "firewall"],
           ["approved, scanned"], kind="guard", num=BN[SUPPLY], tag="sc")
    f.node(cx0, L.MG_Y, cw, card_h(["x"]), "Model gateway", ["approved models"], kind="guard",
           tag="mg")
    f.node(cx0, L.DOWN_Y, cw, card_h(["x", "x"]), "Downstream",
           ["source control,", "APIs, MCP servers"], tag="down")
    ys = [L.SC_Y + card_h(["x"], ["x", "x"]) / 2, L.MG_Y + card_h(["x"]) / 2,
          L.DOWN_Y + card_h(["x", "x"]) / 2]
    o0, o1 = L.OUT
    # the proxies' traffic, and the pull request, leave by one bus
    f.link([(L.P[1][1], pm), (L.BUS, pm)], head=False, tag="bus.in1", group="bus")
    dx = L.P[0][0] + L.DROP_DX
    f.link([(dx, L.PY + L.PH), (dx, L.EGRESS_Y), (L.BUS, L.EGRESS_Y)], head=False,
           tag="bus.in0", group="bus")
    f.link([(L.BUS, ys[0]), (L.BUS, o0)], tag="bus", group="bus")
    for i, y in enumerate(ys):
        f.link([(L.BUS, y), (cx0, y)], tag=f"bus.{i}", group="bus")

    # ── what leaves, right to left, and the outer loop back to the orchestrator ──
    om = mid(L.OUT)
    f.node(L.PR[0], o0, L.PR[1] - L.PR[0], o1 - o0, "Pull request", ["reviewed", "until ready"],
           tag="pr")
    f.node(L.APPR[0], o0, L.APPR[1] - L.APPR[0], o1 - o0, "Approval", APPROVAL_G, tag="appr")
    f.link([(L.PR[0], om), (L.APPR[1], om)], tag="out.pr")
    sx0, sy0, sx1, sy1 = L.SIG
    with f.at("new"):
        f.node(L.DEPLOY[0], o0, L.DEPLOY[1] - L.DEPLOY[0], o1 - o0, "Deploy",
               ["can be", "rolled back"], tag="deploy")
        f.node(L.PROD[0], o0, L.PROD[1] - L.PROD[0], o1 - o0, "Production",
               ["emits incidents", "and metrics"], tag="prod")
        f.link([(L.APPR[0], om), (L.DEPLOY[1], om)], tag="out.appr")
        f.link([(L.DEPLOY[0], om), (L.PROD[1], om)], tag="out.deploy")
        f.node(sx0, sy0, sx1 - sx0, sy1 - sy0, "Signals",
               ["incidents,", "scanner", "findings,", "monitoring,", "evals"], tag="sig")
        f.link([(88, o0), (88, sy1)], "loop", tag="incidents")
        f.link([(ob[0], mid((ob[1], ob[3]))), (sx1, mid((ob[1], ob[3])))], "loop", tag="evals")
        f.link([(L.LOOP_X, sy0), (L.LOOP_X, L.LOOP_Y), (L.LOOP_RISE, L.LOOP_Y),
                (L.LOOP_RISE, L.ORCH_IN), (ox0, L.ORCH_IN)], "loop", tag="outer")
    f.lab(L.LOOP_X + 10, L.LOOP_Y + 24, "outer loop", "outer.l")
    with f.at("newtext"):
        f.gloss(L.LOOP_X + 10, L.LOOP_Y + 38.5, "new work", "outer.g")

    legend(f, 0, L.LEGEND_Y, W)
    delta_key(f, L.KEY[0], L.KEY[1], PREV[3])
    return L.LEGEND_Y + 8


PREV = {1: "as in Figure 2", 2: "as at Level 1", 3: "as at Level 2"}


def build_level(n):
    f = CF(f"sf{n + 2}", W, R.H, CAPTION[n + 2], ALT[n + 2], level=n)
    if n == 3:                     # its own composition, its own height and key
        f.set_height(r_level3(f))
    else:
        {1: r_level1, 2: r_level2}[n](f)
        delta_key(f, R.KEY[0], R.KEY[1], PREV[n])
        f.set_height(R.H)
    f.write(f"figure-{n + 2}")


# ── the levels on a phone: the same skeleton in one column ───────────────────
NW = 360


class NR:
    RAIL = 4
    X0, X1 = 24, 360
    A = (24, 214)
    IN = (36, 214)
    PROXY = (232, 336)
    BUS = 348
    DEST = (24, 326)
    BAR = (36, 330)
    GX = 74
    GRANT_X = 296
    PROP_X = 150
    GUTTER = 16
    KEY = (232, 30)
    # supply chain scanning, between the start card and the frame, clear
    # of the line from one to the other. Its component check drops right of
    # the frame's label and turns into the path that starts the agent; its
    # package check drops down the frame's right-hand side, which is empty
    # above the proxy
    SC = (96, 352)
    LAUNCH_X, PKG_X = 262, 328


def narrow_sc(f, y):
    """Supply chain scanning on a phone, its line in two, its component
    check's label under it, left of the line; returns its foot."""
    bot = sc_card(f, NR.SC[0], y, NR.SC[1], ("approved versions", "the profile allows"))
    f.gloss(NR.LAUNCH_X - 8 - f.width(SC_LAUNCH, "gloss"), bot + 18, SC_LAUNCH, "sc.launch.l")
    return bot


def narrow_launch(f, bot, y_turn, join=None, into=None):
    """Scanning's component check: down the right-hand side, then left
    at y_turn, either joining the line that launches the agent (`join`, its
    x) or turning down into the sandbox's top (`into`, (x, top))."""
    if into:
        x, top = into
        f.link([(NR.LAUNCH_X, bot), (NR.LAUNCH_X, y_turn), (x, y_turn), (x, top)],
               tag="sc.launch")
    else:
        f.link([(NR.LAUNCH_X, bot), (NR.LAUNCH_X, y_turn), (join, y_turn)], tag="sc.launch",
               head=False, dot=True)


def narrow_pkg(f, bot, py0):
    """The proxy's package check, both ways, labelled just above the proxy."""
    f.link([(NR.PKG_X, bot), (NR.PKG_X, py0)], tag="sc.pkg", both=True)
    for i, s in enumerate(("checks", "packages")):
        f.gloss(NR.PKG_X - 8 - f.width(s, "gloss"), py0 - 22.5 + i * 14.5, s, f"sc.pkg.l{i}")


def narrow_level(n):
    f = CF(f"sf{n + 2}n", NW, 1600, CAPTION[n + 2], ALT[n + 2], narrow=True, level=n)
    y = 10
    a = {1: ("Developer", ["kicks off each run"]),
         2: ("Request", ["or an event, a schedule", "or a ticket"]),
         3: ("Signals and requests", ["incidents, scanner", "findings, evals"])}[n]
    ah = card_h(a[1])
    with f.at("new"):
        f.node(NR.A[0], y, NR.A[1] - NR.A[0], ah, a[0], a[1], tag="start")
    delta_key(f, NR.KEY[0], NR.KEY[1], PREV[n])
    a_mid = y + ah / 2
    prev = y + ah
    sc_bot = narrow_sc(f, prev + 24)
    # at Level 1 the component check joins the developer's line above the
    # frame, in a gap made for it, so it never runs under the frame's label
    fy0 = sc_bot + (42 if n == 1 else 28)
    if n == 1:
        narrow_launch(f, sc_bot, sc_bot + 28, join=NR.GX)
    with f.at("newtext" if n == 2 else "old"):
        f.lab(NR.GX + 14, fy0 + 22, "Developer’s machine" if n == 1 else "The factory", "frame.l")
    y = fy0 + 40
    if n in (1, 2):                # as wide, and as the alt text says
        with f.at("newtext" if n == 2 else "old"):
            f.gloss(NR.GX + 14, fy0 + 38, "or a remote environment" if n == 1 else "a shared service",
                    "frame.g")
        y += 14.5
    ix0, ix1 = NR.IN
    orch = None
    if n == 2:
        with f.at("new"):
            f.node(ix0, y, ix1 - ix0, 60, "Workflow", ["on CI/CD or durable", "execution"],
                   tag="wf")
            f.link([(NR.GX, prev), (NR.GX, y)], tag="starts")
        prev = y + 60
        y += 60 + 24
        narrow_launch(f, sc_bot, prev + 12, join=NR.GX)
    elif n == 3:
        oy = y
        with f.at("new"):
            # the wide figure's words on its proposal, which here runs down
            # the gutter with no room for them
            og = ["proposes profile", "and task scope"]
            oh = card_h(og)
            f.node(ix0, y, ix1 - ix0, oh, "Orchestrator agent", og, kind="agent", tag="orch")
            f.link([(NR.GX, prev), (NR.GX, y)], tag="takes")
        orch = oy + 22
        y += oh + 24
        # no line from the orchestrator: its plan is a proposal to the
        # service, never an instruction that starts agents
        f.node(ix0, y, ix1 - ix0, 44, "Execution layer", ["starts each agent"], tag="exec")
        prev = y + 44
        y += 44 + 24
        narrow_launch(f, sc_bot, prev + 12, join=NR.GX)
    if n == 3:
        mids = []
        for i in range(3):
            with f.at("new"):
                f.box(ix0, y, ix1 - ix0, 46, "sandbox", f"sbx{i}")
                f.badge(ix0, y, BN[SANDBOX], f"sbx{i}")
            f.name(ix0 + PAD + 4, y + 20, f"Agent, task {i + 1}", f"sbx{i}.n")
            f.gloss(ix0 + PAD + 4, y + 36, "own identity and scope", f"sbx{i}.g")
            f.loop_glyph(ix1 - 16, y + 14, f"sbx{i}.loop")
            if i == 0:
                f.link([(NR.GX, prev), (NR.GX, y)], tag="starts")
            mids.append(y + 23)
            y += 46 + STACK
        sb_mid = mids[1]
        sb_bottom = y - STACK
        y += 16
        with f.at("new"):
            f.node(ix0, y, ix1 - ix0, 60, "Monitoring agent", ["watches work", "in progress"],
                   kind="agent", tag="mon")
            f.link([(NR.GX + 60, y), (NR.GX + 60, sb_bottom)], "watch", tag="watch")
        y += 60 + 16
    else:
        glosses = (["own identity,", "authenticated profile"] if n == 2 else
                   ["configured by", "its profile"])
        sh = 132
        with f.at("new" if n == 2 else "old"):
            if n == 2:
                for d in (6, 3):
                    f.ghost(ix0 + d, y + d, ix1 - ix0 - 6, sh - 6, f"ghost{d}", "sandbox")
            sw = ix1 - ix0 - (6 if n == 2 else 0)
            f.box(ix0, y, sw, sh - (6 if n == 2 else 0), "sandbox", "sbx")
            f.badge(ix0, y, BN[SANDBOX], "sbx")
        f.lab(ix0 + PAD + 4, y + 24, "Sandbox per run" if n == 2 else "Sandbox", "sbx.l")
        f.name(ix0 + PAD + 4, y + 50, "Coding agent", "sbx.n")
        for i, g_ in enumerate(glosses):
            f.gloss(ix0 + PAD + 4, y + 66 + i * 14.5, g_, f"sbx.g{i}")
        with f.at("new" if n == 1 else "old"):
            f.link([(NR.GX, prev), (NR.GX, y)], tag="into")
        f.loop_glyph(ix0 + PAD + 11, y + 100, "sbx.loop")
        f.gloss(ix0 + PAD + 26, y + 104, "inner loop,", "sbx.lp0")
        f.gloss(ix0 + PAD + 26, y + 118.5, "until it passes", "sbx.lp1")
        sb_mid = y + 62
        sb_bottom = y + sh
        y += sh + 16
    fy1 = y
    ph = card_h(PROXY_G) + 8           # room under its line for the ring on its foot
    py0 = sb_mid - ph / 2
    f.box(NR.X0, fy0, NR.X1 - NR.X0, fy1 - fy0, "zone", "frame")
    with f.at("new" if n == 2 else "old"):
        if n > 1:
            for d in (6, 3):
                f.ghost(NR.PROXY[0] + d, py0 + d, NR.PROXY[1] - NR.PROXY[0], ph, f"pghost{d}", "proxy")
        proxy_card(f, NR.PROXY[0], py0, NR.PROXY[1], py0 + ph, PROXY_G, NR.GRANT_X,
                   kind="guardfill" if n > 1 else "guard")
    narrow_pkg(f, sc_bot, py0)
    f.link([(ix1 - (6 if n == 2 else 0), sb_mid), (NR.PROXY[0], sb_mid)], tag="traffic")
    # the authorization service, beneath the frame; its decision rises into the proxy
    by0 = fy1 + 40
    bh = card_h([AUTH_G])
    f.node(NR.BAR[0], by0, NR.BAR[1] - NR.BAR[0], bh, "Runtime authorization service", [AUTH_G],
           kind="guard", num=BN[IAM], tag="auth")
    f.link([(NR.GRANT_X, by0), (NR.GRANT_X, py0 + ph + (6 if n > 1 else 0))], "grant",
           tag="grant")
    for i, s in enumerate(("authorized", "scope")):
        f.gloss(NR.GRANT_X - 8 - f.width(s, "gloss"), fy1 + 14 + i * 14.5, s, f"grant.l{i}")
    if orch is None:               # the agent proposes the scope it needs (Figure 2)
        f.link([(NR.PROP_X, sb_bottom), (NR.PROP_X, by0)], tag="propose")
        for i, s in enumerate(("proposes", "scope")):
            f.gloss(NR.PROP_X - 8 - f.width(s, "gloss"), fy1 + 14 + i * 14.5, s, f"propose.l{i}")
    else:                          # Level 3: the orchestrator's proposal, down the gutter
        with f.at("new"):
            f.link([(ix0, orch), (NR.GUTTER, orch), (NR.GUTTER, by0 + bh / 2),
                    (NR.BAR[0], by0 + bh / 2)], tag="propose", heavy=True)
    # what the proxy lets through, fed down the right edge past the bar
    order = [DEST[2], DEST[3], DEST[1], DEST[0]]
    y = by0 + bh + 24
    ys = []
    for i, (nm, _, kind) in enumerate(order):
        node_c(f, NR.DEST[0], y, NR.DEST[1] - NR.DEST[0], DEST_H, " ".join(nm), kind=kind,
               tag=f"dest{i}")
        ys.append(y + DEST_H / 2)
        y += DEST_H + STACK
    # the pull request leaves through the proxy like everything else, as it
    # does wide and in Figure 6: the same bus, one more branch
    y += 16
    pr_mid = y + 23
    f.link([(NR.PROXY[1], sb_mid), (NR.BUS, sb_mid)], head=False, tag="bus.in", group="bus")
    f.link([(NR.BUS, sb_mid), (NR.BUS, ys[-1])], head=False, tag="bus", group="bus")
    for i, yy in enumerate(ys):
        f.link([(NR.BUS, yy), (NR.DEST[1], yy)], tag=f"bus.{i}", group="bus")
    with f.at("new" if n == 1 else "old"):
        f.link([(NR.BUS, ys[-1]), (NR.BUS, pr_mid)], head=False, tag="bus.prx", group="bus")
        f.link([(NR.BUS, pr_mid), (NR.DEST[1], pr_mid)], tag="bus.pr", group="bus")
    outs = {1: [("Pull request", ["reviewed by the developer"], 1)],
            2: [("Pull request", ["reviewed until ready"], 2),
                ("Approval", APPROVAL_G, 2),
                ("Merge", ["approved changes"], 2)],
            3: [("Pull request", ["reviewed until ready"], 2),
                ("Approval", APPROVAL_G, 2),
                ("Deploy", ["can be rolled back"], 3),
                ("Production", ["emits incidents and metrics"], 3)]}[n]
    for i, (nm, g, since) in enumerate(outs):
        with f.at("new" if since == n else "old"):
            f.node(NR.X0, y, (NR.DEST[1] if i == 0 else NR.X1) - NR.X0, 46, nm, g, tag=f"out{i}")
        y += 46
        if i < len(outs) - 1:
            with f.at("new" if outs[i + 1][2] == n else "old"):
                f.link([(NR.GX, y), (NR.GX, y + 22)], tag=f"o{i}")
            y += 22
    ly = y + 24
    with f.at("new" if n in (1, 3) else "old"):
        f.link([(NR.GX, y), (NR.GX, ly), (NR.RAIL, ly), (NR.RAIL, a_mid), (NR.A[0], a_mid)], "loop",
               tag="outer")
    with f.at("newtext" if n == 1 else "old"):
        f.lab(NR.GX + 10, ly - 8, "outer loop", "outer.l")
    with f.at("newtext"):
        gloss = {1: "the developer drives the next run", 2: "review feedback drives the next run",
                 3: "production signals start new work"}[n]
        f.gloss(NR.GX + 10, ly + 14, gloss, "outer.g")
    y = ly + 32
    obs = {1: "harness logs, identity and proxy records",
           2: "all four boundaries’ records, by run",
           3: "telemetry and evals across all runs"}[n]
    record(f, NR.X0, y, NR.X1, y + 48, two=True)
    with f.at("newtext" if n > 1 else "old"):
        f.gloss(NR.X0 + PAD, y + 39, obs, "obs.g")
    y += 48
    if n == 1:
        f.rule(y + 14, NR.X0, NR.X1)
        y = key_grid(f, NR.X0, y + 36)
    f.set_height(y + 2)
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
# lies behind it. Above it, supply chain scanning, on the profile's launch
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
    # supply chain scanning, above the row: the profile configures the
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
    """Figure 2 on a phone: the profile, supply chain scanning on its
    launch path, the sandbox beside the proxy, what the proxy lets through under the
    proxy, the decision beneath both, its trusted context in one card under
    it, and what it routes elsewhere down the right edge: approval, then a
    stop for anything outside policy."""
    f = CF("sf2n", NW, 1400, CAPTION[2], ALT[2], narrow=True)
    X, R1 = 8, 352
    y = 10
    f.node(X, y, R1 - X, 44, "Profile", PROFILE_G, tag="prof")
    pb = y + 44
    # supply chain scanning, on the profile's launch path; the profile's
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
# Figure 6 — only a new authorization decision can widen a task. The levels'
# skeleton with one incident's values ("A factory in action").
# ═════════════════════════════════════════════════════════════════════════════
FIG6_AUTH = "checks policy and the alert’s source"
BLOCKED_G = ["blocked: not", "in the task"]   # the proxy blocking, never "outside policy"
# what the orchestrator proposes, wide and narrow alike
FIG6_TASK = ["proposes payments", "logs, last hour;", "one pull request"]
FIG6_ALERT = ["payments", "errors"]


def figure6():
    f = CF("sf6", W, 800, CAPTION[6], ALT[6])
    r_frame(f, label=["The factory"])
    # no path starts the agent here, so the component check lands on the
    # sandbox itself
    r_sc(f, launch=(420, None))
    f.node(R.A[0], R.MID - 38, R.A[1] - R.A[0], 76, ["Production", "alert"], FIG6_ALERT,
           tag="sig")
    node_c(f, R.B[0], R.MID - 26, R.B[1] - R.B[0], 52, ["Orchestrator", "agent"], kind="agent",
           tag="orch")
    f.link([(R.A[1], R.MID), (R.B[0], R.MID)], tag="takes")
    # what the task asks for rides on the proposal, into the authorization service
    px = 210
    f.link([(px, R.MID + 26), (px, R.BAR[1])], tag="propose")
    for i, s in enumerate(FIG6_TASK):
        f.gloss(px + 8, 302 + i * 14.5, s, f"propose.l{i}")
    r_sandbox(f, "Sandbox", "Incident agent", ["configured by", "its profile"],
              loop=("inner loop,", "until tests pass"))
    # wanting more is a request for a new decision, never a grant; its words
    # sit right of its own line, so the line parts them from the proposal's
    wx = 356
    f.link([(wx, R.ROW[1]), (wx, R.BAR[1])], tag="wider")
    for i, s in enumerate(("needs a new", "decision")):
        f.gloss(wx + 8, 302 + i * 14.5, s, f"wider.l{i}")
    r_proxy(f)
    f.link([(R.C[1], R.MID), (R.PROXY[0], R.MID)], tag="traffic")
    r_bar(f, gloss=FIG6_AUTH)
    r_dest(f, [(["Payments", "service logs"], ["last hour only"], "card"),
               (["Authentication", "service logs"], BLOCKED_G, "blocked"),
               (["Package", "registries"], [], "card")])
    # the fix: one pull request, approval, a small first deploy, the error rate
    slots = [(134, 238), (258, 432), (452, 568), (588, 696)]
    o0, o1 = R.OUT
    f.link([(R.EXIT_X, R.PROXY[3]), (R.EXIT_X, R.EXIT_Y), (mid(slots[0]), R.EXIT_Y),
            (mid(slots[0]), o0)], tag="pr.exit")
    for slot, (n_, g_, t_) in zip(slots, [("Pull request", ["one, as", "granted"], "pr"),
                                          ("Approval", APPROVAL_G, "appr"),
                                          ("Deploy", ["small share of", "traffic first"], "deploy"),
                                          ("Production", ["error rate", "afterward"], "prod")]):
        f.node(slot[0], o0, slot[1] - slot[0], o1 - o0, n_, g_, tag=t_)
    for a, b in zip(slots, slots[1:]):
        f.link([(a[1], mid((o0, o1))), (b[0], mid((o0, o1)))], tag=f"out{a[0]}")
    loopy = R.LOOPY
    f.link([(mid(slots[3]), o1), (mid(slots[3]), loopy), (R.LOOP_X, loopy),
            (R.LOOP_X, R.MID + 38)], "loop", tag="outer")
    f.lab(R.LOOP_LABEL_X, loopy - 24, "outer loop", "outer.l")
    f.gloss(R.LOOP_LABEL_X, loopy - 8, "confirms the fix or starts the next run", "outer.g")
    f.set_height(loopy + 8)
    f.write("figure-6")


def figure6_narrow():
    f = CF("sf6n", NW, 1600, CAPTION[6], ALT[6], narrow=True)
    y = 10
    f.node(NR.A[0], y, NR.A[1] - NR.A[0], 44, "Production alert", [" ".join(FIG6_ALERT)],
           tag="start")
    a_mid = y + 22
    prev = y + 44
    sc_bot = narrow_sc(f, prev + 24)
    fy0 = sc_bot + 28
    f.lab(NR.GX + 14, fy0 + 22, "The factory", "frame.l")
    y = fy0 + 40
    ix0, ix1 = NR.IN
    oh = card_h(FIG6_TASK)
    f.node(ix0, y, ix1 - ix0, oh, "Orchestrator agent", FIG6_TASK, kind="agent", tag="orch")
    f.link([(NR.GX, prev), (NR.GX, y)], tag="takes")
    orch = y + 22
    y += oh + 40                   # room for supply chain's line to turn into the sandbox
    sy0, sh = y, 132
    f.box(ix0, sy0, ix1 - ix0, sh, "sandbox", "sbx")
    f.badge(ix0, sy0, BN[SANDBOX], "sbx")
    f.lab(ix0 + PAD + 4, sy0 + 24, "Sandbox", "sbx.l")
    f.name(ix0 + PAD + 4, sy0 + 50, "Incident agent", "sbx.n")
    f.gloss(ix0 + PAD + 4, sy0 + 66, "configured by", "sbx.g0")
    f.gloss(ix0 + PAD + 4, sy0 + 80.5, "its profile", "sbx.g1")
    f.loop_glyph(ix0 + PAD + 11, sy0 + 100, "sbx.loop")
    f.gloss(ix0 + PAD + 26, sy0 + 104, "inner loop,", "sbx.lp0")
    f.gloss(ix0 + PAD + 26, sy0 + 118.5, "until tests pass", "sbx.lp1")
    narrow_launch(f, sc_bot, sy0 - 20, into=(190, sy0))
    sb_mid = sy0 + 62
    fy1 = sy0 + sh + 16
    f.box(NR.X0, fy0, NR.X1 - NR.X0, fy1 - fy0, "zone", "frame")
    ph = card_h(PROXY_G) + 8
    py0 = sb_mid - ph / 2
    proxy_card(f, NR.PROXY[0], py0, NR.PROXY[1], py0 + ph, PROXY_G, NR.GRANT_X)
    narrow_pkg(f, sc_bot, py0)
    f.link([(ix1, sb_mid), (NR.PROXY[0], sb_mid)], tag="traffic")
    by0 = fy1 + 40
    bh = card_h([FIG6_AUTH])
    f.node(NR.BAR[0], by0, NR.BAR[1] - NR.BAR[0], bh, "Runtime authorization service",
           [FIG6_AUTH], kind="guard", num=BN[IAM], tag="auth")
    f.link([(NR.GRANT_X, by0), (NR.GRANT_X, py0 + ph)], "grant", tag="grant")
    for i, s in enumerate(("authorized", "scope")):
        f.gloss(NR.GRANT_X - 8 - f.width(s, "gloss"), fy1 + 14 + i * 14.5, s, f"grant.l{i}")
    f.link([(ix0, orch), (NR.GUTTER, orch), (NR.GUTTER, by0 + bh / 2), (NR.BAR[0], by0 + bh / 2)],
           tag="propose")
    wx = 150
    f.link([(wx, sy0 + sh), (wx, by0)], tag="wider")
    for i, s in enumerate(("needs a new", "decision")):
        f.gloss(wx - 8 - f.width(s, "gloss"), fy1 + 14 + i * 14.5, s, f"wider.l{i}")
    y = by0 + bh + 24
    dests = [("Payments service logs", ["last hour only"], "card"),
             ("Authentication service logs", [" ".join(BLOCKED_G)], "blocked"),
             ("Package registries", [], "card")]
    ys = []
    for i, (nm, g, kind) in enumerate(dests):
        if g:
            f.node(NR.DEST[0], y, NR.DEST[1] - NR.DEST[0], 44, nm, g, kind=kind, tag=f"dest{i}")
        else:
            node_c(f, NR.DEST[0], y, NR.DEST[1] - NR.DEST[0], 44, nm, kind=kind, tag=f"dest{i}")
        ys.append((y + 22, kind))
        y += 44 + STACK
    # the pull request leaves through the proxy like everything else: the
    # same bus, one more branch
    y += 16
    pr_mid = y + 23
    f.link([(NR.PROXY[1], sb_mid), (NR.BUS, sb_mid)], head=False, tag="bus.in", group="bus")
    f.link([(NR.BUS, sb_mid), (NR.BUS, pr_mid)], head=False, tag="bus", group="bus")
    for i, (yy, kind) in enumerate(ys):
        f.link([(NR.BUS, yy), (NR.DEST[1], yy)], tag=f"bus.{i}", group="bus", bar=(kind == "blocked"))
    f.link([(NR.BUS, pr_mid), (NR.DEST[1], pr_mid)], tag="bus.pr", group="bus")
    outs = [("Pull request", ["one, as granted"]),
            ("Approval", APPROVAL_G),
            ("Deploy", ["small share of traffic first"]), ("Production", ["error rate afterward"])]
    for i, (nm, g) in enumerate(outs):
        f.node(NR.X0, y, (NR.DEST[1] if i == 0 else NR.X1) - NR.X0, 46, nm, g, tag=f"out{i}")
        y += 46
        if i < len(outs) - 1:
            f.link([(NR.GX, y), (NR.GX, y + 22)], tag=f"o{i}")
            y += 22
    ly = y + 24
    f.link([(NR.GX, y), (NR.GX, ly), (NR.RAIL, ly), (NR.RAIL, a_mid), (NR.A[0], a_mid)], "loop",
           tag="outer")
    f.lab(NR.GX + 10, ly - 8, "outer loop", "outer.l")
    f.gloss(NR.GX + 10, ly + 14, "confirms the fix or", "outer.g0")
    f.gloss(NR.GX + 10, ly + 28.5, "starts the next run", "outer.g1")
    f.set_height(ly + 34)
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
