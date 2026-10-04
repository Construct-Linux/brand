import fnmatch, glob, os, re, sys, tomllib
import palette

# usage: lint.py <forks_dir> [lint-forks.toml]
# Fails when a fork writes a color that is not in palette.toml - a hex literal or an rgb()/rgba()
# of numbers, in the files the image builds from - when its SCSS draws the accent at an alpha that
# is not one of the scale's tokens (C7), when its SCSS rounds, spaces or shadows off THEMING.md's
# shape and elevation tables (G7), and when a fork's copy of the palette is not what palette/
# holds now. The exceptions are in lint-forks.toml, each with its reason: a file
# that is not ours to color (apps' content palettes), or one value in one file. An exception
# nothing matches any more fails too: left in, it would hide the next color written there.
HERE = os.path.dirname(os.path.abspath(__file__))

HEX = re.compile(r"(?<![\w&$-])#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})(?![\w-])")
RGB = re.compile(r"rgba?\(\s*(\d{1,3}(?:\.\d+)?)\s*,\s*(\d{1,3}(?:\.\d+)?)\s*,\s*(\d{1,3}(?:\.\d+)?)")
BLOCK = re.compile(r"/\*.*?\*/|<!--.*?-->", re.S)
LINE = re.compile(r"(^|\s)//.*$", re.M)  # not the // of a url("http://")


def colors_of(p):
    """Every color palette.toml writes, its nested tables (ansi.dark, ...) included."""
    for v in p.values():
        if isinstance(v, dict):
            yield from colors_of(v)
        elif isinstance(v, str) and v.startswith("#"):
            yield v.upper()


def norm(h):
    h = h.lstrip("#").upper()
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h)
    return "#" + h[:6]


def strip(text, path):
    # Comments go, but each keeps its newlines so a finding's line number stays true.
    keep = lambda m: re.sub(r"[^\n]", " ", m.group(0))
    text = BLOCK.sub(keep, text)
    if path.endswith((".scss", ".js", ".ts")):
        text = LINE.sub(keep, text)
    return text


def colors(text):
    for m in HEX.finditer(text):
        yield m.start(), m.group(0), norm(m.group(0))
    for m in RGB.finditer(text):
        r, g, b = (round(float(x)) for x in m.groups())
        yield m.start(), m.group(0) + "...)", "#%02X%02X%02X" % (r, g, b)


# C7: the accent's alpha is a token. A level of the accent scale (THEMING.md) is an alpha
# palette.toml names - Orchis' $tint, $tint-hover, $tint-active, $selection-alpha,
# $tint-decoration, $tint-track - never a number written where it is used, nor a shade
# lighten() or darken() makes: a number chosen at each place of use is how a scale drifts into
# twenty alphas no one can tell apart. Exceptions are lint-forks.toml's [fork.<name>.accent], each with its reason.
ACCENT = r"\$(?:primary|suggested|link)\b"
TOKENS = {"$tint", "$tint-hover", "$tint-active", "$selection-alpha", "$tint-decoration", "$tint-track"}
ALPHA = re.compile(rf"\b(?:rgba|alpha|gtkalpha)\(\s*{ACCENT}\s*,\s*([^)]*)\)")
COLOR_MIX = re.compile(rf"color-mix\(\s*in\s+[\w-]+\s*,\s*{ACCENT}\s+([^,]+),")
SHADE = re.compile(rf"\b(?:transparentize|lighten|darken)\(\s*{ACCENT}|(?<![\w-])mix\([^;]*?{ACCENT}")


def accent_alphas(text):
    """Every use of the accent at an alpha or a shade that is not one of the scale's tokens."""
    for m in ALPHA.finditer(text):
        if m.group(1).strip() not in TOKENS:
            yield m.start(), m.group(0)
    for m in COLOR_MIX.finditer(text):
        token = re.fullmatch(r"#\{\s*(\$[\w-]+)\s*\*\s*100%\s*\}", m.group(1).strip())
        if not token or token.group(1) not in TOKENS:
            yield m.start(), m.group(0)
    for m in SHADE.finditer(text):
        yield m.start(), m.group(0)


# G7: the forks' shape is the palette's. A radius is 0, a pill, a step of R1 or a radius THEMING.md
# names (RADII); a padding, margin or spacing is 0 or on SP1's grid (3, 6, 12, 18, 24, either
# sign); a shadow that blurs or casts is one of the elevation table's - $shadow-z16 (a GTK
# window), $shadow-z4 (a light popover), $elevation-2 and $elevation-3 (the shell's levels) - and
# one that does neither is a line or a ring, which the table draws everywhere. SCSS is evaluated as far as the sizes go:
# variables (compact off), + - * /, px. A size in em follows the text (T1) and a mixin's parameter
# is only known where the mixin is included, so neither is judged. Anything else is listed in
# lint-forks.toml's [fork.<name>.shape], under "<file> <radius|space|shadow>", with its reason.
SHAPE_PROPS = {
    "radius": re.compile(r"(?:border(?:-(?:top|bottom)-(?:left|right))?|-gtk-outline)-radius"),
    "space": re.compile(r"(?:padding|margin)(?:-(?:top|right|bottom|left))?|(?:border-|row-|column-)?spacing|spacing-(?:rows|columns)"),
    "shadow": re.compile(r"box-shadow"),
}
DECL = re.compile(r"(?<![\w$&-])([a-z-][\w-]*)\s*:\s*([^;{}]+);")
VARDEF = re.compile(r"^([ \t]*)\$([\w-]+)\s*:\s*([^;]+?)\s*(?:!default\s*)?;", re.M)
VARREF = re.compile(r"\$([\w-]+)")
COMPACT = re.compile(r"if\(\s*\$compact\s*==\s*'false'\s*,\s*([^,()]+?)\s*,\s*[^()]+?\)")
SHADOW_TOKENS = {"shadow-z16", "shadow-z4", "elevation-2", "elevation-3"}
PILL = 99  # St and GTK clamp a radius to half the side: from here up every radius is a pill
# R1's steps, and the concentric and libadwaita radii THEMING.md names ("Shape and type"): a
# button in a 24px dialog with 12px of padding and GTK's cards 12, its alert dialogs 18, a search
# section 9 + 12 = 21, quick settings 22 + 18 = 40, the app-folder dialog 48.
RADII = {9, 15, 24} | {12, 18, 21, 40, 48}
SPACE = {3, 6, 12, 18, 24}


class Unknown(Exception):
    """A size lint cannot know: in em, a mixin's parameter, or not arithmetic."""


def size(expr, env, depth=0):
    """A SCSS size in px, through variables and + - * /; Unknown when it is not one."""
    if depth > 20:
        raise Unknown(expr)
    expr = COMPACT.sub(r"\1", expr.replace("!important", "").strip())
    if re.search(r"\d(?:em|rem|pt)\b|to_em\(", expr):
        raise Unknown(expr)
    if expr.endswith("%"):
        return expr
    def var(m):
        if m.group(1) not in env:
            raise Unknown(m.group(0))
        v = size(env[m.group(1)], env, depth + 1)
        if isinstance(v, str):
            raise Unknown(m.group(0))
        return f"({v})"
    arith = VARREF.sub(var, expr).replace("px", "")
    if not re.fullmatch(r"[\d.+\-*/() ]+", arith):
        raise Unknown(expr)
    try:
        return round(eval(arith, {"__builtins__": {}}), 2)
    except (SyntaxError, ZeroDivisionError):
        raise Unknown(expr)


def terms(value):
    """A shorthand's parts: split at whitespace outside parentheses, with a spaced binary operator
    kept between its operands ("$window-radius - $space-size" is one part)."""
    words, depth, cur = [], 0, ""
    for ch in value:
        depth += (ch == "(") - (ch == ")")
        if ch.isspace() and depth == 0:
            if cur:
                words.append(cur)
            cur = ""
        else:
            cur += ch
    words += [cur] if cur else []
    out = []
    for w in words:
        if out and (w in "+-*/" or out[-1][-1] in "+-*/"):
            out[-1] += " " + w
        else:
            out.append(w)
    return out


def split_commas(value):
    parts, depth, cur = [], 0, ""
    for ch in value:
        depth += (ch == "(") - (ch == ")")
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    return parts + [cur.strip()]


def shadow_problems(value, env, depth=0):
    """The parts of a box-shadow that blur or cast and are not one of the elevation table's."""
    for part in split_commas(value.replace("!important", "")):
        one = re.fullmatch(r"\$([\w-]+)", part)
        if one:
            if one.group(1) in SHADOW_TOKENS:
                continue
            if one.group(1) not in env or depth > 20:
                raise Unknown(part)
            # A named shadow is judged by what it draws and reported by its name.
            if any(shadow_problems(env[one.group(1)], env, depth + 1)):
                yield part
            continue
        if part in ("none", "0", "unset", "initial", "inherit", "") or re.search(r"\btransparent\b|,\s*0\)$", part):
            continue  # nothing drawn: a transparent part only gives a transition its shape
        lengths = []
        for t in terms(part):
            if t == "inset":
                continue
            try:
                lengths.append(size(t, env))
            except Unknown:
                if re.match(r"(?:rgba?|hsla?|alpha|gtkalpha|mix|transparentize|lighten|darken|shade)\(|#|\$|[a-z]", t):
                    continue  # the color: C1 and C7 hold it
                raise
        x, y, blur = (lengths + [0, 0, 0])[:3]
        if blur or (x or y) and not part.startswith("inset"):
            yield part


def shape(text, env):
    """G7's findings in one SCSS file: (line, kind, value)."""
    local = dict(env)
    defs = [(m.start(), m.group(2), m.group(3)) for m in VARDEF.finditer(text) if m.group(1)]
    for m in DECL.finditer(text):
        prop, value = m.group(1), m.group(2).strip()
        kind = next((k for k, r in SHAPE_PROPS.items() if r.fullmatch(prop)), None)
        if not kind:
            continue
        for at, name, v in defs:  # a variable set inside a rule holds from there on in the file
            if at < m.start():
                local[name] = v
        try:
            if kind == "shadow":
                bad = list(shadow_problems(value, local))
            else:
                bad = []
                for t in terms(value.replace("!important", "")):
                    if t in ("auto", "0"):
                        continue
                    v = size(t, local)
                    if isinstance(v, str):
                        ok = kind == "radius" and v == "50%"
                    elif kind == "radius":
                        ok = v == 0 or v >= PILL or v in RADII
                    else:
                        ok = v == 0 or abs(v) in SPACE
                    if not ok:
                        bad = [value.replace("!important", "").strip()]
                        break
        except Unknown:
            continue
        for b in bad:
            yield text.count("\n", 0, m.start()) + 1, kind, b


def scss_env(files):
    """Every variable the fork's SCSS sets at the top of a file. The palette's and _variables'
    come first, as every other file imports them."""
    env = {}
    for path in sorted(files, key=lambda p: (not p.endswith(("_construct-palette.scss", "_variables.scss")), p)):
        text = strip(open(path, encoding="utf-8", errors="replace").read(), path)
        for m in VARDEF.finditer(text):
            if not m.group(1):
                env[m.group(2)] = m.group(3)
    return env


def literals(forks, rules, allowed):
    problems, used = [], set()
    for fork, r in rules["fork"].items():
        root = os.path.join(forks, fork)
        if not os.path.isdir(root):
            problems.append(f"{fork}: no checkout in {forks}")
            continue
        files = sorted({p for g in r["files"] for p in glob.glob(os.path.join(root, g), recursive=True)})
        env = scss_env([p for p in files if p.endswith(".scss")]) if "shape" in r else None
        for path in files:
            rel = os.path.relpath(path, root)
            skip = next((k for k in r.get("skip", {}) if fnmatch.fnmatch(rel, k)), None)
            if skip:
                used.add((fork, "skip", skip))
                continue
            text = strip(open(path, encoding="utf-8", errors="replace").read(), path)
            for pos, raw, hexv in colors(text):
                if hexv in allowed:
                    continue
                key = f"{rel} {hexv}"
                if key in r.get("allow", {}):
                    used.add((fork, "allow", key))
                    continue
                line = text.count("\n", 0, pos) + 1
                problems.append(f"{fork}/{rel}:{line}: {raw} ({hexv}) is not in palette.toml")
            if path.endswith(".scss"):
                for pos, raw in accent_alphas(text):
                    key = f"{rel} {raw}"
                    if key in r.get("accent", {}):
                        used.add((fork, "accent", key))
                        continue
                    line = text.count("\n", 0, pos) + 1
                    problems.append(f"{fork}/{rel}:{line}: {raw}: the accent's alpha is a token (C7)")
            if env is not None and path.endswith(".scss"):
                for line, kind, raw in shape(text, env):
                    key = f"{rel} {kind}"
                    if raw in r["shape"].get(key, {}).get("values", []):
                        used.add((fork, "shape", f"{key} {raw}"))
                        continue
                    problems.append(f"{fork}/{rel}:{line}: {kind} {raw}: not the palette's shape (G7)")
        for kind in ("skip", "allow", "accent"):
            for k in r.get(kind, {}):
                if (fork, kind, k) not in used:
                    problems.append(f"{fork}: lint-forks.toml {kind} '{k}' matches nothing: remove it")
        for k, e in r.get("shape", {}).items():
            for v in e["values"]:
                if (fork, "shape", f"{k} {v}") not in used:
                    problems.append(f"{fork}: lint-forks.toml shape '{k}' value '{v}' matches nothing: remove it")
    return problems


def mirrors(forks, p):
    """The forks that hold a copy of the palette rather than reading it: Orchis' SCSS, copied
    under a two-line header, and Bibata's color table, written by hand."""
    problems = []
    orchis = os.path.join(forks, "Orchis-theme/src/_sass/_construct-palette.scss")
    ours = open(os.path.join(HERE, "palette/construct.scss")).read()
    if not os.path.isfile(orchis):
        problems.append(f"{orchis}: missing")
    elif "".join(open(orchis).read().splitlines(keepends=True)[2:]) != ours:
        problems.append("Orchis-theme/src/_sass/_construct-palette.scss: not palette/construct.scss under its "
                        "two-line header: copy it again")
    bibata = os.path.join(forks, "Bibata_Cursor/build.py")
    want = [p["cursor"][k].upper() for k in ("fill", "outline", "watch")]
    table = re.search(r"^COLORS = \{(.*?)^\}", open(bibata).read(), re.S | re.M) if os.path.isfile(bibata) else None
    have = [v.upper() for v in re.findall(r'"#[0-9a-fA-F]{6}"\s*:\s*"(#[0-9a-fA-F]{6})"', table.group(1))] if table else None
    if have != want:
        problems.append(f"Bibata_Cursor/build.py: COLORS is {have}, palette.toml's cursor is {want} (fill, outline, watch)")
    return problems


def main():
    forks = sys.argv[1]
    with open(sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "lint-forks.toml"), "rb") as f:
        rules = tomllib.load(f)
    p = palette.load()
    problems = literals(forks, rules, set(colors_of(p))) + mirrors(forks, p)
    if problems:
        sys.exit("\n".join(problems) + f"\n{len(problems)} problem(s)")
    print("forks: every color is the palette's, every radius, spacing and shadow the tables', every copy of it current")


main()
