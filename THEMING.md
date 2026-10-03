# Theming

How the desktop takes the brand. The colors are written once, in `palette.toml`; `task palette`
checks their contrast and writes them out in `palette/`, and each fork takes them from there.

The forks carry CONSTRUCT and nothing else: GNOME Shell 51 and later, one color, the files the
image installs. Upstream's other colors, desktops and toolkits are removed rather than kept beside
ours, so a fork is small and reads as what it builds. The cost is paid when pulling upstream:
merges conflict on the recolored lines and on files we deleted, and an icon or asset upstream adds
arrives in upstream's color until it is recolored. Each fork's README says what it carries.

`task preview` opens `preview.html`: the desktop drawn with the palette, in dark and light.

## The palette

| Group | What it is |
|---|---|
| `brand` | the logo's cyan, ink and paper; the boot's black |
| `neutral` | the surfaces, a-h, on Orchis' scale: a-d light (a brightest), e-h dark (e darkest) |
| `dark`, `light` | per mode: accent, text on the accent, text, muted text, border, success, warning, error |
| `icons` | Tela's folder body and its glyph |
| `cursor` | Bibata's fill, outline and the watch |
| `gnome` | the fixed libadwaita accent nearest to the cyan |
| `type` | the wordmark, the interface and the monospaced fonts |

Dark is the default. Light keeps the cyan's hue, darkened to `#007A85` so links and selected text
read on white: the logo's `#00E5FF` on white is 1.5:1.

`palette.py` fails when a pair the desktop draws one on the other is below WCAG 2.2 - 7:1 for
body text, 4.5:1 for other text (links, muted, success, warning, error, text on the accent and on
buttons filled with success, warning or error), 3:1 for parts that are not text - and when Orchis
would choose a different text color on the accent than the palette's: Orchis picks the text on a
fill itself, by brightness.

## GNOME Shell's surfaces

The shell is Orchis' dark variant in both modes. Its desktop is `e`, which is also the wallpaper's
ink, so nothing the shell lays over it may be `e`: its menus - quick settings, the calendar, the
panel's menus - its OSDs and its notifications stand on the raised surface, `h`, ringed with a
1px border in `dark.border`. A shadow alone does not lift them: black on ink does not show.
GNOME Shell 51's St draws a `border` with rounded corners, an `outline` only square, and a single
`box-shadow`, so the ring is a border. `preview.html` shows them open.

## What `palette/` holds

| File | For |
|---|---|
| `construct.css` | `preview.html`'s custom properties: dark under `:root`, light under `prefers-color-scheme` or `data-mode="light"`; GNOME Shell's, `--shell-*`, dark in both |
| `construct.scss` | Orchis: `$construct-light`/`$construct-dark`, `$construct-bg-a` ... `-h`, the border and the semantic colors per variant |

## Repository by repository

All on the `gnome-51` branch (`gnome-shell-51` for Orchis) of github.com/Construct-Linux.

**Orchis-theme** (GTK 3, GTK 4/libadwaita, GNOME Shell): Orchis-Construct-Light and
Orchis-Construct-Dark, `./install.sh -d DIR -c light dark`. `construct.scss` is copied in as
`src/_sass/_construct-palette.scss`: the accent per variant, `background(a ... h)` on the
palette's surfaces, the border and the semantic colors; the shell's menus take `h` and the border
(above). The GTK 4 accent is the theme's whatever Settings picks.
`logos/construct-activities.svg` is the Activities button. Copy the palette again when it changes.

**Tela-icon-theme**: Tela and Tela-dark, with upstream's blue recolored in the
sources to `palette.toml`'s `icons.folder` (glyph `icons.folder_glyph`); `sh ./install.sh -d DIR`. Upstream icons
merged later arrive blue: the recipe fails if `#5294e2` is left.

**Bibata_Cursor**: Bibata-Modern-Construct, X cursors and GNOME Shell's `cursors_scalable/`, built
from the SVGs by `build.py` with Python and rsvg-convert; its color table (`COLORS`) holds
`palette.toml`'s `cursor`, copied by hand.

**tilingshell, dash-to-panel**: their highlight colors set to `dark.accent`, as gsettings
overrides in the image, not in the fork.

**Vitals, caffeine, clipboard-indicator, appindicator, dash-to-panel, tilingshell**: GNOME Shell
51 only; the shell theme draws them.

**The image** (spin-desktop): the dconf defaults that tie it together - `gtk-theme` and the shell
theme Orchis-Construct-Dark, `icon-theme` Tela-dark, `cursor-theme` Bibata-Modern-Construct,
`accent-color` = `gnome.accent`, `color-scheme` = `prefer-dark`, the wallpapers, the fonts from
`type` - and the Plymouth theme from `plymouth/`.
