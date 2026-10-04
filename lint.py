import fnmatch, glob, os, re, sys, tomllib
import palette

# usage: lint.py <forks_dir> [lint-forks.toml]
# Fails when a fork writes a color that is not in palette.toml - a hex literal or an rgb()/rgba()
# of numbers, in the files the image builds from - when its SCSS draws the accent at an alpha that
# is not one of the scale's tokens (C7), and when a fork's copy of the palette is not what
# palette/ holds now. The exceptions are in lint-forks.toml, each with its reason: a file
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


def literals(forks, rules, allowed):
    problems, used = [], set()
    for fork, r in rules["fork"].items():
        root = os.path.join(forks, fork)
        if not os.path.isdir(root):
            problems.append(f"{fork}: no checkout in {forks}")
            continue
        files = sorted({p for g in r["files"] for p in glob.glob(os.path.join(root, g), recursive=True)})
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
        for kind in ("skip", "allow", "accent"):
            for k in r.get(kind, {}):
                if (fork, kind, k) not in used:
                    problems.append(f"{fork}: lint-forks.toml {kind} '{k}' matches nothing: remove it")
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
    print("forks: every color is the palette's, every copy of it current")


main()
