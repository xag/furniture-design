"""furniture-standards@: what a tool's entry is held to, for each use it may be put to.

A standard is knowledge like the rest: rules, and in the tree the criteria that group them
and the levels that say which criteria a use requires (kinds `criterion` and `level`, read by
quern.certify.certificate, which knows nothing of tools). It is a package of its own, beside
furniture-design@: its rules grade an entry and refuse none, so they are not among the rules
every design and every node of the knowledge is held to. A tool is certified by running this
package on it; a better standard is a new version of this file, and nothing that reads
certificates changes.

The figures' reliability is quern's grounding contracts (thinly_witnessed, disagreeing): a
figure rests on the observations its lineage reaches, and is closed when two that could each
be wrong on their own agree. The four contracts here are what needs a tool's own data: its
model drawn, its model against its figures, its figures against each other, and the
languages it says itself in.
"""

from __future__ import annotations

import quern.grounding  # noqa: F401 - registers the grounding contracts the rules call
from quern.certify import register_explainer
from quern.grounding import agree
from quern.library import CounterExample, Package
from quern.provenance import Quantity
from quern.solver import SolverDef
from quern.tree import Demonstration, KindDef, Node, Quern, Rule, get_node, register_native

from . import standards_pages as drawn
from . import standards_piece as piece
from . import standards_words as words

STANDARDS = "standards"


# --- the contracts ------------------------------------------------------------------------

def _tool(tree: Quern, path: str) -> Node:
    node = get_node(tree, path)
    if node is None:
        raise ValueError(f"no node at '{path}'")
    return node


def _solids(model) -> list[dict]:
    if not isinstance(model, dict):
        return []
    return list(model.get("parts") or []) + [s for pose in (model.get("poses") or {}).values() for s in pose]


def model_draws(tree: Quern, tool: str) -> float:
    """1 when the tool's payload model draws as line art (its parts, and its flat pose), else 0."""
    from . import lineart

    model = _tool(tree, tool).payload.get("model")
    if not isinstance(model, dict) or not model.get("parts"):
        return 0.0
    try:
        solids = list(model["parts"]) + list((model.get("poses") or {}).get("flat") or [])
        return 1.0 if lineart.draw(lineart.solids(solids), lineart.View.axo(), px=300).lines else 0.0
    except Exception:  # noqa: BLE001 - a model that does not draw is one that does not draw
        return 0.0


def _measure(solid: dict, of: str) -> float | None:
    op = solid.get("op")
    try:
        if op == "cyl":
            return {"diameter": 2.0 * solid["r"], "height": float(solid["h"]), "length": float(solid["h"])}.get(of)
        if op in ("box", "rbox"):
            ext = [abs(h - lo) for lo, h in zip(solid["lo"], solid["hi"])]
            return {"x": ext[0], "y": ext[1], "z": ext[2], "length": max(ext), "thickness": min(ext),
                    "width": sorted(ext)[1]}.get(of)
        if op == "prism":
            return {"x": abs(solid["x"][1] - solid["x"][0])}.get(of)
    except (KeyError, TypeError, IndexError):
        return None
    return None


def _mismatches(tree: Quern, tool: str) -> list[str]:
    node = _tool(tree, tool)
    out = []
    for s in _solids(node.payload.get("model")):
        tag = s.get("shows") if isinstance(s, dict) else None
        if not isinstance(tag, dict):
            continue
        q = node.params.get(tag.get("param"))
        got = _measure(s, str(tag.get("of", "")))
        if q is None or got is None:
            out.append(f"{tag.get('param')}: a solid is tagged as showing it, and it is not a figure "
                       f"of the tool that a {s.get('op')} measures as {tag.get('of')}")
        elif not agree(Quantity(value=got, unit=q.unit, provenance="derived", grounded=False), q):
            out.append(f"{tag['param']}: the model's solid measures {got:g}, the figure is {q.value:g}")
    return out


def model_mismatches(tree: Quern, tool: str) -> float:
    """How many solids of the tool's model, tagged "shows": {"param", "of"}, do not measure the
    figure they are tagged with (of: diameter, length, width, thickness, height, x, y or z)."""
    return float(len(_mismatches(tree, tool)))


def model_shown(tree: Quern, tool: str) -> float:
    """How many of the tool's figures a solid of its model is tagged as showing."""
    node = _tool(tree, tool)
    return float(len({s["shows"].get("param") for s in _solids(node.payload.get("model"))
                      if isinstance(s, dict) and isinstance(s.get("shows"), dict)} & set(node.params)))


def _out_of_order(tree: Quern, tool: str) -> list[str]:
    p = {k: q.value for k, q in _tool(tree, tool).params.items()}
    out = [f"{k} ({p[k]:g}) is above {k[:-4]}_max ({p[k[:-4] + '_max']:g})"
           for k in sorted(p) if k.endswith("_min") and k[:-4] + "_max" in p and p[k] > p[k[:-4] + "_max"]]
    for low, high in (("blade_thickness", "kerf"), ("kerf", "max_kerf")):
        if low in p and high in p and p[low] > p[high]:
            out.append(f"{low} ({p[low]:g}) is above {high} ({p[high]:g})")
    return out


def figures_out_of_order(tree: Quern, tool: str) -> float:
    """How many pairs of the tool's figures contradict each other: a minimum above its maximum
    (<x>_min, <x>_max), a blade's body thicker than its cut, a cut wider than the widest blade."""
    return float(len(_out_of_order(tree, tool)))


def _languages() -> list[str]:
    """The languages furniture-design writes its documents in."""
    from . import drawings, report, sheets, viewer
    return sorted(set(report.TEXT) & set(drawings.LABELS) & set(sheets.LABELS) & set(viewer.WORDS))


def _unsaid(tree: Quern, tool: str) -> list[str]:
    say = _tool(tree, tool).payload.get("say") or {}
    return [lang for lang in _languages()
            if not ((say.get(lang) or {}).get("name") and (say.get(lang) or {}).get("method"))]


def unsaid_languages(tree: Quern, tool: str) -> float:
    """How many of the languages the documents are written in the tool does not say its name and
    its method in (payload say.<language>.name and .method)."""
    return float(len(_unsaid(tree, tool)))


NATIVES = {
    "furniture/model_draws": model_draws,
    "furniture/model_mismatches": model_mismatches,
    "furniture/model_shown": model_shown,
    "furniture/figures_out_of_order": figures_out_of_order,
    "furniture/unsaid_languages": unsaid_languages,
}

EXPLAINERS = {
    "furniture/model_mismatches": _mismatches,
    "furniture/figures_out_of_order": _out_of_order,
    "furniture/unsaid_languages": lambda tree, tool: [f"not said in {lang}" for lang in _unsaid(tree, tool)],
}


# --- the criteria and the levels --------------------------------------------------------------

def _criterion(id_: str, name: str, measures: str, *rules: str, of: str = "tool", per: tuple = ()) -> Node:
    """`per`: the clauses of the knowledge the criterion is held for, when it rests on a publication."""
    return Node(id=id_, kind="criterion", name=name, links={"per": list(per)} if per else {},
                payload={"applies_to": of, "measures": measures, "rules": list(rules), "say": words.SAY[id_]})


def _level(id_: str, name: str, *criteria: str, of: str = "tool", allows: tuple = ()) -> Node:
    return Node(id=id_, kind="level", name=name, payload={"of": of, "allows": list(allows), "say": words.SAY[id_]},
                links={"requires": [f"{STANDARDS}/{c}" for c in criteria]})


def guidance() -> Node:
    """What whoever writes a tool or a piece is told of the standards: a branch to merge beside the
    knowledge's own guidance."""
    from .guidance import branch, say

    return branch(
        say("certifying-a-tool", "A tool is certified, not only written", """
            A tool is not done when it is written: it is certified against the standards (their criteria, and
            the uses each level stands for). Its certificate says the uses it is fit for and, for each it is
            not yet, what to do, in the standards' own words: go on until it is certified, in the same
            conversation, without being asked. A value counts as observed only when the words printed are found
            in its source's document with that value: give each clause payload rows ({param: the words as
            printed}) and an address the document can be fetched from. A figure derived_from two documents, or
            from a document and the figure of another tool it must equal ("tools/<id>/<param>": the disc a
            sander takes), rests on two observations."""),
        say("certifying-a-pieces-design", "A piece's design is certified with its ledger", """
            What is hinged is a motion too (type turn: the line it turns about, where that line is, and how
            far it turns, in degrees): a turning part is held when that line lies on it and on the part that
            carries its hinges, and must cross nothing through its travel.
            A piece's design is certified against the same standards (the criteria and levels of a piece): its
            certificate says the uses the design is fit for and, for each it is not yet, what to do. It reads
            the piece and its ledger together. Every sentence of the purpose is answered by a decision of the
            ledger whose payload answers quotes the words it answers, and which links realised_by to the parts,
            assemblies, joints or motions of the piece that realise it ("pieces/<piece>/..."); a quantity the
            ledger states in words is a figure of that decision (payload figures: [{"says": the words, "value",
            "unit", "tolerance"?, "is": an expression over the piece's params}]) the model must give. Every
            part is held: by a joint that joins it (links joins; payload to names what it is fixed to outside
            the piece, a wall, a lintel), or by a motion that moves it. What moves is a node of kind motion
            beneath the piece (its kind says what it states); a sliding part is held when its guides stop it on
            both sides, and must cross nothing along its travel. When the certificate asks how the piece works
            and the person has not said (which part runs in which, what is fixed to what), ask them: do not
            decide it for them and do not write a decision they did not make."""),
        say("instructions-at-their-level", "When a piece's assembly instructions are shown", """
            A piece's assembly instructions are shown to the person only once its design reaches the level that
            allows them (the level whose payload allows names assembly). Until then, say so to the person when
            they ask for the instructions, and do what the certificate says is left.""",
            f"{STANDARDS}/piece-instructions"),
    )


def knowledge() -> list[Node]:
    """The branch a tree mounts beside the knowledge: the criteria a tool is judged by and the levels
    it may reach, most demanding last."""
    return [Node(id=STANDARDS, kind="", children=[
        _criterion("tool-is-identified", "The tool names its maker and the clauses it is read from", "completeness",
                   "a-tool-names-its-maker", "a-tool-rests-on-clauses"),
        _criterion("tool-is-drawn", "The tool has a model that draws", "presentation", "a-tool-has-a-model-that-draws"),
        _criterion("tool-drawing-is-true", "The model shows the tool's figures", "consistency",
                   "a-tools-model-shows-its-figures"),
        _criterion("tool-is-said", "The tool says its name and method in every language", "completeness",
                   "a-tool-says-itself-in-every-language"),
        _criterion("saw-states-its-cut", "A saw states its cut and its depth", "completeness",
                   "a-saw-states-its-cut", "a-saw-states-its-depth"),
        _criterion("tool-figures-are-consistent", "The tool's figures do not contradict each other", "consistency",
                   "a-tools-figures-are-in-order", "a-tools-figures-agree-with-what-they-are-read-from"),
        _criterion("tool-figures-are-observed", "Every figure was found printed in a document", "reliability",
                   "a-tools-figures-each-rest-on-an-observation"),
        _criterion("tool-figures-are-closed", "Every figure rests on two observations that agree", "reliability",
                   "a-tools-figures-each-rest-on-two-observations"),
        _level("tool-listed", "Shown, drawn, in a person's tools", "tool-is-identified", "tool-is-drawn"),
        _level("tool-cuts-parts", "Its figures are read by a piece's checks", "tool-is-identified", "saw-states-its-cut",
               "tool-figures-are-consistent", "tool-figures-are-observed"),
        _level("tool-in-instructions", "Drawn at work in assembly instructions", "tool-is-identified",
               "tool-is-drawn", "tool-drawing-is-true", "tool-is-said", "tool-figures-are-consistent"),
        _level("tool-shared", "Taken into the shared packages", "tool-is-identified", "tool-is-drawn",
               "tool-drawing-is-true", "tool-is-said", "saw-states-its-cut", "tool-figures-are-consistent",
               "tool-figures-are-observed", "tool-figures-are-closed"),
        _criterion("piece-is-explained", "Every sentence of the piece's purpose is answered by a decision that names "
                   "what realises it", "completeness", "a-pieces-purpose-is-answered",
                   "a-pieces-decisions-name-what-realises-them", of="piece"),
        _criterion("piece-agrees-with-its-ledger", "The model gives the numbers the piece's ledger states",
                   "consistency", "a-pieces-stated-numbers-are-checked", "a-pieces-figures-are-those-of-its-model",
                   of="piece"),
        _criterion("piece-holds-together", "Every part is fixed by a joint or moved by a motion", "completeness",
                   "a-pieces-parts-are-fixed-or-guided", of="piece"),
        _criterion("piece-mechanisms-work", "What slides is held on both sides, what turns is carried, and each "
                   "has room along its travel", "consistency", "a-pieces-motions-are-stated",
                   "a-pieces-sliding-parts-are-held", "a-pieces-sliding-parts-have-room",
                   "a-pieces-turning-parts-are-carried", "a-pieces-turning-parts-have-room", of="piece"),
        _criterion("piece-steps-build-it", "The assembly steps bring in every part and close every joint, each "
                   "once its parts are in", "completeness", "a-pieces-steps-bring-in-every-part",
                   "a-pieces-steps-close-every-joint", of="piece"),
        _criterion("piece-can-be-made", "Every part says what it is cut from and with, and every joint what "
                   "fastens it and how many", "completeness", "a-pieces-parts-say-how-they-are-cut",
                   "a-pieces-joints-say-what-fastens-them", of="piece"),
        _criterion("pages-are-drawn-not-written", "No page of the instructions carries a sentence",
                   "presentation", "a-pieces-pages-carry-no-sentence", of="piece",
                   per=("sources/ikea-why-only-pictures/pictures-not-words",)),
        _criterion("steps-show-how-parts-attach", "Each step attaches one kind of part, drawn apart with a line "
                   "to where it goes, and shows what fastens each joint it closes", "presentation",
                   "a-pieces-steps-attach-one-kind-of-part", "a-pieces-new-parts-are-drawn-apart-with-a-line",
                   "a-pieces-fastenings-are-shown", of="piece",
                   per=("sources/agrawala-2003/grouping", "sources/agrawala-2003/step-by-step",
                        "sources/agrawala-2003/action-diagrams")),
        _criterion("steps-show-their-parts", "Each step's picture shows the parts it brings in, and enough of "
                   "those already there to place them", "presentation", "a-pieces-new-parts-are-visible",
                   "a-pieces-steps-keep-their-context", of="piece",
                   per=("sources/agrawala-2003/visibility", "sources/agrawala-2003/visibility-scores")),
        _level("piece-settled", "Its design says what the person asked for", "piece-is-explained",
               "piece-agrees-with-its-ledger", of="piece"),
        _level("piece-works", "It holds together and what moves in it works", "piece-is-explained",
               "piece-agrees-with-its-ledger", "piece-holds-together", "piece-mechanisms-work", of="piece"),
        _level("piece-buildable", "It can be cut and fastened from what it states", "piece-is-explained",
               "piece-agrees-with-its-ledger", "piece-holds-together", "piece-mechanisms-work", "piece-can-be-made",
               of="piece"),
        _level("piece-instructions", "Its assembly instructions are shown", "piece-is-explained",
               "piece-agrees-with-its-ledger", "piece-holds-together", "piece-mechanisms-work",
               "piece-can-be-made", "piece-steps-build-it", "pages-are-drawn-not-written", "steps-show-how-parts-attach",
               "steps-show-their-parts", of="piece", allows=("assembly",)),
    ])]


# --- a tool that meets the standard, and the ways one does not ------------------------------

def _printed(value: float, unit: str, where: str) -> Quantity:
    return Quantity(value=value, unit=unit, provenance="published", grounded=True, source=where)


def _read(value: float, unit: str, *refs: str) -> Quantity:
    return Quantity(value=value, unit=unit, provenance="derived", grounded=False, derived_from=list(refs))


def _document(id_: str, pad: float = 125.0, grounded: bool = True) -> Node:
    q = _printed(pad, "mm", "Technical data")
    return Node(id=id_, kind="source", name=f"An example maker's {id_}",
                payload={"publisher": "An example maker", "authority": "maker", "licence": "copyrighted"},
                children=[Node(id="data", kind="clause", payload={"locator": "Technical data"},
                               params={"pad_diameter": q if grounded else q.model_copy(update={"grounded": False}),
                                       "speed_min": _printed(6000, "1/min", "Technical data"),
                                       "speed_max": _printed(12000, "1/min", "Technical data"),
                                       "kerf": _printed(2.0, "mm", "Technical data"),
                                       "max_cut_depth": _printed(50.0, "mm", "Technical data")})])


_PAD = {"op": "cyl", "r": 62.5, "h": 10, "axis": "z", "at": [0, 0, 0],
        "shows": {"param": "pad_diameter", "of": "diameter"}}
_BODY = {"op": "rbox", "lo": [-40, -60, 10], "hi": [40, 60, 120], "r": 12, "axis": "z"}
_SAY = {lang: {"name": "Example sander", "method": ["Sand."]} for lang in ("fr", "en")}


def example_tool(*, documents: tuple[str, ...] = ("manual", "page"), pad: float = 125.0, maker: str = "An example maker",
                 model: dict | None = None, say: dict | None = None, per: bool = True, saw: bool = False,
                 speed_min: float = 6000, drop: tuple[str, ...] = ()) -> Node:
    """An example sander (or, with saw, a saw) read from the documents named."""
    def refs(name: str) -> list[str]:
        return [f"sources/{d}/data/{name}" for d in documents]
    params = {"pad_diameter": _read(pad, "mm", *refs("pad_diameter")),
              "speed_min": _read(speed_min, "1/min", *refs("speed_min")),
              "speed_max": _read(12000, "1/min", *refs("speed_max"))}
    payload = {"maker": maker, "does": "sands wood", "say": _SAY if say is None else say,
               "model": {"parts": [_PAD, _BODY]} if model is None else model}
    if saw:
        payload["saw_kind"] = "pull saw"
        params |= {"kerf": _read(2.0, "mm", *refs("kerf")), "max_cut_depth": _read(50.0, "mm", *refs("max_cut_depth"))}
    return Node(id="example-sander", kind="tool", name="Example sander", payload=payload,
                params={k: v for k, v in params.items() if k not in drop},
                links={"per": [f"sources/{d}/data" for d in documents]} if per else {})


def _world(tool: Node | None = None, *, documents: list[Node] | None = None, standards: Node | None = None) -> list[Node]:
    from .knowledge import instruction_sources

    return [Node(id="sources", kind="", children=(documents or [_document("manual"), _document("page")])
                 + instruction_sources()),
            Node(id="tools", kind="", children=[tool or example_tool(), example_tool(saw=True).model_copy(
                update={"id": "example-saw", "name": "Example saw"})]),
            standards or knowledge()[0]]


SPEC = {
    "furniture/model_draws": [
        Demonstration(contract="furniture/model_draws", nodes=_world(), args=["tools/example-sander"], expect=1,
                      because="a pad and a body: it draws"),
        Demonstration(contract="furniture/model_draws", nodes=_world(example_tool(model={})),
                      args=["tools/example-sander"], expect=0, because="a tool with no model has no drawing"),
        Demonstration(contract="furniture/model_draws",
                      nodes=_world(example_tool(model={"parts": [{"op": "sphere", "r": 10}]})),
                      args=["tools/example-sander"], expect=0, because="a solid line art has no op for draws nothing"),
    ],
    "furniture/model_mismatches": [
        Demonstration(contract="furniture/model_mismatches", nodes=_world(), args=["tools/example-sander"], expect=0,
                      because="the solid tagged as the pad measures the pad's diameter"),
        Demonstration(contract="furniture/model_mismatches", nodes=_world(example_tool(pad=150.0)),
                      args=["tools/example-sander"], expect=1,
                      because="the pad drawn is 125 and the figure says 150: one of them is wrong"),
    ],
    "furniture/model_shown": [
        Demonstration(contract="furniture/model_shown", nodes=_world(), args=["tools/example-sander"], expect=1,
                      because="one figure, the pad's diameter, is shown by a solid"),
        Demonstration(contract="furniture/model_shown", nodes=_world(example_tool(model={"parts": [_BODY]})),
                      args=["tools/example-sander"], expect=0, because="a model none of whose solids is tagged"),
    ],
    "furniture/figures_out_of_order": [
        Demonstration(contract="furniture/figures_out_of_order", nodes=_world(), args=["tools/example-sander"],
                      expect=0, because="the slowest speed is under the fastest"),
        Demonstration(contract="furniture/figures_out_of_order", nodes=_world(example_tool(speed_min=20000)),
                      args=["tools/example-sander"], expect=1, because="a minimum above its maximum"),
    ],
    "furniture/unsaid_languages": [
        Demonstration(contract="furniture/unsaid_languages", nodes=_world(), args=["tools/example-sander"], expect=0,
                      because="its name and method in French and in English"),
        Demonstration(contract="furniture/unsaid_languages", nodes=_world(example_tool(say={"en": _SAY["en"]})),
                      args=["tools/example-sander"], expect=1, because="said in English only"),
    ],
}


NATIVES |= piece.NATIVES | drawn.NATIVES
EXPLAINERS |= piece.EXPLAINERS | drawn.EXPLAINERS
SPEC |= piece.SPEC | drawn.SPEC


def register() -> None:
    for name, fn in NATIVES.items():
        register_native(name, fn, SPEC[name])
    for name, fn in EXPLAINERS.items():
        register_explainer(name, fn)


# --- the package: kinds, rules, criteria and levels ------------------------------------------

VOCABULARY = [
    KindDef(kind="criterion", description=(
        "One thing a standard judges about a subject: payload applies_to (the kind of node it judges), "
        "rules (the names of the rules that judge it) and measures (completeness, reliability, "
        "consistency or presentation). Held when every rule it names holds on the subject and beneath "
        "it. Read by quern.certify.")),
    KindDef(kind="level", description=(
        "A use a subject may be put to: payload of (the kind of subject) and allows (what reaching it "
        "opens, by the names its readers ask by: assembly, a piece's assembly instructions shown to "
        "people), and the link requires to the criteria that use needs. Reached when every criterion it "
        "requires is held. Read by quern.certify."),
        links={"requires": "the criteria this use needs"}),
    KindDef(kind="motion", description=(
        "Something of a piece that moves, beneath the piece: payload type (slide, or turn for what is hinged), "
        "axis (x, y or z: the way it slides, or the line it turns about) and travel ([from, to] from where the "
        "parts are modelled, in mm for a slide and in degrees for a turn, anticlockwise positive seen with the "
        "two other axes in their order; numbers or expressions over the piece's params); for a turn, pivot "
        "([a, b]: where the line it turns about is, in the plane across the axis, in the piece's frame); the "
        "link moves to the parts or assemblies that move, and guided_by to the parts that guide them or that "
        "carry their hinges. It places and weighs nothing."),
        links={"moves": "the parts or assemblies that move",
               "guided_by": "the parts that guide them, or that carry their hinges"}),
]

_MEASURES = ("completeness", "reliability", "consistency", "presentation")

RULES = [
    Rule(name="a-criterion-names-what-it-judges", kind="criterion",
         expr="len(payload(self, 'rules', '')) > 0 and len(payload(self, 'applies_to', '')) > 0 and ("
              + " or ".join(f"payload(self, 'measures', '') == '{m}'" for m in _MEASURES) + ")",
         description="A criterion names the kind of node it judges, the rules that judge it, and which of "
                     "completeness, reliability, consistency or presentation it measures."),
    Rule(name="a-level-requires-criteria", kind="level",
         expr="len(payload(self, 'of', '')) > 0 and len(linked(self, 'requires')) > 0 and "
              "every(c, linked(self, 'requires'), kind(c) == 'criterion')",
         description="A level says the kind of subject it is a use of and requires criteria that exist."),
    Rule(name="a-tool-names-its-maker", kind="tool", expr="len(payload(self, 'maker', '')) > 0",
         description="Name the tool's maker (payload maker)."),
    Rule(name="a-tool-rests-on-clauses", kind="tool",
         expr="len(linked(self, 'per')) > 0 and every(c, linked(self, 'per'), kind(c) == 'clause')",
         description="Link the tool per to the clauses of its maker's documents it is read from."),
    Rule(name="a-tool-says-itself-in-every-language", kind="tool",
         expr="solve('furniture/unsaid_languages', self) == 0",
         description="Say the tool's name and method (payload say.<language>.name and .method) in every "
                     "language the documents are written in."),
    Rule(name="a-tool-has-a-model-that-draws", kind="tool", expr="solve('furniture/model_draws', self) == 1",
         description='Give the tool its model (payload model {"parts": [solid, ...]}, mm, Z up, built from the '
                     "maker's dimensions and photos): it is drawn from it."),
    Rule(name="a-tools-model-shows-its-figures", kind="tool",
         expr="solve('furniture/model_mismatches', self) == 0 and solve('furniture/model_shown', self) > 0",
         description='Tag the solids of the model that show a figure ("shows": {"param", "of"}), each measuring '
                     "the figure it shows, so the drawing is held to the figures."),
    Rule(name="a-tools-figures-are-in-order", kind="tool", expr="solve('furniture/figures_out_of_order', self) == 0",
         description="A tool's figures do not contradict each other: correct the one that is wrong."),
    Rule(name="a-tools-figures-each-rest-on-an-observation", kind="tool",
         expr="solve('grounding/thinly_witnessed', self, 1) == 0",
         description="Derive every figure from a clause whose value was found printed in its document: give the "
                     "words exactly as printed (the clause's payload rows) and an address that can be fetched."),
    Rule(name="a-tools-figures-each-rest-on-two-observations", kind="tool",
         expr="solve('grounding/thinly_witnessed', self) == 0",
         description="Close every figure: derive it from a second document of its maker that prints it (the "
                     "product page, the data sheet, a parts or accessories list), or from the figure of "
                     "another tool it must equal (the disc a sander takes, the hose a port takes)."),
    Rule(name="a-tools-figures-agree-with-what-they-are-read-from", kind="tool",
         expr="solve('grounding/disagreeing', self) == 0",
         description="A figure and a value it is derived from differ: find which is right (a unit, another "
                     "variant of the tool) and correct it."),
    Rule(name="a-saw-states-its-cut", kind="tool",
         expr="len(payload(self, 'saw_kind', '')) == 0 or states(self, 'kerf') or states(self, 'max_kerf')",
         description="State the cut of the saw's blade (kerf, or max_kerf), from its maker's document."),
    Rule(name="a-pieces-purpose-is-answered", kind="piece", expr="solve('furniture/purpose_uncovered', self) == 0",
         description="Answer every sentence of the piece's purpose with a decision in its ledger whose payload "
                     "answers quotes the words it answers; ask the person what you do not know, and do not "
                     "decide for them how the piece works."),
    Rule(name="a-pieces-decisions-name-what-realises-them", kind="piece",
         expr="solve('furniture/unrealised_decisions', self) == 0",
         description="Link each decision of the piece's ledger realised_by to the parts, assemblies, joints or "
                     "motions of the piece that realise it."),
    Rule(name="a-pieces-stated-numbers-are-checked", kind="piece", expr="solve('furniture/unchecked_numbers', self) == 0",
         description='Hold the model to every quantity the ledger states in words: a figure of the decision '
                     '(payload figures: {"says", "value", "is": an expression over the piece\'s params}).'),
    Rule(name="a-pieces-figures-are-those-of-its-model", kind="piece", expr="solve('furniture/figures_off', self) == 0",
         description="The model does not give a number the ledger states: change the model, or ask the person "
                     "and change the decision."),
    Rule(name="a-pieces-parts-are-fixed-or-guided", kind="piece", expr="solve('furniture/loose_parts', self) == 0",
         description="Say what holds every part: a joint that joins it (to another part, or payload to: what it "
                     "is fixed to outside the piece), or a motion that moves it."),
    Rule(name="a-pieces-motions-are-stated", kind="piece", expr="solve('furniture/motions_unstated', self) == 0",
         description="State each motion whole: type slide or turn, its axis, its travel [from, to], for a turn "
                     "its pivot, what moves and what it is guided by."),
    Rule(name="a-pieces-turning-parts-are-carried", kind="piece", expr="solve('furniture/unheld_turns', self) == 0",
         description="A turning part turns about a line on itself and on what carries it: put its pivot where its "
                     "hinge is, and name the part the hinge is fixed to (guided_by)."),
    Rule(name="a-pieces-turning-parts-have-room", kind="piece", expr="solve('furniture/turn_crossings', self) == 0",
         description="A turning part crosses another part through its travel: move the pivot or the part, or turn "
                     "it the other way, so it swings clear."),
    Rule(name="a-pieces-sliding-parts-are-held", kind="piece", expr="solve('furniture/unheld_slides', self) == 0",
         description="A sliding part needs a wall on both sides, of the parts its motion says guide it: place a "
                     "guide there, or name the part that is."),
    Rule(name="a-pieces-sliding-parts-have-room", kind="piece", expr="solve('furniture/slide_crossings', self) == 0",
         description="A sliding part crosses another part along its travel: move one of them, so it runs clear."),
    Rule(name="a-pieces-steps-bring-in-every-part", kind="piece", expr="solve('furniture/steps_unplaced', self) == 0",
         description="Bring every part in by an assembly step (payload steps, a step's add)."),
    Rule(name="a-pieces-steps-close-every-joint", kind="piece", expr="solve('furniture/joints_misclosed', self) == 0",
         description="Close every joint in an assembly step (a step's joints), no sooner than the step that "
                     "brings in the last part it joins."),
    Rule(name="a-pieces-parts-say-how-they-are-cut", kind="piece", expr="solve('furniture/parts_uncut', self) == 0",
         description="Link every part uses to the material it is cut from and sawn_with to the saw, or the shop's "
                     "cutting service, that cuts it out: ask the person what they buy and what they cut with."),
    Rule(name="a-pieces-joints-say-what-fastens-them", kind="piece",
         expr="solve('furniture/joints_unfastened', self) == 0",
         description="Link every joint uses to what fastens it (a connector, screws, a glue: a node of the "
                     "knowledge, or of the person's own package) and state how many it takes (param count)."),
    Rule(name="a-pieces-pages-carry-no-sentence", kind="piece", expr="solve('furniture/pages_worded', self) == 0",
         description="Draw what each text on the instructions' pages says, and take the text off: a count, a "
                     "size, a part's letter and the piece's name stay (IKEA: pictures, because the instructions "
                     "are read in every language)."),
    Rule(name="a-pieces-steps-attach-one-kind-of-part", kind="piece",
         expr="solve('furniture/steps_mixing_kinds', self) == 0",
         description="Give each kind of part its own step: parts that carry the same letter come in together, "
                     "another kind in the next step (Agrawala 2003, step-by-step instructions)."),
    Rule(name="a-pieces-new-parts-are-drawn-apart-with-a-line", kind="piece",
         expr="solve('furniture/parts_without_a_line', self) == 0",
         description="Say which way each part comes in (a step's direction), so it is drawn apart from where "
                     "it goes with a line leading there (Agrawala 2003, action diagrams)."),
    Rule(name="a-pieces-fastenings-are-shown", kind="piece", expr="solve('furniture/fastenings_not_shown', self) == 0",
         description="State where the connectors of each joint a step closes sit (the joint's positions, or a "
                     "connector that gives them), so the step's picture draws what fastens it (Agrawala 2003, "
                     "action diagrams: the attachment operations depicted)."),
    Rule(name="a-pieces-new-parts-are-visible", kind="piece",
         expr="solve('furniture/parts_hidden', self, param('sources/agrawala-2003/visibility-scores', 'current_parts')) == 0",
         description="A part a step brings in is hidden behind another: bring it in in a step of its own, or "
                     "from the side it shows from (Agrawala 2003, visibility)."),
    Rule(name="a-pieces-steps-keep-their-context", kind="piece",
         expr="solve('furniture/steps_without_context', self, param('sources/agrawala-2003/visibility-scores', 'previous_parts')) == 0",
         description="The parts a step brings in cover those already there: bring fewer in at once, so what "
                     "they attach to still shows (Agrawala 2003, visibility)."),
    Rule(name="a-saw-states-its-depth", kind="tool",
         expr="len(payload(self, 'saw_kind', '')) == 0 or states(self, 'max_cut_depth')",
         description="State the thickest board the saw cuts (max_cut_depth), from its maker's document."),
]

# what each rule says to people when it does not hold, per language (standards_words.RED): every rule says it
RULES = [r.model_copy(update={"messages": words.messages(r.name)}) for r in RULES]

register()

EXAMPLES = _world() + piece.piece_world() + [drawn.example_pages()]


def _piece_case(pages: dict | None = None, **kw) -> list[Node]:
    """The example piece in its world, with its instructions as drawn (`pages`: example_pages' knobs)."""
    return _world() + piece.piece_world(**kw) + [drawn.example_pages(**(pages or {}))]


_BAD_STANDARD = Node(id=STANDARDS, kind="", children=[
    Node(id="says-nothing", kind="criterion", payload={"applies_to": "tool", "measures": "completeness"}),
    Node(id="needs-nothing", kind="level", payload={"of": "tool"}, links={"requires": ["standards/ghost"]})])

COUNTER_EXAMPLES = [
    CounterExample(rule="a-criterion-names-what-it-judges", nodes=_world(standards=_BAD_STANDARD),
                   because="a criterion that names no rule judges nothing"),
    CounterExample(rule="a-level-requires-criteria", nodes=_world(standards=_BAD_STANDARD),
                   because="a level requiring a criterion that does not exist"),
    CounterExample(rule="a-tool-names-its-maker", nodes=_world(example_tool(maker="")),
                   because="a tool whose maker nobody named"),
    CounterExample(rule="a-tool-rests-on-clauses", nodes=_world(example_tool(per=False)),
                   because="a tool linked to no clause"),
    CounterExample(rule="a-tool-says-itself-in-every-language", nodes=_world(example_tool(say={"en": _SAY["en"]})),
                   because="a tool said in English only"),
    CounterExample(rule="a-tool-has-a-model-that-draws", nodes=_world(example_tool(model={})),
                   because="a tool with figures, sources and a method, and no model: a name with no drawing"),
    CounterExample(rule="a-tools-model-shows-its-figures", nodes=_world(example_tool(pad=150.0),
                   documents=[_document("manual", 150.0), _document("page", 150.0)]),
                   because="the pad drawn is 125 where both documents print 150"),
    CounterExample(rule="a-tools-figures-are-in-order", nodes=_world(example_tool(speed_min=20000)),
                   because="a slowest speed above the fastest"),
    CounterExample(rule="a-tools-figures-each-rest-on-an-observation",
                   nodes=_world(documents=[_document("manual", grounded=False), _document("page", grounded=False)]),
                   because="a pad diameter nobody found printed in either document"),
    CounterExample(rule="a-tools-figures-each-rest-on-two-observations", nodes=_world(example_tool(documents=("manual",))),
                   because="every figure read from one manual: one reading each"),
    CounterExample(rule="a-tools-figures-agree-with-what-they-are-read-from",
                   nodes=_world(documents=[_document("manual"), _document("page", 150.0)]),
                   because="the manual prints 125 and the product page 150"),
    CounterExample(rule="a-saw-states-its-cut", nodes=_world(example_tool(saw=True, drop=("kerf",))),
                   because="a saw whose cut nobody stated"),
    CounterExample(rule="a-saw-states-its-depth", nodes=_world(example_tool(saw=True, drop=("max_cut_depth",))),
                   because="a saw whose depth nobody stated"),
    CounterExample(rule="a-pieces-steps-bring-in-every-part", nodes=_piece_case(piece=piece.example_piece(steps=piece.STEPS[:1])),
                   because="instructions that stop once the rail is up, the doors never hung"),
    CounterExample(rule="a-pieces-steps-close-every-joint",
                   nodes=_piece_case(piece=piece.example_piece(steps=[{"add": ["angle", "channel", "back-panel", "front-panel"]}])),
                   because="one step that shows every part arriving and nothing fixing the rail"),
    CounterExample(rule="a-pieces-pages-carry-no-sentence",
                   nodes=_piece_case(pages={"sentence": "Glue the channel to the angle."}),
                   because="a step that says in a sentence what its picture should show"),
    CounterExample(rule="a-pieces-steps-attach-one-kind-of-part", nodes=_piece_case(pages={"rail_kinds": ("R", "S")}),
                   because="an angle and a channel of two kinds brought in by one step"),
    CounterExample(rule="a-pieces-new-parts-are-drawn-apart-with-a-line",
                   nodes=_piece_case(pages={"doors_guided": ("front-panel",)}),
                   because="a door drawn in its rail, with nothing showing that it goes in or how"),
    CounterExample(rule="a-pieces-fastenings-are-shown", nodes=_piece_case(pages={"fastened": ()}),
                   because="a rail shown arriving, and nothing of the screws and glue that hold it"),
    CounterExample(rule="a-pieces-new-parts-are-visible", nodes=_piece_case(pages={"door_shows": 0.2}),
                   because="a back door four fifths hidden behind the front one"),
    CounterExample(rule="a-pieces-steps-keep-their-context", nodes=_piece_case(pages={"context": 0.02}),
                   because="doors drawn over the whole rail they go in"),
    CounterExample(rule="a-pieces-parts-say-how-they-are-cut", nodes=_piece_case(piece=piece.example_piece(made=False)),
                   because="a channel nobody said what to cut from, or with what"),
    CounterExample(rule="a-pieces-joints-say-what-fastens-them",
                   nodes=_piece_case(piece=piece.example_piece(fastened=False)),
                   because="a rail fixed to a lintel by nothing anyone named or counted"),
    CounterExample(rule="a-pieces-turning-parts-are-carried",
                   nodes=_piece_case(piece=piece.example_piece(flap={"pivot": [-108, 1200]})),
                   because="a flap said to turn about a line in mid-air, where no hinge can be"),
    CounterExample(rule="a-pieces-turning-parts-have-room",
                   nodes=_piece_case(piece=piece.example_piece(flap={"travel": [0, 90]})),
                   because="a flap that opens inwards, through the rail and the door behind it"),
    CounterExample(rule="a-pieces-purpose-is-answered", nodes=_piece_case(ledger=piece.example_ledger(answers=False)),
                   because="doors said to slide in one rail, and no decision on how"),
    CounterExample(rule="a-pieces-decisions-name-what-realises-them",
                   nodes=_piece_case(ledger=piece.example_ledger(realised=False)),
                   because="a decision about the rail that names no part, joint or motion"),
    CounterExample(rule="a-pieces-stated-numbers-are-checked", nodes=_piece_case(ledger=piece.example_ledger(figure=None)),
                   because="an overlap of 50 mm stated in words, that nothing compares with the model"),
    CounterExample(rule="a-pieces-figures-are-those-of-its-model", nodes=_piece_case(piece=piece.example_piece(overlap=47.0)),
                   because="the ledger says the doors overlap by 50 mm, and the model gives 47"),
    CounterExample(rule="a-pieces-parts-are-fixed-or-guided", nodes=_piece_case(piece=piece.example_piece(joints=False)),
                   because="an angle and a channel that nothing fixes"),
    CounterExample(rule="a-pieces-motions-are-stated", nodes=_piece_case(piece=piece.example_piece(travel=[600])),
                   because="a slide whose travel is one number"),
    CounterExample(rule="a-pieces-sliding-parts-are-held",
                   nodes=_piece_case(piece=piece.example_piece(back_guides=("channel",))),
                   because="a back door with the channel in front of it and nothing behind"),
    CounterExample(rule="a-pieces-sliding-parts-have-room", nodes=_piece_case(piece=piece.example_piece(channel_at=7.0)),
                   because="the channel glued in the angle, where the back door was to run between the channel "
                           "and the angle's leg: no room is left for it"),
]

PACKAGE = Package(
    name="furniture-standards",
    version="0.9.1",
    description=(
        "What a tool's entry is held to for each use it may be put to, as criteria and levels a certificate "
        "is run from (quern.certify). Criteria: the tool is identified, drawn, its drawing true to its "
        "figures, said in every language, a saw's cut and depth stated, its figures consistent, each found "
        "printed in a document, each resting on two observations that agree. Levels: shown in a person's "
        "tools, cuts the parts of a piece, drawn at work in assembly instructions, taken into the shared "
        "packages. And what a piece's design is held to: every sentence of its purpose answered by a decision "
        "of its ledger that names what realises it, the numbers the ledger states given by the model, every part "
        "fixed by a joint or moved by a motion (kind motion: a slide's or a turn's axis and travel, a turn's pivot, "
        "what moves and what guides or carries it), what slides held on both sides, what turns carried where "
        "it turns, each with room along its travel; levels: its design says what the "
        "person asked for, it holds together and what moves in it works, its assembly instructions are shown (the "
        "steps bring in every part and close every joint once its parts are in, and the pages as drawn carry no "
        "sentence, attach one kind of part a step with a line to where it goes and what fastens it, and show "
        "the parts brought in and enough of those already there: Agrawala et al. 2003 and IKEA, as clauses of "
        "the knowledge). The rules grade and refuse nothing."),
    publisher="xag/furniture-design",
    vocabulary=VOCABULARY,
    rules=RULES,
    solvers=[SolverDef(name=name, native=True, reads=[""], description=(fn.__doc__ or "").strip().split("\n\n")[0])
             for name, fn in NATIVES.items()],
    examples=EXAMPLES,
    counter_examples=COUNTER_EXAMPLES,
)
