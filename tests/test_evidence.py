"""A verdict that is not a pass names what it rests on that a person only said (evidence.unestablished)."""
from quern import Quern
from quern.tree import Node, get_node

from furniture_design.drawings import checks
from furniture_design.package import PACKAGE

NARROW, MATERIAL = "a-part-is-no-narrower-than-its-saw-cuts", "a-part-is-cut-by-a-saw-that-cuts-its-material"


def _bench(authority: str) -> Quern:
    """The counter-example's side, too narrow for the example shop and of a board it refuses, the shop's
    rules resting on a clause of a source of `authority`."""
    (case,) = [c for c in PACKAGE.counter_examples if c.rule == NARROW]
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = [n.model_copy(deep=True) for n in case.nodes]
    shop = get_node(tree, "tools/example-shop")
    source = get_node(tree, shop.links["per"][0].rsplit("/", 1)[0])
    source.payload = {**source.payload, "authority": authority}
    clause = get_node(tree, shop.links["per"][0])
    clause.payload = {**clause.payload, "quote": "ils ne coupent rien sous 35 cm"}
    return tree


def _details(tree: Quern) -> dict[str, str]:
    return {rule: detail for rule, node, _v, detail in checks(tree, "pieces/bench-side")
            if node == "pieces/bench-side/side"}


def test_a_refusal_on_what_a_customer_reported_quotes_them():
    d = _details(_bench("reported"))
    for rule in (NARROW, MATERIAL):
        assert "«ils ne coupent rien sous 35 cm»" in d[rule] and "reported" in d[rule], d[rule]


def test_a_refusal_on_a_makers_word_names_no_hearsay():
    d = _details(_bench("maker"))
    assert NARROW in d and MATERIAL in d
    assert "only said" not in d[NARROW] + d[MATERIAL]
