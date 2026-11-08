# Direction: the desktop, round 1

What the round-0 council (Codex, Claude Sonnet, Claude Opus as a design-system reviewer; Gemini's
quota was out) agreed on, and what the climb changes. Baseline: median 6, consistency, polish and
responsive 5, identity 7; a reviewer's two passes on the same images differ by at most 1 (Codex 2
once), so a gain of 1 is noise.

THEMING.md's system stays: one palette, `task palette`'s contrast and perception gates, the
elevation table. Every change below is a token or a rule in it, made once and taken by the forks,
not a per-screen override.

## What stays, and why

- **The room** as the one identity mark. The council scored identity highest (7) and asked for
  more of it, not less.
- **Dark first**, the cyan accent, Adwaita Sans and Mono, the spacing grid and radius steps.
- **The top bar's Vitals readings**: the harness freezes them at `00` for comparable captures
  (cmd/image test.go holdReadings), which three reviewers took for a fault. Not a product
  finding; the prompt now says so.

## What changes

1. **Notifications are opaque, and a stack reads as one.** Level-2 surfaces in the shell are
   drawn without alpha: the group behind shows only as edges below the top card, never through
   it (broken on shell-notifications for all three reviewers). A banner does not open over the
   date menu.
2. **Active is a fill, inactive is a surface.** Quick settings' on state is the accent filled
   with `on_accent` text, not a tint with accent text: the two states differ in luminance, not
   only in hue (shell-quick-settings, three reviewers). The same rule for the calendar's today.
3. **Secondary text reads.** `muted` rises to the 7:1 body-text tier on its surfaces wherever it
   carries an explanation (the Construct app's page text, the installer's message): muted is for
   metadata, not for the sentence that explains the page (three reviewers each).
4. **Light is light.** The top bar and dock follow the scheme: in light, `a` with light's line as
   their ring, the shell's popovers too, so a light screen has one scheme (desktop-light,
   gtk-dialog-light, three reviewers). THEMING.md's "g, opaque" in both modes is this round's
   hypothesis to beat, not a rule kept by default; the pairwise vote decides.
5. **The light room is the brand's.** The light wallpaper's lines take `light.accent` at the
   weight the dark one has, not grey on grey (desktop-light, three reviewers).
6. **Status colours mean status.** Data series (System Monitor's CPUs, memory, network, disk)
   take the accent and neutral tints; red, amber and green are left for thresholds (three
   reviewers).

## Not this round

- **Icons** (dock and grid mixing Tela, upstream colour and flat): the forks' area, next.
- **Empty and error states** (the installer's no-disk message, the empty notification column):
  copy and an action, which are the product's, in the installer and the shell theme after the
  slice is judged.
- **The top bar's order and grouping**: Dash to Panel's and Vitals' configuration, with the forks.

## The slice

Three screens judged against the baseline before anything spreads: **shell-notifications**
(dense, broken today), **desktop-light** (overview, the light scheme and the room), and
**io.github.construct_linux.Construct** (a form-like page and muted text). Then the council on the
whole set.
