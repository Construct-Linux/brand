import json, math, os, sys, tomllib

# usage: palette.py [out_dir]
# Reads palette.toml, fails if a pair the desktop draws one on the other reads badly - by WCAG's
# contrast, and by CIEDE2000 under colour-vision deficiencies and dim or non-OLED panels - and writes
# the palette out in the forms its users take (THEMING.md):
#   construct.css          custom properties, dark by default and light under prefers-color-scheme,
#                          and the shell's (--shell-*), dark in both: preview.html's
#   construct.scss         Orchis' variables: the accent, its text, the text, border and semantic
#                          colors per variant, the background scale, the tints and the radii
#   construct.json         every value of palette.toml in one flat object, for the image
#                          (/usr/share/construct/palette.json: Plymouth's theme, the test harness)
#   ghostty/Construct Dark, Construct Light
#                          Ghostty's themes: the view surface, the text, the accent, 16 colors
#   vscode/                VS Code's built-in construct-theme extension: package.json and the two
#                          color themes
#   perception.js          every perceptual pair (ΔE00 per tier, view and verdict), for preview.html
#   simulate.js            the checks' deficiencies and panels as SVG filters, for preview.html
# The other generators import load() instead of copying hex values.
HERE = os.path.dirname(os.path.abspath(__file__))


def load(path=os.path.join(HERE, "palette.toml")):
    with open(path, "rb") as f:
        return tomllib.load(f)


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def luminance(h):
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c / 255) for c in rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


# ---------- perception: what a pair looks like, not only its luminance ratio ----------
# WCAG's ratio says whether text reads; it says nothing about two surfaces a step apart, a state
# told by hue, or a panel dimmed in a lit room. These are CIEDE2000 differences (Sharma 2005)
# under colour-vision deficiencies and viewing conditions, in the stdlib only.

def linear(h):
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(lin(c / 255) for c in rgb(h))


def lab(v):
    """CIELAB (D65) of a linear sRGB triple."""
    x = 0.4124564 * v[0] + 0.3575761 * v[1] + 0.1804375 * v[2]
    y = 0.2126729 * v[0] + 0.7151522 * v[1] + 0.0721750 * v[2]
    z = 0.0193339 * v[0] + 0.1191920 * v[1] + 0.9503041 * v[2]
    f = lambda t: t ** (1 / 3) if t > (6 / 29) ** 3 else t / (3 * (6 / 29) ** 2) + 4 / 29
    fx, fy, fz = f(x / 0.95047), f(y / 1.0), f(z / 1.08883)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def de00(c1, c2):
    """CIEDE2000 between two CIELAB colors (Sharma, Wu and Dalal 2005)."""
    (L1, a1, b1), (L2, a2, b2) = c1, c2
    C = (math.hypot(a1, b1) + math.hypot(a2, b2)) / 2
    G = 0.5 * (1 - math.sqrt(C ** 7 / (C ** 7 + 25 ** 7)))
    a1p, a2p = a1 * (1 + G), a2 * (1 + G)
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    hue = lambda b, a: math.degrees(math.atan2(b, a)) % 360 if (a or b) else 0.0
    h1p, h2p = hue(b1, a1p), hue(b2, a2p)
    dL, dC = L2 - L1, C2p - C1p
    dh = 0.0 if C1p * C2p == 0 else (h2p - h1p if abs(h2p - h1p) <= 180 else
                                     h2p - h1p - 360 if h2p - h1p > 180 else h2p - h1p + 360)
    dH = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2))
    Lm, Cm = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0:
        hm = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hm = (h1p + h2p) / 2
    else:
        hm = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hm - 30)) + 0.24 * math.cos(math.radians(2 * hm))
         + 0.32 * math.cos(math.radians(3 * hm + 6)) - 0.20 * math.cos(math.radians(4 * hm - 63)))
    SL = 1 + 0.015 * (Lm - 50) ** 2 / math.sqrt(20 + (Lm - 50) ** 2)
    SC, SH = 1 + 0.045 * Cm, 1 + 0.015 * Cm * T
    RT = (-2 * math.sqrt(Cm ** 7 / (Cm ** 7 + 25 ** 7))
          * math.sin(math.radians(60 * math.exp(-(((hm - 275) / 25) ** 2)))))
    return math.sqrt((dL / SL) ** 2 + (dC / SC) ** 2 + (dH / SH) ** 2 + RT * (dC / SC) * (dH / SH))


# Sharma's test pair 1: a typo in the formula fails task palette before any pair is judged.
assert abs(de00((50, 2.6772, -79.7751), (50, 0, -82.7485)) - 2.0425) < 1e-3

# Machado, Oliveira and Fernandes 2009 at severity 1.0, applied to linear sRGB: dichromacy, the
# worst case. Anomalous trichromats, most of colour-vision deficiency, see more than this.
MACHADO = {
    "protan": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritan": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}

# How a panel shows a color: (white, black, flare) in cd/m2, and its gamma against sRGB. ref is
# ideal sRGB, what WCAG and ΔE assume; ips a non-OLED panel (830:1); dim an OLED at 30%, which
# crushes its blacks (gamma 1.1); dim_ips an IPS backlight at 30%. The flare is an office: 200 lx
# reflected at 1% off the glass, / pi = 0.6 cd/m2. The eye is taken as adapted to the panel's
# white, so a dim panel in a brighter room does worse than these numbers.
CONDITIONS = {"ref": (250, 0, 0, 1.0), "ips": (250, 0.3, 0.6, 1.0), "dim": (75, 0, 0.6, 1.1), "dim_ips": (75, 0.09, 0.6, 1.0)}

# What a pair's worst is the minimum over: each condition, each deficiency, and protan and deutan
# - 8% of men between them - on the office's IPS panel too.
VIEWS = {"ips": (None, "ips"), "dim": (None, "dim"), "dim_ips": (None, "dim_ips"), "protan": ("protan", "ref"),
         "deutan": ("deutan", "ref"), "tritan": ("tritan", "ref"), "protan+ips": ("protan", "ips"),
         "deutan+ips": ("deutan", "ips")}


def seen(h, cvd=None, cond="ref"):
    """The linear RGB the eye takes from h: through a deficiency, then off a panel."""
    v = linear(h)
    if cvd:
        v = tuple(min(1.0, max(0.0, sum(m * c for m, c in zip(row, v)))) for row in MACHADO[cvd])
    w, b, f, g = CONDITIONS[cond]
    return tuple((b + (w - b) * c ** g + f) / (w + f) for c in v)


def perceive(a, b):
    """ΔE00 of a pair as drawn, and in every view."""
    ref = de00(lab(seen(a)), lab(seen(b)))
    return ref, {k: de00(lab(seen(a, cvd, cond)), lab(seen(b, cvd, cond))) for k, (cvd, cond) in VIEWS.items()}


# A panel at 30% backlight in a room that lights it at 3% of its full white: the eye adapted to
# the room, not to the panel. preview.html's "30% backlight" view draws this; task palette prints
# what it leaves of the edges and states that matter (reported, not held: WCAG's own 0.05 already
# stands for flare, so holding this too would count the room twice).
LOW_LIGHT = (0.30, 0.03)


def low_light_contrast(a, b):
    k, room = LOW_LIGHT
    la, lb = (k * luminance(x) + room for x in (a, b))
    return max(la, lb) / min(la, lb)


def orchis_on_dark(h):
    """Whether Orchis' on() puts dark text on this color (its brightness test, _colors.scss)."""
    r, g, b = rgb(h)
    return (r * 299 + g * 587 + b * 114) / 1000 >= 156


# Orchis' dark text on a bright fill: black at 0.87, over white (the lightest it is drawn on).
ORCHIS_DARK_TEXT = "#212121"

# WCAG 2.2: 4.5 for text, 3 for parts of the interface that are not text; 7 for body text,
# which is read the most. REPORT is a pair printed with its contrast but held to nothing.
TEXT, UI, BODY, REPORT = 4.5, 3.0, 7.0, None

# The shell's quick toggle when off, and its other resting fills: white at 6% over the menu's h.
# States are an alpha over a palette surface, never a grey of their own (THEMING.md).
SHELL_FILL = 0.06


def mix(a, b, t):
    """a over b at opacity t, as an opaque color."""
    return "#" + "".join(f"{round(x * t + y * (1 - t)):02X}" for x, y in zip(rgb(a), rgb(b)))


def surfaces(p, mode):
    """A mode's window background and view: f and g in dark - e is the desktop's, so a window on
    it would have no edge - and c and a in light."""
    n = p["neutral"]
    return (n["f"], n["g"]) if mode == "dark" else (n["c"], n["a"])


def checks(p):
    n = p["neutral"]
    for mode in ("dark", "light"):
        m, t = p[mode], p["tint"][mode]
        window, view = surfaces(p, mode)
        for surface, s in (("window", window), ("view", view)):
            yield f"{mode} text on {surface}", m["text"], s, BODY
            yield f"{mode} muted on {surface}", m["muted"], s, TEXT
            yield f"{mode} accent on {surface} (links)", m["accent"], s, TEXT
            for k in ("success", "warning", "error"):
                yield f"{mode} {k} on {surface}", m[k], s, TEXT
        # The primary action is the solid accent: its label, and the focus ring drawn inside it in
        # the label's color (an accent ring would vanish on the accent).
        yield f"{mode} text on accent (the primary's label and its inner focus ring)", m["on_accent"], m["accent"], TEXT
        if mode == "dark":
            # GNOME Shell's menus, the calendar and the OSDs stand on the raised surface, h: the
            # desktop under them is e, often the wallpaper's own color.
            for k, need in (("text", BODY), ("muted", TEXT), ("accent", TEXT), ("success", TEXT), ("warning", TEXT), ("error", TEXT)):
                yield f"dark {k} on raised (shell menus)", m[k], n["h"], need
        # Buttons filled with a semantic color (destructive, success): Orchis puts black or white
        # on them by brightness, as on the accent. Error is never a fill: the destructive red is.
        for k in ("success", "warning", "destructive"):
            yield f"{mode} text on {k} fill", ORCHIS_DARK_TEXT if orchis_on_dark(m[k]) else "#FFFFFF", m[k], TEXT
        # The accent as a mark - the focus ring, a switch, a slider, the dock's running dot - on
        # every surface the mode draws one on.
        for k in ("efgh" if mode == "dark" else "ac"):
            yield f"{mode} accent mark on {k}", m["accent"], n[k], UI
        # A tint is the accent at an alpha over the surface it sits on; its label and icon are
        # accent_text, any second line text. Muted is printed, not held: it never goes on a tint.
        for k in ("fgh" if mode == "dark" else "abc"):
            for step in ("rest", "hover", "active"):
                fill = mix(m["accent"], n[k], t[step])
                where = f"{step} tint ({t[step]:.2f}) over {k}"
                yield f"{mode} accent_text on {where}", m["accent_text"], fill, TEXT
                yield f"{mode} text on {where}", m["text"], fill, TEXT
                yield f"{mode} muted on {where}", m["muted"], fill, REPORT
            # Focus on a selected item: the 2px ring on the strongest tint it can stand on.
            yield f"{mode} focus ring on active tint over {k}", m["accent"], mix(m["accent"], n[k], t["active"]), UI
            # A switch's track when on: the knob, full accent and checked as a mark above, carries
            # the state where the track falls short (light).
            yield f"{mode} switch track ({t['track']:.2f}) on {k}", mix(m["accent"], n[k], t["track"]), n[k], REPORT
        yield f"{mode} text on selection ({t['selection']:.2f}) over view", m["text"], mix(m["accent"], view, t["selection"]), BODY
        yield f"{mode} accent_text on selection over view", m["accent_text"], mix(m["accent"], view, t["selection"]), TEXT
    # The edges the brand asks for: not text, below WCAG's 3, but each one what tells one surface
    # from the next where no shadow shows (black on ink).
    d, edge = p["dark"], "edge (brand, not WCAG):"
    yield f"{edge} dark border ring on e (the desktop)", d["border"], n["e"], 1.5
    yield f"{edge} dark border ring on h (the menus)", d["border"], n["h"], 1.2
    yield f"{edge} h on e (a menu off the desktop)", n["h"], n["e"], 1.25
    yield f"{edge} light border on c (the window)", p["light"]["border"], n["c"], 1.4
    # Light: the desk under the windows, the shelf under the sidebar, and lines in the ink's hue.
    l, ln = p["light"], p["line"]["light"]
    line = lambda k, s: mix(l["muted"], s, ln[k])
    yield f"{edge} light window c on the desk", n["c"], l["desk"], 1.15
    yield f"{edge} light shelf against the window c", n["c"], l["shelf"], 1.07
    yield f"{edge} light sheet a (the selected row) on the shelf", n["a"], l["shelf"], 1.15
    yield f"{edge} light shelf against the desk", l["shelf"], l["desk"], 1.07
    yield f"{edge} light window ring ({ln['ring']}) over the desk", line("ring", l["desk"]), l["desk"], 1.6
    for k, s in (("a", n["a"]), ("c", n["c"]), ("shelf", l["shelf"])):
        yield f"{edge} light border line ({ln['border']}) over {k}", line("border", s), s, 1.45
    yield f"{edge} light divider line ({ln['divider']}) over a", line("divider", n["a"]), n["a"], 1.25
    for k, s, need in (("shelf", l["shelf"], BODY), ("desk", l["desk"], BODY)):
        yield f"light text on the {k}", l["text"], s, need
        yield f"light muted on the {k}", l["muted"], s, TEXT
    yield "light accent_text icon on the sheet (a mark)", l["accent_text"], n["a"], UI
    off = mix(n["a"], n["h"], SHELL_FILL)
    yield f"shell text on its resting fill ({SHELL_FILL} white over h)", d["text"], off, BODY
    yield f"shell muted on its resting fill ({SHELL_FILL} white over h)", d["muted"], off, TEXT
    yield "dark accent on boot (Plymouth's prompt, the lock ground)", d["accent"], p["brand"]["boot"], UI
    for mode in ("dark", "light"):
        term = terminal(p, mode)
        yield f"{mode} terminal text", term["foreground"], term["background"], BODY
        for i, c in enumerate(term["palette"]):
            # Each mode's background end of the scale - black in dark, white and bright white in
            # light - is drawn as a fill, never read; its other end is body text.
            if (mode, i) in (("dark", 0), ("light", 7), ("light", 15)):
                continue
            body = i in (7, 15) if mode == "dark" else i == 0
            yield f"{mode} terminal color {i}", c, term["background"], BODY if body else TEXT
        yield f"{mode} terminal cursor", term["cursor-color"], term["background"], UI
        yield f"{mode} terminal text under the cursor", term["cursor-text"], term["cursor-color"], TEXT
    yield "folder glyph on folder", p["icons"]["folder_glyph"], p["icons"]["folder"], UI
    yield "folder on dark background", p["icons"]["folder"], n["e"], UI
    yield "cursor outline on fill", p["cursor"]["outline"], p["cursor"]["fill"], UI
    yield "mark on boot", p["brand"]["cyan"], p["brand"]["boot"], BODY


def shape_problems(shape):
    """The radii and the spacing grid are whole pixels, the grid ascending: St and GTK round a
    fraction each their own way, and a concentric radius is a sum of them."""
    for k in ("radius_control", "radius_surface", "radius_sheet", "inset"):
        if type(shape[k]) is not int:
            yield f"shape.{k} = {shape[k]!r}: a whole number of pixels"
    space = shape["space"]
    if not all(type(v) is int for v in space) or any(a >= b for a, b in zip(space, space[1:])):
        yield f"shape.space = {space}: whole pixels, ascending"
    if not shape["radius_control"] < shape["radius_surface"] < shape["radius_sheet"]:
        yield "shape: radius_control < radius_surface < radius_sheet"


# ΔE00 floors (as drawn, worst view) by what a pair does. A ΔE00 of 1 is a just-noticeable
# difference only for large patches side by side under ideal light; thin lines and small marks
# need two to three times more (Szafir 2017), so the line and hue tiers ask more.
#   E   two surfaces meeting at an edge with nothing between them: seen at a glance, and still
#       there dimmed or on an IPS panel. A pair below it must carry a ring or a rule, held to R.
#   R   a 1px line against the surface outside it.
#   S1  a persistent state against its rest - on and off, selected and not - read without hover
#       or motion, by protans and deutans too.
#   S2  a transient step, rest to hover to active: it follows the pointer, so motion helps.
#   K   colors whose hue carries the meaning (status, the terminal's): 10 for protans and
#       deutans, 8% of men; 6 for tritans, about 0.01%.
#   P   the primary action against a selected item: the solid fill against the tint, the one
#       channel that tells them apart.
TIERS = {"E": (3, 2), "R": (6, 4), "S1": (10, 6), "S2": (3, 2), "K": (20, 10), "P": (30, 24)}
K_TRITAN = 6
# D, a transient overlay (the rubberband, the tile preview): it shows (E's 3 as drawn) and stays
# quieter than a selected item on the same surface, at most this share of the selected tint's ΔE.
# Its worst view is carried by the 1px accent edge it always draws.
DECORATION_SHARE = 0.6


def perceptual_checks(p):
    """(tier, name, outside, inside, ring): ring, when given, is the line drawn between the two,
    and a pair below its tier passes if that line holds R against the outside surface. For D the
    fifth is instead the selected tint on the same surface, which the overlay stays quieter than.
    Tier None is a pair reported, not held."""
    n, d, l, ln = p["neutral"], p["dark"], p["light"], p["line"]["light"]
    td, tl = p["tint"]["dark"], p["tint"]["light"]
    line = lambda k, s: mix(l["muted"], s, ln[k])
    # Dark: the elevation steps; the ring makes the edges the steps alone cannot.
    yield "E", "dark e/f: a window on the desktop", n["e"], n["f"], d["border"]
    yield "E", "dark f/g: the content or headerbar beside the window body", n["f"], n["g"], d["border"]
    yield "E", "dark g/h: a menu over the bars or a view", n["g"], n["h"], None
    yield "E", "dark boot/e: the workspace card on the overview", p["brand"]["boot"], n["e"], None
    yield "E", "dark e/g: the bars on the desktop", n["e"], n["g"], None
    yield "E", "dark e/h: a menu on the desktop", n["e"], n["h"], None
    for k in "efg":
        yield "R", f"dark border ring on {k}", n[k], d["border"], None
    # Level 3 over h (a dialog over quick settings) leans on its shadow: the ring alone is not an
    # edge there, until a lighter ring for that level exists.
    yield None, "dark border ring on h (level 3 over a menu)", n["h"], d["border"], None
    off = mix(n["a"], n["h"], SHELL_FILL)
    yield "S1", "dark quick toggle off / on", off, mix(d["accent"], n["h"], td["rest"]), None
    for k in "fgh":
        rest, hover, active = (mix(d["accent"], n[k], td[s]) for s in ("rest", "hover", "active"))
        yield "S1", f"dark {k} / selected (rest tint)", n[k], rest, None
        yield "S2", f"dark rest / hover over {k}", rest, hover, None
        yield "S2", f"dark hover / active over {k}", hover, active, None
    yield "S1", "dark view g / text selection", n["g"], mix(d["accent"], n["g"], td["selection"]), None
    yield "S1", "dark today: accent_text against a day's text", d["text"], d["accent_text"], None
    for k in "gh":
        yield "P", f"dark primary (solid) / selected over {k}", mix(d["accent"], n[k], td["rest"]), d["accent"], None
        yield "D", f"dark decoration over {k}", n[k], mix(d["accent"], n[k], td["decoration"]), mix(d["accent"], n[k], td["rest"])
    # Light: the desk, the window, the shelf and the sheet, each step with its line.
    yield "E", "light desk/c: a window on the desktop", l["desk"], n["c"], line("ring", l["desk"])
    yield "E", "light c/a: a view on the window", n["c"], n["a"], line("border", n["c"])
    yield "E", "light shelf/c: the sidebar beside the content", l["shelf"], n["c"], line("border", l["shelf"])
    yield "E", "light shelf/a: the sheet, the selected sidebar row", l["shelf"], n["a"], line("border", l["shelf"])
    yield "E", "light desk/shelf: a sidebar at the window's edge", l["desk"], l["shelf"], line("ring", l["desk"])
    yield None, "light a/b: alternating rows, faint on purpose", n["a"], n["b"], None
    for k, s in (("a", n["a"]), ("c", n["c"])):
        yield "R", f"light border (solid) on {k}", s, l["border"], None
    for k, s in (("a", n["a"]), ("c", n["c"]), ("shelf", l["shelf"])):
        yield "R", f"light border line on {k}", s, line("border", s), None
    yield "R", "light window ring on the desk", l["desk"], line("ring", l["desk"]), None
    # A light tint reads 3 for protans at best: no alpha keeps accent_text legible and reaches S1.
    # Light's selected and on items carry the border line inside them instead - neutral, so it
    # never reads as focus - and the line holds the state.
    for k in "abc":
        rest, hover, active = (mix(l["accent"], n[k], tl[s]) for s in ("rest", "hover", "active"))
        yield "S1", f"light {k} / selected (rest tint)", n[k], rest, line("border", n[k])
        yield "S2", f"light rest / hover over {k}", rest, hover, None
        yield "S2", f"light hover / active over {k}", hover, active, None
    yield "S1", "light view a / text selection", n["a"], mix(l["accent"], n["a"], tl["selection"]), None
    yield "S1", "light today: accent_text against a day's text", l["text"], l["accent_text"], None
    for k in "ac":
        yield "P", f"light primary (solid) / selected over {k}", mix(l["accent"], n[k], tl["rest"]), l["accent"], None
        yield "D", f"light decoration over {k}", n[k], mix(l["accent"], n[k], tl["decoration"]), mix(l["accent"], n[k], tl["rest"])
    # Hue that carries meaning.
    for mode in ("dark", "light"):
        m, a = p[mode], p["ansi"][mode]
        ks = ("accent", "success", "warning", "error")
        for i, x in enumerate(ks):
            for y in ks[i + 1:]:
                yield "K", f"{mode} {x} / {y}", m[x], m[y], None
        yield "K", f"{mode} terminal blue / cyan", a["blue"], m["accent"], None
        yield "K", f"{mode} terminal magenta / blue", a["magenta"], a["blue"], None


def judge(tier, a, b, ring):
    """One pair's numbers and verdict: ok, ok via its ring, low, or report."""
    ref, views = perceive(a, b)
    where = min(views, key=views.get)
    row = {"tier": tier, "a": a, "b": b, "ring": ring if tier != "D" else None, "ref": round(ref, 2),
           "views": {k: round(v, 2) for k, v in views.items()}, "worst": round(views[where], 2), "where": where}
    if tier is None:
        return {**row, "verdict": "report"}
    if tier == "K":
        others = {k: v for k, v in views.items() if k != "tritan"}
        ok = ref >= TIERS["K"][0] and min(others.values()) >= TIERS["K"][1] and views["tritan"] >= K_TRITAN
        need = f">= {TIERS['K'][0]} / {TIERS['K'][1]}, tritan {K_TRITAN}"
    elif tier == "D":
        cap = DECORATION_SHARE * perceive(a, ring)[0]
        ok = TIERS["E"][0] <= ref <= cap
        need = f"{TIERS['E'][0]} .. {cap:.1f} (quieter than selected)"
    else:
        floor, worst = TIERS[tier]
        ok = ref >= floor and views[where] >= worst
        need = f">= {floor} / {worst}"
    via = None
    if not ok and ring and tier != "D":
        r_ref, r_views = perceive(a, ring)
        if r_ref >= TIERS["R"][0] and min(r_views.values()) >= TIERS["R"][1]:
            ok, via = True, f"ring {r_ref:.1f} / {min(r_views.values()):.1f}"
    return {**row, "need": need, "verdict": ("ok via ring" if via else "ok") if ok else "LOW", "via": via}


def perception(p):
    return [{"name": name, **judge(tier, a, b, ring)} for tier, name, a, b, ring in perceptual_checks(p)]


def low_light(p):
    """What 30% backlight in a lit room leaves of the edges and states the scale leans on."""
    n, d, td = p["neutral"], p["dark"], p["tint"]["dark"]
    off, on = mix(n["a"], n["h"], SHELL_FILL), mix(d["accent"], n["h"], td["rest"])
    yield "dark h on e (a menu off the desktop)", n["h"], n["e"]
    yield "dark border ring on e", d["border"], n["e"]
    yield "dark rest tint over g against g", mix(d["accent"], n["g"], td["rest"]), n["g"]
    yield "dark quick toggle on / off (why an on toggle draws its icon disc)", on, off
    yield "dark icon disc (accent) on the on toggle", d["accent"], on


def validate(p):
    problems, report = [], []
    for name, fg, bg, need in checks(p):
        c = contrast(fg, bg)
        if need is REPORT:
            report.append(f"  {c:5.2f}  --- (report)  {name}")
            continue
        report.append(f"  {c:5.2f}  {'ok ' if c >= need else 'LOW'} (>= {need})  {name}")
        if c < need:
            problems.append(f"{name}: {fg} on {bg} is {c:.2f}:1, needs {need}:1")
    for mode in ("dark", "light"):  # Orchis picks the text on the accent itself: it must agree
        m = p[mode]
        if orchis_on_dark(m["accent"]) != (luminance(m["on_accent"]) < 0.5):
            problems.append(f"{mode}: Orchis would put {'dark' if orchis_on_dark(m['accent']) else 'white'} "
                            f"text on {m['accent']}, the palette says {m['on_accent']}")
    report.append("separation (brand, not WCAG): ΔE00 as drawn / worst view (where), per tier")
    for r in perception(p):
        need = f"({r['need']})" if r["verdict"] != "report" else ""
        report.append(f"  {r['ref']:6.2f} {r['worst']:6.2f} {r['where']:<10} {r['verdict']:<11} {r['tier'] or '-':<2} "
                      f"{r['name']} {need}{' ' + r['via'] if r.get('via') else ''}")
        if r["verdict"] == "LOW":
            problems.append(f"{r['name']}: {r['a']} / {r['b']} is ΔE00 {r['ref']} as drawn, {r['worst']} "
                            f"({r['where']}); tier {r['tier']} needs {r['need']}")
    report.append(f"low light (report): contrast as drawn -> at {LOW_LIGHT[0]:.0%} backlight, {LOW_LIGHT[1]:.0%} room light")
    for name, a, b in low_light(p):
        report.append(f"  {contrast(a, b):5.2f} -> {low_light_contrast(a, b):5.2f}  {name}")
    # The desk and the shelf are steps of d over c: written out so the forks and the image can
    # read them, held here so they cannot drift from the scale.
    n, l = p["neutral"], p["light"]
    for k, t in (("desk", 0.5), ("shelf", 0.25)):
        if max(abs(x - y) for x, y in zip(rgb(l[k]), rgb(mix(n["d"], n["c"], t)))) > 1:
            problems.append(f"light.{k} = {l[k]}: must be d at {t:.0%} over c, {mix(n['d'], n['c'], t)}")
    problems += shape_problems(p["shape"])
    return problems, report


def terminal(p, mode):
    """The terminal's colors in one mode: the view surface - Orchis' headerbar is the same, so the
    window is one surface - the text, the accent as cursor and selection, and the sixteen ANSI
    colors in order."""
    n, m, a = p["neutral"], p[mode], p["ansi"][mode]
    bg = surfaces(p, mode)[1]
    black, white, bright_white = (m["border"], n["d"], n["a"]) if mode == "dark" else (n["h"], n["d"], n["c"])
    normal = [black, m["error"], m["success"], m["warning"], a["blue"], a["magenta"], m["accent"], white]
    bright = [m["muted"], a["bright_red"], a["bright_green"], a["bright_yellow"], a["bright_blue"],
              a["bright_magenta"], a["bright_cyan"], bright_white]
    return {"background": bg, "foreground": m["text"], "cursor-color": m["accent"], "cursor-text": m["on_accent"],
            "selection-background": mix(m["accent"], bg, p["tint"][mode]["selection"]), "selection-foreground": m["text"],
            "split-divider-color": m["border"], "palette": normal + bright}


def ghostty(p, mode):
    t = terminal(p, mode)
    lines = ["# Generated by palette.py from palette.toml - do not edit.",
             f"# CONSTRUCT {mode}: Ghostty's theme, the desktop's view surface and accent."]
    lines += [f"palette = {i}={c}" for i, c in enumerate(t["palette"])]
    lines += [f"{k} = {v}" for k, v in t.items() if k != "palette"]
    return "\n".join(lines) + "\n"


def vscode(p, mode):
    """VS Code's color theme in one mode: GTK's surfaces (the editor is the view, the side bar,
    panel and status bar the sidebar's alternate surface, menus and widgets the raised one), the
    accent, the borders, and the terminal's colors. Syntax colors are VS Code's own 2026 theme,
    which this one includes. Selection in lists and menus is the selected tint (rest), in the
    editor the text selection, where it lies under code: the desktop's own two alphas."""
    n, m, t = p["neutral"], p[mode], terminal(p, mode)
    view, side, raised, backdrop = (n["g"], n["f"], n["h"], n["h"]) if mode == "dark" else (n["a"], n["b"], n["a"], n["b"])
    acc, on, text, muted, border = m["accent"], m["on_accent"], m["text"], m["muted"], m["border"]
    alpha = lambda a: f"{round(a * 255):02X}"
    picked, sel = acc + alpha(p["tint"][mode]["rest"]), acc + alpha(p["tint"][mode]["selection"])
    # Hover and the inactive selection are a state layer: white over dark, black (the boot's) over light.
    tint = n["a"] if mode == "dark" else p["brand"]["boot"]
    c = {
        "foreground": text, "descriptionForeground": muted, "icon.foreground": muted,
        "errorForeground": m["error"], "focusBorder": acc, "widget.border": border,
        "selection.background": sel, "textLink.foreground": m["accent_text"], "textLink.activeForeground": m["accent_text"],
        "button.background": acc, "button.foreground": on, "button.hoverBackground": t["palette"][14],
        "button.secondaryBackground": raised, "button.secondaryForeground": text,
        "badge.background": acc, "badge.foreground": on, "activityBarBadge.background": acc,
        "activityBarBadge.foreground": on, "progressBar.background": acc,
        "titleBar.activeBackground": view, "titleBar.activeForeground": text,
        "titleBar.inactiveBackground": backdrop, "titleBar.inactiveForeground": muted, "titleBar.border": border,
        "activityBar.background": side, "activityBar.foreground": text, "activityBar.inactiveForeground": muted,
        "activityBar.activeBorder": acc, "activityBar.border": border,
        "sideBar.background": side, "sideBar.foreground": text, "sideBar.border": border,
        "sideBarTitle.foreground": text, "sideBarSectionHeader.background": side, "sideBarSectionHeader.border": border,
        "editor.background": view, "editor.foreground": text, "editorCursor.foreground": acc,
        "editorLineNumber.foreground": muted, "editorLineNumber.activeForeground": text,
        "editor.lineHighlightBackground": tint + "0A", "editor.selectionBackground": sel,
        "editor.inactiveSelectionBackground": acc + "20", "editor.selectionHighlightBackground": acc + "1F",
        "editorGroup.border": border, "editorGroupHeader.tabsBackground": side, "editorGroupHeader.tabsBorder": border,
        "tab.activeBackground": view, "tab.activeForeground": text, "tab.activeBorderTop": acc,
        "tab.inactiveBackground": side, "tab.inactiveForeground": muted, "tab.border": border,
        "panel.background": side, "panel.border": border, "panelTitle.activeBorder": acc,
        "panelTitle.activeForeground": text, "panelTitle.inactiveForeground": muted,
        "statusBar.background": side, "statusBar.foreground": muted, "statusBar.border": border,
        "statusBar.noFolderBackground": side, "statusBar.debuggingBackground": m["warning"],
        "statusBar.debuggingForeground": n["e"] if mode == "dark" else n["a"],
        "statusBarItem.remoteBackground": acc, "statusBarItem.remoteForeground": on,
        "input.background": side, "input.border": border, "input.foreground": text,
        "input.placeholderForeground": muted, "inputOption.activeBorder": acc,
        "dropdown.background": raised, "dropdown.border": border, "dropdown.foreground": text,
        "menu.background": raised, "menu.foreground": text, "menu.border": border,
        "menu.selectionBackground": picked, "menu.selectionForeground": text, "menu.separatorBackground": border,
        "quickInput.background": raised, "quickInput.foreground": text,
        "editorWidget.background": raised, "editorWidget.border": border,
        "editorHoverWidget.background": raised, "editorHoverWidget.border": border,
        "editorSuggestWidget.background": raised, "editorSuggestWidget.border": border,
        "editorSuggestWidget.selectedBackground": picked,
        "notifications.background": raised, "notifications.border": border,
        "notificationToast.border": border, "notificationCenter.border": border,
        "list.activeSelectionBackground": picked, "list.activeSelectionForeground": text,
        "list.inactiveSelectionBackground": tint + "14", "list.hoverBackground": tint + "0A",
        "list.focusOutline": acc, "list.highlightForeground": m["accent_text"],
        "editorError.foreground": m["error"], "editorWarning.foreground": m["warning"],
        "editorInfo.foreground": t["palette"][4],
        "gitDecoration.addedResourceForeground": m["success"], "gitDecoration.untrackedResourceForeground": m["success"],
        "gitDecoration.modifiedResourceForeground": m["warning"], "gitDecoration.deletedResourceForeground": m["error"],
        "editorGutter.addedBackground": m["success"], "editorGutter.modifiedBackground": t["palette"][4],
        "editorGutter.deletedBackground": m["error"],
        "terminal.background": t["background"], "terminal.foreground": t["foreground"],
        "terminalCursor.foreground": t["cursor-color"], "terminal.selectionBackground": t["selection-background"],
    }
    names = ["Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"]
    for i, col in enumerate(t["palette"]):
        c[f"terminal.ansi{'Bright' if i > 7 else ''}{names[i % 8]}"] = col
    return json.dumps({"$schema": "vscode://schemas/color-theme", "name": f"Construct {mode.title()}",
                       "type": mode, "include": f"../../theme-defaults/themes/2026-{mode}.json",
                       "colors": c}, indent=2) + "\n"


def vscode_package(p):
    return json.dumps({
        "name": "construct-theme", "displayName": "CONSTRUCT", "description": "The desktop's colors, light and dark",
        "version": "1.0.0", "publisher": "construct", "license": "CC-BY-SA-4.0", "engines": {"vscode": "^1.100.0"},
        "categories": ["Themes"],
        "contributes": {
            "themes": [{"id": f"Construct {m.title()}", "label": f"Construct {m.title()}",
                        "uiTheme": "vs-dark" if m == "dark" else "vs", "path": f"./themes/construct-{m}.json"}
                       for m in ("dark", "light")],
            # Window scope: the defaults any user setting overrides, with the theme following the
            # desktop's color-scheme.
            "configurationDefaults": {
                "workbench.colorTheme": "Construct Dark",
                "workbench.preferredDarkColorTheme": "Construct Dark",
                "workbench.preferredLightColorTheme": "Construct Light",
                "window.autoDetectColorScheme": True,
            },
        },
    }, indent=2) + "\n"


def flat(p):
    return {f"{group}-{k}".replace("_", "-"): v for group, d in p.items() for k, v in d.items()}


def flat_all(d, prefix=""):
    """Every value of palette.toml under its path joined with '-': tint.dark.rest is tint-dark-rest."""
    for k, v in d.items():
        key = f"{prefix}-{k}".replace("_", "-") if prefix else k.replace("_", "-")
        if isinstance(v, dict):
            yield from flat_all(v, key)
        else:
            yield key, v


def palette_json(p):
    return json.dumps(dict(flat_all(p)), indent=1, sort_keys=True) + "\n"


def rgba(h, alpha):
    return f"rgba({', '.join(str(c) for c in rgb(h))}, {alpha:.2f})"


def pct(alpha):
    return f"{round(alpha * 100)}%"


def css(p):
    n, sh = p["neutral"], p["shape"]
    def block(mode, raised, alt):
        m, t = p[mode], p["tint"][mode]
        window, view = surfaces(p, mode)
        term = terminal(p, mode)
        # The ground under windows and the sidebar's pane: light writes them (desk, shelf); in
        # dark they are the desktop e and the window body f. Lines: light draws muted at an alpha,
        # dark one solid border. A light tint that marks a state carries the border line inside it
        # (--tint-edge); a dark one has no edge.
        if mode == "dark":
            ground = {"desk": n["e"], "shelf": n["f"]}
            lines = {"line-divider": m["border"], "line-border": m["border"], "line-ring": m["border"], "tint-edge": "transparent"}
        else:
            ln = p["line"]["light"]
            ground = {}
            lines = {**{f"line-{k}": rgba(m["muted"], v) for k, v in ln.items()}, "tint-edge": rgba(m["muted"], ln["border"])}
        rows = {"bg": window, "view": view, "raised": raised, "alt": alt,
                **{k.replace("_", "-"): v for k, v in m.items()}, **ground, **lines,
                "tint": pct(t["rest"]), "tint-hover": pct(t["hover"]), "tint-active": pct(t["active"]),
                "selection": pct(t["selection"]), "tint-deco": pct(t["decoration"]), "tint-track": pct(t["track"]),
                **{f"term-{i}": c for i, c in enumerate(term["palette"])},
                "term-bg": term["background"], "term-fg": term["foreground"], "term-selection": term["selection-background"]}
        return "\n".join(f"  --{k}: {v};" for k, v in rows.items())
    dark = block("dark", n["h"], n["f"])
    light = block("light", n["a"], n["b"])
    # GNOME Shell is Orchis' dark variant in both modes: its desktop, its chrome (the top bar and
    # the dock, g), its menus (h), its text and its tints.
    td = p["tint"]["dark"]
    shell = "\n".join(f"  --shell-{k}: {v};" for k, v in
                      {"bg": n["e"], "chrome": n["g"], "surface": n["h"], "view": n["g"], "alt": n["f"],
                       "fill": mix(n["a"], n["h"], SHELL_FILL),
                       "tint": pct(td["rest"]), "tint-hover": pct(td["hover"]), "tint-active": pct(td["active"]),
                       "selection": pct(td["selection"]), "tint-deco": pct(td["decoration"]), "tint-track": pct(td["track"]),
                       **{k.replace("_", "-"): v for k, v in p["dark"].items()}}.items())
    brand = "\n".join(f"  --{k}: {v};" for k, v in flat({g: p[g] for g in ("brand", "neutral", "icons", "cursor")}).items())
    shape = "\n".join(f"  --{k.replace('_', '-')}: {sh[k]}px;" for k in ("radius_control", "radius_surface", "radius_sheet", "inset"))
    fonts = (f'  --font-wordmark: "{p["type"]["wordmark"]}", sans-serif;\n'
             f'  --font-ui: "{p["type"]["ui"]}", system-ui, sans-serif;\n'
             f'  --font-mono: "{p["type"]["mono"]}", ui-monospace, monospace;\n'
             f'  --font-terminal: "{p["type"]["terminal"]}", ui-monospace, monospace;')
    return (f"/* Generated by palette.py from palette.toml - do not edit. */\n"
            f":root {{\n{brand}\n  --construct-boot: {p['brand']['boot']};\n{shape}\n{fonts}\n{shell}\n  color-scheme: dark;\n{dark}\n}}\n"
            f"@media (prefers-color-scheme: light) {{\n  :root:not([data-mode=\"dark\"]) {{\n    color-scheme: light;\n"
            + "\n".join("  " + l for l in light.splitlines()) + "\n  }\n}\n"
            # Not only :root: an element marked with a mode draws in it, so a page can show the
            # light desktop beside the dark one.
            f"[data-mode=\"light\"] {{\n  color-scheme: light;\n{light}\n}}\n"
            f"[data-mode=\"dark\"] {{\n  color-scheme: dark;\n{dark}\n}}\n")


def scss(p):
    n, d, l, t, sh = p["neutral"], p["dark"], p["light"], p["tint"], p["shape"]
    # Orchis names a color's two shades by what they are, not where they go: theme() takes
    # $<color>-light for the dark variant and $<color>-dark for the light one.
    lines = ["// Generated by palette.py from palette.toml - do not edit.",
             "// Orchis: the accent as a theme color ('construct'), and the background scale.",
             f"$construct-light: {d['accent']}; // accent in the dark variant",
             f"$construct-dark: {l['accent']}; // accent in the light variant",
             ""]
    lines += [f"$construct-bg-{k}: {v};" for k, v in n.items()]
    lines += ["", "// Border, semantic colors: dark and light variant"]
    for k in ("border", "success", "warning", "error", "destructive"):
        lines += [f"$construct-{k}-light: {d[k]};", f"$construct-{k}-dark: {l[k]};"]
    lines += ["", "// Text: the accent standing alone (labels on a tint, links), body, muted, on a fill of the accent"]
    for k in ("accent_text", "text", "muted", "on_accent"):
        name = k.replace("_", "-")
        lines += [f"$construct-{name}-light: {d[k]};", f"$construct-{name}-dark: {l[k]};"]
    lines += ["", "// The ground under the overview, the lock and login screens; the desktop's ink",
              f"$construct-boot: {p['brand']['boot']};", f"$construct-ink: {p['brand']['ink']};",
              "", "// The accent's alpha over a surface: (rest, hover, active), and selection"]
    for variant, mode in (("light", "dark"), ("dark", "light")):
        lines += [f"$construct-tint-{variant}: ({t[mode]['rest']:.2f}, {t[mode]['hover']:.2f}, {t[mode]['active']:.2f});"]
    for variant, mode in (("light", "dark"), ("dark", "light")):
        lines += [f"$construct-selection-{variant}: {t[mode]['selection']:.2f};"]
    lines += ["", "// Transient overlays (rubberband, tile preview), with a 1px accent edge; a switch's track"]
    for k in ("decoration", "track"):
        for variant, mode in (("light", "dark"), ("dark", "light")):
            lines += [f"$construct-tint-{k}-{variant}: {t[mode][k]:.2f};"]
    ln = p["line"]["light"]
    lines += ["", "// The light variant only: the desktop's ground, the sidebar's pane, and its lines -",
              "// $construct-muted-dark at (divider, border, ring)",
              f"$construct-desk: {l['desk']};", f"$construct-shelf: {l['shelf']};",
              f"$construct-lines: ({ln['divider']:.2f}, {ln['border']:.2f}, {ln['ring']:.2f});"]
    lines += ["", "// libadwaita's radius steps; both bars' distance from the screen edge"]
    lines += [f"$construct-{k.replace('_', '-')}: {sh[k]}px;" for k in ("radius_control", "radius_surface", "radius_sheet", "inset")]
    return "\n".join(lines) + "\n"


def perception_js(p):
    """Every perceptual pair with its numbers, for preview.html's table: a script rather than
    JSON, so the page reads it opened from disk, where fetch() is refused."""
    data = {"views": list(VIEWS), "tiers": {**{k: list(v) for k, v in TIERS.items()}, "K_tritan": K_TRITAN},
            "pairs": perception(p)}
    rows = ",\n  ".join(json.dumps(r, ensure_ascii=False) for r in data.pop("pairs"))
    head = json.dumps(data, ensure_ascii=False)[:-1]
    return ("// Generated by palette.py from palette.toml - do not edit.\n"
            f"window.PERCEPTION = {head},\n \"pairs\": [\n  {rows}\n ]}};\n")


def simulate_js(p):
    """SVG filters that show a drawing as a deficiency or a panel shows it - the models the checks
    use, so the matrices are written once. Same-document filters: Chrome ignores a filter in
    another file on an HTML element. Filter effects work in linear RGB, as the models do."""
    fx = {}
    for k, m in MACHADO.items():
        vals = "  ".join(" ".join(str(v) for v in row) + " 0 0" for row in m) + "  0 0 0 1 0"
        fx[k] = f'<feColorMatrix type="matrix" values="{vals}"/>'

    def transfer(slope, offset, exponent=1.0):
        f = (f'type="linear" slope="{slope:.4f}" intercept="{offset:.4f}"' if exponent == 1 else
             f'type="gamma" amplitude="{slope:.4f}" exponent="{exponent:g}" offset="{offset:.4f}"')
        return "<feComponentTransfer>" + "".join(f"<feFunc{c} {f}/>" for c in "RGB") + "</feComponentTransfer>"
    for k in ("ips", "dim"):
        w, b, f, g = CONDITIONS[k]
        fx[k] = transfer((w - b) / (w + f), (b + f) / (w + f), g)
    fx["low"] = transfer(*LOW_LIGHT)
    fx["grey"] = '<feColorMatrix type="matrix" values="' + "  ".join(["0.2126 0.7152 0.0722 0 0"] * 3) + '  0 0 0 1 0"/>'
    labels = {"protan": "Protan", "deutan": "Deutan", "tritan": "Tritan", "ips": "IPS office",
              "dim": "OLED at 30%", "low": "30% backlight", "grey": "Grey"}
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true">'
           + "".join(f'<filter id="sim-{k}" color-interpolation-filters="linearRGB">{v}</filter>' for k, v in fx.items())
           + "</svg>")
    return ("// Generated by palette.py from palette.toml - do not edit.\n"
            "// task palette's views as SVG filters: Machado 2009 at severity 1.0; an IPS panel and a\n"
            "// dimmed OLED as an eye adapted to them sees them; a panel at 30% backlight in a room lit\n"
            "// to 3% of its white, as an eye adapted to the room sees it.\n"
            f"window.SIMULATIONS = {json.dumps(list(labels.items()))};\n"
            f"document.body.insertAdjacentHTML(\"beforeend\", {json.dumps(svg)});\n")


if __name__ == "__main__":
    OUT = sys.argv[1] if len(sys.argv) > 1 else "palette"
    p = load()
    problems, report = validate(p)
    print("contrast:\n" + "\n".join(report))
    if problems:
        sys.exit("palette.toml:\n  " + "\n  ".join(problems))
    os.makedirs(f"{OUT}/ghostty", exist_ok=True)
    os.makedirs(f"{OUT}/vscode/themes", exist_ok=True)
    open(f"{OUT}/construct.css", "w").write(css(p))
    open(f"{OUT}/construct.scss", "w").write(scss(p))
    open(f"{OUT}/construct.json", "w").write(palette_json(p))
    open(f"{OUT}/vscode/package.json", "w").write(vscode_package(p))
    open(f"{OUT}/perception.js", "w").write(perception_js(p))
    open(f"{OUT}/simulate.js", "w").write(simulate_js(p))
    for mode in ("dark", "light"):
        open(f"{OUT}/ghostty/Construct {mode.title()}", "w").write(ghostty(p, mode))
        open(f"{OUT}/vscode/themes/construct-{mode}.json", "w").write(vscode(p, mode))
    print(f"{OUT}/: construct.css, construct.scss, construct.json, perception.js, simulate.js, ghostty/, vscode/")
