"""Run the ledger's rules and audit the roll. `uv run python -m ledger.check`

Exit 1 on a red nobody expects, an expectation whose red is gone, or an entry that left
the record without a tombstone.
"""

from __future__ import annotations

import sys
from pathlib import Path

from quern import reckon, run_rules
from quern.roll import audit, write

from ledger.tree import build

_ROOT = Path(__file__).resolve().parents[1]
_ROLL = "ledger/roll.json"


def main() -> int:
    quern = build()
    results = run_rules(quern)
    news, carried, stale = reckon(quern, results)
    excused = {n.payload["was"] for _, n in quern.walk("")
               if n.kind == "tombstone" and n.payload.get("was")}
    removals, looked = audit(quern, _ROOT, _ROLL, "HEAD", excused)
    expected_at = {(r.node, r.rule) for r in carried}
    for r in sorted(results, key=lambda r: (r.ok, r.rule, r.node)):
        mark = "ok  " if r.ok else "red*" if (r.node, r.rule) in expected_at else "RED "
        print(f"{mark}{r.rule}" + (f" @ {r.node}" if r.node else "") + (f" - {r.detail}" if r.detail else ""))
    for line in removals:
        print(f"GONE {line}")
    if not looked:
        print("note: no roll at HEAD - nothing compared for removal (right on the first run)")
    if not removals:
        write(quern, _ROOT / _ROLL)
    print(f"{len(results)} verdict(s), {len(news)} red unaccounted for, {len(carried)} carried, {len(stale)} stale")
    return 1 if (news or stale or removals) else 0


if __name__ == "__main__":
    sys.exit(main())
