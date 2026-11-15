"""furniture-piece-ledger@: what a piece's own ledger adds to the estate's ledger@.

A piece keeps a ledger beside its model: what it is for, and what was decided, believed and left
open on the way, in the kinds of ledger@. One kind is the piece's own and is defined here: its
purpose, what the piece is for in the words of the people who use it, which every decision about
it answers to and which the standards read sentence by sentence (furniture-standards@). Two rules
hold it: a ledger has a purpose that stands, and one at a time.

A reader mounts this package's kind and rules beside ledger@'s. Each says itself to people in
whole sentences per language (quern's messages), under ledger@'s ids: heading and superseded on
the kind, red on a rule.
"""
from __future__ import annotations

from quern.library import CounterExample, Package
from quern.tree import KindDef, Node, Rule

PURPOSE = KindDef(
    kind="purpose",
    description=(
        "What the piece is for: what it must carry and hold, where it stands, how it must feel to "
        "the people who use it, in their words. One purpose stands at a time; a purpose that "
        "changes is not edited, a new one `supersedes` it, and every entry that `rests_on` the old "
        "one goes red until somebody revisits it. name: the purpose in one or two sentences; "
        "payload: anything that says more (the brief as it was given, who gave it, when)."),
    links={"supersedes": "the purpose this one replaces",
           "rests_on": "an entry this purpose depends on (rare)"},
    messages={"fr": {"heading": "À quoi il sert",
                     "superseded": "« { $entry } » — ancien but, remplacé par « { $by } »."},
              "en": {"heading": "What it is for",
                     "superseded": "“{ $entry }” — former purpose, replaced by “{ $by }”."}},
)

RULES = [
    Rule(name="a-piece-says-what-it-is-for",
         expr="some(p, i, nodes('purpose'), not superseded(p))",
         description="A piece's ledger has a purpose that stands: what the piece is for, which "
                     "every decision about it answers to.",
         messages={"fr": {"red": "Le registre ne dit pas à quoi sert le meuble."},
                   "en": {"red": "The ledger does not say what the piece is for."}}),
    Rule(name="one-purpose-at-a-time", kind="purpose",
         expr="superseded(self) or every(q, i, nodes('purpose'), q == self or superseded(q))",
         description="Two purposes do not stand together: the new one supersedes the old.",
         messages={"fr": {"red": "Un autre but tient en même temps que celui-ci : le nouveau doit "
                                 "remplacer l'ancien."},
                   "en": {"red": "Another purpose stands beside this one: the new one must replace "
                                 "the old."}}),
]

EXAMPLES = [
    Node(id="a-bench-for-the-hall", kind="purpose",
         name="A bench for the hall, to sit on while putting shoes on, with the shoes under it."),
    Node(id="a-bench-for-two", kind="purpose", name="A bench two people sit on, with the shoes under it.",
         links={"supersedes": ["a-bench-for-the-hall"]}),
]

COUNTER_EXAMPLES = [
    CounterExample(rule="a-piece-says-what-it-is-for",
                   nodes=[Node(id="glued-not-screwed", kind="decision", name="Glued, not screwed.")],
                   because="a ledger of decisions that never says what the piece is for"),
    CounterExample(rule="one-purpose-at-a-time",
                   nodes=[Node(id="a-bench", kind="purpose", name="A bench."),
                          Node(id="a-shelf", kind="purpose", name="A shelf.")],
                   because="two purposes standing together, neither replacing the other"),
]

PACKAGE = Package(
    name="furniture-piece-ledger",
    version="0.1.0",
    description="What a piece's own ledger adds to ledger@: its purpose (what the piece is for, in the "
                "words of the people who use it), which stands one at a time and which every decision "
                "answers to. Said to people in French and English.",
    publisher="xag/furniture-design",
    vocabulary=[PURPOSE],
    rules=RULES,
    examples=EXAMPLES,
    counter_examples=COUNTER_EXAMPLES,
)
