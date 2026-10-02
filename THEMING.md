# Theming

How the desktop takes the brand. The colors are written once, in `palette.toml`; `task palette`
checks their contrast and writes them out in `palette/`, and each fork takes them from there. The
forks stay small patches on top of upstream: a color variant added next to upstream's own, never
upstream's values edited in place, so that pulling upstream keeps merging.

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
body text, 4.5:1 for other text (links, muted, success, warning, error, text on the accent),
3:1 for parts that are not text - and when Orchis would choose a different text color on the
accent than the palette's: Orchis picks it itself, by brightness.

## What `palette/` holds

| File | For |
|---|---|
| `construct.json` | everything, flat (`dark-accent`, `neutral-e`, `icons-folder`, ...) |
| `construct.css` | custom properties: dark under `:root`, light under `prefers-color-scheme` or `data-mode="light"` |
| `construct.scss` | Orchis: `$construct-light`/`$construct-dark`, `$construct-bg-a` ... `-h`, the semantic colors |
| `bibata-render.json` | the two entries for Bibata's `render.json` |

## Repository by repository

**Orchis-theme** (GTK 2/3/4, GNOME Shell)

- Add `construct` as a theme color: import `construct.scss` in `_color-palette-default.scss`, a
  `construct` branch in `theme()` (`_colors.scss`) and in `install.sh`'s `-t`.
- Under the `construct` theme, `background(a ... h)` returns `$construct-bg-a ... -h` instead of
  the greys, so windows, views and popovers carry the ink's blue.
- `logos/construct-activities.svg` as `src/gnome-shell/activities/activities-construct.svg`, for
  `-i construct`.
- `wallpapers/construct-*.png` in place of `wallpaper/`.
- Installed with `-t construct -i construct -l`. `-l` links the GTK 4 theme for libadwaita apps;
  without it they use `gnome-accent` (teal).

**Tela-icon-theme**: a `construct` variant in `install.sh`, next to the others:
`theme_color` = `icons-folder`, `theme_back_color` = `icons-folder-glyph`.

**Bibata_Cursor**: the entries of `bibata-render.json` in `render.json`; the build makes
`Bibata-Modern-Construct` and `-Right` from upstream's SVGs.

**tilingshell, dash-to-panel**: their highlight colors set to `dark-accent`, as gsettings
overrides in `os`, not in the fork.

**Vitals, caffeine, clipboard-indicator, appindicator, gsconnect**: nothing. The shell theme
draws them.

**os**: the gsettings defaults that tie it together (`gtk-theme`, `icon-theme`, `cursor-theme`,
`accent-color` = `gnome-accent`, `color-scheme` = `prefer-dark`, the wallpapers, the fonts from
`type`), and the Plymouth theme from `plymouth/`.
