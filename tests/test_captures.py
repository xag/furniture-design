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

from furniture_design.knowledge import (GRINDER_SOURCES, JOINTER_SOURCES, PINCH_SOURCES, PROFILE_SAW_SOURCES, JOINTER_VIDEOS, OPEN_LICENCES, TROPIX_ROWS, TROPIX_SHEETS, boruvka, design_stress,
                                        european_species, knowledge, sag_limits, schmidtova, seating_tests, thermo_beech,
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
    spaced = {float(n.replace(" ", "")) for n in re.findall(r"\d{1,3}(?: \d{3})+", printed)}  # '1 300' is 1300
    comma = {float(n.replace(" ", "").replace(",", ".")) for n in re.findall(r"\d+(?:,\d+)?", printed)}
    words = {float(v) for w, v in WORDS.items() if re.search(rf"\b{w}\b", printed, re.I)}
    return point | spaced | comma | words


def _si(number: float, how: dict) -> float:
    return how["over"] / number if "over" in how else number * how.get("times", 1.0)


def test_every_sag_limit_and_thermo_beech_value_is_printed_after_its_label_in_the_copy_fetched():
    """Each value of the sag limits, the seating tests and the thermally modified beech studies, whatever the
    source's licence, is the number printed after its label in the copy whose sha256 the
    source records, brought to SI the way its row says; a clause with values has a row for
    each of them, and a clause of a copyrighted source or one of unstated licence quotes nothing."""
    sources = [schmidtova(), boruvka(), *sag_limits(), *seating_tests()]
    assert len(sources) == 21
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


# What each passage the general jointer method rests on says, a few of its words, found in the copy
JOINTER_WORDS = {
    "makita-pj7000-manual": ["Fit the two workpieces together as they will", "Lay the vertical workpiece on the horizontal one"],
    "dewalt-dw682-manual": ["exactly as they are to be assembled", "Lay the shelf down on the mating workpiece",
                            "making test cuts in scrap"],
    "festool-df500-manual": ["Mark the matching surfaces of the", "test rout and join"],
    "woodsmith-aligning-edge-joints": ["Use the same reference face for both workpieces"],
    "woodsmith-biscuit-essentials": ["cutting your workpieces to their final dimensions",
                                     "Align the centerline mark on the biscuit joiner"],
    "popular-woodworking-plate-joiner-tips": ["Clamp the shelf right on the line", "Stand your plate joiner on end"],
    "fine-woodworking-biscuit-basics": ["the distance between the blade and the base does not change"],
}


def test_every_passage_the_jointer_method_rests_on_is_in_the_copy_fetched():
    assert {s[0] for s in JOINTER_SOURCES} == set(JOINTER_WORDS)
    for sid, _name, _publisher, _url, sha, _clauses in JOINTER_SOURCES:
        text = _text(sha)
        for words in JOINTER_WORDS[sid]:
            assert words in text, (sid, words)


def test_every_passage_of_a_video_the_jointer_method_rests_on_is_in_the_account_kept():
    """A video is cited from the account Gemini gave of it, kept privately under videos/ by its YouTube
    id: the copy has the sha256 the source states, and the words each clause rests on are in it."""
    for sid, _name, _publisher, url, _authority, sha, clauses in JOINTER_VIDEOS:
        copy = CAPTURES / "videos" / f"{url.rsplit('=', 1)[1]}.md"
        assert copy.exists(), f"the account {copy} is missing"
        assert hashlib.sha256(copy.read_bytes()).hexdigest() == sha, sid
        text = copy.read_text(encoding="utf-8")
        for cid, _locator, words in clauses:
            for w in words:
                assert w in text, (sid, cid, w)


# What each passage the general angle-grinder method rests on says, a few of its words, found in the copy
GRINDER_WORDS = {
    "makita-xag04-manual": ["Support panels or any oversized workpiece", "Do not start the cutting operation in the workpiece",
                            "lateral pressure", "Always wear eye protection"],
    "metabo-w-18-ltx-manual": ["using clamps", "Always work with the additional handle", "against the run of the disc",
                               "Wear ear protectors"],
    "dewalt-dcg405-manual": ["Type 1 guard", "Use clamps or a", "Apply minimum pressure to the work surface",
                             "do not change the angle of the cut"],
}


def test_every_passage_the_angle_grinder_method_rests_on_is_in_the_copy_fetched():
    assert {s[0] for s in GRINDER_SOURCES} == set(GRINDER_WORDS)
    for sid, _name, _publisher, _url, sha, _clauses in GRINDER_SOURCES:
        text = re.sub(r"\s+", " ", _text(sha))
        for words in GRINDER_WORDS[sid]:
            assert words in text, (sid, words)


# A few words of each passage the hacksaw-on-a-profile method rests on, found in the copy
PROFILE_SAW_WORDS = {
    "doellken-wl-instructions": ["working temperature between 15 °C and 30 °C", "In order to prevent material fractures",
                                 "and mitre saw with a fine saw blade"],
    "schluter-jolly-data-sheet": ["ensure that all burr is removed from the profile ends with a file or similar"],
    "sintra-fabrication-guide": ["place flat pieces of wood or plastic between the work and the clamps"],
    "spaceo-recuttable-doors-notice": ["insérer une cale rigide entre les parois", "utiliser du ruban adhésif sur la zone"],
    "adeo-sliding-doors-guide": ["inserrez des lames de bois ou des chutes de polystyrène"],
    "bricomarche-sliding-door-guide": ["Ébavurez légèrement avec une lime fine", "un bord tranchant peut accrocher les roulettes"],
    "castorama-cutting-plastic": ["boîte à onglet pour bien caler le tube", "La scie à métaux"],
    "bosch-diy-cutting-plastic": ["une cale en bois entre la pièce et le mors", "exercez que peu de pression",
                                  "Si vous allez trop vite, le plastique risque de fondre",
                                  "ébavurer les bords au terme de la découpe"],
    "bobvila-cutting-pvc": ["PVC becomes brittle and a dull blade can crack the pipe", "use a guide for the blade to follow",
                            "jam the blade into the PVC pipe"],
}


def test_every_passage_the_profile_hacksaw_method_rests_on_is_in_the_copy_fetched():
    assert {s[0] for s in PROFILE_SAW_SOURCES} == set(PROFILE_SAW_WORDS)
    for sid, _name, _publisher, _url, sha, _clauses in PROFILE_SAW_SOURCES:
        text = re.sub(r"\s+", " ", _text(sha))
        for words in PROFILE_SAW_WORDS[sid]:
            assert words in text, (sid, words)


# A few words of each passage the marking-a-length-in-place method rests on, found in the copy
PINCH_WORDS = {
    "fhb-avoiding-numbers": ["The simplest way to avoid measuring is to mark your work in place",
                             "sliding two slender sticks alongside each other"],
    "fhb-ten-rules-finish-carpentry": ["It is more accurate to mark trim in place than to measure and then transfer numbers",
                                       "to confuse numbers while walking to the saw", "Cut this end slightly long"],
    "fhb-story-stick-measuring": ["Extend the dowels against the opening, clamp, transfer to workpiece and cut"],
    "fhb-cutting-miters": ["you must leave the piece long, so both ends can be trimmed to fit"],
    "fhb-perfect-scribing": ["low-tack painter", "The knife cuts the tape cleanly"],
    "fww-story-sticks": ["read the tape wrong or simply forget a number"],
    "pw-pinch-rods": ["I use two collars, clamping one at each end of the overlapping rods"],
    "wj-pinch-sticks": ["it was difficult to hold the two sticks in line", "I angle-cut their ends"],
    "swu-install-sliding-doors": ["Carefully measure the width of the opening at top and bottom"],
    "sliding-door-co-closet-door-fts": ["Measure the width of the top of the opening"],
}


INSTRUCTION_WORDS = {
    "agrawala-2003": ["parts within a group are added", "part at a time",
                      "Action diagrams spatially separate the parts to be attached",
                      "new parts added in each step of the assembly must be visible",
                      "If only the new parts are visible",
                      "how the shelf is fastened by the screws"],
    "ikea-why-only-pictures": ["IKEA products are sold worldwide",
                               "ensures our assembly instructions are accessible to all"],
}


def test_every_passage_the_instruction_standard_rests_on_is_in_the_copy_fetched():
    from furniture_design.knowledge import INSTRUCTION_SOURCES, VISIBILITY_SCORES, instruction_sources

    assert {s[0] for s in INSTRUCTION_SOURCES} == set(INSTRUCTION_WORDS)
    for sid, _name, _publisher, _url, sha, _clauses in INSTRUCTION_SOURCES:
        text = re.sub(r"\s+", " ", _text(sha))
        for words in INSTRUCTION_WORDS[sid]:
            assert words in text, (sid, words)
    paper = instruction_sources()[0]
    text = re.sub(r"\s+", " ", _text(paper.payload["sha256"]))
    scores = next(c for c in paper.children if c.id == "visibility-scores")
    for param, label, printed, value in VISIBILITY_SCORES:
        assert f"{label} {printed}" in text, (param, label, printed)
        assert scores.params[param].value == value == float(printed.rstrip("%")) / 100


def test_every_passage_the_marking_in_place_method_rests_on_is_in_the_copy_fetched():
    assert {s[0] for s in PINCH_SOURCES} == set(PINCH_WORDS)
    for sid, _name, _publisher, _url, sha, _clauses in PINCH_SOURCES:
        text = re.sub(r"\s+", " ", _text(sha))
        for words in PINCH_WORDS[sid]:
            assert words in text, (sid, words)
