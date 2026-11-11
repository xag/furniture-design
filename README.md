# furniture-design

Skills and tooling for designing furniture as a beginner: from what you want, to a piece that stands up, fits where it goes, and can be cut and assembled.

This repo holds only the general method. It names no home, no piece and nobody's furniture. A project that designs real furniture keeps that in its own repo and pins this one.

## Sources

A rule enters here from a published source, cited by name and clause. Copies of public-domain sources may be kept here so quotes can be checked offline, for example the USDA Forest Products Laboratory's *Wood Handbook* (FPL-GTR-282) and the Federal Register text of 16 CFR 1261. Copyrighted standards (EN 14749, EN 16121 and EN 16122, ASTM F2057, ANSI/BIFMA X5.9, ANSI/AWI 0641) are cited here and never copied in.

## Design ledger

The decisions this repo is bound by, with the alternatives turned down, are a quern ledger in `ledger/tree.py`. Read it with the brief, not the source:

```sh
uv sync
uv run quern brief .
uv run python -m ledger.check   # exits 1 on a red nobody expected
```

There is no flight-recorder boundary yet: nothing here touches storage, the network, the clock or randomness. The first code that does declares one.

## Tests

`uv run pytest --testmon` runs the tests that failed last time or whose code changed, then `uv run pytest` runs the whole suite. Both stop at the first failure.
