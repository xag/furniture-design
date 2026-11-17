"""Every rule and calculation says where it is written, so a reader held back by one can read it."""

from __future__ import annotations

from pathlib import Path

from furniture_design import natives, package, standards
from furniture_design.package import written_at

ROOT = Path(package.__file__).resolve().parents[1]


def _line(at: str) -> str:
    f, n = at.rsplit(":", 1)
    return (ROOT / f).read_text(encoding="utf-8").splitlines()[int(n) - 1]


def test_every_rule_is_found_at_the_line_that_names_it():
    for r in [*package.RULES, *standards.OWN_RULES]:
        assert f'name="{r.name}"' in _line(written_at(r.name)), r.name


def test_every_calculation_is_found_at_its_function():
    for name, fn in [*natives.NATIVES.items(), *standards.NATIVES.items()]:
        assert _line(written_at(name)).startswith(f"def {fn.__name__}("), name


def test_a_name_neither_package_writes_is_nowhere():
    """certification@ is required from the registry, not written here."""
    assert written_at("a-level-requires-criteria") == ""
    assert written_at("no-such-rule") == ""
