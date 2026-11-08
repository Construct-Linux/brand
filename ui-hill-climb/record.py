#!/usr/bin/env python3
"""Un-blinds one round's reviews of one batch and appends them to ledger.jsonl.

record.py ROUND BATCH [--kind full|single]

Each reviewer's answer: Codex writes the schema's JSON itself; Claude and Antigravity put it in
the result's structured_output. Pair winners become baseline/candidate through the batch's key,
screen ids become screen names. A reviewer whose answer does not parse is reported and left out. HILL_ROOT names
another review's directory, as for council.py.
"""
import argparse
import os
import json
import sys
from pathlib import Path

HERE = Path(os.environ.get("HILL_ROOT") or Path(__file__).resolve().parent).resolve()


def answer(path: Path):
    text = path.read_text().strip()
    if not text:
        raise ValueError("empty")
    data = json.loads(text)
    if isinstance(data, dict) and "structured_output" in data:
        data = data["structured_output"]
        if isinstance(data, str):
            data = json.loads(data)
    if not isinstance(data, dict) or "scores" not in data:
        raise ValueError("no scores in the answer")
    return data


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("round")
    p.add_argument("batch")
    p.add_argument("--kind", default="full")
    a = p.parse_args()
    rnd = HERE / "rounds" / a.round
    key = json.loads((rnd / f"council-key-{a.batch}.json").read_text())
    names = {k: v["screen"] for k, v in key["pairs"].items()} | key["control"]
    rows = []
    for reviewer in ("codex", "claude", "opus"):
        path = rnd / f"review-{a.batch}-{reviewer}.json"
        try:
            ans = answer(path)
        except (OSError, ValueError) as e:
            print(f"{reviewer}: left out: {e}", file=sys.stderr)
            continue
        pairs = []
        for pr in ans.get("pairs", []):
            k = key["pairs"].get(pr["screen"])
            if k is None:
                continue
            winner = "tie" if pr["winner"] == "tie" else k[pr["winner"]]
            pairs.append({"screen": k["screen"], "winner": winner, "reason": pr["reason"]})
        findings = []
        for f in ans.get("findings", []):
            sid = f["screen"].split("-")[0]
            findings.append({**f, "screen": names.get(sid, f["screen"])})
        rows.append({"round": int(a.round), "reviewer": reviewer, "batch": a.batch, "kind": a.kind,
                     "scores": ans["scores"], "control": ans.get("control") or {},
                     "pairs": pairs, "findings": findings})
    with open(HERE / "ledger.jsonl", "a") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"{len(rows)} reviews recorded")


if __name__ == "__main__":
    main()
