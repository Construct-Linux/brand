# Audit, round 0: the site

Baseline: `preview.html` at f1a16cc (`index.html` only redirects to it), served locally and
captured by Playwright at 1440x900 and 390x844 in the browser's dark and light schemes, each shot
scrolled to one section (`screens.json`). Each finding names the screen it is seen on.

## Broken

- **menus.mobile**: at 390 the drawing keeps its 16:9 box and the text inside it a 9px floor, so
  the authentication prompt runs out of the drawing and is cut at its bottom edge; the calendar's
  drawing loses its calendar (hidden below 640px) and is left as an empty desktop with a caption
  that describes what is not there.
- **compare.mobile**: the comparison's column heads ("Shell, on h", "GTK dark, on g", "GTK light,
  on a") stack at the top as three orphan lines, and the cards below no longer say which column
  they were: the comparison cannot be read.
- **perception.desktop**: the table is wider than its box at 1440; the Verdict column is cut at
  "VERDIC" and "ok via rir", with no sign that it scrolls.

## Structural

- **top (every width)**: the page has no title and no sentence saying what it is. The wordmark
  and three unlabelled pill groups are the first thing seen; nothing says CONSTRUCT is a desktop,
  that this is its design language, or links to the project. No `h1`.
- **every section**: section titles are 13px uppercase muted labels, the same weight as a table
  header; on a page this long they do not mark where one subject ends and the next begins. There
  is no table of contents and no way to jump to a section.
- **top.mobile**: the "See as" group wraps inside its pill into a three-line blob; the three
  groups have no label, so "Default / Quiet / Offset / Mark" says nothing about wallpapers.
- **accent (both widths)**: the scale's two columns (the shell, GTK in this mode) carry no
  header; the note above explains them in prose.
- **every drawing on mobile**: the desktop drawings are scaled to 390px, their labels 9px; the
  drawings are the page's main evidence and on a phone they are thumbnails.

## Systemic

- **Notes**: every section opens with one long muted paragraph (up to 7 lines at 75ch) that mixes
  what the drawing shows with the rule behind it; the drawing's caption on the first desktop sits
  below the fold.
- **Rhythm**: sections are 44px apart, the same as the gap between a drawing and its caption in
  places, so the page reads as one stream.
- **Accessibility (axe)**: no `h1`; a heading jump (`h4` inside the Settings drawing); the
  sixteen-colour strip has an `aria-label` on a plain `div`; the perception table and the
  repository table scroll but cannot be focused; the comparison's 36% tint fails contrast, on
  purpose (its point is that it is below 4.5:1), but is not marked as an illustration.
- **End of page**: the page stops after the repository table, with no footer: no source link, no
  licence, though the README names both.

## Cosmetic

- **accent**: the lineup strip under the scale is cut by the fold and its items spread to the
  edges with uneven gaps.
- **identity.desktop**: the cards' captions are 13px muted with a bold title, smaller than the
  table's body under them.

## Generic tells

Few: the wordmark, the room, the cyan and Adwaita Sans are the product's, and the drawings are
specific. What reads as generic is the frame around them: a centred logo over pill groups and a
stack of uppercase labels, with none of the navigation or hierarchy of a design-system site.
