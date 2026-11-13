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

from furniture_design.knowledge import (OPEN_LICENCES, TROPIX_ROWS, TROPIX_SHEETS, boruvka, design_stress,
                                        european_species, knowledge, sag_limits, schmidtova, thermo_beech,
                                        tropix)
from furniture_design.package import PACKAGE

ROOT = Path(__file__).resolve().parents[1]
CAPTURES = Path(os.environ.get("FURNITURE_DESIGN_CAPTURES", ROOT.parent / "furniture" / "sources"))


@lru_cache(maxsize=1)
def _by_sha() -> dict[str, list[Path]]:
    assert CAPTURES.is_dir(), (f"the private copies are not at {CAPTURES}: check them out there or set "
                               "FURNITURE_DESIGN_CAPTURES")
    found: dict[str, list[Path]] = {}
    for pattern in ("*.pdf", "*.html"):
        for p in sorted(CAPTURES.rglob(pattern)):
            found.setdefault(hashlib.sha256(p.read_bytes()).hexdigest(), []).append(p)
    return found


def _text(sha: str) -> str:
    """The text beside every copy with this sha256, one after the other: the same document kept
    in two folders may have been extracted two ways, and a value need be found in one."""
    copies = _by_sha().get(sha)
    assert copies, f"no copy under {CAPTURES} has sha256 {sha}"
    return " | ".join(re.sub(r"\s+", " ", c.with_suffix(".txt").read_text(encoding="utf-8"))
                      for c in copies)


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


# The words a copy spells a number with, where it does
WORDS = {"one": 1, "double": 2, "three": 3, "four": 4, "five": 5, "seven": 7, "ten": 10}


def _printed_numbers(printed: str) -> set[float]:
    """Every number a cell prints, read with a decimal point ('10,056' is 10056, '0.0625' is
    0.0625), with a decimal comma ('0,5' is 0.5), or spelt ('seven' is 7)."""
    point = {float(n.replace(",", "")) for n in re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?|\.\d+", printed)}
    comma = {float(n.replace(" ", "").replace(",", ".")) for n in re.findall(r"\d+(?:,\d+)?", printed)}
    words = {float(v) for w, v in WORDS.items() if re.search(rf"\b{w}\b", printed, re.I)}
    return point | comma | words


def _si(number: float, how: dict) -> float:
    return how["over"] / number if "over" in how else number * how.get("times", 1.0)


def test_every_sag_limit_and_thermo_beech_value_is_printed_after_its_label_in_the_copy_fetched():
    """Each value of the sag limits and the thermally modified beech studies, whatever the
    source's licence, is the number printed after its label in the copy whose sha256 the
    source records, brought to SI the way its row says; a clause with values has a row for
    each of them, and a clause of a copyrighted source or one of unstated licence quotes nothing."""
    sources = [schmidtova(), boruvka(), *sag_limits()]
    assert len(sources) == 17
    for source in sources:
        text = _text(source.payload["sha256"])
        for clause in source.children:
            if source.payload["licence"] not in OPEN_LICENCES:
                assert "quote" not in clause.payload, (source.id, clause.id)
            rows = clause.payload["rows"]
            assert sorted(r[0] for r in rows) == sorted(clause.params), (source.id, clause.id)
            for param, label, printed, number, how in rows:
                assert any(printed in text[m.start():m.start() + 600]
                           for m in re.finditer(re.escape(label), text)), (source.id, clause.id, param, printed)
                assert number in _printed_numbers(printed), (source.id, clause.id, param, printed)
                stated = clause.params[param].value
                assert abs(stated - _si(number, how)) <= 1e-9 * max(1.0, abs(stated)), (source.id, param)


def test_the_thermally_modified_beech_is_read_from_its_study():
    beech = thermo_beech()
    p = beech.params
    assert p["design_bending_stress"].value == design_stress(17.27, "x", characteristic=True).value
    assert p["modulus_of_elasticity"].value == 13_620 and p["density"].value == 663.1
    assert "190 °C" in beech.payload["treatment"] and "unknown" in beech.payload["treatment"]
    table_3 = next(c for c in schmidtova().children if c.id == "table-3")
    assert table_3.params["bending_strength_characteristic"].value == 17.27
    assert table_3.params["modulus_of_elasticity_mean"].value == 13_620
