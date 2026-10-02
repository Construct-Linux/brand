# CONSTRUCT

Animación de 48 frames (1080×1080): una habitación en wireframe cian que se dibuja sola, una puerta que se ilumina y el texto **CONSTRUCT**. El video final dura 5 s (48 frames a 9.6 fps).

## Requisitos

- Python 3 con `numpy`, `opencv-python` y `pillow`
- [Task](https://taskfile.dev) (`brew install go-task` o ver la web)
- Fuente **DejaVu Sans**, la que usa Plymouth por defecto:
  - Debian/Ubuntu: `apt install fonts-dejavu-core`
  - Fedora/RHEL: `dnf install dejavu-sans-fonts`
  - Arch: `pacman -S ttf-dejavu`

```sh
python3 -m venv .venv
.venv/bin/pip install numpy opencv-python pillow
```

## Uso

| Comando         | Qué hace                                                   |
|-----------------|------------------------------------------------------------|
| `task generate` | Renderiza `frames/construct_01.png` … `construct_48.png`   |
| `task encode`   | Arma `construct.mp4` (5 s) a partir de los frames          |
| `task play`     | Reproduce `construct.mp4` en bucle (`q` / `Esc` para salir) |
| `task sprite`   | Arma `sprite.png`: grilla 8×6 con los 48 frames numerados  |
| `task clean`    | Borra `frames/`, `construct.mp4` y `sprite.png`            |

Cada tarea ejecuta antes las que necesita (`play` → `encode` → `generate`) y se salta las que ya están al día.

Variables que se pueden cambiar:

```sh
task play PYTHON=.venv/bin/python        # usar el venv
task encode DURATION=8                   # mismo número de frames, más lento
task generate FRAMES_DIR=out
task sprite COLS=12                      # grilla de 12 columnas
```

## Scripts

- `video.py [dir] [frame ...]`: renderiza todos los frames, o solo los índices que se le pasen (desde 0), p. ej. `python3 video.py out 0 47`.
- `encode.py [dir] [out.mp4] [segundos]`: une los PNG en un mp4 con fps = frames / segundos.
- `play.py [video]`: reproduce el video en bucle.
- `sprite.py [dir] [out.png] [columnas] [px]`: une todos los frames en una sola imagen (por defecto 8 columnas, miniaturas de 270 px).

## Fuente

`video.py` busca `DejaVuSans.ttf` en las rutas habituales de Debian/Ubuntu, Fedora/RHEL, Arch y openSUSE. Para usar otra ruta:

```sh
FONT=/ruta/DejaVuSans.ttf task generate
```
