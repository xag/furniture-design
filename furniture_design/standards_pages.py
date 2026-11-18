"""What a piece's assembly instructions are held to, on the pages as they were drawn.

The drawing notes what each page shows (pages.model: a branch instructions/<piece id>, its pages
with their words, their pictures with what each shows). The contracts here count, for a piece, what
of that record a rule may refuse: the texts that read as sentences, the steps that bring in parts of
several kinds, the parts brought in with no line to where they go, the parts and the context too
hidden to see, the joints closed with nothing drawn of what fastens them, the kinds of part a step
brings in with no letter beside them, and what is drawn or set beyond the edge of the paper. How many
words make a
sentence and how much of a part must show are arguments the rules give, read from the knowledge.

A piece whose instructions were not drawn in the tree judged has nothing to judge: each contract
then counts one, and says so.
"""
from __future__ import annotations

import re

from quern.tree import Node, Quern, get_node

from .pages import INSTRUCTIONS

_NOT_DRAWN = "the instructions were not drawn in this build: build the piece with its documents"
_WORD = re.compile(r"[^\W\d_]{2,}", re.UNICODE)
# What the drawing notes as no sentence (sheets.Pen.text's roles): the piece's name, a heading, the name
# of a thing or a size, and the sentence of a step no picture can say.
_NOT_SENTENCES = ("name", "heading", "label", "note")


def _drawn(tree: Quern, piece: str) -> Node | None:
    return get_node(tree, f"{INSTRUCTIONS}/{piece.rpartition('/')[2]}")


def _pages(node: Node) -> list[Node]:
    return [p for p in node.children if p.kind == "page"]


def _steps(node: Node) -> list[dict]:
    """The pictures of the steps that assemble (a step that prepares parts attaches nothing)."""
    return [f.payload for p in _pages(node) for f in p.children
            if f.kind == "frame" and f.payload.get("kind") == "step" and not f.payload.get("prepare")]


def _lines(fn):
    def lines(tree: Quern, piece: str, *args) -> list[str]:
        node = _drawn(tree, piece)
        return [_NOT_DRAWN] if node is None else fn(node, *args)
    return lines


@_lines
def _worded(node: Node, words: float = 2) -> list[str]:
    return [f"page {p.payload.get('number')}: \"{w['text']}\"" for p in _pages(node)
            for w in p.payload.get("words") or []
            if w.get("role") not in _NOT_SENTENCES and len(_WORD.findall(w.get("text", ""))) >= words]


def pages_worded(tree: Quern, piece: str, words: float = 2) -> float:
    """How many texts on the pages of the piece's instructions read as sentences: at least `words`
    words of letters (a count, a size, a part's letter, the piece's own name, a heading, the name of a
    tool or of the hardware, and the sentence of a step that brings in, cuts and closes nothing, are not)."""
    return float(len(_worded(tree, piece, words)))


@_lines
def _mixed(node: Node) -> list[str]:
    return [f"step {s.get('step')} brings in parts of {len(s['kinds'])} kinds ({', '.join(s['kinds'])})"
            for s in _steps(node) if len(s.get("kinds") or []) > 1]


def steps_mixing_kinds(tree: Quern, piece: str) -> float:
    """How many steps of the piece's instructions bring in parts of more than one kind (parts that
    carry the same letter are one kind)."""
    return float(len(_mixed(tree, piece)))


@_lines
def _unguided(node: Node) -> list[str]:
    return [f"step {s.get('step')}: {part} has no line to where it goes" for s in _steps(node) if s.get("shows")
            for part in s.get("brings") or [] if part not in (s.get("guided") or [])]


def parts_without_a_line(tree: Quern, piece: str) -> float:
    """How many parts a step brings in, to parts already there, are not drawn apart from where they
    go with a line leading there."""
    return float(len(_unguided(tree, piece)))


@_lines
def _hidden(node: Node, share: float) -> list[str]:
    return [f"step {s.get('step')}: {part} shows {seen:.0%} of itself, under {share:.0%}" for s in _steps(node)
            for part, seen in (s.get("visible") or {}).items() if seen < share]


def parts_hidden(tree: Quern, piece: str, share: float) -> float:
    """How many parts a step brings in show less than `share` of themselves in its picture."""
    return float(len(_hidden(tree, piece, share)))


@_lines
def _no_context(node: Node, share: float) -> list[str]:
    return [f"step {s.get('step')}: the parts already there show {s.get('context', 0):.0%} of themselves, under "
            f"{share:.0%}" for s in _steps(node) if s.get("shows") and s.get("context", 0) < share]


def steps_without_context(tree: Quern, piece: str, share: float) -> float:
    """How many steps show less than `share` of the parts already there, taken together."""
    return float(len(_no_context(tree, piece, share)))


@_lines
def _unfastened(node: Node) -> list[str]:
    return [f"step {s.get('step')} closes {j} and draws nothing of what fastens it" for s in _steps(node)
            for j in s.get("closes") or [] if j not in (s.get("fastened") or [])]


def fastenings_not_shown(tree: Quern, piece: str) -> float:
    """How many joints a step closes have nothing drawn of what fastens them in its picture."""
    return float(len(_unfastened(tree, piece)))


@_lines
def _unlettered(node: Node) -> list[str]:
    return [f"step {s.get('step')}: nothing letters the part {k} it brings in" for s in _steps(node)
            for k in s.get("kinds") or [] if k not in (s.get("lettered") or []) and k not in (s.get("wholes") or [])]


def steps_unlettered(tree: Quern, piece: str) -> float:
    """How many kinds of part a step brings in carry no letter in its picture: the letter the page of what
    is needed gives that kind. An assembly brought in whole carries none: its parts carried theirs when it
    was put together."""
    return float(len(_unlettered(tree, piece)))


@_lines
def _off_the_paper(node: Node) -> list[str]:
    out = []
    for p in _pages(node):
        if any(f.kind == "frame" and f.payload.get("kind") == "spill" for f in p.children):
            out.append(f"page {p.payload.get('number')}: something is drawn beyond the edge of the paper")
        out += [f"page {p.payload.get('number')}: \"{w['text']}\" is set beyond the edge of the paper"
                for w in p.payload.get("words") or [] if w.get("off")]
    return out


def drawn_off_the_paper(tree: Quern, piece: str) -> float:
    """How many pages of the piece's instructions draw something beyond the edge of the paper, and how many
    texts are set beyond it: what is there is in the model and never reaches whoever builds."""
    return float(len(_off_the_paper(tree, piece)))


NATIVES = {
    "furniture/steps_unlettered": steps_unlettered,
    "furniture/drawn_off_the_paper": drawn_off_the_paper,
    "furniture/pages_worded": pages_worded,
    "furniture/steps_mixing_kinds": steps_mixing_kinds,
    "furniture/parts_without_a_line": parts_without_a_line,
    "furniture/parts_hidden": parts_hidden,
    "furniture/steps_without_context": steps_without_context,
    "furniture/fastenings_not_shown": fastenings_not_shown,
}

EXPLAINERS = {
    "furniture/steps_unlettered": _unlettered,
    "furniture/drawn_off_the_paper": _off_the_paper,
    "furniture/pages_worded": _worded,
    "furniture/steps_mixing_kinds": _mixed,
    "furniture/parts_without_a_line": _unguided,
    "furniture/parts_hidden": _hidden,
    "furniture/steps_without_context": _no_context,
    "furniture/fastenings_not_shown": _unfastened,
}


# --- the example: the two doors' instructions as drawn ------------------------------------------

_PIECE = "pieces/doors"


def example_pages(*, sentence: str | None = None, role: str = "", rail_kinds: tuple = ("R",), doors_guided: tuple = ("back-panel", "front-panel"),
                  door_shows: float = 0.9, context: float = 0.8, fastened: tuple = ("angle-to-lintel", "channel-to-angle"),
                  drawn: bool = True, lettered: bool = True, spilled: bool = False, off: str = "") -> Node:
    """The instructions of the two doors as their drawing would note them: a cover with the piece's
    name, a page of what is needed with counts and sizes, the rail, then the doors hung in it. Not
    `lettered`: the doors' step draws no letter beside them. `spilled`: the page of what is needed draws a
    part beyond the paper's foot; `off`: a text it sets there."""
    if not drawn:
        return Node(id=INSTRUCTIONS, kind="")
    step = lambda **kw: Node(id=f"frame-{kw['step'] + 2}", kind="frame", payload={"kind": "step", **kw})  # noqa: E731
    return Node(id=INSTRUCTIONS, kind="", children=[Node(id="doors", kind="instructions", children=[
        Node(id="page-1", kind="page", payload={"number": 1, "words": [{"text": "Two sliding doors", "role": "name"}]},
             children=[Node(id="frame-1", kind="frame", payload={"kind": "cover"})]),
        Node(id="page-2", kind="page", payload={"number": 2, "words": [{"text": "A"}, {"text": "2 ×"},
                                                                       {"text": "600 × 8 × 1190"}]
                                                + ([{"text": off, "role": "label", "off": True}] if off else [])},
             children=[Node(id="frame-2", kind="frame", payload={"kind": "board", "mark": "A"})]
             + ([Node(id="frame-9", kind="frame", payload={"kind": "spill"})] if spilled else [])),
        Node(id="page-3", kind="page",
             payload={"number": 3, "words": [{"text": "1"}, {"text": "2"}] + ([{"text": sentence, **({"role": role} if role else {})}] if sentence else [])},
             children=[
                 step(step=1, shows=[], brings=["angle", "channel"], kinds=list(rail_kinds), guided=["channel"],
                      lettered=list(rail_kinds),
                      closes=["angle-to-lintel", "channel-to-angle"], fastened=list(fastened),
                      visible={"angle": 1.0, "channel": 0.7}, context=1.0),
                 step(step=2, shows=["angle", "channel"], brings=["back-panel", "front-panel"], kinds=["A"],
                      lettered=["A"] if lettered else [],
                      guided=list(doors_guided), closes=[], fastened=[],
                      visible={"back-panel": door_shows, "front-panel": 1.0}, context=context)]),
    ])])


def _demo(contract: str, expect: float, because: str, *args, **kw):
    from quern.tree import Demonstration

    from .standards_piece import piece_world
    return Demonstration(contract=contract, nodes=piece_world() + [example_pages(**kw)], args=[_PIECE, *args],
                         expect=expect, because=because)


SPEC = {
    "furniture/steps_unlettered": [
        _demo("furniture/steps_unlettered", 0, "the rail's parts and the doors each carry their letter where "
              "they come in"),
        _demo("furniture/steps_unlettered", 1, "two doors drawn coming in, and nothing saying they are the "
              "parts lettered A", lettered=False),
        _demo("furniture/steps_unlettered", 1, "instructions that were not drawn have no page to judge", drawn=False),
    ],
    "furniture/drawn_off_the_paper": [
        _demo("furniture/drawn_off_the_paper", 0, "every picture and every text is on its page"),
        _demo("furniture/drawn_off_the_paper", 1, "a part of what is needed drawn below the foot of the page",
              spilled=True),
        _demo("furniture/drawn_off_the_paper", 1, "the name of the screws set below the foot of the page",
              off="Screws 3 x 16"),
    ],
    "furniture/pages_worded": [
        _demo("furniture/pages_worded", 0, "the piece's name, letters, counts and sizes: nothing to read as a sentence"),
        _demo("furniture/pages_worded", 1, "a sentence under a step's picture",
              sentence="Glue the channel to the angle."),
        _demo("furniture/pages_worded", 1, "instructions that were not drawn have no page to judge", drawn=False),
        _demo("furniture/pages_worded", 0, "a heading the drawing sets", sentence="Avant de commencer", role="heading"),
        _demo("furniture/pages_worded", 0, "the name of a tool no package draws", sentence="Serre-joint à pompe",
              role="label"),
        _demo("furniture/pages_worded", 0, "the sentence of a step that brings in, cuts and closes nothing",
              sentence="Passer deux couches de peinture.", role="note"),
    ],
    "furniture/steps_mixing_kinds": [
        _demo("furniture/steps_mixing_kinds", 0, "the rail, then the two doors, which carry one letter"),
        _demo("furniture/steps_mixing_kinds", 1, "an angle and a channel that carry two letters, in one step",
              rail_kinds=("R", "S")),
    ],
    "furniture/parts_without_a_line": [
        _demo("furniture/parts_without_a_line", 0, "each door is drawn apart from the rail with a line into it; the "
              "rail's own step attaches to nothing yet"),
        _demo("furniture/parts_without_a_line", 1, "the back door drawn in place, with nothing saying it goes in",
              doors_guided=("front-panel",)),
    ],
    "furniture/parts_hidden": [
        _demo("furniture/parts_hidden", 0, "the back door shows nine tenths of itself behind the front one", 0.5),
        _demo("furniture/parts_hidden", 1, "the back door all but hidden behind the front one", 0.5, door_shows=0.2),
    ],
    "furniture/steps_without_context": [
        _demo("furniture/steps_without_context", 0, "the rail still shows behind the doors that go in it", 0.1),
        _demo("furniture/steps_without_context", 1, "the doors drawn over the whole rail: nothing says what they "
              "go in", 0.1, context=0.02),
    ],
    "furniture/fastenings_not_shown": [
        _demo("furniture/fastenings_not_shown", 0, "the screws into the lintel and the glue line are drawn"),
        _demo("furniture/fastenings_not_shown", 2, "the rail's step shows two profiles and nothing that fixes them",
              fastened=()),
    ],
}
