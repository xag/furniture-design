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
        Node(
            id="the-rules-read-the-knowledge", kind="decision",
            name="A rule carries no number a source states: every limit, test condition, material property "
                 "and coefficient is a param on a knowledge node (a clause quoted verbatim from a captured "
                 "source, or a material or requirement derived from clauses), and the rule reads it there. "
                 "A new source adds nodes, not kinds or rules",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "Create rules you suggested from public sources and do that by building a smart "
                                  "knowledge base and implement rules on the knowledge with a quern package. Don't "
                                  "hardcode the knowledge base structure from these rules; more will come.",
                     "why": "A number written into a rule hides where it came from and has to be found and edited "
                            "when its source changes; on a node it carries its clause, its unit and its "
                            "derivation, and every check that needs it reads the same one."},
            links={"rests_on": ["a-copyrighted-standard-is-cited-never-copied-here"]},
            children=[
                _alt("constants-in-rules", "Write each limit and test load into the rule that uses it",
                     "The rule then states the source's number without the source, and two rules that need "
                     "it state it twice."),
                _alt("a-table-per-check", "One table per check (a sag table, a tip-over table)",
                     "Shapes the knowledge around the first checks; the next check would need a new table "
                     "for facts the existing ones already hold."),
            ],
        ),
        Node(
            id="a-check-reads-its-requirement-over-its-own-link", kind="decision",
            name="A design names the requirement a check reads over that check's own link (stability_case, "
                 "sag_limit), not over one shared link filtered by a field of the requirement",
            payload={"decided_on": "2026-11-11",
                     "why": "quern's rules evaluate both sides of `or`, and a value a node does not carry is a "
                            "red. A shared link filtered by `measure` makes every check read the params of every "
                            "other check's requirements, and go red on their absence."},
            links={"rests_on": ["the-rules-read-the-knowledge"]},
            children=[
                _alt("one-held-to-link", "One `held_to` link, each rule keeping the requirements whose "
                     "measure it checks",
                     "Reds that mean only that a sag requirement has no tilt block."),
            ],
        ),
        Node(
            id="what-the-grammar-cannot-sum-is-a-calculation-with-cases", kind="decision",
            name="A check that needs more than quern's rule grammar (a sum of products over parts, an opened "
                 "drawer, a tilt) is a furniture/* calculation registered beside its code, with cases worked "
                 "by hand in spec.py that quern's publish gate runs; a check the grammar can state stays a rule",
            payload={"decided_on": "2026-11-11",
                     "why": "The grammar sums one list at a time, so mass times lever arm over the parts of a "
                            "piece has no expression; shelf sag is arithmetic over params and stays a rule."},
            links={"rests_on": ["the-rules-read-the-knowledge"]},
            children=[
                _alt("a-weighted-sum-verb-in-quern", "Add a weighted sum to quern's grammar",
                     "Covers mass times arm, not opening the drawers, tilting the piece or the fill share."),
                _alt("a-wasm-solver", "Ship the calculation as a wasm solver inside the package",
                     "It would travel as data, but needs a toolchain this repo does not have, for a "
                     "calculation every consumer already installs as Python."),
            ],
        ),
        Node(
            id="the-static-margin-predicts-the-stability-tests", kind="hypothesis",
            name="The static moment about the front edge, with every extendible element open and the "
                 "conditions a requirement states, predicts whether a built piece passes ASTM F2057-23's "
                 "stability tests 9.2.1 and 9.2.3",
            payload={"stated_on": "2026-11-11",
                     "basis": "The Federal Register's description of the tests (88 FR 28405): loads, block, "
                              "open elements. Not modelled: doors, the dynamic pull of 9.2.2, the test's own "
                              "procedure, which is ASTM's."},
            links={"rests_on": ["what-the-grammar-cannot-sum-is-a-calculation-with-cases"]},
            children=[
                Node(id="a-built-piece-disagrees", kind="falsification",
                     name="A built piece the calculation passes tips in the physical test, or one it fails "
                          "stands"),
            ],
        ),
        Node(
            id="a-makers-products-are-their-own-package", kind="decision",
            name="Knowledge of one maker's products (Lamello's connectors and machines) is not in "
                 "furniture-design@: it is an unofficial package of its own, which requires furniture-design@ "
                 "and adds that maker's products as data on furniture-design's kinds. furniture-design names "
                 "no maker",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "lamello specific should not be in furniture design package, they should be in "
                                  "a lamello unofficial package.",
                     "why": "furniture-design is the general method. A maker's catalogue changes when the maker "
                            "changes it, its pages are the maker's copyrighted text, and 'unofficial' says the "
                            "maker neither wrote nor endorsed the package."},
            links={"rests_on": ["the-rules-read-the-knowledge"]},
            children=[
                _alt("makers-in-the-knowledge-base", "Add Lamello's connectors to furniture-design's knowledge base",
                     "Ties the general method's releases to one maker's catalogue, and puts a maker's name in a "
                     "package meant for every maker."),
            ],
        ),
        Node(
            id="the-package-is-in-the-open-registry", kind="decision",
            name="furniture-design@ is published to the public registry (xag/quern-registry), not the "
                 "private fleet registry",
            payload={"decided_on": "2026-11-11",
                     "why": "A collaborator on this public repo must be able to pin and sync the package; the "
                            "fleet registry is private."},
            links={"rests_on": ["the-method-is-public-and-names-no-home"]},
            children=[
                _alt("the-fleet-registry", "Publish beside the estate's other packages in xag/fleet-registry",
                     "Nobody outside the owner's account could sync it."),
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
