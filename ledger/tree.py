"""The decisions furniture-design is bound by, as a ledger: what the skills and tooling must
and must not do, with the alternatives turned down. Read it with `uv run quern brief .`,
never whole.

Vocabulary: ledger@0.7.0 and grounding@1.2.0, pinned in quern.lock.
"""

from __future__ import annotations

import os
from pathlib import Path

import quern.grounding  # noqa: F401
from quern import Node, Quern
from quern.library import consume


def _alt(id_: str, name: str, why: str) -> Node:
    return Node(id=id_, kind="alternative", name=name, payload={"why": why})


def entries() -> list[Node]:
    return [
        Node(
            id="the-method-is-public-and-names-no-home", kind="decision",
            name="This repo is public and holds only the general method, skills and tooling; it names no home, "
                 "no piece and nobody's furniture. Real furniture lives in its own repo, which pins this one, "
                 "and nothing here refers back to it",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "Would you suggest a public repo with only the tooling and skills, or a private "
                                  "repo with also the content? ... Do it.",
                     "why": "A design is fitted to a survey of a home: room sizes, layout, photos. That stays "
                            "private. The method is the same for every home, so it can be public, and keeping it "
                            "apart is what stops it from quietly coming to depend on one home."},
            children=[
                _alt("one-private-repo-with-everything", "One private repo holding the method and the furniture",
                     "The method ends up written against one home, and nobody else can use it."),
                _alt("one-public-repo-with-everything", "One public repo holding the method and the furniture",
                     "Publishes the survey of a home."),
            ],
        ),
        Node(
            id="a-copyrighted-standard-is-cited-never-copied-here", kind="decision",
            name="A rule taken from a copyrighted standard (EN 14749, EN 16121/16122, ASTM F2057, ANSI/BIFMA X5.9, "
                 "ANSI/AWI 0641) is cited here by number and clause and its text is never committed here; a "
                 "public-domain source (the Wood Handbook FPL-GTR-282, 16 CFR 1261 in the Federal Register) may "
                 "be copied in whole so its quotes can be checked",
            payload={"decided_on": "2026-11-11",
                     "why": "A rule enters from a fetched source quoted verbatim, so a reader can refute it from "
                            "the file. A public repo cannot hold a paywalled text; a private repo that pins this "
                            "one can, and is where such a copy goes."},
            links={"rests_on": ["the-method-is-public-and-names-no-home"]},
            children=[
                _alt("copy-every-source-here", "Keep every source's text here, as for public-domain ones",
                     "Republishes copyrighted standards."),
                _alt("copy-no-source-anywhere", "Cite every source and copy none",
                     "Leaves the quotes behind the paywalled rules uncheckable by anyone who has not bought them."),
            ],
        ),
    ]


def build() -> Quern:
    root = Path(__file__).resolve().parents[1]
    lib, refs = consume(root, os.environ.get("QUERN_REGISTRY", root.parent / "quern-registry"))
    quern = Quern(packages=list(refs))
    quern = lib.effective(quern)
    quern.root.children = entries()
    return quern
