"""The knowledge base against its sources, and the package against quern's publish gate.

A quote is the one claim here no rule can check: whether the publication says it. The
capture under sources/ is what was fetched, and every quote must be found in it.
"""

import re
from pathlib import Path

import pytest

from furniture_design.knowledge import OPEN_LICENCES, knowledge

ROOT = Path(__file__).resolve().parents[1]


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _clauses():
    sources = knowledge()[0]
    for source in sources.children:
        if source.payload["licence"] not in OPEN_LICENCES:
            continue  # cited by locator and values: test_cited_sources_carry_no_quote
        for clause in source.children:
            yield source, clause


def test_cited_sources_carry_no_quote_and_no_capture_here():
    cited = [s for s in knowledge()[0].children if s.payload["licence"] not in OPEN_LICENCES]
    assert cited, "the GSA test method is cited"
    for s in cited:
        assert s.payload["licence"] in ("copyrighted", "unstated")
        assert "capture" not in s.payload or "private" in s.payload["capture"]
        assert all("quote" not in c.payload for c in s.children)


@pytest.mark.parametrize("source,clause", list(_clauses()),
                         ids=lambda v: getattr(v, "id", ""))
def test_every_quote_is_in_the_capture_of_its_source(source, clause):
    capture = ROOT / source.payload["capture"]
    assert source.payload["licence"] in OPEN_LICENCES, "only public-domain and CC BY sources are captured"
    assert _flat(clause.payload["quote"]) in _flat(capture.read_text(encoding="utf-8")), \
        f"{clause.id}: the quote is not in {capture.name}"


def test_no_copyrighted_words_are_quoted_in_this_repo():
    """Ledger: a-copyrighted-standard-is-cited-never-copied-here. The package's examples
    hold a copyrighted catalogue, cited by locator and values; none of its clauses carries
    a quote."""
    from furniture_design.package import PACKAGE
    cited = [s for top in PACKAGE.examples if top.id == "sources" for s in top.children
             if s.payload.get("licence") == "copyrighted"]
    assert cited
    assert all("quote" not in c.payload for s in cited for c in s.children)


def test_knowledge_mounted_under_a_branch_keeps_its_links():
    from quern import Quern, run_rules

    from furniture_design.knowledge import knowledge, mount
    from furniture_design.package import PACKAGE
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = [mount(knowledge(), "knowledge")]
    oak = tree.get("knowledge/materials/oak-northern-red")
    assert oak.links["per"][0].startswith("knowledge/sources/wood-handbook/")
    assert oak.params["density"].derived_from[0].startswith("knowledge/sources/")
    assert [r for r in run_rules(tree) if not r.ok] == []


# Table 4-2 as printed (°C, relative humidity, moisture content %), across its range
TABLE_4_2 = [(-1.1, 0.05, 1.4), (21.1, 0.30, 6.2), (21.1, 0.50, 9.2), (21.1, 0.65, 12.0),
             (21.1, 0.80, 16.0), (48.9, 0.95, 22.0), (87.8, 0.40, 5.0)]


@pytest.mark.parametrize("temperature,rh,printed", TABLE_4_2)
def test_the_moisture_equation_reproduces_the_published_table(temperature, rh, printed):
    """The equation's coefficients come from the knowledge base; the table they must
    reproduce is printed beside them in the Handbook, to 0.1%."""
    from quern import Quern

    from furniture_design.natives import emc
    from furniture_design.spec import climate
    tree = Quern()
    tree.root.children = climate(temperature, rh, rh)
    assert abs(emc(tree, "climates/room", "max") - printed) <= 0.05 + 1e-9


def test_the_package_passes_its_own_publish_gate(tmp_path):
    from quern.library import validate_package

    from furniture_design.package import PACKAGE
    log = validate_package(PACKAGE, tmp_path)
    assert any("a-beam-sags-within-its-limit" in line for line in log)


def test_every_typed_strength_is_in_its_quoted_row():
    """The modulus of rupture of each species is typed beside its Table 5-3a row; the row
    is checked against the capture, and this holds the typed number to the row (12% line:
    specific gravity, then the modulus of rupture in kPa)."""
    from furniture_design.knowledge import MOR_KPA, SPECIES
    for id_, _name, row, g12, *_ in SPECIES:
        assert f"12% {g12:.2f} {MOR_KPA[id_]:,}" in row, id_


def test_a_typed_panel_value_is_in_its_quoted_row():
    from furniture_design.knowledge import FIBRE_PANELS, PLYWOOD_SHEATHING
    for _id, _name, row, g, e, mor in PLYWOOD_SHEATHING:
        flat = row.replace(" ", "")
        assert f"{g:.2f}{e:.2f}" in flat and f"{mor:.2f}" in flat, row
    for _id, _name, row, g0, g1, e0, e1, m0, m1 in FIBRE_PANELS:
        assert f"{m0:.2f}" in row and f"{e0:.2f}" in row, row
