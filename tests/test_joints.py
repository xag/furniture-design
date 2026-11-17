"""A joint fastened by screws or a glue is not judged by the rules of a connector.

The rules on a joint's seat (how thick and wide its parts must be, the tool that cuts it) read a
connector's limits through `uses`. Screws, or a glue, named in `uses` have no seat and state none of
them: judged anyway, the joint came out absent or broken and the piece non-compliant.
"""

from __future__ import annotations

from quern import Quern, run_rules

CONNECTOR_RULES = {"a-joined-part-is-thick-enough-for-the-cut", "a-joined-part-is-wide-enough",
                   "a-joint-is-cut-with-a-tool-its-connector-takes"}


def _judged(uses: list[str], made_with: list[str] | None = None, payload: dict | None = None) -> list[str]:
    from furniture_design.package import PACKAGE, _world

    nodes = _world()
    box = next(p for p in next(n for n in nodes if n.id == "pieces").children if p.id == "box")
    corner = next(c for c in box.children if c.id == "corner")
    corner.payload = corner.payload if payload is None else payload
    corner.links = {"joins": corner.links["joins"], "uses": uses, "made_with": made_with or []}
    tree = Quern(vocabulary=PACKAGE.vocabulary, rules=PACKAGE.rules, solvers=PACKAGE.solvers)
    tree.root.children = nodes
    return sorted(r.rule for r in run_rules(tree)
                  if not r.ok and r.rule in CONNECTOR_RULES and r.node == "pieces/box/corner")


def test_a_screwed_joint_is_not_judged_by_a_connectors_rules():
    """Screws the knowledge holds as a material, as a person's own package may."""
    assert _judged(["materials/birch-yellow"], payload={}) == []


def test_a_joint_with_a_connector_still_is():
    """The same joint fastened by the connector again, its seat cut with nothing: its sides are
    thick and wide enough for the connector, and no tool cuts its seat."""
    assert _judged(["connectors/example-connector"]) == ["a-joint-is-cut-with-a-tool-its-connector-takes"]
