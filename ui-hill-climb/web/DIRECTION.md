# Direction: the site, round 1

What the round-0 council (Codex, Claude Sonnet, Claude Opus as a designer of design-system sites;
the same weaker, two-family council as the desktop's) agreed on, and what the climb changes.
Baseline: median 6, usability 4 for both Claude reviewers, identity 8-9; a reviewer's two passes
on the same images differ by 1.5 at most, so a gain of 1 is noise.

The site speaks the desktop's language rather than a marketing site's: every colour is a token of
`palette/construct.css`, the accent keeps THEMING.md's seven meanings (a link is level 6, the
section in view is level 3, focus is the 2px ring), and the type steps are libadwaita's. No value
of its own, no palette change.

## What stays, and why

- **The drawings, as large as the layout allows.** Identity scored 8-9 from everyone; the
  drawings are the evidence and the reason to visit.
- **Dark first, the cyan, Audiowide for the wordmark only, Adwaita Sans for the rest.**
- **Every fact and number**: the notes, the comparison's figures, the perception table, the
  repository table. The page's content is THEMING.md's, said with pictures.

## What changes

1. **The page is a GNOME window.** A sidebar on the shelf (f in dark) holds the wordmark, the
   three controls with their names (Mode, See as, Wallpaper) and the sections; the section in view
   is the sidebar's selected place, drawn exactly as the desktop draws one (the tint in dark, the
   white sheet in light). Below 1100px the sidebar becomes the page's head: controls in a row,
   sections as a sideways row of chips. (No title, no index, unlabelled pills: three reviewers.)
2. **A title and a lead.** An `h1`, one paragraph saying what CONSTRUCT is and what the page
   shows, the tagline, and the links to the source and THEMING.md. The surface letters (a-h) are
   defined once there.
3. **Sections are headed.** Real `h2`s at libadwaita's Title 1 (26px, 700), a rule and 56px
   between sections; every drawing has its own heading or caption before it, never after.
4. **The drawings keep their proportions on a phone**: at 720px wide inside a sideways scroller
   (focusable when it scrolls), rather than a 390px thumbnail with 9px labels and a cut prompt.
5. **Comparisons name their columns**: the accent scale's two columns and the comparison's three
   carry headers on a wide screen and a label on each card on a phone.
6. **The perception table fits**: at its own height with a header that stays, the views named as
   the note names them, every column inside the box at 1440; on a phone each pair is a card.
7. **Assets are assets**: the wallpapers at twice the size, each picture a link to its file, file
   names and paths in Adwaita Mono.
8. **Accessibility**: one `h1`, headings in order, focusable scrolling regions, labelled groups;
   the 36% tint's failing contrast is the comparison's point and stays (three axe nodes, as in the
   baseline), marked as a picture with its figure in words.

## Not this round

- **The drawings' own content** (the empty window body, the overview's small card): the desktop's
  design, reviewed separately.
- **Copy and download actions** on swatches: a script for a convenience; the hex is selectable.
