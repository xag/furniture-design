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

from quern.provenance import Quantity
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
    return [f"step {s.get('step')}: nothing letters the part {k} it brings in" for s in _steps(node) if "lettered" in s
            for k in s.get("kinds") or [] if k not in s["lettered"] and k not in (s.get("wholes") or [])]


def steps_unlettered(tree: Quern, piece: str) -> float:
    """How many kinds of part a step brings in carry no letter in its picture: the letter the page of what
    is needed gives that kind. An assembly brought in whole carries none: its parts carried theirs when it
    was put together. A step drawn before the drawing noted its letters is judged as before, until drawn
    again."""
    return float(len(_unlettered(tree, piece)))


@_lines
def _off_the_paper_node(node: Node, tree: Quern, piece: str) -> list[str]:
    out = []
    for branch, doc in _DOCUMENTS:
        drawn = node if branch == INSTRUCTIONS else get_node(tree, f"{branch}/{piece.rpartition('/')[2]}")
        for p in _pages(drawn) if drawn is not None else []:
            where = f"page {p.payload.get('number')}" if branch == INSTRUCTIONS else f"{doc}, page {p.payload.get('number')}"
            if any(f.kind == "frame" and f.payload.get("kind") == "spill" for f in p.children):
                out.append(f"{where}: something is drawn beyond the edge of the paper")
            out += [f"{where}: \"{w['text']}\" is set beyond the edge of the paper"
                    for w in p.payload.get("words") or [] if w.get("off")]
    return out


def _off_the_paper(tree: Quern, piece: str) -> list[str]:
    return _off_the_paper_node(tree, piece, tree, piece)


_DOCUMENTS = ((INSTRUCTIONS, "the instructions"), ("plans", "the plans"), ("cutting", "the cutting sheet"))
_A_SIZE = re.compile(r"\d\s*×\s*\d")   # a text that prints a size: a number times a number
# how far a fastening's bar may be from its connector's proportions (thickness over length), drawn as
# sheets._fastening draws it: 16 long, between 1.2 and 6 thick
_BAR = (1.2 / 16, 6 / 16, 0.02)


def _things(tree: Quern, piece: str) -> tuple[set, dict, list[str]]:
    """The piece's parts (natives.bodies: what is already there is no part of it), which thing that
    stands apart each is in (scene.standing_apart, as the documents group them), and each thing's name."""
    from .natives import bodies
    from .scene import standing_apart

    base = piece.rstrip("/")
    bs = bodies(tree, piece)

    def holder(path: str) -> str:   # the part, or the outermost group of the piece holding it
        segs = path[len(base) + 1:].split("/")
        for i, seg in enumerate(segs[:-1]):
            if get_node(tree, "/".join([base, *segs[:i + 1]])).kind != "part":
                return seg
        return segs[-1]

    keyed = [(b.path, holder(b.path), b.lo, b.hi) for b in bs]
    groups = standing_apart(keyed)
    key = {path: k for path, k, _, _ in keyed}
    names = [" + ".join(dict.fromkeys((get_node(tree, f"{base}/{key[q]}").name or key[q]) for q in g)) for g in groups]
    return {b.path for b in bs}, {q: i for i, g in enumerate(groups) for q in g}, names


@_lines
def _unsupported_node(node: Node, tree: Quern, piece: str) -> list[str]:
    from .scene import connector_size, material_label

    pid = piece.rpartition("/")[2]
    parts, thing, names = _things(tree, piece)
    out: list[str] = []
    for branch, doc in _DOCUMENTS:
        drawn = node if branch == INSTRUCTIONS else get_node(tree, f"{branch}/{pid}")
        for page in _pages(drawn) if drawn is not None else []:
            where = f"{doc}, page {page.payload.get('number')}"
            for w in page.payload.get("words") or []:
                text, says = w.get("text", ""), w.get("says") or {}
                if not says:
                    if _A_SIZE.search(text):
                        out.append(f"{where}: \"{text}\" prints a size and says nothing of what it measures")
                    continue
                if "size" in says:
                    of = says["size"]
                    gone = [q for q in of if get_node(tree, q) is None]
                    if gone or not of:
                        out.append(f"{where}: \"{text}\" measures {gone[0] if gone else 'nothing'}, which is "
                                   "not in the model")
                    elif not says.get("each") and len({thing[q] for q in of if q in parts}) > 1:
                        apart = " and ".join(dict.fromkeys(names[thing[q]] for q in of if q in parts))
                        out.append(f"{where}: \"{text}\" measures across things that stand apart ({apart}): "
                                   "the model sets no distance between them but the one it draws them at")
                left = [m for m in dict.fromkeys(material_label(tree, piece, q) for q in says.get("material") or [])
                        if m and m not in text]
                if left:
                    out.append(f"{where}: \"{text}\" leaves out {'the material' if len(left) == 1 else 'materials'} "
                               f"the model gives: {'; '.join(left)}")
                if "name" in says:
                    named = get_node(tree, says["name"])
                    name = (named.name or named.id) if named is not None else ""
                    if named is None or name not in text:
                        out.append(f"{where}: \"{text}\" stands for {says['name']}, whose name is "
                                   f"{name or 'not in the model'}")
                fasteners = []
                for j in says.get("connector") or []:
                    joint = get_node(tree, j)
                    for c in ((joint.links or {}).get("uses") or []) if joint is not None else []:
                        known = get_node(tree, c)
                        fasteners.append((known.name if known is not None else "") or c.rsplit("/", 1)[-1])
                left = [f for f in dict.fromkeys(fasteners) if f not in text]
                if left:
                    out.append(f"{where}: \"{text}\" leaves out what the model fastens with: {'; '.join(left)}")
            coloured = [f.payload for f in page.children if (f.payload or {}).get("kind") == "colour"]
            if coloured:
                made_of = "; ".join(dict.fromkeys(material_label(tree, piece, c.get("part", "")) or "nothing"
                                                  for c in coloured))
                out.append(f"{where}: {len(coloured)} part{'s are' if len(coloured) > 1 else ' is'} drawn in a colour "
                           f"({', '.join(dict.fromkeys(c.get('colour', '') for c in coloured))}), which says what "
                           f"{'they are' if len(coloured) > 1 else 'it is'} made of, and the model says {made_of}")
            for f in page.children:
                facts = f.payload or {}
                if facts.get("kind") == "fastening":
                    drawn_as = facts.get("drawn")
                    for j in facts.get("joints") or []:
                        joint = get_node(tree, j)
                        size = connector_size(tree, joint.links or {}) if joint is not None else None
                        if drawn_as and size is None:
                            out.append(f"{where}: what fastens {j} is drawn as a bar of a size the model does "
                                       "not give it")
                        elif size and not drawn_as:
                            out.append(f"{where}: what fastens {j} is drawn as a dot, and the model gives it "
                                       f"{size[0]:g} × {size[1]:g}")
                        elif size and drawn_as:
                            lo, hi, slack = _BAR
                            want = min(max(size[1] / size[0], lo), hi)
                            if abs(drawn_as[1] / drawn_as[0] - want) > slack:
                                out.append(f"{where}: what fastens {j} is drawn {drawn_as[0]:g} by {drawn_as[1]:g}, "
                                           f"and the model gives it {size[0]:g} × {size[1]:g}")
    return out


def _unsupported(tree: Quern, piece: str) -> list[str]:
    return _unsupported_node(tree, piece, tree, piece)


def printed_unsupported(tree: Quern, piece: str) -> float:
    """How many things the piece's documents print or draw that its model does not say, read from what
    each noted as it drew (pages.model: the instructions, the plans, the cutting sheet): a size across
    things that stand apart, or of something that is no part of it; a text that cuts short the name or
    the material it stands for, or leaves out what fastens a joint it names; a part drawn in a colour,
    which says a material; a fastening drawn in proportions its connector does not have; and a size
    printed that says nothing of what it measures."""
    return float(len(_unsupported(tree, piece)))


def drawn_off_the_paper(tree: Quern, piece: str) -> float:
    """How many pages of the piece's documents (the instructions, the plans, the cutting sheet, as each
    noted what it drew) draw something beyond the edge of the paper, and how many texts are set beyond it:
    what is there is in the model and never reaches whoever builds."""
    return float(len(_off_the_paper(tree, piece)))


NATIVES = {
    "furniture/printed_unsupported": printed_unsupported,
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
    "furniture/printed_unsupported": _unsupported,
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


_DOORS = [f"{_PIECE}/angle", f"{_PIECE}/channel", f"{_PIECE}/front-door/front-panel", f"{_PIECE}/back-door/back-panel"]


def example_knowledge() -> list[Node]:
    """What the two doors are cut from and screwed with, named as the documents name them."""
    return [Node(id="materials", kind="", children=[
                Node(id="example-profile", kind="material", name="Aluminium profile, white")]),
            Node(id="connectors", kind="", children=[
                Node(id="example-screw", kind="connector", name="Screw 3 x 16",
                     params={k: Quantity(value=v, unit="mm", provenance="published", grounded=False)
                             for k, v in (("length", 16), ("thickness", 3))})])]


def example_pages(*, sentence: str | None = None, role: str = "", rail_kinds: tuple = ("R",), doors_guided: tuple = ("back-panel", "front-panel"),
                  door_shows: float = 0.9, context: float = 0.8, fastened: tuple = ("angle-to-lintel", "channel-to-angle"),
                  drawn: bool = True, lettered: bool | None = True, spilled: bool = False, off: str = "",
                  overall: tuple = (), material: str = "Aluminium profile", unsaid: bool = False,
                  coloured: bool = False, bar: tuple = (16, 3)) -> Node:
    """The instructions of the two doors as their drawing would note them: a cover with the piece's
    name and its overall size, a page of what is needed with counts, sizes, the material and the screws,
    then the rail, then the doors hung in it. Not `lettered`: the doors' step draws no letter beside them.
    `spilled`: the page of what is needed draws a part beyond the paper's foot; `off`: a text it sets there.
    What the pages say of the model: `overall`, more parts the overall size measures across; `material`,
    the material as printed; `unsaid`: a size printed with nothing said of what it measures; `coloured`: the
    front panel drawn in a wood's colour; `bar`: the screws' mark as drawn, length and thickness."""
    if not drawn:
        return Node(id=INSTRUCTIONS, kind="")
    lintel = f"{_PIECE}/angle-to-lintel"
    needed = [{"text": "A"}, {"text": "2 ×"},
              {"text": "600 × 8 × 1190", **({} if unsaid else {"says": {"size": [_DOORS[2]]}})},
              {"text": material, "role": "label", "says": {"material": [_DOORS[2]]}},
              {"text": "Screw 3 x 16", "role": "label", "says": {"connector": [lintel]}}]
    step = lambda **kw: Node(id=f"frame-{kw['step'] + 2}", kind="frame", payload={"kind": "step", **kw})  # noqa: E731
    return Node(id=INSTRUCTIONS, kind="", children=[Node(id="doors", kind="instructions", children=[
        Node(id="page-1", kind="page", payload={"number": 1, "words": [
                {"text": "Two sliding doors", "role": "name"},
                {"text": "Overall size : 1150 × 22 × 1200 mm", "role": "label",
                 "says": {"size": _DOORS + [f"{_PIECE}/{q}" for q in overall]}}]},
             children=[Node(id="frame-1", kind="frame", payload={"kind": "cover"})]
             + ([Node(id="frame-10", kind="frame", payload={"kind": "colour", "part": _DOORS[2], "colour": "0xe5c9a0"})]
                if coloured else [])),
        Node(id="page-2", kind="page", payload={"number": 2, "words": needed
                                                + ([{"text": off, "role": "label", "off": True}] if off else [])},
             children=[Node(id="frame-2", kind="frame", payload={"kind": "board", "mark": "A"}),
                       Node(id="frame-11", kind="frame", payload={"kind": "fastening", "joints": [lintel],
                                                                  "drawn": list(bar)})]
             + ([Node(id="frame-9", kind="frame", payload={"kind": "spill"})] if spilled else [])),
        Node(id="page-3", kind="page",
             payload={"number": 3, "words": [{"text": "1"}, {"text": "2"}] + ([{"text": sentence, **({"role": role} if role else {})}] if sentence else [])},
             children=[
                 step(step=1, shows=[], brings=["angle", "channel"], kinds=list(rail_kinds), guided=["channel"],
                      lettered=list(rail_kinds),
                      closes=["angle-to-lintel", "channel-to-angle"], fastened=list(fastened),
                      visible={"angle": 1.0, "channel": 0.7}, context=1.0),
                 step(step=2, shows=["angle", "channel"], brings=["back-panel", "front-panel"], kinds=["A"],
                      **({} if lettered is None else {"lettered": ["A"] if lettered else []}),
                      guided=list(doors_guided), closes=[], fastened=[],
                      visible={"back-panel": door_shows, "front-panel": 1.0}, context=context)]),
    ])])


def _demo(contract: str, expect: float, because: str, *args, piece: Node | None = None, **kw):
    from quern.tree import Demonstration

    from .standards_piece import piece_world
    return Demonstration(contract=contract, nodes=piece_world(piece) + example_knowledge() + [example_pages(**kw)],
                         args=[_PIECE, *args], expect=expect, because=because)


def _beside() -> Node:
    from .standards_piece import example_piece
    return example_piece(beside=300)


SPEC = {
    "furniture/printed_unsupported": [
        _demo("furniture/printed_unsupported", 0, "the overall size measures the doors and their rail, the panel's "
              "size, material and screws are the model's, and the screws' mark has their proportions"),
        _demo("furniture/printed_unsupported", 1, "a spare panel stands 300 mm beside the opening, and the cover "
              "prints one overall size across it and the doors", piece=_beside(), overall=("spare",)),
        _demo("furniture/printed_unsupported", 0, "the same spare panel beside, and the cover sizes the doors alone",
              piece=_beside()),
        _demo("furniture/printed_unsupported", 1, "the panel's material cut short to fit its box",
              material="Aluminium pro"),
        _demo("furniture/printed_unsupported", 1, "a panel's size printed with nothing saying what it measures",
              unsaid=True),
        _demo("furniture/printed_unsupported", 1, "the front panel drawn in a wood's colour", coloured=True),
        _demo("furniture/printed_unsupported", 1, "the screws marked with a biscuit's fixed proportions",
              bar=(16, 6)),
        _demo("furniture/printed_unsupported", 1, "instructions that were not drawn have no page to judge",
              drawn=False),
    ],
    "furniture/steps_unlettered": [
        _demo("furniture/steps_unlettered", 0, "the rail's parts and the doors each carry their letter where "
              "they come in"),
        _demo("furniture/steps_unlettered", 1, "two doors drawn coming in, and nothing saying they are the "
              "parts lettered A", lettered=False),
        _demo("furniture/steps_unlettered", 1, "instructions that were not drawn have no page to judge", drawn=False),
        _demo("furniture/steps_unlettered", 0, "steps drawn before the drawing noted letters are judged as before",
              lettered=None),
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
