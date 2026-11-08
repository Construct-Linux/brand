#!/usr/bin/env python3
"""Builds a council's blind image set for one round and one batch of screens.

council.py ROUND BATCH --screens id,id,... [--candidate DIR] [--control id,id,...]

Without --candidate (round 0), every screen is a single cNN image to score. With it, each screen
is a pair sNN-a/sNN-b of round 00 and the candidate, sides at random, and --control's screens are
round 00's images again as cNN. Images are halved to 1440x900: the reviewers judge layout and
colour, and the full 2880x1800 costs four times the tokens for detail the harness's lf measures.
The key (which image is which) goes to rounds/ROUND/council-key-BATCH.json, outside the
directory the reviewers read. References are copied as they are named.
"""
import argparse
import json
import random
import shutil
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent


def half(src: Path, dst: Path) -> None:
    Image.open(src).convert("RGB").resize((1440, 900), Image.LANCZOS).save(dst, optimize=True)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("round")
    p.add_argument("batch")
    p.add_argument("--screens", required=True)
    p.add_argument("--candidate")
    p.add_argument("--control", default="")
    p.add_argument("--refs", default="")
    a = p.parse_args()

    rnd = HERE / "rounds" / a.round
    out = rnd / f"council-{a.batch}"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    base = HERE / "rounds" / "00" / "shots"
    key = {"pairs": {}, "control": {}}
    rng = random.SystemRandom()

    n = 0
    for sid in a.screens.split(","):
        n += 1
        if a.candidate is None:
            half(base / f"{sid}.png", out / f"c{n:02d}.png")
            key["control"][f"c{n:02d}"] = sid
            continue
        cand = Path(a.candidate) / f"{sid}.png"
        sides = ["baseline", "candidate"]
        rng.shuffle(sides)
        for side, which in zip("ab", sides):
            half(base / f"{sid}.png" if which == "baseline" else cand, out / f"s{n:02d}-{side}.png")
        key["pairs"][f"s{n:02d}"] = {"screen": sid, "a": sides[0], "b": sides[1]}
    for sid in filter(None, a.control.split(",")):
        n += 1
        half(base / f"{sid}.png", out / f"c{n:02d}.png")
        key["control"][f"c{n:02d}"] = sid
    for ref in filter(None, a.refs.split(",")):
        src = HERE / "references" / ref
        shutil.copy(src, out / src.name)
    (rnd / f"council-key-{a.batch}.json").write_text(json.dumps(key, indent=1) + "\n")
    print(out)


if __name__ == "__main__":
    main()
