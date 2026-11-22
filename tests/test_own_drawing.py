"""The checks of the package's own drawing are its tests, not rules of a piece's certificate: a lettered step, a
step picture that brings something, everything on the paper, and only what the model says printed are faults of
this package's code, which no change to a piece answers (the plan of 2026-11-22 for how Soban talks to assistants,
step 10). Each check still finds the fault it was made for, and the package's drawing of its examples has none."""
import json
from pathlib import Path

import pytest
from quern.tree import Node, Quern

from furniture_design import drawings, standards
from furniture_design import standards_pages as pg
from furniture_design import standards_piece as sp
from tests.test_drawings import BENCH, _tree

OURS = ("furniture/steps_unlettered", "furniture/steps_repeating", "furniture/drawn_off_the_paper",
        "furniture/printed_unsupported")
DROPPED = ("a-pieces-steps-letter-their-parts", "a-pieces-step-pictures-each-bring-something",
           "a-pieces-pages-keep-to-the-paper", "a-pieces-documents-print-only-its-model")


def _example(**pages) -> Quern:
    t = Quern(vocabulary=standards.VOCABULARY, rules=standards.RULES, solvers=standards.SOLVERS)
    t.root.children = standards._piece_case(pages=pages)
    return t


def test_no_rule_of_a_pieces_certificate_judges_the_packages_own_drawing():
    names = {r.name for r in standards.RULES}
    assert not names & set(DROPPED)
    assert not {"pages-hold-what-they-draw", "documents-say-only-the-model"} & set(standards.ON_THE_PAGES)


@pytest.mark.parametrize("check, knobs", [
    ("furniture/steps_unlettered", {"lettered": False}),
    ("furniture/steps_repeating", {"after": "picture"}),
    ("furniture/drawn_off_the_paper", {"spilled": True}),
    ("furniture/printed_unsupported", {"nameless": True}),
    ("furniture/printed_unsupported", {"coloured": True}),
    ("furniture/printed_unsupported", {"bar": (16, 6)}),
    ("furniture/printed_unsupported", {"material": "Aluminium pro"}),
])
def test_each_check_finds_the_fault_it_was_made_for(check, knobs):
    assert pg.EXPLAINERS[check](_example(**knobs), sp._PIECE), (check, knobs)
    assert pg.EXPLAINERS[check](_example(), sp._PIECE) == [], check


def test_the_packages_drawing_of_the_bench_passes_every_check_of_its_own_drawing(tmp_path: Path):
    tree = _tree()
    made = drawings.documents(tree, BENCH, tmp_path)
    for key in ("pages", "pages-design", "pages-cutting"):
        tree.root.children = tree.root.children + [Node.model_validate(json.loads(made[key].read_text(encoding="utf-8")))]
    for check in OURS:
        assert pg.EXPLAINERS[check](tree, BENCH) == [], check
