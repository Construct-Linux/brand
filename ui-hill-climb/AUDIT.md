# Audit, round 0: the desktop

Baseline: the needles approved for os main (Construct-Linux/needles 81a8d56), captured by the
harness on the USB stick at 2880x1800, 200%. Each finding names the screen it is seen on.

## Broken

- **shell-notifications**: the stacked notification group draws the card behind through the top
  one: "Connected" over "Disk almost full", "Just now" twice, two close buttons. The cards are
  translucent, so a stack reads as a smear. The needle approving it hid a defect, which lf
  measured nothing about.

## Structural

- **Top bar (every screen)**: everything but the logo sits in one right-hand cluster of ~12 items:
  date, clock, three Vitals readings with their own icons, clipboard, tiling, then the system
  icons. Nothing is centred and nothing is grouped, so the clock, the one thing everyone reads,
  has the weight of a network counter. Vitals' live numbers (`45%`, `0.8`, `33 KB/s`) move at rest
  in a bar that should be quiet.
- **Dock and app grid (desktop, shell-app-grid)**: icons from three families side by side: Tela's
  teal glyph-on-folder (Files, Software, Construct), upstream full-colour (Chrome, Calendar, VS
  Code, Contacts, Weather, Music), and flat blue (Ptyxis, Settings). The teal identity reads as
  one more style, not the system's.
- **System Monitor**: CPU1..4 in red, orange, yellow, green and memory in red: status colours used
  as decoration, so "red" means "the first CPU". The palette has roles; the app's colours do not
  use them.
- **The Construct app**: the explanatory text under "Security keys" is small and low-contrast, and
  the page is a narrow column in a wide window with two thirds empty.
- **installer**: the empty state (no disk) is a large grey logo and one line; it does not say what
  to do next, which is the only thing a person needs there.

## Systemic

- **Light mode (desktop-light, gtk-dialog-light)**: the top bar and dock stay dark over a light
  wallpaper and light windows: two schemes on one screen. The light wallpaper's room is grey on
  grey, low enough contrast to read as a smudge.
- **Window chrome (org.gnome.Settings, Nautilus, Ghostty, SystemMonitor)**: headerbar, sidebar and
  content share nearly one surface; separation leans on hairlines. Acceptable, but the sidebar's
  selected row (accent fill + accent text) is the loudest element of every window.
- **App grid**: labels truncate ("Google Chr...", "Install Con...") at a width the screen could
  afford; two tiny workspace thumbnails float above the grid with no purpose at rest.
- **Calendar drawer (shell-calendar)**: "Clear" with nothing to clear is still drawn, dim; the
  empty state's bell and "No Notifications" are the heaviest elements of the drawer.

## Cosmetic

- **Dock**: the running-app dot and the hover/active fill differ between the Files and Settings
  states (desktop vs org.gnome.Settings).
- **Ghostty**: the headerbar's grid button (tab overview) and title "~" are the only content of a
  tall bar.
- **Lock prompt**: the user is "Live session" with a generic avatar: acceptable on the stick,
  generic once installed.

## Generic tells

The wallpaper's room is the one strong identity mark, and it is good: thin, technical, the
product's. Around it the shell is stock GNOME with Dash to Panel's floating dock and a teal
accent; nothing of the brand reaches the top bar, notifications or quick settings beyond colour.
