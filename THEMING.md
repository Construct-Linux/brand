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
| `dark`, `light` | per mode: accent, the accent standing alone (`accent_text`), text on the accent, text, muted text, border, success, warning, error; light's desk (the desktop's ground) and shelf (the sidebar's pane) |
| `tint` | per mode, the accent's alpha over a surface: rest, hover, active; selection; decoration (transient overlays); a switch's track |
| `line.light` | light's lines: `light.muted` at an alpha, for dividers, borders and the window's ring |
| `shape` | libadwaita's radius steps, the spacing grid, the bars' distance from the screen edge |
| `icons` | Tela's folder body and its glyph |
| `cursor` | Bibata's fill, outline and the watch |
| `gnome` | the fixed libadwaita accent nearest to the cyan |
| `type` | the wordmark's font; the interface's and apps' monospaced, GNOME's own (Adwaita Sans, regular; Adwaita Mono); the terminal's |
| `ansi` | per mode, the terminal colors the other groups do not give: blue, magenta, the brights |

Dark is the default. Light keeps the cyan's hue, darkened, as two colors: `#007A85` (`accent`)
for fills and marks - the primary, indicators, focus - and `#00646D` (`accent_text`) for links and
labels, which must read on white and on every tint. The logo's `#00E5FF` on white is 1.5:1.

`palette.py` fails when a pair the desktop draws one on the other is below WCAG 2.2 - 7:1 for
body text, 4.5:1 for other text (links, muted, success, warning, error, text on the accent and on
buttons filled with success, warning or error, labels on a tint), 3:1 for parts that are not text
(the accent as a mark, on every surface) - when an edge is below the brand's minimum (below), when
a pair that carries meaning falls below its perceptual tier ("Perception"), and when Orchis would
choose a different text color on the accent than the palette's: Orchis picks the text on a fill
itself, by brightness. `desk` and `shelf` are held to being `d` at 50% and 25% over `c`.

## Elevation

Each level up is one step lighter on the ink scale. In dark, the 1px ring in `dark.border` makes
the edge: a black shadow does not show on ink, so a shadow only adds depth, never the edge.

| Level | What | Dark surface | Light surface | Ring | Shadow |
|---|---|---|---|---|---|
| ground | firmware, Plymouth, the overview and app grid, the lock screen and GDM | `brand.boot` | `brand.boot` | none | none |
| 0 | the desktop and the wallpaper | `e` | `desk` | none | none |
| 1 | GTK window body | `f` | `c` | `0 0 0 1px`: `dark.border`, light's ring line (40%); kept when tiled, none when maximized | GTK's shadow-z16 |
| 1 | the sidebar's pane | `f` | `shelf` | the pane separator, the border line | - |
| 1 | GTK views, cards and boxed lists; the headerbar | `g` | `a`; the headerbar flat on its pane (`c` or `shelf`) | the headerbar's bottom rule; in light, cards and lists the border line and no drop shadow | - |
| 1 | the top bar and the dock | `g`, opaque | `g`, opaque | 1px all round | none |
| 2 | menus, popovers, quick settings, the calendar, notifications, tooltips, the dock's labels and previews, window captions, the overview's search entry and result cards | `h` | popovers `a`; the shell stays `h` | 1px; light popovers the border line | `0 4px 12px` black at 35%; light popovers shadow-z4 |
| 2a | an expanded shell submenu | a `g` well inside the `h` menu; its parent row white at 8% | the same | none | none |
| 3 | the shell's modal and app-folder dialogs, OSDs | `h` | `h` | 1px | `0 12px 28px` black at 45% |

The overview's workspace card is `e` on the black ground: 1.11:1, lighter than what it stands on,
as a card should be. The top bar and the dock are opaque `g` with the ring; never black glass:
over ink it is 1.07:1, no edge at all, and over paper it is a grey without the ink's hue.
In dark, no window is `e`: that is the desktop's own color, and a window on it has no edge.

In light the same holds: on paper `#F4F6F8` a `c` window stands on its own color (1.00:1), with
only a shadow's gradient for an edge. So it stands on the desk, `d` at 50% over `c` (1.18:1), with
the ring outside it (1.69:1 on the desk, where dark's ring is 1.58:1 on `e`). On paper the shadow
is depth; the ring is the edge, as in dark. The sidebar is the shelf, `d` at 25% over `c`, a step
below the window as libadwaita's sidebar is. Every step is a
luminance step, so the deficiencies lose nothing, and dimmed the edge is the ring's.
The shell is Orchis' dark variant in both modes, so the bars are `g` there too: 12.9:1 on the desk.

GNOME Shell 51's St draws a `border` with rounded corners, an `outline` only square, and a single
`box-shadow`, so the ring is a border. `preview.html` shows every level.

The edges the brand holds to (`task palette`, "edge (brand, not WCAG)"): the dark ring on `e`
1.5:1, on `h` 1.2:1; `h` on `e` 1.25:1; the light border on `c` 1.4:1; light's `c` on the desk
1.15:1, the shelf against `c` and against the desk 1.07:1, the sheet `a` on the shelf 1.15:1, the
ring line on the desk 1.6:1, the border line over `a`, `c` and the shelf 1.45:1, the divider over
`a` 1.25:1.

### Lines (light)

Every light line is `light.muted` (`#536672`, OKLCH hue 236) at an alpha, over whatever surface,
so it keeps the ink's hue: chroma 0.010-0.015 where GNOME's `rgba(black, 0.12)` has 0.001. Hue-less
lines are most of what makes a light window read as customized GNOME; this is light's brand
gesture, an edge rather than more cyan. Ink itself at an alpha is no better (its chroma 0.014 leaves 0.004 at line
alphas); muted carries 0.030.

| Line | Alpha | Over `a` | Over `c` | Over the shelf | Over the desk |
|---|---|---|---|---|---|
| divider: separators inside a card or a list | 20% | 1.33 | 1.31 | 1.30 | - |
| border: card and list outlines, the headerbar's rule, the pane separator, popovers, entries | 30% | 1.54 | 1.51 | 1.50 | - |
| ring: the window's outer ring | 40% | - | - | - | 1.69 |

`light.border` `#C9D1D8` is the border line's solid twin over `a`, for what cannot draw an alpha
(VS Code, Ghostty's splits). Dark draws one solid line, `dark.border`.

**The title rule.** The light headerbar stays flat on its pane (`c` over the content, the shelf
over the sidebar) and always draws `inset 0 -1px` in the border line, not only when the view
scrolls; libadwaita's raised top-bar shade goes. Both headerbars are one height, so the rule runs as
one line across the window: the drawing sheet's title block. Bottom bars mirror it, `inset 0 1px`.

## Accent: one scale

One color, seven meanings. Drawn only two ways, full and tint, they collide: a primary button and
a selected row become the same pixels, a 2px ring means focus, today, the current workspace and the
selected theme at once, and every place picks its own alpha. The scale gives each level one channel
no other level uses.

**A level is a meaning; its rendering follows from its size.** A mark - at most 4px of stroke, or a
disc or knob up to 24px - may be the full accent. Anything larger is a tint or a solid fill, by
level. Strongest first:

| # | Level | Where | Dark (the shell on `h`, GTK on `g`) | Light (GTK on `a`/`c`; the shell stays dark) |
|---|---|---|---|---|
| 1 | **Brand** | the mark and the wordmark, Plymouth, the wallpaper, About, the installer. Never chrome: the Activities glyph is white | `brand.cyan` on ink or black only; a glow where the boot draws one | the mono mark, or the room in the light accent on the desk (the mark wallpaper); no cyan chrome |
| 2 | **Primary action** | one per view: GTK's `suggested-action`; the shell dialog's default (prompt, polkit, unlock); a banner's or an infobar's button | **solid accent**, label `on_accent` at 700 (12.34:1). Hover and active: `on_accent` at 8% and 16% over the fill; disabled: opacity 0.5. Focus: in the shell an inset 2px ring in `on_accent` inside the fill; in GTK the 2px accent outline, 2px offset | solid `#007A85`, white label at 700 (5.09:1); the same states; focus an inset 2px white or the offset outline |
| 3 | **Selected, on** | quick toggles on and their arrow, selected rows, the sidebar, the selected day, view-switcher and stack-switcher tabs, checked toggle buttons, the Alt+Tab item, the IBus candidate, the dock's focused app | the tint, rest / hover / active, label `accent_text`, a second line `text`, **no edge**. A quick toggle that is on also draws its icon on a 24px accent disc with an `on_accent` glyph | the tint with the **border line inside it** (`inset 0 0 0 1px`, neutral); the navigation sidebar is the sheet instead (below) |
| 3a | Text selection | entries, text views, terminals, VS Code | the selection alpha, 25%; the text keeps `text` | 20% |
| 3b | Selected on imagery | window thumbnails (the screenshot UI, the workspace thumbnails), Settings' style previews | a 2px frame in `text` plus the accent's check badge; no accent ring | the same |
| 4 | **Indicator** | switch, checkbox, radio, slider fill, progress, the OSD's level, levelbar, badges, the dock's running dot, the workspace dot, the caret, the tab indicator, Calendar's now-strip | full accent, mark-sized. A switch's track is the accent at 50% (3.48:1 on `h`), its knob the full accent; the slider's knob stays `text` | `#007A85`; the track 50% (2.12:1: the knob carries the state) |
| 5 | **Focus** | keyboard focus, on every focusable control, calendar days included | a 2px full-accent ring: `inset 0 0 0 2px` in St, an outline in GTK. Never a fill. **Nothing else draws an accent ring**: tilingshell's border and the Alt+Esc frame are focus | 2px `#007A85` |
| 6 | **Link** | links, `.shell-link`, URL highlighting | `accent_text` with a 1px accent underline; hover the rest tint, active the hover tint | `#00646D`, underlined |
| 7 | **Decoration** | the wallpaper; transient overlays only (the rubberband, the tile preview, a drop target, the hot corner's ripple) | the decoration tint, 8%, with a 1px accent edge. Never a resting surface, a pane, a banner or a control | 5% with the edge; light has no other cyan decoration |

**Today** in a calendar is `accent_text` at 700 - no ring, no tint: ΔE00 22.4 from a day's text in
dark, 27.3 in light (2.59:1, plus the weight). GtkCalendar's today is not selected, so it draws no
tint. The ring is free for focus, and calendar days lose their exemption from F1; popup-menu items
keep theirs (hover is focus there).

**Primary is solid, in dark too.** It is the only rendering that tells the primary from a selected
item without a third tint or an edge that reads as focus: against the rest tint 7.02:1 and ΔE00 56
over `g` (light 38.6 over `c`), 49 or more in every view. The cost is one button per view - Clocks'
"Add World Clock..." is 0.89% of a 1280x800 screen - where solid quick toggles would be 1.29%, so
they stay a tint. The alternative, the tint with a 1px accent ring at 50%, measures 3.04:1 against
the tint, 2.32 at low brightness, and reads as half focused.

| Tint | Rest | Hover | Active | Selection | Decoration | Track |
|---|---|---|---|---|---|---|
| dark | 18% | 23% | 28% | 25% | 8% | 50% |
| light | 10% | 17% | 24% | 20% | 5% | 50% |

28% is the dark ceiling: at 32% over `h`, `accent_text` falls to 4.29:1. Dark's rest is 18% so an
on quick toggle stays ΔE00 6.5 from an off one for deutans on an IPS panel (at 16%, 5.6). Light's
steps are each ΔE00 3.6 or more, well past one just-noticeable difference, and `#00646D` still
reads 4.57:1 on the active tint. `accent_text` is the accent in dark (`#00E5FF`,
4.79:1 at its worst, active over `h`) and `#00646D` in light: the light accent `#007A85` reads only
4.25:1 on its own 10% tint over `b`.

**Light marks a state with a line, not more cyan.** No light alpha keeps `accent_text` legible and
still reads for protans (the rest tint is ΔE00 3.1 from `a` at worst; a state needs 6), so a light
tint that marks a state also draws the border line inside it - neutral, so it never reads as focus
- and the line holds the state (ΔE00 10.6 from `a`, 10.2 at worst). The navigation sidebar
(Settings, Files' places, stack sidebars) is the **sheet**: the selected row is `a` with the border
line inside it, its label `text` at 700 (17.9:1) and its icon `accent_text` (6.9:1, a mark). Hover
is white at 50% over the shelf, which is `c`; pressed is black at 6%. Cyan shrinks from a
238x43 tint to a 16px icon, and weight carries the selection without color.

**How the levels stay apart** (ΔE00 as drawn, `task palette` holds them):

| Pair | Channel | Dark | Light |
|---|---|---|---|
| primary / selected | solid against tint | 56.2 over `g`, 51.3 over `h` | 40.3 over `a`, 38.6 over `c` |
| selected / its surface | the tint; light its line | 14.0 over `g`, 13.9 over `h` | 6.1, and the line 10.6 |
| rest / hover / active | a tint step | 3.1-3.5 | 3.6-3.8 |
| focus / selected | the ring on the active tint | 4.79:1 over `h` | 3.38:1 over `c` |
| focus / primary | the `on_accent` ring inside the fill | 12.34:1 | white 5.09:1 |
| decoration / its surface | sub-tint, transient, with its edge | 7.6 over `g` (selected: 14.0) | 3.2 over `a` (selected: 6.1) |
| today / a day | accent_text at 700 | 22.4 | 27.3 |

**Muted text never goes on a tint**: muted on `h` at 23% is 3.85:1, at 28% 3.40:1. A second line
on a tint is `text`. `task palette` prints muted on every tint without holding it to anything.

**One selection alpha**, for GTK, the shell's entries, Ghostty and VS Code: 25% in dark (over `g`
`#11515E`, text 7.52:1), 20% in light (over `a` `#CCE4E7`, text 13.48:1). VS Code's list and menu
selection is the rest tint, its editor selection the selection alpha. The dock's focus highlight
is the rest tint, 18% (dash-to-panel's own key): over `g` `#13434F`, the accent on it 7.02:1.

**States are white, black or the accent at an alpha over a palette surface**, never a grey of
their own. Panel buttons: hover white 8%, active, checked and open 12%. A quick toggle off: white
6% over `h`, `#2C373F`, text 10.29:1 and muted 5.61:1 on it. The shell's primary text is
`dark.text` (12.36:1 on `h`), its secondary `dark.muted` (6.74:1); what was white at 30% - 'No
Notifications', the other month's days - is secondary.

**The accent's alpha is a token.** The forks write the accent only as `$primary` at `$tint`,
`$tint-hover`, `$tint-active`, `$selection-alpha`, `$tint-decoration` or `$tint-track` - never a
number at the place of use, never `lighten()`, `darken()`, `transparentize()` or `mix()` of it
(`task lint`, C7).

## Perception

WCAG's ratio says whether text reads. It says nothing about two surfaces a step apart, a state
told by hue, or a panel dimmed in a lit room. `task palette` also holds every pair that carries
meaning to a CIEDE2000 floor (Sharma 2005; its formula is checked against Sharma's test pair),
as drawn and in eight views:

| View | Model |
|---|---|
| ips | a non-OLED panel, 250 cd/m2 white, 0.3 black (830:1), 0.6 cd/m2 of office flare (200 lx at 1%, / pi) |
| dim | an OLED at 30%: 75 cd/m2, black crushed (gamma 1.1), the same flare |
| dim_ips | an IPS backlight at 30%: 75 cd/m2, 0.09 black, the same flare |
| protan, deutan, tritan | Machado, Oliveira and Fernandes 2009 at severity 1.0 (dichromacy, the worst case), in linear RGB |
| protan+ips, deutan+ips | protan and deutan, 8% of men between them, on the office's IPS panel |

The eye is taken as adapted to the panel's white, so a dim panel in a brighter room does worse.
Flare squeezes `e`-`h` from 11.6 L* of range to 7-8: for the surfaces the risk is the panel and
the room, not colour-vision deficiency; for the accent and the semantic colors it is the
deficiencies.

| Tier | What | As drawn | Worst view |
|---|---|---|---|
| E | two surfaces at an edge with nothing between them | 3 | 2 |
| R | a 1px line against the surface outside it | 6 | 4 |
| S1 | a state that persists: on and off, selected and not, today | 10 | 6 |
| S2 | a step under the pointer: rest, hover, active | 3 | 2 |
| K | hue that carries meaning: status colors, the terminal's | 20 | 10; tritan 6 |
| P | the primary against a selected item | 30 | 24 |
| D | a transient overlay: shows (3), and stays under 0.6 of a selected tint's ΔE00 | | its edge |

A pair below its tier passes only through the line drawn between the two, held to R: the dark
window on the desktop (`e`/`f` 2.31, 1.33 dimmed; its ring 12.4) and the content beside its body
(`f`/`g` 2.70; the separator and the headerbar rule 10.3); light's view on the window (`c`/`a`
2.24), the shelf beside the content (2.17) and the desk beside a sidebar (2.22). A light tint
passes S1 through its line. The dark ring on `h` (4.49, level 3 over a menu) is reported, not
held: level 3 leans on its shadow there until a lighter ring for it exists.

**Low light, reported.** At 30% backlight in a room lit to 3% of the panel's white (`task palette`
prints it; `preview.html`'s "30% backlight" draws it): `h` on `e` 1.30 -> 1.16, the ring on `e`
1.58 -> 1.30, the rest tint on `g` 1.53 -> 1.29, a quick toggle on against off 1.28 -> 1.18. That
last one, with the label alone a hue step protans barely see (accent against text 1.30:1), is why
an on quick toggle draws its icon on the accent disc: 6.16:1 on the tint, 4.56 dimmed.

**No meaning by hue alone.** Even after these fixes a status color is a floor of 10 for
deficiencies, not comfort: status carries an icon or a shape (C9).

`preview.html`'s "See as" draws the page through the same models (`palette/simulate.js`: the
matrices are written once, in `palette.py`), and its Perception table lists every pair
(`palette/perception.js`).

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
400, with tabular numbers.

GTK keeps Adwaita Sans and libadwaita's sizes; composition is where it is worked. Adwaita Sans
has a variable `opsz` axis (14-32) and `wght` (100-900): no letter-spacing and no text-transform
anywhere, the face adapts its display sizes itself.

| Rule | |
|---|---|
| TY1 | Weights 400 and 700 in GTK too. Orchis' off-scale weights map: `.large-title` 300 -> 400; `.title-1`, `.title-2` 800 -> 700; generic buttons 500 -> 700 (libadwaita's); sidebar labels 500 -> 400 and their selected rows 500 -> 700; Weather's temperature 900 -> 400, like the lock clock; the 300s and 500s elsewhere likewise |
| TY2 | Sizes are libadwaita's: large-title 24pt, title-1 20pt, title-2 and title-3 15pt (both 700 now), title-4 13pt, heading and body 11pt, caption 9pt |
| TY3 | The headerbar: the title 1em at 700 in `text`, the subtitle 9pt at 400 in `muted`, centred; the title rule under it. Nothing else in a headerbar is 700 but text buttons |
| TY4 | Preference groups: the title `.heading`, 11pt at 700 in `text` (not muted, not capitals); the description 9pt `muted`, 3px above it; 12px from the header to its list, 24px between groups and from the title rule to the first list; lists clamped at libadwaita's 600 |
| TY5 | Rows: the title 1em at 400 in `text`, the subtitle 9pt `muted`, 3px between them. Sidebar section labels are `.caption-heading`, 9pt at 700 `muted`: 5.08:1 on the shelf |
| TY6 | Status pages: the icon `muted`, 18px, title-1, 6px, the body `muted`, 24px, the button |
| TY7 | Numbers that change - clocks, sizes, Vitals, Weather - are `.numeric` (tabular) |
| TY8 | Gaps on the 3 / 6 / 12 / 18 / 24 grid; cards keep their 12 |

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
  over on the wallpaper's drawing. The default wallpaper is that drawing held still: it may not
  move (W1).
- Plymouth's prompt is the shell's unlock entry: a 36px pill on `g`, a 2px accent ring (13.65:1 on
  black) and dots in `text`, its colors from `palette.json`.
- The lock screen and GDM draw Orchis through the system's gnome-shell-theme.gresource: User Themes
  is off in the unlock-dialog mode. GNOME Shell's SystemBackground is black, not its own #282828.
- The session starts on the overview.

## Wallpapers

Four pairs, each a light file with its dark one in `construct.xml`, so Settings shows one
thumbnail that follows the style switch. All from `room.py`'s camera and edges. Dark draws in the
accent on ink; light draws the room in the ink's hue (`light.muted`) on the desk, a technical
drawing, with no cyan - except the mark, the brand mark.

| Pair | What | Dark: outline / grid / glow | Light: outline / grid |
|---|---|---|---|
| `construct` (default) | the boot's drawing held still, its mark at 0.4222 of the height | 55% / 22% / 0.6 | 50% / 15% |
| `construct-quiet` | the same drawing at a third of the level, no glow: it may take over from the boot too | 17% / 4.5% / none | 28% / 11% |
| `construct-offset` | the room at 0.62, its outline's corner at 5/6 of the width and 0.80 of the height: the window area left empty | 24% / 8% / none | 34% / 12% |
| `construct-mark` | the outline alone at 0.22, 201px from the right and the bottom: 90px of `zoom` crop on a 16:9 or 3:2 panel plus the dock's top and a space step at 150% | the accent at 45% | the light accent at 40% |

The default's busyness is mostly its glow: its haze covers 6.6% of the screen against 1.1% for the
lines alone. That stays: it is the boot's look. `task wallpaper` prints each file's outline
contrast, its lines' ΔE00 against the ground and the share of the screen they cover, and fails
(W2) unless each variant is calmer than its mode's default on both - a lower outline contrast and
no more coverage - and unless every line is ΔE00 3 or more from its ground, so nothing vanishes on
a washed-out panel. Quiet's dark lines are held to the perceptual target for a calm field: the
outline at most ΔE00 15 from ink and the grid 6 (the default's are 39.6 and 18), the grid still 5
from `h`, so a menu's edge never merges with a line under it.

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
  follow the desktop's color scheme. Selection in lists and menus is the rest tint, in the editor
  the selection alpha.
- **Firefox**: a link `Orchis-Construct` to `Orchis-Construct-Light`, so its lookup for the other
  scheme stops falling back to Adwaita's blue. No color preferences.
- **Chrome**: no policy: BrowserThemeColor would take it out of GTK mode.
- **libadwaita's accent setting** stays `teal` (`gnome.accent`): it only feeds the portal and
  Settings' swatches. Orchis' own `:root` accent wins wherever the theme reaches.

## What a theme change must keep

Each rule says where it is tested: **P** `task palette` (or the generator named), **L** `task
lint`, **H** the image's harness (`lf:` checks), **N** its needles.

| Rule | | Test |
|---|---|---|
| C1 | Every color is `palette.toml`'s, or white, black or the accent at an alpha over one | L |
| C2 | Text and marks meet WCAG 2.2 on every surface they are drawn on | P |
| C3 | Full accent only on marks and on the one primary action per view, solid; other areas larger than a mark are a tint, labelled in `accent_text` | P, H |
| C4 | Muted text never on a tint | H |
| C5 | One selection alpha: 25% dark, 20% light | P, H |
| C6 | Every copy of the palette (Orchis' SCSS, Bibata's table) is the current one | L |
| C7 | The accent's alpha is a token: `$tint`, `$tint-hover`, `$tint-active`, `$selection-alpha`, `$tint-decoration`, `$tint-track`; no `lighten`, `darken`, `transparentize` or `mix` of it | L |
| C8 | An accent ring means focus only; selection on imagery is a frame in `text` plus the check badge | H |
| C9 | No meaning by hue alone: a status color comes with an icon or a shape | H (review) |
| C10 | Light lines are `light.muted` at the line alphas (divider 20%, border 30%, ring 40%) | L, H |
| C11 | Light: a tint that marks a state carries the border line inside it; the navigation sidebar's selection is the sheet | P, H |
| P1 | Pairs that carry meaning meet their perceptual tier, as drawn and in every view (Perception) | P |
| S1 | The top bar and the dock: opaque `g`, the 1px ring all round | H |
| S2 | Menus, popovers, notifications, tooltips, OSDs, dialogs: `h`, the ring, a shadow by level | H |
| S3 | A dark GTK window is `f` with an outer 1px ring; its headerbar and views `g` | H |
| S4 | The overview, the app grid, the lock and login ground: `brand.boot` | H |
| S5 | A light window is `c` on the desk with the ring line; its sidebar the shelf | H |
| S6 | The light headerbar always draws the border rule, one line across both panes; no gradient shade | H |
| E1 | Edges: the ring 1.5:1 on `e`, 1.2:1 on `h`; `h` on `e` 1.25:1; light border on `c` 1.4:1 | P |
| E2 | Both bars' edge shows over every wallpaper, dark and light | H |
| E3 | Two surfaces that meet below tier E have a ring or a rule between them: dark's window ring, the sidebar's separator and the headerbar rule; light's ring, pane separator and view edges | P, H |
| E4 | Light views on `c` or the shelf always have the border line at their edge | H |
| E5 | Light edges: `c` on the desk 1.15:1, the shelf against `c` and the desk 1.07:1, the sheet on the shelf 1.15:1, the ring line 1.6:1, the border line 1.45:1, the divider 1.25:1 | P |
| F1 | Every focusable shell control shows focus as `inset 0 0 0 2px` accent, calendar days included; popup-menu items are exempt (hover is focus). Today is `accent_text` at 700, never a ring | H |
| F2 | GTK's focus outlines are the accent | H |
| R1 | Radii 9 / 15 / 24 / pill, concentric | P, H |
| R2 | GTK cards and boxed lists 12, alert dialogs 18 | H |
| SP1 | Spacing on 3 / 6 / 12 / 18 / 24 | P |
| SP2 | Both bars 6px from the edge; the top bar 36px, the dock 44px | H |
| T1 | The shell's `stage` is 1em; every size under it in `em` | H |
| T2 | Weights 400 and 700 only, in the shell and in GTK (TY1) | L, H |
| TY4 | Preference groups: 12px from the header to its list, 24px between groups | H |
| T3 | No font or rendering keys in the image; fontconfig maps the generic families to Adwaita Sans and Mono | H |
| X1 | Ghostty's and VS Code's themes come from `palette/` | P, H |
| X2 | Every visible app's icon resolves in Tela or a brand tile; no absolute `Icon=` | H |
| X3 | Firefox's `Orchis-Construct` link; Chrome without a theme policy | H |
| W1 | The default wallpaper's mark centre is at 0.4222 of the height; quiet keeps it | P (`task wallpaper`) |
| W2 | Every wallpaper variant is calmer than its mode's default: lower outline contrast, no more coverage; every line ΔE00 3 from its ground | P (`task wallpaper`) |
| W3 | Light wallpapers draw in the ink's hue, not cyan, except the mark | P (`task wallpaper`) |
| - | Anything that changes the picture at all | N |

## Checks

| Check | Where | What it holds |
|---|---|---|
| `task palette` | brand | contrast of every pair, the tints, the selection, the edges (dark and light), the shell's resting fill, the terminal's colors; ΔE00 per tier under colour-vision deficiencies, IPS and dim panels; the desk and shelf as steps of `d`; whole-pixel radii and an ascending grid |
| `task wallpaper` | brand | each variant calmer than its mode's default, quiet's levels, the mark's centre, light in ink |
| `task lint` | brand, over the forks checked out beside it | a color no palette writes, the accent at an alpha that is not a token (C7), an exception nothing needs, a stale copy of the palette |
| harness `lf:` | spin-desktop's image test | St's computed styles through eval, pixel probes inside the chrome's extents, the CSS and gsettings in the guest |
| needles | spin-desktop's image test | whether any view changed at all |

## What `palette/` holds

| File | For |
|---|---|
| `construct.css` | `preview.html`'s custom properties: dark under `:root`, light under `prefers-color-scheme` or any element marked `data-mode="light"`; GNOME Shell's, `--shell-*`, dark in both; per mode the tints (`--tint`, `--tint-hover`, `--tint-active`, `--selection`, `--tint-deco`, `--tint-track`), the ground (`--desk`, `--shelf`: `e` and `f` in dark), the lines (`--line-divider`, `--line-border`, `--line-ring`; dark's solid border), `--tint-edge` (light's line inside a state, transparent in dark) and the terminal's (`--term-0` ... `--term-15`, `--term-bg`, `--term-fg`, `--term-selection`); the radii and `--inset` |
| `construct.scss` | Orchis: `$construct-light`/`$construct-dark`, `$construct-bg-a` ... `-h`; per variant the border, semantic colors, `accent-text`, text, muted and on-accent; `$construct-boot`, `$construct-ink`; the tints, selection, `$construct-tint-decoration-*` and `$construct-tint-track-*`; the light variant's `$construct-desk`, `$construct-shelf` and `$construct-lines` (divider, border, ring); the radii and the inset |
| `perception.js` | `preview.html`'s Perception table: every perceptual pair, its ΔE00 per view and its verdict |
| `simulate.js` | `preview.html`'s "See as": the deficiencies and panels of the checks as SVG filters |
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
theme's running dot; its focus highlight (the rest tint, 18%: the focused app is selected) and
tilingshell's `window-border-color` (the accent: it marks focus) are dconf keys in the image's
`00-construct`.

**Vitals, caffeine, clipboard-indicator, appindicator, dash-to-panel, tilingshell**: GNOME Shell
51 only; the shell theme draws them.

**The image** (spin-desktop): the dconf defaults that tie it together - `gtk-theme` and the shell
theme Orchis-Construct-Dark, `icon-theme` Tela-dark, `cursor-theme` Bibata-Modern-Construct,
`accent-color` = `gnome.accent`, `color-scheme` = `prefer-dark`, the four wallpaper pairs and
`construct.xml` (the default stays `construct-*`) - the Plymouth theme from `plymouth/`,
`palette.json`, Ghostty's themes and VS Code's extension. The fonts in
`type` are GNOME's and Ghostty's defaults: GTK takes them from gsettings; browsers and Electron ask
fontconfig, which the image maps to Adwaita Sans and Adwaita Mono (56-construct.conf) ahead of
Noto.
