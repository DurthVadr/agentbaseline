#!/usr/bin/env python3
"""The Secure Software Factory — its six figures, generated.

Drawn with the first paper's kit (whitepaper/figures/figkit.py): the same plate,
the same four voices (Figtree names, Plex Serif glosses, Chakra Petch labels,
Plex Mono numerals) and the same hairline cards. Structure comes from position,
whitespace and hairlines. Colour encodes exactly one thing, the paper's own
central distinction:

  * GUARD (the site's accent) marks what is enforced outside the agent's loop —
    the four boundaries and the enforcement infrastructure. Each boundary
    carries its number on the corner of the part that enforces it:
    1 Identity and access, 2 Supply chain, 3 Sandbox, 4 Network.
  * WASH marks untrusted agent execution: the inside of a sandbox, and any
    agent that plans or watches from outside one.

Everything else is ink on the plate.

Figures 2 to 6 share one skeleton. The authorization service, the sandbox
frame, the egress proxy, the destinations behind it and the observability
floor sit at the same coordinates in every one of them, because the paper's
claim is that the boundaries don't change between levels and only what runs
inside them does. Flipping Figure 3 → 4 → 5 should show what was added and who
took over, never a re-layout. Figure 1 is the process the boundaries serve, so
it has its own composition.

Every label is the paper's vocabulary (final draft, 12 October 2026). Sizes are
set for the PDF column: at 6.5 in (468 pt) a 720-unit drawing prints at 0.65 pt
per unit, so the smallest run here (11 units) prints at 7.15 pt.

Writes figure-N.svg (+ figure-N-narrow.svg for 1, 3, 4, 5), each with the box
manifest bin/check-figure reads and a geometry manifest for the checks that
only boxed figures need (containment, connectors that land, nothing drawn
through text).
"""
import json, math, pathlib, re, sys

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

# ── type, sized for the PDF column ───────────────────────────────────────────
# Every figure is drawn on a 720-unit content width (360 for phones) and set on
# a canvas MARGIN wider on every side, so no stroke meets the canvas edge. At
# 6.5 in the 736-unit canvas prints at 0.636 pt a unit; the smallest run here
# (11.25) prints at 7.15 pt.
W = 720
MARGIN = 8
PRINT_IN, MIN_PT = 6.5, 7.0          # checked by bin/check-figure
NAME, GLOSS, LAB, NUM = 12.5, 11.25, 11.25, 11.25
PAD = 10                              # card inset
LS = 0.06                             # label tracking (em)


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

    # ── text in the page's four voices ──
    def name(self, x, y, s, tag, size=NAME):
        return self.text(x, y, s, size, C["ink"], "600", tag=tag, face="head")

    def gloss(self, x, y, s, tag, size=GLOSS, fill=None):
        return self.text(x, y, s, size, fill or C["soft"], tag=tag)

    def lab(self, x, y, s, tag, fill=None, size=LAB):
        return self.text(x, y, s.upper(), size, fill or C["soft"], "500", False, LS,
                         tag=tag, face="label")

    def width(self, s, kind):
        if kind == "name":
            return len(s) * self._adv(NAME, False, "600", "head")
        if kind == "label":
            return len(s) * (self._adv(LAB, False, "500", "label") + LS * LAB)
        return len(s) * self._adv(GLOSS, False)

    # ── shapes ──
    STYLE = {
        "card":    ('fill="none"', C["rule"], 1, ""),
        "guard":   ('fill="none"', GUARD, 1.25, ""),
        "sandbox": (f'fill="{WASH}"', GUARD, 1.25, ""),
        "agent":   (f'fill="{WASH}"', C["rule"], 1, ""),
        "ghost":   (f'fill="{C["plate"]}"', GUARD, 0.75, ""),
        "zone":    ('fill="none"', C["faint"], 1, ' stroke-dasharray="4 3"'),
        "blocked": ('fill="none"', C["rule"], 1, ' stroke-dasharray="3 3"'),
        "floor":   ('fill="none"', C["rule"], 1, ""),
    }
    SOLID = {"card", "guard", "sandbox", "agent", "blocked", "floor"}

    def box(self, x, y, w, h, kind, tag):
        """Drawn half a unit inside its box, so a hairline on the canvas edge is
        not clipped and every edge lands on the pixel grid; recorded at its box."""
        fill, stroke, sw, dash = self.STYLE[kind]
        self.parts.append(f'<rect x="{x + .5:g}" y="{y + .5:g}" width="{w - 1:g}" '
                          f'height="{h - 1:g}" rx="4" {fill} '
                          f'stroke="{stroke}" stroke-width="{sw}"{dash}/>')
        self.shapes.append({"tag": tag, "kind": kind, "x": x, "y": y, "w": w, "h": h,
                            "solid": kind in self.SOLID})

    def badge(self, cx, cy, n, tag):
        """A boundary number: an accent disc with the numeral knocked out. It
        sits on the corner of the part that enforces the boundary, so it reads
        as a mark on that part rather than as a word in its name."""
        self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="{GUARD}"/>')
        self.text(cx - 3.3, cy + 3.9, str(n), NUM, C["plate"], "600", True, tag=f"#{tag}")
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
        meta = {"W": self.W, "H": self.H, "shapes": self.shapes, "links": self.links,
                "margin": m}
        if self.narrow:
            meta["phone"] = {"display_px": 343, "min_px": 10}
        else:
            meta["print"] = {"width_in": PRINT_IN, "min_pt": MIN_PT}
        super().write(name, out_dir=HERE)
        (HERE / f".{name}.geom.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")



# ═════════════════════════════════════════════════════════════════════════════
# The shared skeleton (Figures 2–6). Every coordinate the levels share is here.
# ═════════════════════════════════════════════════════════════════════════════
class K:
    """Columns, left to right: A who or what starts the work · B what
    orchestrates and runs it · C the sandbox(es) · D the egress proxy · E what
    the proxy lets through. Rows, top to bottom: the authorization service, the
    frame where agents run (main row, then a lane below it), the outputs, the
    outer loop, the observability floor. `shifted(dy)` moves everything below
    the authorization service, for a figure whose service says more."""
    A = (0, 112)
    FX = (122, 572)
    B = (134, 234)
    BUS_B = 246
    C = (264, 436)
    D = (460, 560)
    BUS_E = 582
    E = (600, 720)
    AUTH = (264, 10, 560, 66)
    GRANT_Y = 80
    FY = (88, 350)
    FY_SHORT = 290            # the frame ends under the main row until Level 3 fills the lane
    LABY = 108
    ROW = (124, 276)
    MID = 200
    PROXY = (460, 158, 560, 242)
    LANE = (296, 342)
    EXIT_Y = 374              # pull requests leave through the proxy along here
    OUT = (394, 450)
    PR = (264, 364)
    APPROVAL = (384, 476)
    SLOT3 = (496, 588)
    SLOT4 = (608, 720)
    LOOPY = 492
    LOOP_X = 36               # the outer loop climbs back to column A here
    LOOP_LABEL_X = 66         # and is labelled here, at every level
    FLOOR = (508, 550)
    H = 552

    @classmethod
    def shifted(cls, dy):
        k = type("Kd", (cls,), {})
        for a in ("GRANT_Y", "LABY", "MID", "LOOPY", "H", "FY_SHORT", "EXIT_Y"):
            setattr(k, a, getattr(cls, a) + dy)
        for a in ("FY", "ROW", "LANE", "OUT", "FLOOR"):
            setattr(k, a, tuple(v + dy for v in getattr(cls, a)))
        k.PROXY = (cls.PROXY[0], cls.PROXY[1] + dy, cls.PROXY[2], cls.PROXY[3] + dy)
        k.AUTH = (cls.AUTH[0], cls.AUTH[1], cls.AUTH[2], cls.AUTH[3] + dy)
        return k


def mid(a):
    return (a[0] + a[1]) / 2


def skel_auth(f, k=K, gloss=("decides what access each task gets",), grant_label=True):
    x0, y0, x1, y1 = k.AUTH
    f.node(x0, y0, x1 - x0, y1 - y0, "Runtime authorization service", gloss,
           kind="guard", num=1, tag="auth")
    # authorized scope, down to the proxy — the same line at every level
    px = mid((k.PROXY[0], k.PROXY[2]))
    f.link([(px, y1), (px, k.PROXY[1])], "grant", tag="grant")
    if grant_label:
        f.gloss(px + 8, k.GRANT_Y, "authorized scope", "grant.l")


def skel_frame(f, label, gloss="", k=K, full=False):
    """Where the agents run. It grows to take in the lane below the main row
    only when something runs there (Level 3's monitoring agent)."""
    y1 = k.FY[1] if full else k.FY_SHORT
    f.box(k.FX[0], k.FY[0], k.FX[1] - k.FX[0], y1 - k.FY[0], "zone", "frame")
    w = f.lab(k.B[0], k.LABY, label, "frame.l")
    if gloss:
        f.gloss(k.B[0] + w + 8, k.LABY, gloss, "frame.g")


def skel_proxy(f, gloss=("default-deny;", "attaches", "credentials"), k=K, stack=False):
    """From Level 2 the paper has "an egress proxy per agent": the proxy keeps
    its place and gains the same stack the per-run sandbox has."""
    x0, y0, x1, y1 = k.PROXY
    if stack:  # the others sit behind it, so the one drawn in front keeps its size
        for d in (6, 3):
            f.box(x0 + d, y0 + d, x1 - x0, y1 - y0, "ghost", f"pghost{d}")
    f.node(x0, y0, x1 - x0, y1 - y0, "Egress proxy", gloss, kind="guard", num=4, tag="proxy")
    return x1, y1


# What the proxy lets through — the same four at every level. The admission
# point is the paper's generic term ("an admission point, such as a registry or
# a dedicated firewall"), so the label holds from Level 1, where it is an
# approved registry, to Level 3, where it is usually a supply chain firewall.
DEST = [  # (name, gloss lines, kind, boundary)
    ("Source control", ["the repository"], "card", None),
    ("Services", ["the task needs"], "card", None),
    ("Model gateway", ["approved models"], "guard", None),
    ("Admission point", ["approved, scanned", "packages"], "guard", 2),
]


def card_h(gloss, name=""):
    """A destination card's height: one name line and one gloss line is 44;
    each further line adds its leading."""
    names = len(name) if isinstance(name, (list, tuple)) else 1
    # even heights, so every fan branch lands on a whole unit
    return 44 + 16 * (names - 1) + 14 * max(len(gloss) - 1, 0)


def skel_dest(f, dest=DEST, blocked_note=True, k=K, px1=None):
    """The proxy's one way out, fanned to the destinations it allows."""
    ys = []
    y = k.ROW[0]
    for i, (n, g, kind, num) in enumerate(dest):
        h = card_h(g, n)
        f.node(k.E[0], y, k.E[1] - k.E[0], h, n, g, kind=kind, num=num, tag=f"dest{i}")
        ys.append((y + h / 2, kind))
        y += h + 8
    f.link([(px1 or k.PROXY[2], k.MID), (k.BUS_E, k.MID)], head=False, tag="bus.in",
           group="bus")
    f.link([(k.BUS_E, ys[0][0]), (k.BUS_E, ys[-1][0])], head=False, tag="bus", group="bus")
    for i, (yy, kind) in enumerate(ys):
        f.link([(k.BUS_E, yy), (k.E[0], yy)], tag=f"bus.{i}", group="bus",
               bar=(kind == "blocked"))
    if blocked_note:
        f.gloss(k.E[0], y + 10, "everything else", "blocked1")
        f.gloss(k.E[0], y + 24.5, "is blocked", "blocked2")
    return y


def skel_pr_exit(f, k=K, bottom=None):
    """Pull requests leave by the same path as everything else: the proxy."""
    px = mid((k.PROXY[0], k.PROXY[2]))
    yy = k.EXIT_Y
    f.link([(px, bottom or k.PROXY[3]), (px, yy), (mid(k.PR), yy), (mid(k.PR), k.OUT[0])],
           tag="pr.exit")
    f.gloss(px - 10 - f.width("opens a pull request", "gloss"), yy - 6, "opens a pull request",
            "pr.exit.l")


def outer_loop(f, start_x, end_y, gloss, k=K):
    """The outer loop: one route and one label position at every level. It
    leaves the bottom of the outputs row, runs left under it and climbs back
    to column A — where work starts — and its gloss names what drives it, as
    the paper's definition does (the developer; review feedback; signals)."""
    f.link([(start_x, k.OUT[1]), (start_x, k.LOOPY), (k.LOOP_X, k.LOOPY), (k.LOOP_X, end_y)],
           "loop", tag="outer")
    f.lab(k.LOOP_LABEL_X, k.LOOPY - 24, "outer loop", "outer.l")
    f.gloss(k.LOOP_LABEL_X, k.LOOPY - 8, gloss, "outer.g")


def out_card(f, slot, name, gloss, tag, k=K):
    f.node(slot[0], k.OUT[0], slot[1] - slot[0], k.OUT[1] - k.OUT[0], name, gloss, tag=tag)


def out_chain(f, slots, k=K):
    my = mid(k.OUT)
    for a, b in zip(slots, slots[1:]):
        f.link([(a[1], my), (b[0], my)], tag=f"out{a[0]}")


def floor(f, gloss, k=K):
    y0, y1 = k.FLOOR
    f.box(0, y0, W, y1 - y0, "floor", "obs")
    f.name(PAD, y0 + 26, "Observability", "obs.n")
    f.gloss(PAD + f.width("Observability", "name") + 14, y0 + 26, gloss, "obs.g")


def sandbox_one(f, label, name, gloss, loop=("inner loop,", "until it passes"),
                stack=False, k=K):
    x0, x1 = k.C
    y0, y1 = k.ROW
    if stack:  # a fresh sandbox per run: the ones before it, behind it
        for d in (8, 4):
            f.box(x0 + d, y0 + d, x1 - x0 - 8, y1 - y0 - 8, "ghost", f"ghost{d}")
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
    return (x0, y0, x1, y1)


def sandbox_three(f, k=K):
    """Level 3: several agents, each in its own sandbox with its own profile."""
    x0, x1 = k.C
    hh = (k.ROW[1] - k.ROW[0] - 16) / 3
    mids = []
    for i in range(3):
        y0 = k.ROW[0] + i * (hh + 8)
        f.box(x0, y0, x1 - x0, hh, "sandbox", f"sbx{i}")
        f.badge(x0, y0, 3, f"sbx{i}")
        f.name(x0 + PAD + 4, y0 + 20, f"Agent, task {i + 1}", f"sbx{i}.n")
        f.gloss(x0 + PAD + 4, y0 + 35, "its own profile", f"sbx{i}.g")
        f.loop_glyph(x1 - 18, y0 + hh / 2, f"sbx{i}.loop")
        mids.append(y0 + hh / 2)
    return mids


# ── Level 1 ──────────────────────────────────────────────────────────────────
def level1(f):
    skel_auth(f)
    skel_frame(f, "Developer's machine", "or a remote environment")
    f.node(K.A[0], K.MID - 40, K.A[1] - K.A[0], 80, "Developer",
           ["directs the", "agent, reviews", "its output"], tag="dev")
    sx0, sy0, sx1, sy1 = sandbox_one(f, "Sandbox", "Coding agent",
                                     ["profile in its harness,", "workflow in a skill"])
    f.link([(K.A[1], K.MID), (sx0, K.MID)], tag="directs")
    skel_proxy(f)
    f.link([(sx1, K.MID), (K.PROXY[0], K.MID)], tag="traffic")
    skel_dest(f)
    skel_pr_exit(f)
    out_card(f, K.PR, "Pull request", ["the developer", "reviews it"], "pr")
    outer_loop(f, mid(K.PR), K.MID + 40, "the developer drives the next run")
    floor(f, "harness logs, identity and proxy records, reviewed by the developer")


# ── Level 2 ──────────────────────────────────────────────────────────────────
def level2(f):
    skel_auth(f)
    skel_frame(f, "The factory", "a shared service with its own identity")
    f.node(K.A[0], K.MID - 48, K.A[1] - K.A[0], 96, "Request",
           ["or an event,", "a schedule", "or a ticket"], tag="req")
    f.node(K.B[0], K.MID - 48, K.B[1] - K.B[0], 96, "Workflow",
           ["on CI/CD, a", "step runner", "or Temporal"], tag="wf")
    f.link([(K.A[1], K.MID), (K.B[0], K.MID)], tag="starts")
    sx0, sy0, sx1, sy1 = sandbox_one(f, "Sandbox per run", "Coding agent",
                                     ["own identity,", "own profile"], stack=True)
    f.link([(K.B[1], K.MID), (sx0, K.MID)], tag="launches")
    px1, py1 = skel_proxy(f, stack=True)
    f.link([(sx1, K.MID), (K.PROXY[0], K.MID)], tag="traffic")
    skel_dest(f, px1=px1)
    skel_pr_exit(f, bottom=py1)
    out_card(f, K.PR, "Pull request", ["reviewed", "until ready"], "pr")
    out_card(f, K.APPROVAL, "Approval", ["a person or", "automatic"], "appr")
    out_card(f, K.SLOT3, "Merge", ["approved", "changes"], "merge")
    out_chain(f, [K.PR, K.APPROVAL, K.SLOT3])
    outer_loop(f, mid(K.PR), K.MID + 48, "review feedback drives the next run")
    floor(f, "records from all four boundaries, linked by run; evals track quality")


# ── Level 3 ──────────────────────────────────────────────────────────────────
def level3(f):
    skel_auth(f)
    skel_frame(f, "The factory", full=True)
    f.node(K.A[0], K.MID - 56, K.A[1] - K.A[0], 112, ["Signals and", "requests"],
           ["incidents,", "scanner", "findings,", "evals"], tag="sig")
    # the orchestrator plans; the execution layer starts agents
    ob = (K.B[0], K.ROW[0], K.B[1] - K.B[0], 70)
    f.node(*ob, ["Orchestrator", "agent"], ["preflight"], kind="agent", tag="orch")
    eb = (K.B[0], K.ROW[0] + 82, K.B[1] - K.B[0], K.ROW[1] - K.ROW[0] - 82)
    f.node(*eb, ["Execution", "layer"], ["starts each", "agent"], tag="exec")
    f.link([(K.A[1], K.ROW[0] + 35), (K.B[0], K.ROW[0] + 35)], tag="takes")
    # the proposal goes up to the authorization service — never straight to a grant
    pxp = K.B[1] - 8
    ay = mid((K.AUTH[1], K.AUTH[3]))
    f.link([(pxp, K.ROW[0]), (pxp, ay), (K.AUTH[0], ay)], tag="propose")
    f.gloss(pxp - 8 - f.width("proposes profile", "gloss"), 34, "proposes profile", "propose.l1")
    f.gloss(pxp - 8 - f.width("and task scope", "gloss"), 48.5, "and task scope", "propose.l2")
    mids = sandbox_three(f)
    ey = eb[1] + eb[3] / 2
    f.link([(K.B[1], ey), (K.BUS_B, ey)], head=False, tag="exec.bus", group="xb")
    f.link([(K.BUS_B, mids[0]), (K.BUS_B, mids[-1])], head=False, tag="xbus", group="xb")
    for i, m in enumerate(mids):
        f.link([(K.BUS_B, m), (K.C[0], m)], tag=f"xb{i}", group="xb")
    px1, py1 = skel_proxy(f, stack=True)
    f.link([(K.C[1], K.MID), (K.PROXY[0], K.MID)], tag="traffic")
    skel_dest(f, px1=px1)
    # a monitoring agent watches from outside the sandboxes and feeds back work
    mx0, mx1 = K.C
    f.node(mx0, K.LANE[0], mx1 - mx0, K.LANE[1] - K.LANE[0], "Monitoring agent",
           ["watches, never grants"], kind="agent", tag="mon")
    f.link([(mid(K.C), K.LANE[0]), (mid(K.C), K.ROW[1])], tag="watch")
    my = mid(K.LANE)
    f.link([(mx0, my), (80, my), (80, K.MID + 56)], tag="flags")
    f.gloss(mx0 - 10 - f.width("flags new work", "gloss"), my - 6, "flags new work", "flags.l")
    skel_pr_exit(f, bottom=py1)
    out_card(f, K.PR, "Pull request", ["reviewed", "until ready"], "pr")
    out_card(f, K.APPROVAL, "Approval", ["a person or", "automatic"], "appr")
    out_card(f, K.SLOT3, "Deploy", ["can be", "rolled back"], "deploy")
    out_card(f, K.SLOT4, "Production", ["sends back", "signals"], "prod")
    out_chain(f, [K.PR, K.APPROVAL, K.SLOT3, K.SLOT4])
    outer_loop(f, mid(K.SLOT4), K.MID + 56, "production signals start new work")
    floor(f, "telemetry and evals across runs; monitoring of running agents")


def build_level(n, fn, title, desc):
    f = SF(f"sf{n}", W, K.H, title, desc)
    fn(f)
    f.set_height(K.H)
    f.write(f"figure-{n}")


# ═════════════════════════════════════════════════════════════════════════════
# Figure 2 — the agent proposes, policy authorizes, infrastructure enforces.
# The skeleton with the authorization model in the place where, from Figure 3
# on, the work starts; and the legend, introduced once.
# ═════════════════════════════════════════════════════════════════════════════
FIG2_DESC = ("The profile sets the most an agent can ever do, the task narrows it to the work "
             "at hand, and delegation can only narrow it further; together they bound the "
             "runtime authorization service's decision. The agent, free to reason and try "
             "things inside its sandbox, proposes the scope it needs. The authorization service "
             "decides, and passes the authorized scope to the egress proxy, which enforces it "
             "and attaches credentials, so the agent holds none and only authorized operations "
             "reach downstream systems.")


def scope_nest(f, x0, y0, x1, y1):
    """Profile ⊃ task ⊃ delegation: each a hairline card inside the last."""
    f.box(x0, y0, x1 - x0, y1 - y0, "card", "prof")
    f.name(x0 + PAD, y0 + 21, "Profile", "prof.n")
    f.gloss(x0 + PAD, y0 + 37, "the most it can ever do", "prof.g")
    f.box(x0 + 10, y0 + 46, x1 - x0 - 20, y1 - y0 - 56, "card", "task")
    f.name(x0 + 20, y0 + 67, "Task", "task.n")
    f.gloss(x0 + 20, y0 + 83, "narrows it to the work", "task.g")
    f.box(x0 + 20, y0 + 92, x1 - x0 - 40, y1 - y0 - 112, "card", "dlg")
    f.name(x0 + 30, y0 + 113, "Delegation", "dlg.n")
    f.gloss(x0 + 30, y0 + 129, "only narrows it further", "dlg.g")


def legend(f, x, y, width):
    """The legend, once: what the colour, the fill, the numbers and the two
    kinds of line mean. Wraps to the width it is given."""
    f.rule(y - 18, x, x + width)
    f.box(x, y - 11, 28, 16, "guard", "lg.guard")
    lines = (["Enforced outside the agent's loop, numbered by the boundary it holds"]
             if width > 600 else ["Enforced outside the agent's loop,", "numbered by the boundary"])
    for i, s in enumerate(lines):
        f.text(x + 40, y + 1 + i * 15, s, GLOSS, C["ink"], tag=f"lg.g{i}")
    y += (len(lines) - 1) * 15 + 26
    bx, by = x + 40, y
    for n, s in ((1, "Identity and access"), (2, "Supply chain"), (3, "Sandbox"), (4, "Network")):
        w = 22 + f.width(s, "gloss")
        if bx + w > x + width:
            bx, by = x + 40, by + 24
        f.badge(bx + 8, by - 4, n, f"lg{n}")
        f.gloss(bx + 22, by, s, f"lg{n}.t")
        bx += w + 20
    y = by + 32
    f.box(x, y - 11, 28, 16, "agent", "lg.wash")
    f.text(x + 40, y + 1, "Untrusted agent execution", GLOSS, C["ink"], tag="lg.wash.t")
    if width > 600:
        sx = [x + 246, x + 452]
        ys = [y, y]
    else:
        sx = [x, x]
        ys = [y + 26, y + 50]
    f.link([(sx[0], ys[0] - 4), (sx[0] + 28, ys[0] - 4)], tag="lg.flow", free=True)
    f.text(sx[0] + 40, ys[0] + 1, "Request or traffic", GLOSS, C["ink"], tag="lg.flow.t")
    f.link([(sx[1], ys[1] - 4), (sx[1] + 28, ys[1] - 4)], "grant", tag="lg.grant", free=True)
    f.text(sx[1] + 40, ys[1] + 1, "Authorization decision", GLOSS, C["ink"], tag="lg.grant.t")
    return ys[1] + 6


def figure2():
    k = K.shifted(10)
    f = SF("sf2", W, 440, "The agent proposes, policy authorizes, and infrastructure enforces",
           FIG2_DESC)
    skel_auth(f, k, ("decides what access each task gets,", "routes high-impact actions to approval"),
              grant_label=False)
    px = mid((k.PROXY[0], k.PROXY[2]))
    f.gloss(px + 8, mid((k.AUTH[3], k.PROXY[1])) + 4, "authorized scope", "grant.l")
    # profile ⊃ task ⊃ delegation bound the decision
    y0, y1 = k.ROW
    scope_nest(f, 0, y0, K.B[1], y1)
    ay = mid((k.AUTH[1], k.AUTH[3]))
    bx = mid((0, K.B[1]))
    f.link([(bx, y0), (bx, ay), (k.AUTH[0], ay)], tag="bound")
    f.gloss(bx + 12, ay - 8, "bound the decision", "bound.l")
    # the agent, free inside its sandbox, proposes what it needs
    sx0, sx1 = k.C
    f.box(sx0, y0, sx1 - sx0, y1 - y0, "sandbox", "sbx")
    f.badge(sx0, y0, 3, "sbx")
    f.lab(sx0 + PAD + 4, y0 + 24, "Sandbox", "sbx.l")
    f.name(sx0 + PAD + 4, y0 + 52, "Agent", "sbx.n")
    f.gloss(sx0 + PAD + 4, y0 + 68, "holds no credentials", "sbx.g")
    gy = y1 - 30
    f.loop_glyph(sx0 + PAD + 11, gy - 4, "sbx.loop")
    f.gloss(sx0 + PAD + 26, gy, "free to reason", "sbx.lp0")
    f.gloss(sx0 + PAD + 26, gy + 14.5, "and try things", "sbx.lp1")
    ux = sx1 - 40
    f.link([(ux, y0), (ux, k.AUTH[3])], tag="propose")
    f.gloss(ux - 8 - f.width("proposes scope", "gloss"), mid((k.AUTH[3], y0)) + 4,
            "proposes scope", "propose.l")
    skel_proxy(f, ("enforces it,", "attaches", "credentials"), k=k)
    f.link([(sx1, k.MID), (k.PROXY[0], k.MID)], tag="request")
    f.node(K.E[0], k.PROXY[1], K.E[1] - K.E[0], k.PROXY[3] - k.PROXY[1], "Downstream",
           ["only authorized", "operations", "reach it"], tag="down")
    f.link([(k.PROXY[2], k.MID), (K.E[0], k.MID)], tag="out")
    end = legend(f, 0, y1 + 44, W)
    f.set_height(end)
    f.write("figure-2")


# ═════════════════════════════════════════════════════════════════════════════
# Figure 6 — only a new authorization decision can widen a task. Level 3's
# skeleton with one incident running through it, in the paper's own words
# ("A factory in action").
# ═════════════════════════════════════════════════════════════════════════════
FIG6_DESC = ("A production alert reports elevated errors in a payments service. The "
             "orchestrator agent proposes a task for an incident agent: read the service's logs "
             "for the last hour and open one pull request. The runtime authorization service "
             "checks it against policy and the alert's authenticated source, and the egress "
             "proxy attaches credentials only to the requests it grants. When the agent reaches "
             "for an unrelated authentication service's logs, the task doesn't cover them and "
             "the proxy blocks the call; only a new authorization decision could widen the task. "
             "The fix uses a library admitted through the supply chain and leaves as a pull "
             "request that approval policy routes to a person or approves automatically. The "
             "deploy reaches a small share of traffic first, and the error rate afterward "
             "confirms the fix or starts the next run.")
FIG6_AUTH = ("checks it against policy and the", "alert's authenticated source")


def figure6():
    k = K.shifted(10)
    f = SF("sf6", W, k.H, "Only a new authorization decision can widen a task", FIG6_DESC)
    skel_auth(f, k, FIG6_AUTH)
    skel_frame(f, "The factory", k=k)
    f.node(k.A[0], k.MID - 48, k.A[1] - k.A[0], 96, ["Production", "alert"],
           ["elevated errors", "in a payments", "service"], tag="sig")
    ob = (k.B[0], k.ROW[0], k.B[1] - k.B[0], 110)
    f.node(*ob, ["Orchestrator", "agent"], ["proposes a", "task for an", "incident", "agent"],
           kind="agent", tag="orch")
    f.link([(k.A[1], k.ROW[0] + 46), (k.B[0], k.ROW[0] + 46)], tag="takes")
    # what the task asks for rides on the proposal, into the authorization service
    pxp = k.B[1] - 8
    ay = mid((k.AUTH[1], k.AUTH[3]))
    f.link([(pxp, k.ROW[0]), (pxp, ay), (k.AUTH[0], ay)], tag="propose")
    for i, s in enumerate(("read the service's logs,", "last hour, one pull request")):
        f.gloss(pxp - 8 - f.width(s, "gloss"), ay + 20 + i * 14.5, s, f"propose.l{i}")
    x0, x1 = k.C
    y0, y1 = k.ROW
    f.box(x0, y0, x1 - x0, y1 - y0, "sandbox", "sbx")
    f.badge(x0, y0, 3, "sbx")
    f.lab(x0 + PAD + 4, y0 + 24, "Sandbox", "sbx.l")
    f.name(x0 + PAD + 4, y0 + 52, "Incident agent", "sbx.n")
    f.gloss(x0 + PAD + 4, y0 + 68, "configured from", "sbx.g0")
    f.gloss(x0 + PAD + 4, y0 + 82.5, "its profile", "sbx.g1")
    gy = y1 - 30
    f.loop_glyph(x0 + PAD + 11, gy - 4, "sbx.loop")
    f.gloss(x0 + PAD + 26, gy, "inner loop,", "sbx.lp0")
    f.gloss(x0 + PAD + 26, gy + 14.5, "until tests pass", "sbx.lp1")
    # wanting more is a request for a new decision, never a grant
    ux = x1 - 40
    f.link([(ux, y0), (ux, k.AUTH[3])], tag="wider")
    f.gloss(ux - 8 - f.width("asks for a new decision", "gloss"), k.GRANT_Y,
            "asks for a new decision", "wider.l")
    skel_proxy(f, ("enforces it,", "attaches", "credentials"), k=k)
    f.link([(x1, k.MID), (k.PROXY[0], k.MID)], tag="traffic")
    skel_dest(f, [(["Payments", "service logs"], ["last hour only"], "card", None),
                  (["Authentication", "service logs"], ["blocked: outside", "the task"],
                   "blocked", None),
                  ("Admission point", ["serves the", "approved library"], "guard", 2)],
              blocked_note=False, k=k)
    skel_pr_exit(f, k=k)
    slots = [(264, 364), (384, 470), (490, 600), (620, 720)]
    out_card(f, slots[0], "Pull request", ["one, as", "granted"], "pr", k=k)
    out_card(f, slots[1], "Approval", ["a person or", "automatic"], "appr", k=k)
    out_card(f, slots[2], "Deploy", ["small share of", "traffic first"], "deploy", k=k)
    out_card(f, slots[3], "Production", ["error rate", "afterward"], "prod", k=k)
    out_chain(f, slots, k=k)
    outer_loop(f, mid(slots[3]), k.MID + 48, "confirms the fix or starts the next run", k=k)
    f.set_height(k.LOOPY + 8)
    f.write("figure-6")


# ═════════════════════════════════════════════════════════════════════════════
# Figure 1 — work loops until it passes, and problems feed back to design
# ═════════════════════════════════════════════════════════════════════════════
FIG1_DESC = ("Work arrives as a prompt, a PRD or a ticket, and design sets its limits. The "
             "inner loop assembles what the task needs, builds the change in a sandbox and "
             "verifies it against the organization's standards, repeating until the work passes. "
             "Review, and deployment under approval policy, follow. The outer loop feeds review, "
             "evals and production feedback back into design, and production sends back signals "
             "that start new work.")


def figure1():
    f = SF("sf1", W, 340, "Work loops until it passes, and problems feed back to design",
           FIG1_DESC)
    y0, h = 40, 64
    ym = y0 + h / 2
    f.node(28, y0, 96, h, "Inputs", ["a prompt, PRD", "or ticket"], tag="in")
    f.node(148, y0, 114, h, "Design", ["sets the limits", "in advance"], tag="design")
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
    f.gloss(xs[1] + 6, ly + 18, "until it passes", "again.l")
    f.gloss(xs[0], 186, "Assembled from agents and harnesses, models, skills,", "blocks1")
    f.gloss(xs[0], 200.5, "tools and MCP servers, dependencies and blueprints", "blocks2")
    # out of the loop, right to left: review → deploy → production
    b0, rw, bg = 256, 140, 36
    rx = [W - rw, W - 2 * rw - bg, W - 3 * rw - 2 * bg]
    bm = b0 + h / 2
    f.node(rx[0], b0, rw, h, "Review", ["of the change"], tag="review")
    f.node(rx[1], b0, rw, h, "Deploy", ["under approval", "policy"], tag="deploy")
    f.node(rx[2], b0, rw, h, "Production", ["sends back signals,", "such as incidents"],
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


# ═════════════════════════════════════════════════════════════════════════════
# Narrow compositions (phones). Not the wide drawing scaled down: the same
# relationships in one column, with one skeleton shared by Figures 3, 4 and 5.
# ═════════════════════════════════════════════════════════════════════════════
NW = 360


class N:
    """The narrow skeleton, shared by Figures 3, 4 and 5 on a phone. A rail
    down the left margin carries the outer loop back to the start card."""
    RAIL = 4
    X0, X1 = 24, 360
    AUTH = (24, 10, 360, 62)
    A = (24, 214)
    IN = (36, 214)        # inside the frame: orchestration, sandboxes, monitoring
    PROXY = (232, 330)
    BUS = 345
    DEST = (24, 326)
    GX = 74               # where the vertical arrows run


def narrow_level(n, title, desc):
    f = SF(f"sf{n + 2}n", NW, 1000, title, desc, narrow=True)
    x0, y0, x1, y1 = N.AUTH
    f.node(x0, y0, x1 - x0, y1 - y0, "Runtime authorization service",
           ["decides what access each task gets"], kind="guard", num=1, tag="auth")
    y = 84
    a = {1: ("Developer", ["directs the agent and", "reviews its output"]),
         2: ("Request", ["or an event, a schedule", "or a ticket"]),
         3: ("Signals and requests", ["incidents, scanner", "findings, evals"])}[n]
    f.node(N.A[0], y, N.A[1] - N.A[0], 66, a[0], a[1], tag="start")
    a_mid = y + 33
    prev = y + 66
    y += 66 + 24
    fy0 = y
    f.lab(N.GX + 14, fy0 + 22, "Developer's machine" if n == 1 else "The factory", "frame.l")
    y += 40
    ix0, ix1 = N.IN
    if n == 2:
        f.node(ix0, y, ix1 - ix0, 66, "Workflow", ["on CI/CD, a step runner", "or Temporal"],
               tag="wf")
        f.link([(N.GX, prev), (N.GX, y)], tag="starts")
        prev = y + 66
        y += 66 + 24
    elif n == 3:
        oy = y
        f.node(ix0, y, ix1 - ix0, 52, "Orchestrator agent", ["preflight: proposes scope"],
               kind="agent", tag="orch")
        f.link([(N.GX, prev), (N.GX, y)], tag="takes")
        f.link([(ix1, oy + 26), (ix1 + 12, oy + 26), (ix1 + 12, N.AUTH[3])], tag="propose")
        y += 52 + 24
        f.node(ix0, y, ix1 - ix0, 52, "Execution layer", ["starts each agent"], tag="exec")
        f.link([(N.GX, oy + 52), (N.GX, y)], tag="plans")
        prev = y + 52
        y += 52 + 24
    if n == 3:
        mids = []
        for i in range(3):
            f.box(ix0, y, ix1 - ix0, 46, "sandbox", f"sbx{i}")
            f.badge(ix0, y, 3, f"sbx{i}")
            f.name(ix0 + PAD + 4, y + 20, f"Agent, task {i + 1}", f"sbx{i}.n")
            f.gloss(ix0 + PAD + 4, y + 36, "its own profile", f"sbx{i}.g")
            f.loop_glyph(ix1 - 18, y + 23, f"sbx{i}.loop")
            if i == 0:
                f.link([(N.GX, prev), (N.GX, y)], tag="starts")
            mids.append(y + 23)
            y += 46 + 8
        sb_mid = mids[1]
        y += 16
        f.node(ix0, y, ix1 - ix0, 46, "Monitoring agent", ["watches, never grants"],
               kind="agent", tag="mon")
        f.link([(N.GX + 60, y), (N.GX + 60, y - 24)], tag="watch")
        y += 46 + 16
    else:
        sh = 118
        if n == 2:  # a fresh sandbox per run
            for d in (6, 3):
                f.box(ix0 + d, y + d, ix1 - ix0 - 6, sh - 6, "ghost", f"ghost{d}")
        sw = ix1 - ix0 - (6 if n == 2 else 0)
        f.box(ix0, y, sw, sh - (6 if n == 2 else 0), "sandbox", "sbx")
        f.badge(ix0, y, 3, "sbx")
        f.lab(ix0 + PAD + 4, y + 24, "Sandbox per run" if n == 2 else "Sandbox", "sbx.l")
        f.name(ix0 + PAD + 4, y + 50, "Coding agent", "sbx.n")
        f.gloss(ix0 + PAD + 4, y + 66, "own identity and profile" if n == 2 else
                "profile in its harness", "sbx.g")
        f.loop_glyph(ix0 + PAD + 11, y + 86, "sbx.loop")
        f.gloss(ix0 + PAD + 26, y + 90, "inner loop,", "sbx.lp0")
        f.gloss(ix0 + PAD + 26, y + 104.5, "until it passes", "sbx.lp1")
        f.link([(N.GX, prev), (N.GX, y)], tag="into")
        sb_mid = y + 56
        y += sh + 16
    fy1 = y
    f.box(N.X0, fy0, N.X1 - N.X0, fy1 - fy0, "zone", "frame")
    # the proxy beside the sandbox (from Level 2, one per agent), and the
    # authorization decision down to it
    py0 = sb_mid - 42
    if n > 1:
        for d in (6, 3):
            f.box(N.PROXY[0] + d, py0 + d, N.PROXY[1] - N.PROXY[0], 84, "ghost", f"pghost{d}")
    f.node(N.PROXY[0], py0, N.PROXY[1] - N.PROXY[0], 84, "Egress proxy",
           ["default-deny;", "attaches", "credentials"], kind="guard", num=4, tag="proxy")
    f.link([(ix1 - (6 if n == 2 else 0), sb_mid), (N.PROXY[0], sb_mid)], tag="traffic")
    gx = mid(N.PROXY) + 16
    f.link([(gx, N.AUTH[3]), (gx, py0)], "grant", tag="grant")
    # the destinations, one list, fed down the right edge
    order = [DEST[2], DEST[3], DEST[1], DEST[0]]
    y = fy1 + 24
    ys = []
    for i, (nm, g, kind, num) in enumerate(order):
        gl = [", ".join(g).replace(", packages", " packages")]
        f.node(N.DEST[0], y, N.DEST[1] - N.DEST[0], 44, nm, gl, kind=kind, num=num,
               tag=f"dest{i}")
        ys.append(y + 22)
        y += 44 + 8
    sc_bottom = y - 8
    f.link([(N.PROXY[1], sb_mid), (N.BUS, sb_mid)], head=False, tag="bus.in", group="bus")
    f.link([(N.BUS, sb_mid), (N.BUS, ys[-1])], head=False, tag="bus", group="bus")
    for i, yy in enumerate(ys):
        f.link([(N.BUS, yy), (N.DEST[1], yy)], tag=f"bus.{i}", group="bus")
    f.gloss(N.GX + 40, y + 8, "Everything else is blocked.", "blocked")
    y += 24
    outs = {1: [("Pull request", "the developer reviews it")],
            2: [("Pull request", "reviewed until ready"), ("Approval", "a person or automatic"),
                ("Merge", "approved changes")],
            3: [("Pull request", "reviewed until ready"), ("Approval", "a person or automatic"),
                ("Deploy", "can be rolled back"), ("Production", "sends back signals")]}[n]
    f.link([(N.GX, sc_bottom), (N.GX, y)], tag="pr")
    for i, (nm, g) in enumerate(outs):
        f.node(N.X0, y, N.X1 - N.X0, 46, nm, [g], tag=f"out{i}")
        y += 46
        if i < len(outs) - 1:
            f.link([(N.GX, y), (N.GX, y + 22)], tag=f"o{i}")
            y += 22
    # the outer loop: down from the last card, back up the rail to the start card
    ly = y + 24
    f.link([(N.GX, y), (N.GX, ly), (N.RAIL, ly), (N.RAIL, a_mid), (N.A[0], a_mid)], "loop",
           tag="outer")
    f.lab(N.GX + 10, ly - 8, "outer loop", "outer.l")
    gloss = {1: "the developer drives the next run", 2: "review feedback drives the next run",
             3: "production signals start new work"}[n]
    f.gloss(N.GX + 10, ly + 14, gloss, "outer.g")
    y = ly + 32
    obs = {1: "harness logs, identity and proxy records",
           2: "records from all four boundaries, by run",
           3: "telemetry, evals, monitoring of agents"}[n]
    f.box(N.X0, y, N.X1 - N.X0, 46, "floor", "obs")
    f.name(N.X0 + PAD, y + 20, "Observability", "obs.n")
    f.gloss(N.X0 + PAD, y + 36, obs, "obs.g")
    f.set_height(y + 48)
    f.write(f"figure-{n + 2}-narrow")


def figure1_narrow():
    f = SF("sf1n", NW, 1000, "Work loops until it passes, and problems feed back to design",
           "Inputs, then design, then the inner loop of assemble, build and verify, repeated "
           "until the work passes; then review, deploy under approval policy, and production. "
           "The outer loop feeds review, evals and production feedback back into design, and "
           "production's signals start new work.", narrow=True)
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


if __name__ == "__main__":
    figure1()
    figure1_narrow()
    figure2()
    build_level(3, level1, "Level 1: a developer gives an agent room to work",
                "The developer directs one coding agent, which runs in a sandbox on the "
                "developer's machine or a remote environment and loops until its work passes. "
                "All of its traffic leaves through a default-deny egress proxy that enforces "
                "the runtime authorization service's decision and attaches credentials, so it "
                "reaches source control, the services the task needs, a model gateway and an "
                "admission point for packages, and nothing else. Its pull request goes back to "
                "the developer for review.")
    build_level(4, level2, "Level 2: a workflow orchestrates",
                "A request, event, schedule or ticket starts a predefined workflow on a durable "
                "execution layer, which launches a coding agent in a fresh sandbox for each run. "
                "The boundaries are the same as at Level 1. The pull request goes through "
                "approval policy and merges; review feedback drives the next run.")
    build_level(5, level3, "Level 3: an agent orchestrates but can't grant itself access",
                "Signals and requests reach an orchestrator agent, which proposes a profile and "
                "task scope for each piece of work to the runtime authorization service. The "
                "execution layer starts each agent in its own sandbox, with its own profile, "
                "and only with the access the service granted. A monitoring agent watches from "
                "outside the sandboxes. The boundaries are the same as at Levels 1 and 2. "
                "Approval is by a person or automatic; deploys reach production, which sends "
                "back signals.")
    for n, t in ((1, "Level 1"), (2, "Level 2"), (3, "Level 3")):
        narrow_level(n, t, f"{t}, as a single column for narrow screens.")
    figure6()
