# CONSTRUCT

Identidad y animación de arranque de **CONSTRUCT**, un escritorio Linux para desarrolladores sobre Wolfi: una imagen base de solo lectura, verificada, con actualización A/B y vuelta atrás automática; encima, GNOME.

La idea: **la imagen no se mueve; el espacio de trabajo sí.** La habitación abierta tiene dos capas con roles fijos:

- **El contorno** (el símbolo del logo) es la base estable. Se dibuja temprano, en un solo gesto desde la esquina (cada línea sale de una ya dibujada; los cantos cuelgan del borde de arriba), y desde el frame 7 queda fijo, a intensidad plena, hasta el final.
- **La grilla interior** es el espacio de trabajo: más fina y más tenue, se construye dentro del contorno, se activa, respira mientras el sistema espera y se apaga al final. Nunca toca ni modifica el contorno.

La secuencia (48 frames, 1080×1080; el video de vista previa dura 5 s a 9.6 fps) tiene tres tramos:

| Tramo | Frames | Qué pasa |
|---|---|---|
| intro | 1–26 | contorno (cerrado en el 7), CONSTRUCT (completa en el 10), grilla en trazo y activación |
| espera | 27–38 | la grilla respira, uniforme y sin dirección; se repite sin costura todo lo que haga falta |
| cierre | 39–48 | la grilla se apaga; quedan el símbolo y la palabra: el logo |

Nada está conectado al estado real del arranque, así que nada simula progreso ni verificación: la intro es coreografía de duración fija y la espera no avanza hacia ningún lado. Si el arranque termina durante la intro, la marca ya es reconocible desde el primer segundo. El tagline no va en el splash.

El tagline de identidad se presenta en minúsculas y en dos líneas:

> the workspace.<br>
> the image, verified.

Primero, el espacio donde trabajás; después, la base verificada que lo sostiene. Se usa en la presentación de la distribución y piezas de identidad. La revisión está en `review/comparison.png`.

## Requisitos

- Python 3 y [Task](https://taskfile.dev) (`brew install go-task` o ver la web)
- El resto se instala con:

```sh
task deps
```

`task deps` ejecuta dos tareas:

- `task setup`: crea `.venv` e instala `requirements.txt` (`numpy`, `opencv-python`, `pillow`).
- `task pngquant`: instala `pngquant` de la misma forma.

## Uso

| Comando         | Qué hace                                                   |
|-----------------|------------------------------------------------------------|
| `task` / `task all` | **Todo**: dependencias, frames, video, sprite, frames de Plymouth comprimidos, logo y hojas de revisión |
| `task generate` | Renderiza `frames/construct_01.png` … `construct_48.png`   |
| `task encode`   | Arma `construct.mp4` (5 s) a partir de los frames          |
| `task play`     | Reproduce `construct.mp4` en bucle (`q` / `Esc` para salir) |
| `task sprite`   | Arma `sprite.png`: grilla 8×6 con los 48 frames numerados  |
| `task plymouth` | PNG transparentes por frame para Plymouth en `plymouth/`, comprimidos con pngquant |
| `task logo`     | Propuestas de logo en `logos/`: SVG color y mono, PNG de 16 a 512 px y `preview.png` |
| `task review`   | `review/comparison.png` (momentos clave del splash, logo junto al último frame, tagline de identidad) y `review/sequence.png` (frames por tramo y niveles de luz) |
| `task compress` | Vuelve a pasar pngquant sobre `plymouth/*.png`, reemplazando los archivos |
| `task clean`    | Borra `frames/`, `construct.mp4`, `sprite.png`, `plymouth/` y `logos/` |

Cada tarea ejecuta antes las que necesita (`play` → `encode` → `generate` → `deps`) y se salta las que ya están al día.

Variables que se pueden cambiar:

```sh
task play PYTHON=python3                 # usar otro intérprete en vez de .venv
task encode DURATION=8                   # mismo número de frames, más lento
task generate FRAMES_DIR=out
task sprite COLS=12                      # grilla de 12 columnas
task plymouth SIZE=800                   # frames de Plymouth a 800 px
task plymouth QUALITY=65-85              # pngquant más agresivo
```

## Scripts

- `video.py [dir] [frame ...]`: renderiza todos los frames, o solo los índices que se le pasen (desde 0), p. ej. `python3 video.py out 0 47`.
- `encode.py [dir] [out.mp4] [segundos]`: une los PNG en un mp4 con fps = frames / segundos.
- `play.py [video]`: reproduce el video en bucle.
- `plymouth.py [dir] [out] [colores]`: convierte los frames a PNG transparentes con paleta (`colores=0`: RGBA completo).
- `sprite.py [dir] [out.png] [columnas] [px]`: une todos los frames en una sola imagen (por defecto 8 columnas, miniaturas de 270 px).

## Plymouth

`task plymouth` genera un PNG por frame, separado por tramo (cada uno numerado desde 1):

- `intro-0001.png` … `intro-0026.png`: se reproduce una vez al empezar.
- `loop-0001.png` … `loop-0012.png`: se repite mientras el sistema arranca; el último frame empalma con el primero.
- `outro-0001.png` … `outro-0010.png`: se reproduce una vez al terminar (después de una vuelta completa del loop); el último frame es el logo.
- Si el arranque termina antes de que acabe la intro, lo más limpio es mostrar directamente `outro-0010.png` (el logo) en lugar de saltar al medio de la secuencia.

Formato:

- Un PNG por frame, sin números ni bordes, con **fondo transparente**: el negro lo pone Plymouth.
- Se dibujan directamente al tamaño final (`SIZE`, 1080 por defecto; mínimo recomendado 800), no se escalan.
- Se generan en RGBA sin pérdida (~4.6 MB) y `pngquant` los comprime en el mismo lugar (`--quality 80-95`, variable `QUALITY`): ~1.6 MB los 48 frames a 1080 px (~34 KiB por frame; la grilla está presente en casi todos), pensado para un UKI sin initrd.
- Sin pngquant, `plymouth.py frames plymouth 256` hace una paleta propia (~1.1 MB, algo menos fiel).

## Fuente

La palabra usa **Audiowide**, con licencia SIL Open Font License 1.1: se puede usar, incrustar en imágenes y redistribuir con la distro. El archivo va en el repo (`fonts/Audiowide-Regular.ttf`, licencia en `fonts/OFL.txt`), así que no hace falta instalar nada y sale igual en cualquier máquina. "Audiowide" es un nombre reservado de la licencia: se usa el archivo tal cual; si alguna vez se modifica la fuente, hay que cambiarle el nombre. La misma fuente y el mismo espaciado se usan en la animación y en el logo; en los dos casos la palabra mide lo mismo que el borde del piso que tiene encima.

Para probar otra fuente:

```sh
FONT=/ruta/Fuente.ttf task generate
```
