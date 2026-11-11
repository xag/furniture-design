"""The knowledge base against its sources, and the package against quern's publish gate.

A quote is the one claim here no rule can check: whether the publication says it. The
capture under sources/ is what was fetched, and every quote must be found in it.
"""

import re
from pathlib import Path

import pytest

from furniture_design.knowledge import knowledge

ROOT = Path(__file__).resolve().parents[1]


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _clauses():
    sources = knowledge()[0]
    for source in sources.children:
        for clause in source.children:
            yield source, clause


@pytest.mark.parametrize("source,clause", list(_clauses()),
                         ids=lambda v: getattr(v, "id", ""))
def test_every_quote_is_in_the_capture_of_its_source(source, clause):
    capture = ROOT / source.payload["capture"]
    assert source.payload["licence"] == "public-domain", "only public-domain sources are captured"
    assert _flat(clause.payload["quote"]) in _flat(capture.read_text(encoding="utf-8")), \
        f"{clause.id}: the quote is not in {capture.name}"


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
