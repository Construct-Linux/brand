# CONSTRUCT

The identity and boot animation of **CONSTRUCT**, a Linux desktop for developers built on Wolfi:
a read-only, verified base image with A/B updates and automatic rollback, and GNOME on top.

**[See the desktop with the palette](https://construct-linux.github.io/brand/)** - `preview.html`,
published by GitHub Pages from `main`
([dark](https://construct-linux.github.io/brand/preview.html?mode=dark),
[light](https://construct-linux.github.io/brand/preview.html?mode=light)).

The idea: **the image does not move; the workspace does.** The open room has two layers with
fixed roles:

- **The outline** (the logo's mark) is the stable base. It is drawn early, in a single gesture
  from the corner (each line leaves from one already drawn; the edges hang from the top one),
  and from frame 7 it stays fixed, at full intensity, to the end.
- **The inner grid** is the workspace: finer and dimmer, it is built inside the outline, comes
  alive, breathes while the system waits, and goes out at the end. It never touches or changes
  the outline.

The sequence (48 frames, 1080×1080; the preview video lasts 5 s at 9.6 fps) has three parts:

| Part | Frames | What happens |
|---|---|---|
| intro | 1–26 | the outline (closed at 7), CONSTRUCT (complete at 10), the grid drawn and lit |
| wait | 27–38 | the grid breathes, evenly and without direction; it repeats seamlessly for as long as needed |
| outro | 39–48 | the grid goes out; the mark and the word remain: the logo |

Nothing is tied to the boot's real state, so nothing pretends to show progress or verification:
the intro is choreography of fixed length and the wait goes nowhere. If the boot ends during the
intro, the brand is already recognizable from the first second. The tagline is not on the splash.

The tagline is set in lowercase, on two lines:

> the workspace.<br>
> the image, verified.

First the space you work in, then the verified base that holds it up. It is used in the
distribution's presentation and identity pieces.

## Requirements

[Task](https://taskfile.dev) and Docker. Every generator runs in the image the `Dockerfile`
describes - Python 3.13 by digest, pinned `numpy`, `opencv-python-headless` and `pillow`
(`requirements.txt`), and `pngquant` from a dated Debian snapshot - so the same sources make the
same images on any machine. `task image` builds it; every task that needs it builds it first.

## Usage

| Command | What it does |
|---|---|
| `task` / `task all` | **Everything**: frames, video, sprite, compressed Plymouth frames, logo, palette and wallpapers |
| `task generate` | Renders `frames/construct_01.png` … `construct_48.png` |
| `task encode` | Builds `construct.mp4` (5 s) from the frames |
| `task play` | Opens `construct.mp4` in this machine's video player |
| `task sprite` | Builds `sprite.png`: an 8×6 grid of the 48 numbered frames |
| `task plymouth` | Transparent PNGs per frame for Plymouth in `plymouth/`, compressed with pngquant |
| `task logo` | The logo in `logos/`: SVG in color, mono, GNOME symbolic and Orchis' Activities button, PNG from 16 to 512 px, and `preview.png` |
| `task palette` | Checks `palette.toml`'s contrast and writes it for the theme forks into `palette/` ([THEMING.md](THEMING.md)) |
| `task wallpaper` | The desktop backgrounds, dark and light, at 4K into `wallpapers/` |
| `task preview` | Opens `preview.html`: the desktop with the palette, in dark and light; GitHub Pages publishes it from `main` |
| `task compress` | Runs pngquant over `plymouth/*.png` again, replacing the files |
| `task check` | Fails if the committed `plymouth/`, `logos/`, `wallpapers/` and `palette/` are not what the sources make |
| `task clean` | Removes `frames/`, `construct.mp4` and `sprite.png` |

`plymouth/`, `logos/`, `wallpapers/` and `palette/` are committed - they are what the
distribution takes - and `task check` holds them to the sources: it regenerates them and compares
each image over black, within a small tolerance (OpenCV picks its vector code by processor, and
pngquant's palette follows the pixels), and the SVGs and the palette byte for byte. After
changing `video.py`, `room.py`, `plymouth.py`, `logo.py`, `wallpaper.py`, `palette.toml` or the font, run
`task plymouth logo palette wallpaper` and commit the result. The video and the sprite are previews,
not committed.

Each task runs the ones it needs first (`play` → `encode` → `generate` → `image`) and skips the
ones that are up to date.

Variables that can be changed:

```sh
task encode DURATION=8                   # same number of frames, slower
task generate FRAMES_DIR=out
task sprite COLS=12                      # a 12-column grid
task plymouth SIZE=800                   # Plymouth frames at 800 px
task plymouth QUALITY=65-85              # more aggressive pngquant
```

## Scripts

- `video.py [dir] [frame ...]`: renders every frame, or only the indexes given (from 0), e.g.
  `python video.py out 0 47`.
- `encode.py [dir] [out.mp4] [seconds]`: joins the PNGs into an mp4 with fps = frames / seconds.
- `plymouth.py [dir] [out] [colors]`: turns the frames into transparent paletted PNGs
  (`colors=0`: full RGBA).
- `sprite.py [dir] [out.png] [columns] [px]`: puts every frame into one image (8 columns and
  270 px thumbnails by default).
- `logo.py [out_dir]`: the logo files and the preview sheet.
- `palette.py [out_dir]`: checks the palette's contrast and writes it out; `palette.load()` is what
  the other generators read the colors from.
- `wallpaper.py [out_dir] [width] [height]`: the dark and light desktop backgrounds.
- `room.py`: the room, its camera and its lines, which `video.py`, `wallpaper.py` and `logo.py`
  all draw.
- `check.py <committed_dir> <regenerated_dir>`: compares two sets of images over black.

## Plymouth

`task plymouth` makes one PNG per frame, split by part (each numbered from 1):

- `intro-0001.png` … `intro-0026.png`: played once at the start.
- `loop-0001.png` … `loop-0012.png`: repeated while the system boots; the last frame joins the
  first.
- `outro-0001.png` … `outro-0010.png`: played once at the end; its last frame is the logo.
  Plymouth hands the screen to the login screen as soon as the boot is done, so the
  distribution plays the outro when the disk asks for its password, with the prompt under the
  logo.
- If the boot ends before the intro does, the cleanest thing is to show `outro-0010.png` (the
  logo) directly instead of jumping into the middle of the sequence.

Format:

- One PNG per frame, with no numbers or borders, on a **transparent background**: Plymouth puts
  the black behind it.
- Drawn at their final size (`SIZE`, 1080 by default; 800 at least) rather than scaled.
- Made as lossless RGBA (~4.6 MB) and compressed in place by `pngquant` (`--quality 80-95`,
  variable `QUALITY`): ~1.7 MB for the 48 frames at 1080 px (~34 KiB a frame; the grid is in
  almost all of them). They go into the boot's initrd, which the firmware reads from the disk
  before anything else, so every kilobyte is in the boot time.
- Without pngquant, `plymouth.py frames plymouth 256` makes its own palette (~1.1 MB, a little
  less faithful).

## Font

The word uses **Audiowide**, under the SIL Open Font License 1.1: it may be used, embedded in
images and redistributed with the distribution. The file is in the repository
(`fonts/Audiowide-Regular.ttf`, license in `LICENSES/OFL-1.1.txt`), so nothing needs installing
and it comes out the same on any machine. "Audiowide" is a Reserved Font Name: the file is used
as it is; if the font is ever modified, it must be renamed. The same font and spacing are used in
the animation and the logo; in both the word is as wide as the edge of the floor above it.

To try another font:

```sh
FONT=/path/Font.ttf task generate
```

The path must be inside the repository: the generators run in a container that only sees it.

## License

- The artwork - the logo (`logos/`), the animation's frames (`plymouth/` and what `task`
  generates), the wallpapers (`wallpapers/`), the palette and the tagline - is under the Creative Commons Attribution-ShareAlike 4.0
  International license (`LICENSES/CC-BY-SA-4.0.txt`).
- The scripts, `preview.html`, the `Taskfile.yml` and the `Dockerfile` are under the MIT license
  (`LICENSES/MIT.txt`).
- The Audiowide font is under the SIL Open Font License 1.1 (`LICENSES/OFL-1.1.txt`).
