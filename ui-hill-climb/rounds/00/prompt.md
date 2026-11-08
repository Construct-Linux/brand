You are reviewing the UI of a real product. You cannot and must not modify any file.

Product: CONSTRUCT, a Linux desktop for software developers: GNOME 51 on a read-only, verified
system image (Wolfi), with its own theme (an Orchis fork in CONSTRUCT's colours), icons (a Tela
fork), the Dash to Panel dock, Vitals in the top bar, and its own wallpaper of an open wireframe
"room". The people who use it are developers working all day in a terminal, an editor and a
browser, on laptops with HiDPI screens, mostly in dark mode. Top workflows: launching and switching
apps (top bar, dock, overview, app grid), reading the system's state at a glance (clock, quick
settings, notifications), working in windows (terminal, files, settings), and locking/unlocking.
Screenshots are 2880x1800 at 200% scale, shown halved.

Direction constraints: the brand is the wireframe room, a teal accent and a quiet, technical
character ("the workspace. the image, verified."); the system should feel calm at rest. The
rubric's "responsive" here means how the design holds across light and dark and across display
scales, not phone layouts.

Attached:
- Reference products in the same category (ref-*.png, ref-*.jpg): the bar for a 10. Some show the
  screen inside a device frame; judge the screen.
- Single screens (cNN.png) to score on their own. There are no pairs this time: answer "pairs" with
  an empty array.

Tasks:
1. For the cNN set as a whole, score each rubric category 1-10, where 10 is the best reference
   product in the set, not perfection. Give the same scores as "scores" and as "control".
   hierarchy: what matters most is seen first, on every screen.
   typography: scale, weights, line length, legibility of data and identifiers.
   spacing: a consistent scale, alignment to a grid, no orphaned gaps.
   color: semantic roles, contrast, restraint; status colours mean one thing.
   consistency: the same thing looks and behaves the same everywhere.
   density: information per screen fit for the audience; neither cramped nor padded.
   usability: navigation, discoverability, affordances, state feedback.
   polish: edges, states, icons, details a careful team would fix.
   responsive: how the design holds across light/dark and display scales.
   identity: feels purpose-built for this product and audience, not a generic template.
2. List concrete findings: screen id (cNN), location on the screen, the problem, and the fix.
   Prefer structural problems over cosmetic ones. No generic advice.

Judge only what is visible. Answer with JSON matching the attached schema and nothing else.
