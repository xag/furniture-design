"""furniture-standards@ (furniture_design/standards.py): a tool is certified by running the package's
criteria and levels on it (quern.certify), and the package passes quern's publish gate."""

from quern import Quern
from quern.certify import certificate
from quern.library import validate_package

from furniture_design import standards
from furniture_design.standards import PACKAGE, _document, _world, example_tool

TOOL = "tools/example-sander"


def cert(*args, **kw) -> dict:
    t = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    t.root.children = _world(*args, **kw)
    return certificate(t, TOOL)


def reached(c: dict) -> list[str]:
    return [p.rpartition("/")[2] for p in c["reached"]]


def test_the_package_passes_the_publish_gate(tmp_path):
    log = validate_package(PACKAGE, tmp_path)
    assert any("a-tools-figures-each-rest-on-two-observations" in line for line in log)


def test_a_tool_read_from_two_documents_with_a_true_model_reaches_every_level():
    assert reached(cert()) == ["tool-listed", "tool-cuts-parts", "tool-in-instructions", "tool-shared"]


def test_a_tool_read_from_one_manual_is_used_where_it_is_fit_and_told_what_closes_it():
    """One document vouches for each figure: it cuts parts and is drawn, and is not taken into the shared
    packages; the red is the rule's own sentence and the figures it counted."""
    c = cert(example_tool(documents=("manual",)))
    assert reached(c) == ["tool-listed", "tool-cuts-parts", "tool-in-instructions"]
    [closed] = [k for k in c["criteria"] if k["criterion"] == "standards/tool-figures-are-closed"]
    [red] = closed["reds"]
    assert red["says"].startswith("Close every figure") and "pad_diameter: 1 of 2 (sources/manual)" in red["why"]


def test_a_tool_without_a_model_is_not_drawn_and_still_cuts_parts():
    c = cert(example_tool(model={}))
    assert reached(c) == ["tool-cuts-parts"]
    [listed] = [lv for lv in c["levels"] if lv["level"] == "standards/tool-listed"]
    assert listed["blocked_by"] == ["standards/tool-is-drawn"]


def test_figures_nobody_found_printed_reach_no_level_that_reads_them():
    c = cert(documents=[_document("manual", grounded=False), _document("page", grounded=False)])
    assert reached(c) == ["tool-listed", "tool-in-instructions"]


def test_a_document_that_prints_another_value_is_named():
    c = cert(documents=[_document("manual"), _document("page", 150.0)])
    whys = [w for k in c["criteria"] for r in k["reds"] for w in r["why"]]
    assert "pad_diameter: 125 here, 150 at sources/page/data/pad_diameter" in whys


def test_the_levels_are_data_a_tree_may_replace():
    """A stricter standard, the same runner: the list level now asks for closed figures too."""
    [branch] = standards.knowledge()
    for node in branch.children:
        if node.id == "tool-listed":
            node.links["requires"].append("standards/tool-figures-are-closed")
    assert "tool-listed" not in reached(cert(example_tool(documents=("manual",)), standards=branch))
