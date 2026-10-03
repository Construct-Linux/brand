import json, os, sys, tomllib

# usage: palette.py [out_dir]
# Reads palette.toml, fails if a pair the desktop draws one on the other reads badly, and writes
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
        yield f"{mode} text on accent", m["on_accent"], m["accent"], TEXT
        if mode == "dark":
            # GNOME Shell's menus, the calendar and the OSDs stand on the raised surface, h: the
            # desktop under them is e, often the wallpaper's own color.
            for k, need in (("text", BODY), ("muted", TEXT), ("accent", TEXT), ("success", TEXT), ("warning", TEXT), ("error", TEXT)):
                yield f"dark {k} on raised (shell menus)", m[k], n["h"], need
        # Buttons filled with a semantic color (destructive, success): Orchis puts black or white
        # on them by brightness, as on the accent.
        for k in ("success", "warning", "error"):
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
        yield f"{mode} text on selection ({t['selection']:.2f}) over view", m["text"], mix(m["accent"], view, t["selection"]), BODY
    # The edges the brand asks for: not text, below WCAG's 3, but each one what tells one surface
    # from the next where no shadow shows (black on ink).
    d, edge = p["dark"], "edge (brand, not WCAG):"
    yield f"{edge} dark border ring on e (the desktop)", d["border"], n["e"], 1.5
    yield f"{edge} dark border ring on h (the menus)", d["border"], n["h"], 1.2
    yield f"{edge} h on e (a menu off the desktop)", n["h"], n["e"], 1.25
    yield f"{edge} light border on c (the window)", p["light"]["border"], n["c"], 1.4
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
    which this one includes. Selection in lists and menus is the accent at 0x26 (15%), in the
    editor at 0x40 (25%), where it lies under code."""
    n, m, t = p["neutral"], p[mode], terminal(p, mode)
    view, side, raised, backdrop = (n["g"], n["f"], n["h"], n["h"]) if mode == "dark" else (n["a"], n["b"], n["a"], n["b"])
    acc, on, text, muted, border = m["accent"], m["on_accent"], m["text"], m["muted"], m["border"]
    # Hover and the inactive selection are a state layer: white over dark, black (the boot's) over light.
    tint = n["a"] if mode == "dark" else p["brand"]["boot"]
    c = {
        "foreground": text, "descriptionForeground": muted, "icon.foreground": muted,
        "errorForeground": m["error"], "focusBorder": acc, "widget.border": border,
        "selection.background": acc + "40", "textLink.foreground": m["accent_text"], "textLink.activeForeground": m["accent_text"],
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
        "editor.lineHighlightBackground": tint + "0A", "editor.selectionBackground": acc + "40",
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
        "menu.selectionBackground": acc + "26", "menu.selectionForeground": text, "menu.separatorBackground": border,
        "quickInput.background": raised, "quickInput.foreground": text,
        "editorWidget.background": raised, "editorWidget.border": border,
        "editorHoverWidget.background": raised, "editorHoverWidget.border": border,
        "editorSuggestWidget.background": raised, "editorSuggestWidget.border": border,
        "editorSuggestWidget.selectedBackground": acc + "26",
        "notifications.background": raised, "notifications.border": border,
        "notificationToast.border": border, "notificationCenter.border": border,
        "list.activeSelectionBackground": acc + "26", "list.activeSelectionForeground": text,
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


def pct(alpha):
    return f"{round(alpha * 100)}%"


def css(p):
    n, sh = p["neutral"], p["shape"]
    def block(mode, raised, alt):
        m, t = p[mode], p["tint"][mode]
        window, view = surfaces(p, mode)
        term = terminal(p, mode)
        rows = {"bg": window, "view": view, "raised": raised, "alt": alt,
                **{k.replace("_", "-"): v for k, v in m.items()},
                "tint": pct(t["rest"]), "tint-hover": pct(t["hover"]), "tint-active": pct(t["active"]),
                "selection": pct(t["selection"]),
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
                       "selection": pct(td["selection"]),
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
            f":root[data-mode=\"light\"] {{\n  color-scheme: light;\n{light}\n}}\n"
            f":root[data-mode=\"dark\"] {{\n  color-scheme: dark;\n{dark}\n}}\n")


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
    for k in ("border", "success", "warning", "error"):
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
    lines += ["", "// libadwaita's radius steps; both bars' distance from the screen edge"]
    lines += [f"$construct-{k.replace('_', '-')}: {sh[k]}px;" for k in ("radius_control", "radius_surface", "radius_sheet", "inset")]
    return "\n".join(lines) + "\n"


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
    for mode in ("dark", "light"):
        open(f"{OUT}/ghostty/Construct {mode.title()}", "w").write(ghostty(p, mode))
        open(f"{OUT}/vscode/themes/construct-{mode}.json", "w").write(vscode(p, mode))
    print(f"{OUT}/: construct.css, construct.scss, construct.json, ghostty/, vscode/")
