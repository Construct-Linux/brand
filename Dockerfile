# Where every image of the brand is generated: the same Python, libraries and pngquant on every
# machine, so what is committed (plymouth/, logos/) comes from the sources and not from whatever
# a laptop had installed. task builds it (task image) and runs every generator in it.
# Python 3.13 on Debian trixie, by digest; pngquant from the Debian archive as it stood on the
# snapshot date.
FROM python:3.13-slim-trixie@sha256:7c61056e61ac89e852de05f3dc6fa51a6dd2181797bceed46aa725dd7cb2cd3b

ARG DEBIAN_SNAPSHOT=20260914T000000Z
RUN rm -f /etc/apt/sources.list.d/debian.sources && \
    printf 'Types: deb\nURIs: http://snapshot.debian.org/archive/debian/%s\nSuites: trixie\nComponents: main\nSigned-By: /usr/share/keyrings/debian-archive-keyring.gpg\nCheck-Valid-Until: no\n' \
        "$DEBIAN_SNAPSHOT" > /etc/apt/sources.list.d/snapshot.sources && \
    apt-get update && apt-get install -y --no-install-recommends pngquant && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
