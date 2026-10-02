# CONSTRUCT

Animación de 48 frames (1080×1080): una habitación en wireframe cian que se dibuja sola, una entrada en la pared derecha cuyo marco se enciende y el texto **CONSTRUCT**. El video final dura 5 s (48 frames a 9.6 fps).

La animación va de menos a más: el contenido se dibuja a lo largo de los 48 frames y, a la vez, el color pasa de un turquesa apagado a cian saturado y el brillo del neón crece hasta el último frame (`intensity()` en `video.py`).

## Requisitos

- Python 3 y [Task](https://taskfile.dev) (`brew install go-task` o ver la web)
- El resto se instala con:

```sh
task deps
```

`task deps` ejecuta dos tareas:

- `task setup`: crea `.venv` e instala `requirements.txt` (`numpy`, `opencv-python`, `pillow`).
- `task font`: instala **DejaVu Sans**, la fuente por defecto de Plymouth, con el gestor de paquetes del sistema (`apt`, `dnf`, `pacman`, `zypper` o `brew`). Si la fuente ya está, no hace nada. En Linux pide `sudo`.

## Uso

| Comando         | Qué hace                                                   |
|-----------------|------------------------------------------------------------|
| `task generate` | Renderiza `frames/construct_01.png` … `construct_48.png`   |
| `task encode`   | Arma `construct.mp4` (5 s) a partir de los frames          |
| `task play`     | Reproduce `construct.mp4` en bucle (`q` / `Esc` para salir) |
| `task sprite`   | Arma `sprite.png`: grilla 8×6 con los 48 frames numerados  |
| `task clean`    | Borra `frames/`, `construct.mp4` y `sprite.png`            |

Cada tarea ejecuta antes las que necesita (`play` → `encode` → `generate` → `deps`) y se salta las que ya están al día.

Variables que se pueden cambiar:

```sh
task play PYTHON=python3                 # usar otro intérprete en vez de .venv
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

`video.py` busca `DejaVuSans-Bold.ttf` en las rutas habituales de Debian/Ubuntu, Fedora/RHEL, Arch y openSUSE. Para usar otra ruta:

```sh
FONT=/ruta/DejaVuSans-Bold.ttf task generate
```
