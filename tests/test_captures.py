"""The values read from copyrighted sources, against the copies they were read from.

Those copies are not in this public repo (ledger: a-copyrighted-source-is-cited-by-locator-and-
values). They are kept private, found by the sha256 each source records, under
$FURNITURE_DESIGN_CAPTURES or the private sources folder checked out beside this repo; each PDF
sits beside its text (pdftotext). Without them these tests fail, saying where they looked, and
never skip.
"""

import hashlib
import os
import re
from functools import lru_cache
from pathlib import Path

from quern import Quern, run_rules

from furniture_design.knowledge import (TROPIX_ROWS, TROPIX_SHEETS, design_stress, european_species,
                                        knowledge, tropix)
from furniture_design.package import PACKAGE

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = Path(os.environ.get("FURNITURE_DESIGN_CAPTURES", ROOT.parent / "furniture" / "sources"))


@lru_cache(maxsize=1)
def _by_sha() -> dict[str, Path]:
    assert CAPTURES.is_dir(), (f"the private copies are not at {CAPTURES}: check them out there or set "
                               "FURNITURE_DESIGN_CAPTURES")
    return {hashlib.sha256(p.read_bytes()).hexdigest(): p for p in CAPTURES.rglob("*.pdf")}


def _text(sha: str) -> str:
    pdf = _by_sha().get(sha)
    assert pdf, f"no copy under {CAPTURES} has sha256 {sha}"
    return re.sub(r"\s+", " ", pdf.with_suffix(".txt").read_text(encoding="utf-8"))


def test_every_copyrighted_value_is_printed_after_its_row_in_the_copy_fetched():
    sources = [s for s in tropix() if s.payload["licence"] == "copyrighted"]
    assert len(sources) == len(TROPIX_SHEETS) + 1
    for source in sources:
        text = _text(source.payload["sha256"])
        for clause in source.children:
            assert "quote" not in clause.payload
            for param, label, printed in clause.payload["rows"]:
                assert any(printed in text[m.start():m.start() + 600]
                           for m in re.finditer(re.escape(label), text)), (source.id, clause.id, param, printed)
                stated = clause.params[param]
                assert round(stated.value * (100 if stated.unit == "1/%" else 1), 6) in _numbers(printed), (source.id, param)


def _numbers(printed: str) -> list[float]:
    """The numbers a cell prints: '13 300 MPa' is 13300, '7.700-11.760' is 7700 and 11760, '0,55' is 0.55."""
    return [round(float(n.replace(" ", "").replace(".", "").replace(",", ".")), 6)
            for n in re.findall(r"\d+(?:[ .]\d{3})*(?:,\d+)?", printed)]


def test_the_tropix_rows_are_the_three_the_species_need():
    assert [p for p, _ in TROPIX_ROWS] == ["relative_density", "modulus_of_rupture", "modulus_of_elasticity"]


def test_a_characteristic_strength_takes_only_the_handbooks_factor_and_a_mean_its_cov_first():
    assert abs(design_stress(21.0, "x", characteristic=True).value - 10.0) < 1e-9
    assert abs(design_stress(21.0, "x", characteristic=False).value - 21.0 * (1 - 1.645 * 0.16) / 2.1) < 1e-9


def test_every_species_is_judged_by_its_own_values_and_passes_the_rules():
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = knowledge()
    assert [(r.rule, r.node) for r in run_rules(tree) if not r.ok] == []
    oak = next(m for m in european_species() if m.id == "oak-european")
    assert oak.params["density"].value == 740 and abs(oak.params["modulus_of_elasticity"].value - 13_300 / 1.1) < 1e-6
    assert oak.payload["measured_along"] == "grain" and oak.payload["modulus"] == "apparent"
