#!/usr/bin/env python3
"""The Secure Software Factory — its six figures, generated.

Drawn with the first paper's kit (whitepaper/figures/figkit.py): the same plate,
the same four voices (Figtree names, Plex Serif glosses, Chakra Petch labels,
Plex Mono numerals) and the same hairline cards. Structure comes from position,
whitespace and hairlines. Colour encodes exactly one thing, the paper's own
central distinction:

  * GUARD (the site's accent) marks what is enforced outside the agent's loop —
    the four boundaries, the enforcement infrastructure and the record. Each
    boundary carries its number on the corner of the part that enforces it:
    1 Identity and access, 2 Supply chain, 3 Sandbox, 4 Network.
  * WASH marks untrusted agent execution: the inside of a sandbox, and any
    agent that plans or watches from outside one.

Everything else is ink on the plate. The levels (Figures 3–5) are each drawn
complete, and what a level adds is marked by weight and a pale tint (NEWT),
which survive a greyscale print and leave the accent its one meaning:

  new card       tint fill (a wash card keeps its wash) and a heavier outline
  new connector  ink, heavier
  new words      outside a card, set on the tint
  carried over   drawn as the level before drew it

Figure 2 draws the architecture once, as one row — the profile, the agent in
its sandbox, the egress proxy, and what lies behind it — with the runtime
authorization service beneath it as a decision, not a container: the profile's
bounds and the agent's proposal (a request, never a grant) come into it from
above, the rest of the trusted context (the agent and whoever it acts for, the
task, any delegation, policy) from below as one box and one arrow; up out of
it goes the scope the proxy enforces, and to its right high-impact actions to
approval and, ending in a stop, anything outside policy. Figures 3 to 6 reuse
that row, the service as the bar beneath it, and the record as its own band,
so flipping Figure 3 → 4 → 5 shows what was added and who took over, never a
re-layout. Figure 1 is the process the boundaries serve, so it has its own
composition.

Every label is the paper's vocabulary (final draft, 12 October 2026). Sizes are
set for the PDF column: at 150 mm (425.2 pt) a 736-unit canvas prints at 0.578
pt per unit, so the smallest run here (12.25 units) prints at 7.08 pt.

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
    # Figure 2's is proposed, not yet the paper's: the paper's two sentences, in
    # their order, with what the drawing now adds after them. The owner approves
    # it and the paper takes it before this ships (check-copy holds the two equal).
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

    def badge(self, cx, cy, n, tag):
        """A boundary number: an accent disc with the numeral knocked out. It
        sits on the corner of the part that enforces the boundary, so it reads
        as a mark on that part rather than as a word in its name."""
        self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="{GUARD}"/>')
        self.text(cx - 3.3, cy + 3.9, str(n), self.ns, C["plate"], "600", True, tag=f"#{tag}")
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


# What the proxy lets through — the same four at every level. The admission
# point is the paper's generic term ("an admission point, such as a registry or
# a dedicated firewall"), so the label holds from Level 1, where it is an
# approved registry, to Level 3, where it is usually a supply chain firewall.
DEST = [  # (name, gloss lines, kind, boundary)
    ("Source control", ["the repository"], "card", None),
    ("Services", ["the task needs"], "card", None),
    ("Model gateway", ["approved models"], "guard", None),
    ("Admission point", ["approved,", "scanned", "packages"], "guard", 2),
]


def card_h(gloss, name=""):
    """A destination card's height: one name line and one gloss line is 44;
    each further line adds its leading."""
    names = len(name) if isinstance(name, (list, tuple)) else 1
    # each further line at its leading (15 for names, 14.5 for glosses),
    # rounded up to even units so every fan branch lands on a whole unit
    return 44 + 16 * (names - 1) + 16 * max(len(gloss) - 1, 0)


# The key's own text, measured: Chrome, the site's IBM Plex Serif 400 at 12.25
# units (GLOSS), getComputedTextLength (12 Oct 2026). The key is spaced by these,
# with one constant gap. Spaced by the checker's deliberately pessimistic
# estimate, which overstates long phrases (+24 units on "Identity and access")
# and slightly understates short capitalised words, evenly meant items came out
# about three times further apart in one place than another.
KEY_W = {"Enforced outside the agent’s loop:": 194.34, "Identity and access": 110.31,
         "Supply chain": 75.2, "Sandbox": 50.2, "Network": 49.3}
KEY_GAP = 14


def legend(f, x, y, width, marks=((1, "Identity and access"), (3, "Sandbox"), (4, "Network"))):
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


ALL_MARKS = ((1, "Identity and access"), (2, "Supply chain"), (3, "Sandbox"), (4, "Network"))


def key_grid(f, x, y, marks=ALL_MARKS, cols=2):
    """Figure 2's key in a block: its heading, then the marks in a grid, each
    column as wide as its widest measured name, one gap between. For a figure
    whose free space is a corner rather than a line."""
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
# Approval reads the same in Figures 2, 4, 5 and 6 (the glossary's approval
# policy: "approved automatically or waits for a person"); the proxy, in every
# level, where its card is too narrow for Figure 2's longer gloss.
APPROVAL_G = ["a person, or automatic;", "never the agent"]
PROXY_G = ["default-deny,", "enforces it,", "attaches", "credentials"]

# Words set on the tint, measured: Chrome, the site's fonts at the size each is
# set, getComputedTextLength, without letter-spacing (12 Oct 2026). The tint is
# drawn to the measured width; figkit's estimate overstates long runs by up to a
# tenth, which would leave a ragged tail of tint. A run that isn't here stops
# the build rather than guessing.
TINT_W = {
    "label|500|12.25|OUTER LOOP": 73.09,
    "label|500|12.25|THE FACTORY": 77.53,
    "label|500|12.5|OUTER LOOP": 74.58,
    "label|500|12.5|THE FACTORY": 79.11,
    "serif|400|12.25|a shared service with its own identity": 213.55,
    "serif|400|12.25|and task scope": 85.08,
    "serif|400|12.25|production signals start new work": 195.89,
    "serif|400|12.25|proposes profile": 93.53,
    "serif|400|12.25|records from all four boundaries, linked by run; evals track quality": 381.53,
    "serif|400|12.25|review feedback drives the next run": 205.91,
    "serif|400|12.25|telemetry and evals across runs; monitoring of running agents": 359.33,
    "serif|400|12.25|the developer drives the next run": 190.73,
    "serif|400|12.5|production signals start new work": 199.89,
    "serif|400|12.5|records from all four boundaries, by run": 235.69,
    "serif|400|12.5|review feedback drives the next run": 210.11,
    "serif|400|12.5|telemetry, evals, monitoring of agents": 220.86,
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
             heavy=False, stop=False):
        """SF's connectors, plus watch (dotted, no head: watching, not acting)
        and heavy (Level 3's proposal, the line that matters most). A grant,
        the decision going out, is solid accent and heavier than any flow:
        dashes already mean the frames, the outer loop and a stop."""
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


# ── shared pieces ────────────────────────────────────────────────────────────
def node_c(f, x, y, w, h, name, kind="card", num=None, tag=""):
    """A card carried over with its name only, centred in the same box it had."""
    f.box(x, y, w, h, kind, tag)
    if num:
        f.badge(x, y, num, tag)
    f.name(x + PAD, y + h / 2 + 4.5, name, f"{tag}.n0")


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
# lets through. Rows: the frame where agents run, the runtime authorization
# service as a bar beneath it, the outputs, the outer loop, the record.
# ═════════════════════════════════════════════════════════════════════════════
class R:
    A, B, BUS_B, C, D, BUS_E, E = (0, 112), (134, 234), 246, (264, 436), (456, 560), 582, (600, 720)
    FX = (122, 572)
    FY0, LABY = 10, 30
    ROW, MID = (46, 198), 122
    PROXY = (456, 68, 560, 176)
    LANE = (216, 276)
    FY1, FY1_SHORT = 284, 214
    # the bar reaches back to x 56, so Figure 2's "using trusted context" fits
    # on its one line; nothing is drawn at x 56–134 under the frame. It sits
    # 42 under Level 3's full frame, room for "authorized / scope" in two
    # lines set against the grant, in the same place at every level.
    BAR = (56, 326, 510, 378)
    GRANT_X, GRANT_LY = 484, (300, 314.5)
    PROP_X = 340              # the agent proposes the scope it needs, as in Figure 2
    EXIT_X, EXIT_Y = 536, 394
    OUT = (412, 472)
    PR, APPROVAL, SLOT3, SLOT4 = (134, 238), (258, 432), (452, 548), (568, 672)
    # the outer loop's label sits above its return line, right of the pull
    # request's leg, at the same place in every level
    LOOPY, LOOP_X, LOOP_LABEL_X = 512, 36, 198
    FLOOR = (528, 574)
    H = 576
    KEY = (600, 20)


def r_frame(f, full=False, label="", gloss="", s_label="old"):
    y1 = R.FY1 if full else R.FY1_SHORT
    f.box(R.FX[0], R.FY0, R.FX[1] - R.FX[0], y1 - R.FY0, "zone", "frame")
    with f.at("newtext" if s_label == "new" else "old"):
        w = f.lab(R.B[0], R.LABY, label, "frame.l")
    if gloss:
        with f.at("newtext" if s_label in ("new", "gloss") else "old"):
            f.gloss(R.B[0] + w + 8, R.LABY, gloss, "frame.g")


LEVEL_AUTH_G = "decides what access each task gets, using trusted context"   # Figure 2's


def r_grant(f, x, y0, y1):
    """The scope the service authorizes, up into the proxy: the decision going
    out, labelled in two lines set right against its own line."""
    f.link([(x, y0), (x, y1)], "grant", tag="grant")
    for i, s_ in enumerate(("authorized", "scope")):
        f.gloss(x - 8 - f.width(s_, "gloss"), R.GRANT_LY[i], s_, f"grant.l{i}")


def r_bar(f, stack=False):
    """The runtime authorization service: a decision, drawn as Figure 2 draws
    it — what the agent proposes comes in, the scope it authorizes goes up to
    the proxy that enforces it. Behind a stack of proxies the grant ends on the
    back card, so its head is not drawn over by the cards in front."""
    x0, y0, x1, y1 = R.BAR
    f.node(x0, y0, x1 - x0, y1 - y0, "Runtime authorization service", [LEVEL_AUTH_G],
           kind="guard", num=1, tag="auth")
    r_grant(f, R.GRANT_X, y0, R.PROXY[3] + (6 if stack else 0))


def r_proxy(f, stack=False, s="old"):
    x0, y0, x1, y1 = R.PROXY
    with f.at(s):
        if stack:
            for d in (6, 3):
                f.ghost(x0 + d, y0 + d, x1 - x0, y1 - y0, f"pghost{d}", "proxy")
        f.node(x0, y0, x1 - x0, y1 - y0, "Egress proxy", PROXY_G,
               kind="guardfill" if stack else "guard", num=4, tag="proxy")


def r_dest(f, names_only=False):
    """The four destinations; from Level 2 the sublines, which repeat Level 1's
    word for word, are dropped, and each name sits centred in the box it had."""
    ys, y = [], R.ROW[0]
    for i, (n, g, kind, num) in enumerate(DEST):
        h = card_h(g, n)
        if names_only:
            # each card keeps its centre, so names and arrows stay put between
            # tabs; a card Level 1 drew taller for its gloss closes to the
            # others' height round that centre rather than standing empty
            hh = min(h, card_h([]))
            node_c(f, R.E[0], y + (h - hh) / 2, R.E[1] - R.E[0], hh, n, kind=kind, num=num,
                   tag=f"dest{i}")
        else:
            f.node(R.E[0], y, R.E[1] - R.E[0], h, n, g, kind=kind, num=num, tag=f"dest{i}")
        ys.append(y + h / 2)
        y += h + STACK
    f.link([(R.PROXY[2], R.MID), (R.BUS_E, R.MID)], head=False, tag="bus.in", group="bus")
    f.link([(R.BUS_E, ys[0]), (R.BUS_E, ys[-1])], head=False, tag="bus", group="bus")
    for i, yy in enumerate(ys):
        f.link([(R.BUS_E, yy), (R.E[0], yy)], tag=f"bus.{i}", group="bus")


def r_sandbox(f, label, name, gloss, s="old", stack=False, loop=("inner loop,", "until it passes")):
    x0, x1 = R.C
    y0, y1 = R.ROW
    with f.at(s):
        if stack:
            for d in (8, 4):
                f.ghost(x0 + d, y0 + d, x1 - x0 - 8, y1 - y0 - 8, f"ghost{d}", "sandbox")
            x1, y1 = x1 - 8, y1 - 8
        f.box(x0, y0, x1 - x0, y1 - y0, "sandbox", "sbx")
        f.badge(x0, y0, 3, "sbx")
    f.lab(x0 + PAD + 4, y0 + 24, label, "sbx.l")
    f.name(x0 + PAD + 4, y0 + 52, name, "sbx.n")
    for i, g in enumerate(gloss):
        f.gloss(x0 + PAD + 4, y0 + 68 + i * 14.5, g, f"sbx.g{i}")
    gy = y1 - 30
    f.loop_glyph(x0 + PAD + 11, gy - 4, "sbx.loop")
    f.gloss(x0 + PAD + 26, gy, loop[0], "sbx.lp0")
    f.gloss(x0 + PAD + 26, gy + 14.5, loop[1], "sbx.lp1")


def r_proposes(f):
    """The agent proposes the scope it needs: Figure 2's arrow, at every level
    where the agent's own request is the only proposal."""
    f.link([(R.PROP_X, R.ROW[1]), (R.PROP_X, R.BAR[1])], tag="propose")
    f.gloss(R.PROP_X - 8 - f.width("proposes scope", "gloss"), 262, "proposes scope", "propose.l")


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
    r_frame(f, label="Developer’s machine", gloss="or a remote environment")
    r_bar(f)
    with f.at("new"):
        f.node(R.A[0], R.MID - 40, R.A[1] - R.A[0], 80, "Developer",
               ["directs the", "agent, reviews", "its output"], tag="dev")
        f.link([(R.A[1], R.MID), (R.C[0], R.MID)], tag="directs")
    r_sandbox(f, "Sandbox", "Coding agent", ["profile across its", "harness and sandbox,",
                                              "workflow in a skill"])
    r_proposes(f)
    r_proxy(f)
    f.link([(R.C[1], R.MID), (R.PROXY[0], R.MID)], tag="traffic")
    r_dest(f)
    with f.at("new"):
        r_pr_exit(f)
        out_card(f, R.PR, "Pull request", ["the developer", "reviews it"], "pr")
        r_outer(f, mid(R.PR), R.MID + 40)
    r_outer_labels(f, "the developer drives the next run", "new", "new")
    # Figure 3 is the first level to draw all four boundaries, so it keys them,
    # in the corner Levels 2 and 3 fill with approval and what follows it
    key_grid(f, 300, R.OUT[0] + 12)
    r_floor(f, "harness logs, identity and proxy records, reviewed by the developer")


# ── Level 2 ──────────────────────────────────────────────────────────────────
def r_level2(f):
    r_frame(f, label="The factory", gloss="a shared service with its own identity", s_label="new")
    r_bar(f, stack=True)
    with f.at("new"):
        f.node(R.A[0], R.MID - 48, R.A[1] - R.A[0], 96, "Request",
               ["or an event,", "a schedule", "or a ticket"], tag="req")
        f.node(R.B[0], R.MID - 48, R.B[1] - R.B[0], 96, "Workflow",
               ["on CI/CD or", "a durable", "execution", "engine"], tag="wf")
        f.link([(R.A[1], R.MID), (R.B[0], R.MID)], tag="starts")
        f.link([(R.B[1], R.MID), (R.C[0], R.MID)], tag="launches")
    r_sandbox(f, "Sandbox per run", "Coding agent", ["own identity,", "authenticated profile"],
              s="new", stack=True)
    r_proposes(f)
    r_proxy(f, stack=True, s="new")
    f.link([(R.C[1] - 8, R.MID), (R.PROXY[0], R.MID)], tag="traffic")
    r_dest(f, names_only=True)
    r_pr_exit(f)
    with f.at("new"):
        out_card(f, R.PR, "Pull request", ["reviewed", "until ready"], "pr")
        out_card(f, R.APPROVAL, "Approval", APPROVAL_G, "appr")
        out_card(f, R.SLOT3, "Merge", ["approved", "changes"], "merge")
        out_link(f, R.PR, R.APPROVAL)
        out_link(f, R.APPROVAL, R.SLOT3)
    r_outer(f, mid(R.PR), R.MID + 48)
    r_outer_labels(f, "review feedback drives the next run", "old", "new")
    r_floor(f, "records from all four boundaries, linked by run; evals track quality", "new")


# ── Level 3 ──────────────────────────────────────────────────────────────────
SIG = (R.A[0], 106, R.A[1], 218)           # signals and requests
ORCH = (R.B[0], R.LANE[0], R.B[1], R.LANE[1])
FLAGS_Y = 208


def r_level3(f):
    r_frame(f, full=True, label="The factory")
    r_bar(f, stack=True)
    with f.at("new"):
        x0, y0, x1, y1 = SIG
        f.node(x0, y0, x1 - x0, y1 - y0, ["Signals and", "requests"],
               ["incidents,", "scanner", "findings,", "evals"], tag="sig")
    # the execution layer (Level 2's durable system) starts each agent
    eb = (R.B[0], R.ROW[0], R.B[1] - R.B[0], R.ROW[1] - R.ROW[0])
    f.node(*eb, ["Execution", "layer"], ["starts each", "agent"], tag="exec")
    with f.at("new"):
        # the orchestrator plans beside the bar; its proposal is the heaviest
        # line in the figure, and it lands on the service that alone grants
        f.node(ORCH[0], ORCH[1], ORCH[2] - ORCH[0], ORCH[3] - ORCH[1], ["Orchestrator", "agent"],
               ["preflight"], kind="agent", tag="orch")
        f.link([(56, SIG[3]), (56, mid(R.LANE)), (ORCH[0], mid(R.LANE))], tag="takes")
        px = mid((ORCH[0], ORCH[2]))
        f.link([(px, ORCH[3]), (px, R.BAR[1])], tag="propose", heavy=True)
    with f.at("newtext"):
        for i, s in enumerate(("proposes profile", "and task scope")):
            f.gloss(px + 8, 296 + i * 14.5, s, f"propose.l{i}")
    # each agent in its own sandbox
    x0, x1 = R.C
    hh = (R.ROW[1] - R.ROW[0] - 2 * STACK) / 3
    mids = []
    with f.at("new"):
        for i in range(3):
            y0 = R.ROW[0] + i * (hh + STACK)
            f.box(x0, y0, x1 - x0, hh, "sandbox", f"sbx{i}")
            f.badge(x0, y0, 3, f"sbx{i}")
            mids.append(y0 + hh / 2)
    for i in range(3):
        y0 = R.ROW[0] + i * (hh + STACK)
        f.name(x0 + PAD + 4, y0 + 19, f"Agent, task {i + 1}", f"sbx{i}.n")
        f.gloss(x0 + PAD + 4, y0 + 34, "own identity and scope", f"sbx{i}.g")
        f.loop_glyph(x1 - 16, y0 + 14, f"sbx{i}.loop")
    ey = mid(R.ROW)
    f.link([(R.B[1], ey), (R.BUS_B, ey)], head=False, tag="exec.bus", group="xb")
    f.link([(R.BUS_B, mids[0]), (R.BUS_B, mids[-1])], head=False, tag="xbus", group="xb")
    for i, m in enumerate(mids):
        f.link([(R.BUS_B, m), (R.C[0], m)], tag=f"xb{i}", group="xb")
    # the monitoring agent watches from outside the sandboxes and flags new
    # work back into signals and requests, as an untrusted request
    with f.at("new"):
        f.node(R.C[0], R.LANE[0], R.C[1] - R.C[0], R.LANE[1] - R.LANE[0], "Monitoring agent",
               ["flags new work,", "never grants"], kind="agent", tag="mon")
        f.link([(mid(R.C), R.LANE[0]), (mid(R.C), R.ROW[1])], "watch", tag="watch")
        f.link([(R.C[0] + 20, R.LANE[0]), (R.C[0] + 20, FLAGS_Y), (SIG[2], FLAGS_Y)], tag="flags")
    r_proxy(f, stack=True)
    f.link([(R.C[1], R.MID), (R.PROXY[0], R.MID)], tag="traffic")
    r_dest(f, names_only=True)
    r_pr_exit(f)
    out_card(f, R.PR, "Pull request", ["reviewed", "until ready"], "pr")
    out_card(f, R.APPROVAL, "Approval", APPROVAL_G, "appr")
    out_link(f, R.PR, R.APPROVAL)
    with f.at("new"):
        out_card(f, R.SLOT3, "Deploy", ["can be", "rolled back"], "deploy")
        out_card(f, R.SLOT4, "Production", ["sends back", "signals"], "prod")
        out_link(f, R.APPROVAL, R.SLOT3)
        out_link(f, R.SLOT3, R.SLOT4)
        r_outer(f, mid(R.SLOT4), SIG[3])
    r_outer_labels(f, "production signals start new work", "old", "new")
    r_floor(f, "telemetry and evals across runs; monitoring of running agents", "new")


PREV = {1: "as in Figure 2", 2: "as at Level 1", 3: "as at Level 2"}


def build_level(n):
    f = CF(f"sf{n + 2}", W, R.H, CAPTION[n + 2], ALT[n + 2], level=n)
    {1: r_level1, 2: r_level2, 3: r_level3}[n](f)
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


def narrow_level(n):
    f = CF(f"sf{n + 2}n", NW, 1400, CAPTION[n + 2], ALT[n + 2], narrow=True, level=n)
    y = 10
    a = {1: ("Developer", ["directs the agent and", "reviews its output"]),
         2: ("Request", ["or an event, a schedule", "or a ticket"]),
         3: ("Signals and requests", ["incidents, scanner", "findings, evals"])}[n]
    with f.at("new"):
        f.node(NR.A[0], y, NR.A[1] - NR.A[0], 66, a[0], a[1], tag="start")
    delta_key(f, NR.KEY[0], NR.KEY[1], PREV[n])
    a_mid = y + 33
    prev = y + 66
    y += 66 + 24
    fy0 = y
    with f.at("newtext" if n == 2 else "old"):
        f.lab(NR.GX + 14, fy0 + 22, "Developer’s machine" if n == 1 else "The factory", "frame.l")
    if n == 1:                     # as wide, and as the alt text says
        f.gloss(NR.GX + 14, fy0 + 38, "or a remote environment", "frame.g")
        y += 14.5
    y += 40
    ix0, ix1 = NR.IN
    orch = None
    if n == 2:
        with f.at("new"):
            f.node(ix0, y, ix1 - ix0, 66, "Workflow", ["on CI/CD or a durable", "execution engine"],
                   tag="wf")
            f.link([(NR.GX, prev), (NR.GX, y)], tag="starts")
        prev = y + 66
        y += 66 + 24
    elif n == 3:
        oy = y
        with f.at("new"):
            f.node(ix0, y, ix1 - ix0, 66, "Orchestrator agent",
                   ["preflight: proposes", "profile and task scope"], kind="agent", tag="orch")
            f.link([(NR.GX, prev), (NR.GX, y)], tag="takes")
        orch = oy + 46
        y += 66 + 24
        # no line from the orchestrator: its plan is a proposal to the
        # service, never an instruction that starts agents
        f.node(ix0, y, ix1 - ix0, 52, "Execution layer", ["starts each agent"], tag="exec")
        prev = y + 52
        y += 52 + 24
    if n == 3:
        mids = []
        for i in range(3):
            with f.at("new"):
                f.box(ix0, y, ix1 - ix0, 46, "sandbox", f"sbx{i}")
                f.badge(ix0, y, 3, f"sbx{i}")
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
            f.node(ix0, y, ix1 - ix0, 60, "Monitoring agent",
                   ["flags new work,", "never grants"], kind="agent", tag="mon")
            f.link([(NR.GX + 60, y), (NR.GX + 60, sb_bottom)], "watch", tag="watch")
        y += 60 + 16
    else:
        glosses = (["own identity,", "authenticated profile"] if n == 2 else
                   ["profile across", "harness and sandbox,", "workflow in a skill"])
        extra = (len(glosses) - 2) * 14.5
        sh = 132 + extra
        with f.at("new" if n == 2 else "old"):
            if n == 2:
                for d in (6, 3):
                    f.ghost(ix0 + d, y + d, ix1 - ix0 - 6, sh - 6, f"ghost{d}", "sandbox")
            sw = ix1 - ix0 - (6 if n == 2 else 0)
            f.box(ix0, y, sw, sh - (6 if n == 2 else 0), "sandbox", "sbx")
            f.badge(ix0, y, 3, "sbx")
        f.lab(ix0 + PAD + 4, y + 24, "Sandbox per run" if n == 2 else "Sandbox", "sbx.l")
        f.name(ix0 + PAD + 4, y + 50, "Coding agent", "sbx.n")
        for i, g_ in enumerate(glosses):
            f.gloss(ix0 + PAD + 4, y + 66 + i * 14.5, g_, f"sbx.g{i}")
        with f.at("new" if n == 1 else "old"):
            f.link([(NR.GX, prev), (NR.GX, y)], tag="into")
        f.loop_glyph(ix0 + PAD + 11, y + 100 + extra, "sbx.loop")
        f.gloss(ix0 + PAD + 26, y + 104 + extra, "inner loop,", "sbx.lp0")
        f.gloss(ix0 + PAD + 26, y + 118.5 + extra, "until it passes", "sbx.lp1")
        sb_mid = y + 62
        sb_bottom = y + sh
        y += sh + 16
    fy1 = y
    ph = card_h(PROXY_G)
    py0 = sb_mid - ph / 2
    f.box(NR.X0, fy0, NR.X1 - NR.X0, fy1 - fy0, "zone", "frame")
    with f.at("new" if n == 2 else "old"):
        if n > 1:
            for d in (6, 3):
                f.ghost(NR.PROXY[0] + d, py0 + d, NR.PROXY[1] - NR.PROXY[0], ph, f"pghost{d}", "proxy")
        f.node(NR.PROXY[0], py0, NR.PROXY[1] - NR.PROXY[0], ph, "Egress proxy", PROXY_G,
               kind="guardfill" if n > 1 else "guard", num=4, tag="proxy")
    f.link([(ix1 - (6 if n == 2 else 0), sb_mid), (NR.PROXY[0], sb_mid)], tag="traffic")
    # the authorization service, beneath the frame; its decision rises into the proxy
    by0 = fy1 + 40
    nb = ["decides what access each task gets,", "using trusted context"]   # LEVEL_AUTH_G
    bh = card_h(nb)
    f.node(NR.BAR[0], by0, NR.BAR[1] - NR.BAR[0], bh, "Runtime authorization service", nb,
           kind="guard", num=1, tag="auth")
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
    for i, (nm, g, kind, num) in enumerate(order):
        if n == 1:
            f.node(NR.DEST[0], y, NR.DEST[1] - NR.DEST[0], 44, nm, [" ".join(g)], kind=kind,
                   num=num, tag=f"dest{i}")
        else:
            node_c(f, NR.DEST[0], y, NR.DEST[1] - NR.DEST[0], 44, nm, kind=kind, num=num,
                   tag=f"dest{i}")
        ys.append(y + 22)
        y += 44 + STACK
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
    appr = " ".join(APPROVAL_G)
    outs = {1: [("Pull request", ["the developer reviews it"], 1)],
            2: [("Pull request", ["reviewed until ready"], 2),
                ("Approval", [appr], 2),
                ("Merge", ["approved changes"], 2)],
            3: [("Pull request", ["reviewed until ready"], 2),
                ("Approval", [appr], 2),
                ("Deploy", ["can be rolled back"], 3), ("Production", ["sends back signals"], 3)]}[n]
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
           2: "records from all four boundaries, by run",
           3: "telemetry, evals, monitoring of agents"}[n]
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
# lies behind it. Beneath it the runtime authorization service, drawn as a
# decision rather than a container. Into it come the profile's bounds and the
# agent's proposal (a request, never a grant) from above, and the rest of the
# trusted context from below, as one box and one arrow that enters clear of
# every line above, so nothing seems to pass straight through. Out of it go the
# scope the proxy enforces (the strongest line in the figure), high-impact
# actions to approval and, ending in a stop, anything outside policy. The
# agent works task after task and hands work to other agents; each is a new
# decision, which the service says in words. Profile ⊇ task ⊇ delegation is
# the shape of the scope it grants, not something it holds, so the task and
# delegation are inputs here, beside who's asking and policy.
# ═════════════════════════════════════════════════════════════════════════════
PROFILE_G = ["one per kind of agent,", "the most it can ever do"]
AGENT_G = ["untrusted, holds", "no credentials"]
# the proxy knows the task, so it enforces that task's scope (the paper's
# "knows the task and can allow only the repositories, operations, and
# resources it covers"); the levels' narrower cards keep PROXY_G
F2_PROXY_G = ["default-deny,", "knows the task and", "enforces its scope,", "attaches credentials"]
F2_AUTH_G = ["decides what access each task gets, using trusted context,",
             "a new decision for every task and delegation, and records every grant"]
F2_AUTH_GN = ["decides what access each task gets,", "using trusted context, a new decision",
              "for every task and delegation,", "and records every grant"]
F2_PROPOSE = ["proposes scope,", "never a grant"]
F2_DENY = ["outside policy: denied,", "or sent to a person"]
REC2 = "each boundary keeps a tamper-evident record, out of any agent’s reach"
# the trusted context besides the profile, each in the paper's own words:
# "each action is attributed to both the agent and whoever it acts for", a
# task "narrows that to the work at hand", delegation "to another agent ...
# can narrow that scope but never expand it", "policy written in advance"
CONTEXT = [("Identity", ["the agent, and", "whoever it acts for"]),
           ("Task", ["the work", "at hand"]),
           ("Delegation", ["to another agent,", "only narrows scope"]),
           ("Policy", ["written", "in advance"])]


def f2_sandbox(f, x0, x1, y0, h, gloss):
    f.box(x0, y0, x1 - x0, h, "sandbox", "sbx")
    f.badge(x0, y0, 3, "sbx")
    f.lab(x0 + PAD + 4, y0 + 24, "Sandbox", "sbx.l")
    f.name(x0 + PAD + 4, y0 + 52 if not f.narrow else y0 + 50, "Agent", "sbx.n")
    gy = y0 + (68 if not f.narrow else 66)
    for i, g in enumerate(gloss):
        f.gloss(x0 + PAD + 4, gy + i * 14.5, g, f"sbx.g{i}")
    ly = y0 + h - 30
    f.loop_glyph(x0 + PAD + 11, ly - 4, "sbx.loop")
    f.gloss(x0 + PAD + 26, ly, "free to reason", "sbx.lp0")
    f.gloss(x0 + PAD + 26, ly + 14.5, "and try things", "sbx.lp1")


def context_box(f, x0, y0, x1, cols):
    """The trusted context as one input, not four more components: one card,
    each part a name and its gloss, in `cols` columns with hairlines between
    them, each column as wide as its widest run and the slack shared. Returns
    the card's bottom."""
    rows = [CONTEXT[i:i + cols] for i in range(0, len(CONTEXT), cols)]
    rh = card_h(CONTEXT[0][1])
    h = rh * len(rows)
    f.box(x0, y0, x1 - x0, h, "card", "ctx")
    need = [max(max(f.width(n_, "name"), *(f.width(g, "gloss") for g in g_)) + 2 * PAD
                for n_, g_ in CONTEXT[c::cols]) for c in range(cols)]
    slack = (x1 - x0 - sum(need)) / cols
    xs = [x0]
    for w_ in need[:-1]:
        xs.append(round(xs[-1] + w_ + slack))
    for r, row in enumerate(rows):
        for c, (n_, g_) in enumerate(row):
            k = r * cols + c
            f.name(xs[c] + PAD, y0 + r * rh + 21, n_, f"ctx{k}.n0")
            for i, g in enumerate(g_):
                f.gloss(xs[c] + PAD, y0 + r * rh + 37 + i * 14.5, g, f"ctx{k}.g{i}")
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
    PR_, SB, PX, BUS, DN = (6, 180), (194, 342), (362, 514), 530, (548, 720)
    y0, y1 = 46, 178
    ym = mid((y0, y1))
    # the profile, once: one per kind of agent, the most it can ever do
    f.node(PR_[0], y0, PR_[1] - PR_[0], y1 - y0, "Profile", PROFILE_G, tag="prof")
    f2_sandbox(f, SB[0], SB[1], y0, y1 - y0, AGENT_G)
    # its first job: it configures the sandbox at launch, over the top of the row
    lx0, lx1, ly = 80, 262, 22
    f.link([(lx0, y0), (lx0, ly), (lx1, ly), (lx1, y0)], tag="launch")
    f.gloss(lx0 + 8, ly - 8, "configures the sandbox at launch", "launch.l")
    # the egress proxy, the sandbox's one way out
    f.node(PX[0], y0, PX[1] - PX[0], y1 - y0, "Egress proxy", F2_PROXY_G, kind="guard", num=4,
           tag="proxy")
    f.link([(SB[1], ym), (PX[0], ym)], tag="request")
    # downstream, and the admission point packages come through
    dh = (y1 - y0 - STACK) / 2
    f.node(DN[0], y0, DN[1] - DN[0], dh, "Downstream", ["only authorized", "operations reach it"],
           tag="down")
    f.node(DN[0], y0 + dh + STACK, DN[1] - DN[0], dh, "Admission point",
           ["approved, scanned", "packages"], kind="guard", num=2, tag="adm")
    m1, m2 = y0 + dh / 2, y0 + dh + STACK + dh / 2
    f.link([(PX[1], ym), (BUS, ym)], head=False, tag="out.in", group="out")
    f.link([(BUS, m1), (BUS, m2)], head=False, tag="out.bus", group="out")
    f.link([(BUS, m1), (DN[0], m1)], tag="out.0", group="out")
    f.link([(BUS, m2), (DN[0], m2)], tag="out.1", group="out")
    # the decision, beneath the row from the profile's edge to the proxy's
    s0, s1 = 234, 300
    f.node(PR_[0], s0, PX[1] - PR_[0], s1 - s0, "Runtime authorization service", F2_AUTH_G,
           kind="guard", num=1, tag="auth")
    # from above: the profile's second job, and the agent's proposal, a
    # request it can't grant itself; up to the proxy, the scope it authorizes
    bx, ux, gx = 48, 322, 470
    f.link([(bx, y1), (bx, s0)], tag="bounds")
    for i, s in enumerate(("bounds every", "decision")):
        f.gloss(bx + 8, 200 + i * 14.5, s, f"bounds.l{i}")
    f.link([(ux, y1), (ux, s0)], tag="propose")
    for i, s in enumerate(F2_PROPOSE):
        f.gloss(ux - 8 - f.width(s, "gloss"), 200 + i * 14.5, s, f"propose.l{i}")
    f.link([(gx, s0), (gx, y1)], "grant", tag="grant")
    for i, s in enumerate(("authorized", "scope")):
        f.gloss(gx - 8 - f.width(s, "gloss"), 200 + i * 14.5, s, f"grant.l{i}")
    # from below: the rest of the trusted context, one card, one arrow, which
    # enters clear of every line above the service
    cx, c0 = 190, s1 + 30
    end = context_box(f, PR_[0], c0, PX[1], 4)
    f.link([(cx, c0), (cx, s1)], tag="ctx.in")
    f.lab(cx + 8, s1 + 19, "Trusted context", "ctx.l")
    # out to the right, apart from what the proxy lets through: high-impact
    # actions to approval, and anything outside policy stopped there, denied
    # or sent to a person
    ay0 = 214
    f.node(DN[0], ay0, DN[1] - DN[0], 60, "Approval", APPROVAL_G, tag="appr")
    f.link([(PX[1], ay0 + 30), (DN[0], ay0 + 30)], tag="route")
    f.gloss(DN[0], ay0 - 8, "high-impact actions", "route.l")
    dy, dx = s1 - 8, PX[1] + 20
    f.link([(PX[1], dy), (dx, dy)], tag="deny", bar=True, stop=True)
    for i, s in enumerate(F2_DENY):
        f.gloss(dx + 8, dy + 4 + i * 14.5, s, f"deny.l{i}")
    # the record, its own band
    r0 = end + 22
    gx2 = record(f, 0, r0, W, r0 + 48, tag="rec")
    f.gloss(gx2, r0 + 28, REC2, "rec.g")
    end = legend(f, 0, r0 + 48 + 38, W, marks=ALL_MARKS)
    f.set_height(end)
    f.write("figure-2")


def figure2_narrow():
    """Figure 2 on a phone: the sandbox beside the proxy, what the proxy lets
    through stacked under the proxy, the decision beneath both, its trusted
    context in one card right under it, and what it routes elsewhere down the
    right edge: approval, then a stop for anything outside policy."""
    f = CF("sf2n", NW, 1400, CAPTION[2], ALT[2], narrow=True)
    X, R1 = 8, 352
    y = 10
    f.node(X, y, R1 - X, 60, "Profile", PROFILE_G, tag="prof")
    pb = y + 60
    sy0 = pb + 44
    SB, PX, BUS = (38, 176), (194, 348), 360
    sh = 132
    # the profile configures the sandbox at launch, and bounds every decision;
    # that line runs between the sandbox's badge and the service's, clear of both
    lx, bx = 140, 22
    f.link([(lx, pb), (lx, sy0)], tag="launch")
    for i, s in enumerate(("configures the sandbox", "at launch")):
        f.gloss(lx + 8, pb + 16 + i * 14.5, s, f"launch.l{i}")
    for i, s in enumerate(("bounds every", "decision")):
        f.gloss(bx + 8, pb + 16 + i * 14.5, s, f"bounds.l{i}")
    f2_sandbox(f, SB[0], SB[1], sy0, sh, AGENT_G)
    ph = card_h(F2_PROXY_G)
    f.node(PX[0], sy0, PX[1] - PX[0], ph, "Egress proxy", F2_PROXY_G, kind="guard", num=4,
           tag="proxy")
    rm = sy0 + 46
    f.link([(SB[1], rm), (PX[0], rm)], tag="request")
    # under the proxy, what it lets through, fed down its right edge
    DC = (220, 340)
    ys, yy = [], sy0 + ph + 18
    for i, (n_, g_, kind, num, t_) in enumerate(
            [("Downstream", ["only authorized", "operations", "reach it"], "card", None, "down"),
             ("Admission point", ["approved,", "scanned", "packages"], "guard", 2, "adm")]):
        h = card_h(g_)
        f.node(DC[0], yy, DC[1] - DC[0], h, n_, g_, kind=kind, num=num, tag=t_)
        ys.append(yy + h / 2)
        yy += h + STACK
    f.link([(PX[1], rm), (BUS, rm)], head=False, tag="out.in", group="out")
    f.link([(BUS, rm), (BUS, ys[-1])], head=False, tag="out.bus", group="out")
    for i, m in enumerate(ys):
        f.link([(BUS, m), (DC[1], m)], tag=f"out.{i}", group="out")
    # the decision, beneath both columns
    b0 = yy - STACK + 24
    bh = card_h(F2_AUTH_GN)
    f.node(X, b0, R1 - X, bh, "Runtime authorization service", F2_AUTH_GN, kind="guard", num=1,
           tag="auth")
    # into it from above: the profile's bounds (left edge) and the proposal;
    # up into the proxy, the scope it authorizes
    f.link([(bx, pb), (bx, b0)], tag="bounds")
    ux, gx = 60, 206
    f.link([(ux, sy0 + sh), (ux, b0)], tag="propose")
    for i, s in enumerate(F2_PROPOSE):
        f.gloss(ux + 8, sy0 + sh + 22 + i * 14.5, s, f"propose.l{i}")
    f.link([(gx, b0), (gx, sy0 + ph)], "grant", tag="grant")
    for i, s in enumerate(("authorized", "scope")):
        f.gloss(gx - 8 - f.width(s, "gloss"), sy0 + sh + 70 + i * 14.5, s, f"grant.l{i}")
    # into it from below: the rest of the trusted context, one card, one arrow
    cx, c0 = 140, b0 + bh + 30
    end = context_box(f, X, c0, 326, 2)
    f.link([(cx, c0), (cx, b0 + bh)], tag="ctx.in")
    f.lab(cx + 8, b0 + bh + 19, "Trusted context", "ctx.l")
    # out of it, down the right edge: high-impact actions to approval, and
    # anything outside policy stopped there, denied or sent to a person
    rx = 344
    ay0 = end + 34
    f.gloss(336 - f.width("high-impact actions", "gloss"), ay0 - 8, "high-impact actions",
            "route.l")
    f.node(X, ay0, 326 - X, 46, "Approval", [" ".join(APPROVAL_G)], tag="appr")
    dy = ay0 + 46 + 26
    f.link([(rx, b0 + bh), (rx, dy)], tag="deny", group="route", bar=True, stop=True)
    f.link([(rx, ay0 + 23), (326, ay0 + 23)], tag="route", group="route")
    for i, s in enumerate(F2_DENY):
        f.gloss(334 - f.width(s, "gloss"), dy - 10 + i * 14.5, s, f"deny.l{i}")
    r0 = dy + 26
    record(f, X, r0, R1, r0 + 62, tag="rec", two=True)
    f.gloss(X + PAD, r0 + 39, "each boundary keeps a tamper-evident", "rec.g0")
    f.gloss(X + PAD, r0 + 53.5, "record, out of any agent’s reach", "rec.g1")
    f.rule(r0 + 62 + 20, X, R1)
    end = key_grid(f, X, r0 + 62 + 42)
    f.set_height(end)
    f.write("figure-2-narrow")


# ═════════════════════════════════════════════════════════════════════════════
# Figure 6 — only a new authorization decision can widen a task. Figure 2's
# skeleton, as the levels draw it, with one incident's values ("A factory in
# action").
# ═════════════════════════════════════════════════════════════════════════════
FIG6_AUTH = ["checks it against policy and", "the alert’s authenticated source"]
BLOCKED_G = ["blocked: not", "in the task"]   # the proxy blocking, never "outside policy"


def figure6():
    f = CF("sf6", W, 700, CAPTION[6], ALT[6])
    f.box(R.FX[0], R.FY0, R.FX[1] - R.FX[0], R.FY1_SHORT - R.FY0, "zone", "frame")
    f.lab(R.B[0], R.LABY, "The factory", "frame.l")
    f.node(R.A[0], 66, R.A[1] - R.A[0], 112, ["Production", "alert"],
           ["elevated", "errors in a", "payments", "service"], tag="sig")
    f.node(R.B[0], R.ROW[0], R.B[1] - R.B[0], 112, ["Orchestrator", "agent"],
           ["proposes a", "task for an", "incident", "agent"], kind="agent", tag="orch")
    f.link([(R.A[1], R.MID), (R.B[0], R.MID)], tag="takes")
    # what the task asks for rides on the proposal, into the authorization service
    px = 210
    f.link([(px, R.ROW[0] + 112), (px, R.BAR[1])], tag="propose")
    for i, s in enumerate(("payments", "service logs,", "last hour;", "one pull request")):
        f.gloss(px + 8, 226 + i * 14.5, s, f"propose.l{i}")
    r_sandbox(f, "Sandbox", "Incident agent", ["configured from", "its profile"],
              loop=("inner loop,", "until tests pass"))
    # wanting more is a request for a new decision, never a grant; its words
    # sit right of its own line, so the line parts them from the proposal's
    wx = 356
    f.link([(wx, R.ROW[1]), (wx, R.BAR[1])], tag="wider")
    for i, s in enumerate(("needs a new", "decision")):
        f.gloss(wx + 8, 236 + i * 14.5, s, f"wider.l{i}")
    r_proxy(f)
    f.link([(R.C[1], R.MID), (R.PROXY[0], R.MID)], tag="traffic")
    x0, y0, x1, y1 = R.BAR[0], R.BAR[1], R.BAR[2], R.BAR[1] + 60
    f.node(x0, y0, x1 - x0, y1 - y0, "Runtime authorization service", FIG6_AUTH, kind="guard",
           num=1, tag="auth")
    r_grant(f, R.GRANT_X, y0, R.PROXY[3])
    dest = [(["Payments", "service logs"], ["last hour only"], "card", None),
            (["Authentication", "service logs"], BLOCKED_G, "blocked", None),
            ("Admission point", ["serves the", "approved", "library"], "guard", 2)]
    ys, yy = [], R.ROW[0]
    for i, (n_, g_, kind, num) in enumerate(dest):
        h = card_h(g_, n_)
        f.node(R.E[0], yy, R.E[1] - R.E[0], h, n_, g_, kind=kind, num=num, tag=f"dest{i}")
        ys.append((yy + h / 2, kind))
        yy += h + STACK
    f.link([(R.PROXY[2], R.MID), (R.BUS_E, R.MID)], head=False, tag="bus.in", group="bus")
    f.link([(R.BUS_E, ys[0][0]), (R.BUS_E, ys[-1][0])], head=False, tag="bus", group="bus")
    for i, (m_, kind) in enumerate(ys):
        f.link([(R.BUS_E, m_), (R.E[0], m_)], tag=f"bus.{i}", group="bus", bar=(kind == "blocked"))
    # the fix: one pull request, approval, a small first deploy, the error rate
    ex_y, o0, o1 = y1 + 16, y1 + 34, y1 + 94
    slots = [(134, 238), (258, 432), (452, 568), (588, 696)]
    f.link([(R.EXIT_X, R.PROXY[3]), (R.EXIT_X, ex_y), (mid(slots[0]), ex_y), (mid(slots[0]), o0)],
           tag="pr.exit")
    for slot, (n_, g_, t_) in zip(slots, [("Pull request", ["one, as", "granted"], "pr"),
                                          ("Approval", APPROVAL_G, "appr"),
                                          ("Deploy", ["small share of", "traffic first"], "deploy"),
                                          ("Production", ["error rate", "afterward"], "prod")]):
        f.node(slot[0], o0, slot[1] - slot[0], o1 - o0, n_, g_, tag=t_)
    for a, b in zip(slots, slots[1:]):
        f.link([(a[1], mid((o0, o1))), (b[0], mid((o0, o1)))], tag=f"out{a[0]}")
    loopy = o1 + 40
    f.link([(mid(slots[3]), o1), (mid(slots[3]), loopy), (R.LOOP_X, loopy), (R.LOOP_X, 178)],
           "loop", tag="outer")
    f.lab(R.LOOP_LABEL_X, loopy - 24, "outer loop", "outer.l")
    f.gloss(R.LOOP_LABEL_X, loopy - 8, "confirms the fix or starts the next run", "outer.g")
    f.set_height(loopy + 8)
    f.write("figure-6")


def figure6_narrow():
    f = CF("sf6n", NW, 1600, CAPTION[6], ALT[6], narrow=True)
    y = 10
    f.node(NR.A[0], y, NR.A[1] - NR.A[0], 66, "Production alert",
           ["elevated errors in a", "payments service"], tag="start")
    a_mid = y + 33
    prev = y + 66
    y += 66 + 24
    fy0 = y
    f.lab(NR.GX + 14, fy0 + 22, "The factory", "frame.l")
    y += 40
    ix0, ix1 = NR.IN
    f.node(ix0, y, ix1 - ix0, 112, "Orchestrator agent",
           ["proposes a task for an", "incident agent:", "payments service logs,", "last hour,",
            "one pull request"], kind="agent", tag="orch")
    f.link([(NR.GX, prev), (NR.GX, y)], tag="takes")
    orch = y + 88
    y += 112 + 24
    sy0, sh = y, 132
    f.box(ix0, sy0, ix1 - ix0, sh, "sandbox", "sbx")
    f.badge(ix0, sy0, 3, "sbx")
    f.lab(ix0 + PAD + 4, sy0 + 24, "Sandbox", "sbx.l")
    f.name(ix0 + PAD + 4, sy0 + 50, "Incident agent", "sbx.n")
    f.gloss(ix0 + PAD + 4, sy0 + 66, "configured from", "sbx.g0")
    f.gloss(ix0 + PAD + 4, sy0 + 80.5, "its profile", "sbx.g1")
    f.loop_glyph(ix0 + PAD + 11, sy0 + 100, "sbx.loop")
    f.gloss(ix0 + PAD + 26, sy0 + 104, "inner loop,", "sbx.lp0")
    f.gloss(ix0 + PAD + 26, sy0 + 118.5, "until tests pass", "sbx.lp1")
    sb_mid = sy0 + 62
    fy1 = sy0 + sh + 16
    f.box(NR.X0, fy0, NR.X1 - NR.X0, fy1 - fy0, "zone", "frame")
    ph = card_h(PROXY_G)
    py0 = sb_mid - ph / 2
    f.node(NR.PROXY[0], py0, NR.PROXY[1] - NR.PROXY[0], ph, "Egress proxy", PROXY_G, kind="guard",
           num=4, tag="proxy")
    f.link([(ix1, sb_mid), (NR.PROXY[0], sb_mid)], tag="traffic")
    by0, bh = fy1 + 40, 66
    f.node(NR.BAR[0], by0, NR.BAR[1] - NR.BAR[0], bh, "Runtime authorization service", FIG6_AUTH,
           kind="guard", num=1, tag="auth")
    f.link([(NR.GRANT_X, by0), (NR.GRANT_X, py0 + ph)], "grant", tag="grant")
    for i, s in enumerate(("authorized", "scope")):
        f.gloss(NR.GRANT_X - 8 - f.width(s, "gloss"), fy1 + 14 + i * 14.5, s, f"grant.l{i}")
    f.link([(ix0, orch), (NR.GUTTER, orch), (NR.GUTTER, by0 + 26), (NR.BAR[0], by0 + 26)],
           tag="propose")
    wx = 150
    f.link([(wx, sy0 + sh), (wx, by0)], tag="wider")
    for i, s in enumerate(("needs a new", "decision")):
        f.gloss(wx - 8 - f.width(s, "gloss"), fy1 + 14 + i * 14.5, s, f"wider.l{i}")
    y = by0 + bh + 24
    dests = [("Payments service logs", ["last hour only"], "card", None),
             ("Authentication service logs", [" ".join(BLOCKED_G)], "blocked", None),
             ("Admission point", ["serves the approved library"], "guard", 2)]
    ys = []
    for i, (nm, g, kind, num) in enumerate(dests):
        f.node(NR.DEST[0], y, NR.DEST[1] - NR.DEST[0], 44, nm, g, kind=kind, num=num, tag=f"dest{i}")
        ys.append((y + 22, kind))
        y += 44 + STACK
    # the pull request leaves through the proxy like everything else: the
    # same bus, one more branch, never out of the admission point above it
    y += 16
    pr_mid = y + 23
    f.link([(NR.PROXY[1], sb_mid), (NR.BUS, sb_mid)], head=False, tag="bus.in", group="bus")
    f.link([(NR.BUS, sb_mid), (NR.BUS, pr_mid)], head=False, tag="bus", group="bus")
    for i, (yy, kind) in enumerate(ys):
        f.link([(NR.BUS, yy), (NR.DEST[1], yy)], tag=f"bus.{i}", group="bus", bar=(kind == "blocked"))
    f.link([(NR.BUS, pr_mid), (NR.DEST[1], pr_mid)], tag="bus.pr", group="bus")
    outs = [("Pull request", ["one, as granted"]),
            ("Approval", [" ".join(APPROVAL_G)]),
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
