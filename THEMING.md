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
| `brand` | the logo's cyan, ink (the wallpaper's) and paper; the boot's black, the ground under all that is not a window or the desktop |
| `neutral` | the surfaces, a-h, on Orchis' scale: a-d light (a brightest), e-h dark (e darkest) |
| `dark`, `light` | per mode: accent, the accent standing alone (`accent_text`), text on the accent, text, muted text, border, success, warning, error |
| `tint` | per mode, the accent's alpha over a surface: rest, hover, active, and selection |
| `shape` | libadwaita's radius steps, the spacing grid, the bars' distance from the screen edge |
| `icons` | Tela's folder body and its glyph |
| `cursor` | Bibata's fill, outline and the watch |
| `gnome` | the fixed libadwaita accent nearest to the cyan |
| `type` | the wordmark's font; the interface's and apps' monospaced, GNOME's own (Adwaita Sans, regular; Adwaita Mono); the terminal's |
| `ansi` | per mode, the terminal colors the other groups do not give: blue, magenta, the brights |

Dark is the default. Light keeps the cyan's hue, darkened to `#007A85` so links and selected text
read on white: the logo's `#00E5FF` on white is 1.5:1.

`palette.py` fails when a pair the desktop draws one on the other is below WCAG 2.2 - 7:1 for
body text, 4.5:1 for other text (links, muted, success, warning, error, text on the accent and on
buttons filled with success, warning or error, labels on a tint), 3:1 for parts that are not text
(the accent as a mark, on every surface) - when an edge is below the brand's minimum (below), and
when Orchis would choose a different text color on the accent than the palette's: Orchis picks the
text on a fill itself, by brightness.

## Elevation

Each level up is one step lighter on the ink scale. In dark, the 1px ring in `dark.border` makes
the edge: a black shadow does not show on ink, so a shadow only adds depth, never the edge.

| Level | What | Dark surface | Ring | Shadow |
|---|---|---|---|---|
| ground | firmware, Plymouth, the overview and app grid, the lock screen and GDM | `brand.boot` | none | none |
| 0 | the desktop and the wallpaper | `e` | none | none |
| 1 | GTK window body | `f` | `0 0 0 1px`, kept when tiled, none when maximized | GTK's shadow-z16 |
| 1 | GTK views and the headerbar | `g` | the headerbar's bottom rule | - |
| 1 | the top bar and the dock | `g`, opaque | 1px all round | none |
| 2 | menus, popovers, quick settings, the calendar, notifications, tooltips, the dock's labels and previews, window captions, the overview's search entry and result cards | `h` | 1px | `0 4px 12px` black at 35% |
| 2a | an expanded shell submenu | a `g` well inside the `h` menu; its parent row white at 8% | none | none |
| 3 | the shell's modal and app-folder dialogs, OSDs | `h` | 1px | `0 12px 28px` black at 45% |

The overview's workspace card is `e` on the black ground: 1.11:1, lighter than what it stands on,
as a card should be. The top bar and the dock are opaque `g` with the ring; never black glass:
over ink it is 1.07:1, no edge at all, and over paper it is a grey without the ink's hue.
In dark, no window is `e`: that is the desktop's own color, and a window on it has no edge.

In light, GTK keeps the window on `c`, views and popovers on `a`; on paper the shadow lifts them.
The shell is Orchis' dark variant in both modes, so the bars are `g` there too: 15.2:1 on paper.

GNOME Shell 51's St draws a `border` with rounded corners, an `outline` only square, and a single
`box-shadow`, so the ring is a border. `preview.html` shows every level.

The edges the brand holds to (`task palette`, "edge (brand, not WCAG)"): the dark ring on `e`
1.5:1, on `h` 1.2:1; `h` on `e` 1.25:1; the light border on `c` 1.4:1.

## Accent

**Full accent goes only on marks**: the focus ring (2px), a switch's knob and track, a slider,
progress and the OSD's level, the dock's running dot, badges, the caret, a link's underline, the
rubberband, and the calendar's ring around today.

**Anything larger takes a tint**: the accent at an alpha over the surface under it, its label and
icon in `accent_text`. Quick toggles when on and their arrow, the selected calendar day, sidebar
and list selection, the shell's default button, GTK's suggested buttons in dark, the dock's focus
highlight, the message list's collapse button, the selected audio device.

| Tint | Rest | Hover | Active | Selection |
|---|---|---|---|---|
| dark | 16% | 22% | 28% | 25% |
| light | 10% | 14% | 18% | 20% |

28% is the ceiling: at 32% over `h`, `accent_text` falls to 4.29:1. `accent_text` is the accent
in dark (`#00E5FF`, 4.79:1 at its worst, active over `h`) and `#00646D` in light: the light accent
`#007A85` reads only 4.25:1 on its own 10% tint over `b`, while `#00646D` is 5.0:1 or more on every
tint. Light suggested buttons stay filled with `#007A85` and white text (5.09:1).

**Muted text never goes on a tint**: muted on `h` at 22% is 3.96:1, at 28% 3.40:1. A second line
on a tint is `text`. `task palette` prints muted on every tint without holding it to anything.

**One selection alpha**, for GTK, the shell's entries, Ghostty and VS Code: 25% in dark (over `g`
`#11515E`, text 7.52:1), 20% in light (over `a` `#CCE4E7`, text 13.48:1). The dock's focus
highlight is the accent at 14% (dash-to-panel's own key): over `g` `#143C46`, accent on it 7.74:1.

**States are white, black or the accent at an alpha over a palette surface**, never a grey of
their own. Panel buttons: hover white 8%, active, checked and open 12%. A quick toggle off: white
6% over `h`, `#2C373F`, text 10.29:1 and muted 5.61:1 on it. The shell's primary text is
`dark.text` (12.36:1 on `h`), its secondary `dark.muted` (6.74:1); what was white at 30% - 'No
Notifications', the other month's days - is secondary.

## Shape and type

| Token | Value | For |
|---|---|---|
| `radius_control` | 9 | buttons, entries, menu items, rows, tooltips, cards inside menus |
| `radius_surface` | 15 | GTK windows and popovers, the shell's popup menus, notification banners, the dock, the dock's previews |
| `radius_sheet` | 24 | the date menu, modal dialogs, app tiles, the folder icon |
| pill | 9999 | the top bar and its buttons, quick toggles, the shell's entries, calendar days |

These are libadwaita's steps, so the shell and the apps match. **Concentric**: a container takes its
child's radius plus its padding. Quick settings is 22 + 18 = 40; a search section 9 + 12 = 21; the
app-folder dialog 48; a button in a 24px dialog with 12px padding 12. GTK's cards and boxed lists
keep libadwaita's 12, its alert dialogs 18: Orchis does not override them.

Spacing is on the grid 3, 6, 12, 18, 24. Both bars sit `inset`, 6px, from the screen edge; the top
bar is 36px tall with its ring, the dock 44px.

Type: the shell's `stage` is `font-size: 1em`, following `font-name` ('Adwaita Sans 11') and the
text scaling factor; every size under it is in `em`. Weights are 400 and 700 only, 700 for titles
and the labels of controls you act on; the top bar is regular. The lock screen's clock is 6.5em,
400, with tabular numbers. GTK keeps libadwaita's typography.

The image sets no rendering keys: grayscale, slight hinting and automatic are right for the OLED
panels it runs on. The X9-15 is scaled to 150% (a step of the OS, not of the theme).

## Boot to desktop

Black, `brand.boot`, from the firmware through Plymouth, the shell's startup, the overview's ground
and the lock screen's: the desktop's ink only fades or zooms in over it.

- The mark is centred horizontally, its centre at 0.4222 of the screen's height, where the
  wallpaper draws it. Plymouth's frames carry where the mark's centre is in them
  (`plymouth/sequence.json`'s `mark_center`, 0.4329 of the frame), so the theme places the frame,
  not a guess.
- After the disk's password, the outro plays and goes back to the grid's loop, so GDM always takes
  over on the wallpaper's drawing.
- Plymouth's prompt is the shell's unlock entry: a 36px pill on `g`, a 2px accent ring (13.65:1 on
  black) and dots in `text`, its colors from `palette.json`.
- The lock screen and GDM draw Orchis through the system's gnome-shell-theme.gresource: User Themes
  is off in the unlock-dialog mode. GNOME Shell's SystemBackground is black, not its own #282828.
- The session starts on the overview.

## App icons

Every app the desktop shows resolves its icon in Tela or in a brand tile installed in hicolor
(`logos/io.github.construct_linux.Installer.svg`, drawn in Tela's geometry); no `Icon=` names a
path. An unofficial build that carries no brand of its own (Firefox's) takes `web-browser`. Tela's
`#549bff` family (its software and store icons) is recolored to `icons.folder` with the folders.

## Apps outside GTK

- **Ghostty**: `palette/ghostty/Construct Dark` and `Construct Light`, installed to
  /usr/share/ghostty/themes. Ghostty reads no system configuration, so `construct theme` seeds the
  user's once. The terminal's background is the view, `g` or `a`, which is Orchis' headerbar: the
  window is one surface. Its font is JetBrains Mono, Ghostty's built-in default.
- **VS Code**: `palette/vscode/`, a built-in `construct-theme` extension. Its themes include VS
  Code's own 2026 themes for syntax; its `configurationDefaults` pick Construct Dark and Light and
  follow the desktop's color scheme. Selection in lists and menus is the accent at 15%, in the
  editor at 25%.
- **Firefox**: a link `Orchis-Construct` to `Orchis-Construct-Light`, so its lookup for the other
  scheme stops falling back to Adwaita's blue. No color preferences.
- **Chrome**: no policy: BrowserThemeColor would take it out of GTK mode.
- **libadwaita's accent setting** stays `teal` (`gnome.accent`): it only feeds the portal and
  Settings' swatches. Orchis' own `:root` accent wins wherever the theme reaches.

## What a theme change must keep

Each rule says where it is tested: **P** `task palette`, **L** `task lint`, **H** the image's
harness (`lf:` checks), **N** its needles.

| Rule | | Test |
|---|---|---|
| C1 | Every color is `palette.toml`'s, or white, black or the accent at an alpha over one | L |
| C2 | Text and marks meet WCAG 2.2 on every surface they are drawn on | P |
| C3 | Full accent only on marks; larger areas are a tint, labelled in `accent_text` | P, H |
| C4 | Muted text never on a tint | H |
| C5 | One selection alpha: 25% dark, 20% light | P, H |
| C6 | Every copy of the palette (Orchis' SCSS, Bibata's table) is the current one | L |
| S1 | The top bar and the dock: opaque `g`, the 1px ring all round | H |
| S2 | Menus, popovers, notifications, tooltips, OSDs, dialogs: `h`, the ring, a shadow by level | H |
| S3 | A dark GTK window is `f` with an outer 1px ring; its headerbar and views `g` | H |
| S4 | The overview, the app grid, the lock and login ground: `brand.boot` | H |
| E1 | Edges: the ring 1.5:1 on `e`, 1.2:1 on `h`; `h` on `e` 1.25:1; light border on `c` 1.4:1 | P |
| E2 | Both bars' edge shows over the dark and the light wallpaper | H |
| F1 | Every focusable shell control shows focus as `inset 0 0 0 2px` accent; popup-menu items and calendar days are exempt (hover is focus; the ring is today) | H |
| F2 | GTK's focus outlines are the accent | H |
| R1 | Radii 9 / 15 / 24 / pill, concentric | P, H |
| R2 | GTK cards and boxed lists 12, alert dialogs 18 | H |
| SP1 | Spacing on 3 / 6 / 12 / 18 / 24 | P |
| SP2 | Both bars 6px from the edge; the top bar 36px, the dock 44px | H |
| T1 | The shell's `stage` is 1em; every size under it in `em` | H |
| T2 | Weights 400 and 700 only | H |
| T3 | No font or rendering keys in the image; fontconfig maps the generic families to Adwaita Sans and Mono | H |
| X1 | Ghostty's and VS Code's themes come from `palette/` | P, H |
| X2 | Every visible app's icon resolves in Tela or a brand tile; no absolute `Icon=` | H |
| X3 | Firefox's `Orchis-Construct` link; Chrome without a theme policy | H |
| - | Anything that changes the picture at all | N |

## Checks

| Check | Where | What it holds |
|---|---|---|
| `task palette` | brand | contrast of every pair, the tints, the selection, the edges, the shell's resting fill, the terminal's colors; whole-pixel radii and an ascending grid |
| `task lint` | brand, over the forks checked out beside it | a color no palette writes, an exception nothing needs, a stale copy of the palette |
| harness `lf:` | spin-desktop's image test | St's computed styles through eval, pixel probes inside the chrome's extents, the CSS and gsettings in the guest |
| needles | spin-desktop's image test | whether any view changed at all |

## What `palette/` holds

| File | For |
|---|---|
| `construct.css` | `preview.html`'s custom properties: dark under `:root`, light under `prefers-color-scheme` or `data-mode="light"`; GNOME Shell's, `--shell-*`, dark in both; per mode the tints (`--tint`, `--tint-hover`, `--tint-active`, `--selection`) and the terminal's (`--term-0` ... `--term-15`, `--term-bg`, `--term-fg`, `--term-selection`); the radii and `--inset` |
| `construct.scss` | Orchis: `$construct-light`/`$construct-dark`, `$construct-bg-a` ... `-h`; per variant the border, semantic colors, `accent-text`, text, muted and on-accent; `$construct-boot`, `$construct-ink`; the tints and selection; the radii and the inset |
| `construct.json` | the image, at /usr/share/construct/palette.json: every value of `palette.toml`, flat (`neutral-e`, `dark-border`, `tint-dark-rest`), for Plymouth's theme and the harness |
| `ghostty/` | Ghostty's Construct Dark and Construct Light |
| `vscode/` | VS Code's `construct-theme` extension: `package.json` and `themes/` |

## Repository by repository

All on the `gnome-51` branch (`gnome-shell-51` for Orchis) of github.com/Construct-Linux.

**Orchis-theme** (GTK 3, GTK 4/libadwaita, GNOME Shell): Orchis-Construct-Light and
Orchis-Construct-Dark, `./install.sh -d DIR -c light dark`. `construct.scss` is copied in as
`src/_sass/_construct-palette.scss` under a two-line header (`task lint` compares them): the
accent per variant, `background(a ... h)` on the palette's surfaces, the text, border and semantic
colors, the tints and the radii; the shell takes the levels above. The GTK 4 accent is the theme's
whatever Settings picks. `logos/construct-activities.svg` is the Activities button. Copy the
palette again when it changes.

**Tela-icon-theme**: Tela and Tela-dark, with upstream's blue recolored in the sources to
`palette.toml`'s `icons.folder` (glyph `icons.folder_glyph`); `sh ./install.sh -d DIR`. Upstream
icons merged later arrive blue: the recipe fails if `#5294e2` is left.

**Bibata_Cursor**: Bibata-Modern-Construct, X cursors and GNOME Shell's `cursors_scalable/`, built
from the SVGs by `build.py` with Python and rsvg-convert; its color table (`COLORS`) holds
`palette.toml`'s `cursor`, copied by hand and compared by `task lint`.

**dash-to-panel, tilingshell**: the dock takes `#panel`'s color from the shell theme and the
theme's running dot; its focus highlight (the accent at 14%) and tilingshell's
`window-border-color` (the accent) are dconf keys in the image's `00-construct`.

**Vitals, caffeine, clipboard-indicator, appindicator, dash-to-panel, tilingshell**: GNOME Shell
51 only; the shell theme draws them.

**The image** (spin-desktop): the dconf defaults that tie it together - `gtk-theme` and the shell
theme Orchis-Construct-Dark, `icon-theme` Tela-dark, `cursor-theme` Bibata-Modern-Construct,
`accent-color` = `gnome.accent`, `color-scheme` = `prefer-dark`, the wallpapers - the Plymouth
theme from `plymouth/`, `palette.json`, Ghostty's themes and VS Code's extension. The fonts in
`type` are GNOME's and Ghostty's defaults: GTK takes them from gsettings; browsers and Electron ask
fontconfig, which the image maps to Adwaita Sans and Adwaita Mono (56-construct.conf) ahead of
Noto.
