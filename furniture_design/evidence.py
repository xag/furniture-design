"""What a rule's verdict rests on that nobody established: the clauses of sources of authority reported (a
person's account) or none (a person's video, page or post) behind the values a rule read, quoted.

A rule that refuses a part on what one person said refuses it on hearsay, and the person reading the
refusal is the one who can tell it is wrong: so every verdict that is not a pass names those clauses,
with their words and their source, beside its reason (drawings.checks). What a maker publishes, a
standard, research and an edited publication are not listed: they are the knowledge's own grounds.

The values a rule read are found in its trace (run_rules(..., trace=True)): the nodes a param or a
payload was read on, the nodes a link was followed from and to, and for a calculation the node it was
asked about and every node that node links to, one step away.
"""
from __future__ import annotations

from quern.tree import Node, Quern, RuleResult, get_node

# The authorities whose clauses a verdict names, as knowledge.AUTHORITIES calls them.
UNESTABLISHED = ("reported", "none")


def _read(tree: Quern, result: RuleResult) -> list[str]:
    """The paths of the nodes the rule's trace read, in the order it read them."""
    paths: list[str] = []
    for r in result.reads:
        args = [a for a in r.args if isinstance(a, str)]
        if r.call in ("param", "payload") and args:
            paths.append(args[0])
        elif r.call == "linked" and args:
            paths.append(args[0])
            paths += [v for v in (r.value or []) if isinstance(v, str)]
        elif r.call == "solve" and len(args) > 1:
            paths.append(args[1])
            subject = get_node(tree, args[1])
            if subject is not None:
                paths += [t for targets in subject.links.values() for t in targets]
    return list(dict.fromkeys(paths))


def _clauses(node: Node) -> list[str]:
    """The clauses a node rests on: its links per, and what its params are derived from."""
    out = list(node.links.get("per", []))
    for q in node.params.values():
        for d in getattr(q, "derived_from", None) or []:
            out.append(d)
    return list(dict.fromkeys(out))


def unestablished(tree: Quern, result: RuleResult) -> list[str]:
    """For each node the rule read, each clause it rests on from a source of authority reported or none:
    "<node>: «<quote>» (<source>, <authority>)"."""
    out = []
    for path in _read(tree, result):
        node = get_node(tree, path)
        if node is None:
            continue
        for cpath in _clauses(node):
            clause = get_node(tree, cpath)
            if clause is not None and clause.kind != "clause" or clause is None and "/" in cpath:
                cpath = cpath.rsplit("/", 1)[0]   # a param of a clause: the clause
                clause = get_node(tree, cpath)
            source = get_node(tree, cpath.rsplit("/", 1)[0]) if "/" in cpath else None
            if clause is None or source is None:
                continue
            authority = (source.payload or {}).get("authority", "")
            if authority in UNESTABLISHED:
                quote = (clause.payload or {}).get("quote") or (clause.payload or {}).get("locator", "")
                out.append(f"{path}: «{quote}» ({source.name or source.id}, {authority})")
    return list(dict.fromkeys(out))
