"""What the standards know of a piece's design flaws (furniture_design.flaws), over the domains it names:
every criterion of a piece, every rule of a design criterion, every rule of the package that judges a piece,
its parts, its joints or its loads, and every row the checks report."""
from quern import Quern

from furniture_design import flaws, standards
from furniture_design.package import EXAMPLES, PACKAGE
from furniture_design.package import RULES as PACKAGE_RULES
from furniture_design.report import checks

PIECE_KINDS = {"piece", "part", "joint", "load"}


def _criteria() -> dict:
    [branch] = [b for b in standards.knowledge() if b.id == standards.STANDARDS]
    return {n.id: n for n in branch.children if n.kind == "criterion" and n.payload.get("applies_to") == "piece"}


def test_each_criterion_of_a_piece_reads_the_design_or_the_pages_as_drawn():
    assert set(flaws.CRITERIA) | set(standards.ON_THE_PAGES) == set(_criteria())
    assert not set(flaws.CRITERIA) & set(standards.ON_THE_PAGES)


def test_each_rule_of_a_design_criterion_is_in_its_criterions_family():
    for cid, family in flaws.CRITERIA.items():
        for rule in _criteria()[cid].payload["rules"]:
            assert flaws.family(rule) == family, (cid, rule)


def test_no_rule_judged_on_the_pages_is_the_designs():
    for cid in standards.ON_THE_PAGES:
        assert not set(_criteria()[cid].payload["rules"]) & set(flaws.RULES), cid


def test_each_rule_that_judges_a_piece_says_itself_in_every_language():
    """A standards rule says itself (its messages); a package rule says itself here, and, when its failure
    means the piece fails, what it says when it could not tell."""
    standards_rules = {r.name for r in standards.RULES}
    for r in PACKAGE_RULES:
        if r.kind not in PIECE_KINDS:
            continue
        assert r.name in flaws.RULES, r.name
        assert set(flaws.RED[r.name]) == {"en", "fr"}, r.name
        if flaws.RULES[r.name][1] == "fails":
            assert set(flaws.UNSETTLED[r.name]) == {"en", "fr"}, r.name
    assert set(flaws.RED) | set(flaws.UNSETTLED) <= set(flaws.RULES) - standards_rules
    assert set(flaws.UNSETTLED) <= set(flaws.RED)


def test_the_families_and_levels_are_said_in_every_language():
    assert {f for f, _ in flaws.RULES.values()} | set(flaws.CRITERIA.values()) <= {f for f, _ in flaws.FAMILIES}
    for _, say in flaws.FAMILIES + flaws.LEVELS:
        assert set(say) == {"en", "fr"}


def test_a_rule_that_could_not_tell_whether_the_piece_fails_may_fail():
    assert flaws.level("a-piece-takes-its-sideways-load") == "fails"
    assert flaws.level("a-piece-takes-its-sideways-load", settled=False) == "may_fail"
    assert flaws.level("a-pieces-parts-say-how-they-are-cut", settled=False) == "incomplete"
    assert flaws.words("a-piece-takes-its-sideways-load", settled=False)["fr"].startswith("On ne sait pas")
    assert flaws.words("a-pieces-parts-say-how-they-are-cut") is None   # a standards rule says itself
    ordered = sorted(["a-pieces-parts-say-how-they-are-cut", "a-pieces-purpose-is-answered",
                      "a-step-closes-each-joint-the-way-its-connector-engages"], key=flaws.order)
    assert ordered == ["a-step-closes-each-joint-the-way-its-connector-engages", "a-pieces-purpose-is-answered",
                       "a-pieces-parts-say-how-they-are-cut"]


def test_each_row_the_checks_report_names_the_rules_it_reports():
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = [n.model_copy(deep=True) for n in EXAMPLES]
    rows = checks(tree, "pieces/bench")
    assert rows
    for row in rows:
        assert row["rules"] and set(row["rules"]) <= set(flaws.RULES), row


def test_the_steps_criterion_does_not_say_a_part_reaches_its_place():
    """The review (prototypes/design-card, stage one finding 6): 'chaque pièce arrive à sa place' held beside a
    failing 'Tablette n'arrive pas droit' at step 7; the criterion says what its rule checks: no part crosses
    another on its way in."""
    say = _criteria()["piece-steps-build-it"].payload["say"]
    assert "arrive à sa place" not in say["fr"] and "reaches its place" not in say["en"]
    assert "traverse" in say["fr"] and "crosses" in say["en"]
