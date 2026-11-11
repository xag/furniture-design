"""furniture-design@: the kinds a furniture design and its knowledge base are made of, and
the rules that judge a design against that knowledge.

The rules carry no number a source states. Every limit, test load, material property and
beam coefficient is a param on a node in the knowledge base (furniture_design.knowledge),
quoted from its source, and a rule reads it there: a new source adds nodes, not rules.

Publish (importing the module registers the furniture/* calculations):

    uv run quern --registry <registry checkout> publish furniture_design/package.py:PACKAGE
"""

from __future__ import annotations

from quern.library import CounterExample, Package
from quern.provenance import Quantity
from quern.solver import SolverDef
from quern.tree import KindDef, Node, Rule

# Absolute imports: `quern publish` loads this file by path. Importing furniture_design
# registers the furniture/* calculations.
from furniture_design import natives
from furniture_design.knowledge import REQUIREMENTS, WOOD_HANDBOOK, knowledge

VOCABULARY = [
    KindDef(kind="source", description=(
        "A publication the knowledge base quotes: payload title-like name, publisher, year, "
        "identifier, url, sha256 of what was fetched, licence (public-domain or copyrighted) "
        "and, when the licence allows, capture (the path of the text kept in the repo). Its "
        "children are the clauses quoted from it.")),
    KindDef(kind="clause", description=(
        "A located statement of its parent source: payload locator (chapter, table, page) "
        "and quote (verbatim); transcribed when the statement is an equation or a table row "
        "text extraction cannot read, read from the page and marked as transcription. Its "
        "params are the quantities it states, converted to SI, provenance published."),
        params={"(any)": "a quantity the clause states, in SI, its original wording in note"}),
    KindDef(kind="material", description=(
        "A material a part is made of. Its params are its properties, each derived_from the "
        "clauses it was computed from; a part links to it with `uses` and reads them as its "
        "own."),
        params={"density": "kg/m3", "modulus_of_elasticity": "EL, MPa",
                "shear_modulus_lr": "GLR, MPa", "shear_modulus_lt": "GLT, MPa",
                "initial_share_of_longtime": "the share of a permitted longtime deflection "
                                             "the initial deflection may reach (creep)"},
        links={"per": "the clauses its properties come from"}),
    KindDef(kind="requirement", description=(
        "A demand a design can be checked against: payload measure (what it limits, e.g. "
        "overturning, longtime_sag), scope {category} when it applies to a category of "
        "piece, and the test conditions in words; params its limits and test conditions, "
        "and min_<x> for a scope threshold on the piece's x (height, mass, or a param the "
        "piece carries). A design may author its own requirement (a target it sets itself), "
        "provenance design-target."),
        params={"limit": "the largest value the measure may take",
                "min_<x>": "the piece is in scope only when its x reaches this"},
        links={"per": "the clauses it rests on"}),
    KindDef(kind="piece", description=(
        "A piece of furniture: its parts beneath it. Frame: x across, y from the front "
        "(smallest y) to the back, z up from the floor, mm. payload category (e.g. "
        "clothing-storage-unit) brings it into a requirement's scope."),
        params={"storage_volume": "mm3, what it holds, when a requirement's scope reads it"},
        links={"stability_case": "the overturning requirements it is held to"}),
    KindDef(kind="part", description=(
        "A component to make. payload shape {op: box, size: [x, y, z]} with sizes in mm or "
        "naming the part's params, transform {translate} placing its minimum corner "
        "relative to the enclosing part or piece (geometry@'s convention); extends (mm it "
        "opens towards the front) for a drawer or pull-out shelf; hinged for a door "
        "(not modelled yet); shear_modulus naming the material property that is G for it "
        "(shear_modulus_lr for a board whose vertical faces are edge-grained, the common "
        "flat-sawn board lying flat; shear_modulus_lt for flat-grained vertical faces). "
        "A part that bends names its span, depth and thickness params and its Table 9-1 "
        "case. A part that swells and shrinks with the air (a floating panel) links the "
        "climate it lives in and its movement equation, names in payload across_grain the "
        "param that is its width across the grain and in dimensional_change the material "
        "property that moves it (dimensional_change_tangential for a flat-sawn face, "
        "dimensional_change_radial for a quartersawn one), and states the clearance it "
        "has."),
        params={"mass": "kg, when it is not its volume times its material's density",
                "span": "mm between supports", "depth": "mm, the beam's width b",
                "thickness": "mm, the beam's depth h", "storage_volume": "mm3",
                "clearance": "mm the part may grow across the grain before it is stopped"},
        links={"uses": "its material", "bends_as": "the Table 9-1 clause for its loading "
               "and supports", "sag_limit": "the longtime-sag requirements it is held to",
               "moves_in": "the climates it lives in",
               "moves_per": "the clause of the movement equation it is judged by"}),
    KindDef(kind="climate", description=(
        "The air a piece lives in: params temperature (°C) and rh_min and rh_max, the "
        "driest and dampest relative humidity it sees, as decimals; a design states it "
        "(design-target) or a home measures it. It links emc_per to the equation that "
        "turns it into the moisture content wood settles at (furniture/emc)."),
        params={"temperature": "°C", "rh_min": "decimal, 0 to 1", "rh_max": "decimal, 0 to 1"},
        links={"emc_per": "the equilibrium moisture equation's clause"}),
    KindDef(kind="load", description=(
        "Something a part carries: param mass (kg), payload distribution (uniform or a "
        "point), provenance published when a clause states it, design-target when the "
        "design does."),
        params={"mass": "kg"}, links={"on": "the part it acts on"}),
]

RULES = [
    Rule(name="a-clause-quotes-its-source", kind="clause",
         expr="len(payload(self, 'quote', '')) > 0 and some(s, nodes('source'), s == parent(self))",
         description="A clause sits under the source it is quoted from and quotes it."),
    Rule(name="a-requirement-rests-on-clauses", kind="requirement",
         expr="len(linked(self, 'per')) > 0 and "
              "every(c, linked(self, 'per'), some(k, nodes('clause'), k == c))",
         description="A requirement links `per` to the clauses it rests on, and each is a "
                     "clause in the tree; a target a design sets itself still names the "
                     "clause that makes it a sensible measure."),
    Rule(name="a-material-rests-on-clauses", kind="material",
         expr="len(linked(self, 'per')) > 0 and "
              "every(c, linked(self, 'per'), some(k, nodes('clause'), k == c))",
         description="A material links `per` to the clauses its properties come from."),
    Rule(name="a-load-acts-on-a-part", kind="load",
         expr="len(linked(self, 'on')) > 0 and "
              "every(p, linked(self, 'on'), some(k, nodes('part'), k == p))",
         description="A load names the part it acts on."),
    Rule(name="a-piece-is-held-to-what-applies-to-it", kind="piece",
         expr="solve('furniture/unheld', self) == 0",
         description="A piece in a requirement's scope (its category, and every min_<x> "
                     "threshold reached) links to that requirement, so the check that "
                     "requirement asks for is run."),
    Rule(name="a-piece-stands-in-its-stability-cases", kind="piece",
         expr="solve('furniture/tipping_cases', self) == 0",
         description="Under every overturning requirement a piece links as stability_case, "
                     "the static moment about its front edge keeps it standing. A prediction "
                     "of the physical test the requirement describes, not a substitute for it."),
    Rule(name="a-beam-sags-within-its-limit", kind="part",
         expr="every(r, linked(self, 'sag_limit'), "
              "let(W, 9.80665 * (solve('furniture/mass', self) "
              "+ sum(params_of(backlinked(self, 'on'), 'mass'))), "
              "let(L, param(self, 'span'), let(b, param(self, 'depth'), "
              "let(h, param(self, 'thickness'), "
              "let(E, param(self, 'modulus_of_elasticity'), "
              "let(G, param(self, payload(self, 'shear_modulus')), "
              "let(kb, sum(params_of(linked(self, 'bends_as'), 'kb')), "
              "let(ks, sum(params_of(linked(self, 'bends_as'), 'ks')), "
              "len(linked(self, 'bends_as')) == 1 and "
              "kb * W * L * L * L * 12 / (E * b * h * h * h) + ks * W * L * 6 / (5 * G * b * h) "
              "<= param(self, 'initial_share_of_longtime') * param(r, 'limit'))))))))))",
         description="Wood Handbook Equation (9-2) with (9-3) and (9-4): the initial "
                     "deflection kb W L^3/(E I) + ks W L/(G A') of a part under its own weight "
                     "and the loads on it, kb and ks from its one Table 9-1 case, E and G from "
                     "its material, is at most the share of each sag_limit's longtime limit "
                     "that creep leaves (Chapter 9, Creep Deflections). W in N (9.80665 m/s2 "
                     "is standard gravity), lengths in mm, moduli in MPa. The part's own "
                     "weight counts as part of W whatever the case's loading."),
    Rule(name="a-moving-part-stays-where-its-equation-holds", kind="part",
         expr="every(c, linked(self, 'moves_in'), "
              "len(linked(self, 'moves_per')) == 1 and "
              "solve('furniture/emc', c, 'min') >= sum(params_of(linked(self, 'moves_per'), 'mc_min')) "
              "and solve('furniture/emc', c, 'max') <= sum(params_of(linked(self, 'moves_per'), 'mc_max')))",
         description="The movement equation a part is judged by holds over a range of moisture "
                     "content (Wood Handbook Eq. 13-3: 6% to 14%); in a climate that takes the "
                     "wood outside it, the movement it predicts is not to be trusted, and this "
                     "says so instead of answering."),
    Rule(name="a-moving-part-has-room-to-move", kind="part",
         expr="every(c, linked(self, 'moves_in'), "
              "param(self, payload(self, 'across_grain')) "
              "* param(self, payload(self, 'dimensional_change')) "
              "* (solve('furniture/emc', c, 'max') - solve('furniture/emc', c, 'min')) "
              "<= param(self, 'clearance'))",
         description="Wood Handbook Eq. 13-3: across the grain a part changes by its width times "
                     "its material's dimensional change coefficient times the change in moisture "
                     "content between the driest and dampest air of its climate (Eq. 4-5); its "
                     "clearance takes at least that."),
]

SOLVERS = [SolverDef(name=name, native=True, reads=[""],
                     description=(fn.__doc__ or "").strip().split("\n\n")[0])
           for name, fn in natives.NATIVES.items()]


# --- examples: the knowledge base itself, and two designs that pass ---------------------

def _target(value: float, unit: str, note: str) -> Quantity:
    return Quantity(value=value, unit=unit, provenance="design-target", grounded=False, note=note)


def _chest(links: dict | None = None) -> Node:
    """A low chest of one drawer, in scope of the clothing-storage-unit requirements."""
    drawer = Node(id="drawer", kind="part",
                  params={"mass": _target(5, "kg", "drawer box and front"),
                          "storage_volume": _target(60e6, "mm3", "inside the drawer")},
                  payload={"extends": 350, "shape": {"op": "box", "size": [900, 450, 200]},
                           "transform": {"translate": [50, 0, 300]}})
    return Node(id="chest", kind="piece", payload={"category": "clothing-storage-unit"},
                params={"storage_volume": _target(100e6, "mm3", "the drawer and the cupboard")},
                links=links if links is not None else {"stability_case": [
                    f"{REQUIREMENTS}/csu-simulated-clothing-load",
                    f"{REQUIREMENTS}/csu-carpet-child-weight"]},
                children=[Node(id="carcass", kind="part",
                               params={"mass": _target(60, "kg", "carcass, top and back")},
                               payload={"shape": {"op": "box", "size": [1000, 500, 800]}}),
                          drawer])


def _shelf(limit_mm: float) -> list[Node]:
    """A bookshelf's oak shelf, 800 mm between supports, with 30 kg of books on it."""
    sag = Node(id="bookshelf-sag", kind="requirement",
               name="The shelf sags at most this much under its books, over the years",
               payload={"measure": "longtime_sag"},
               params={"limit": _target(limit_mm, "mm", "a target the design sets")},
               links={"per": [f"{WOOD_HANDBOOK}/creep-chapter-9"]})
    shelf = Node(id="shelf", kind="part",
                 params={"span": _target(800, "mm", "between the sides"),
                         "depth": _target(250, "mm", "front to back"),
                         "thickness": _target(19, "mm", "board thickness")},
                 payload={"shape": {"op": "box", "size": ["span", "depth", "thickness"]},
                          "shear_modulus": "shear_modulus_lr"},
                 links={"uses": ["materials/oak-northern-red"],
                        "bends_as": [f"{WOOD_HANDBOOK}/table-9-1-uniform-simply-supported"],
                        "sag_limit": [f"{REQUIREMENTS}/bookshelf-sag"]})
    books = Node(id="books", kind="load", params={"mass": _target(30, "kg", "a row of books")},
                 payload={"distribution": "uniform"}, links={"on": ["pieces/bookshelf/shelf"]})
    return [sag, Node(id="bookshelf", kind="piece", children=[shelf, books])]


def _cabinet(clearance_mm: float, rh_max: float) -> list[Node]:
    """A wall cabinet's oak back panel, 400 mm across the grain, floating in a groove, in a
    room between 30% and `rh_max` relative humidity at 20 °C."""
    room = Node(id="living-room", kind="climate",
                params={"temperature": _target(20, "degC", "heated room"),
                        "rh_min": _target(0.30, "", "dry winter"),
                        "rh_max": _target(rh_max, "", "damp summer")},
                links={"emc_per": [f"{WOOD_HANDBOOK}/emc-4-5"]})
    panel = Node(id="back-panel", kind="part",
                 params={"width": _target(400, "mm", "across the grain"),
                         "clearance": _target(clearance_mm, "mm", "room left in the groove")},
                 payload={"shape": {"op": "box", "size": ["width", 6, 300]},
                          "across_grain": "width",
                          "dimensional_change": "dimensional_change_tangential"},
                 links={"uses": ["materials/oak-northern-red"],
                        "moves_in": ["climates/living-room"],
                        "moves_per": [f"{WOOD_HANDBOOK}/dimensional-change-13-3"]})
    return [Node(id="climates", kind="", children=[room]),
            Node(id="cabinet", kind="piece", children=[panel])]


def _world(*, chest: Node | None = None, sag_limit: float = 4.0, clearance: float = 8.0,
           rh_max: float = 0.65) -> list[Node]:
    kb = knowledge()
    sag, bookshelf = _shelf(sag_limit)
    kb[2].children.append(sag)
    climates, cabinet = _cabinet(clearance, rh_max)
    return kb + [climates,
                 Node(id="pieces", kind="", children=[chest or _chest(), bookshelf, cabinet])]


EXAMPLES = _world()

_UNQUOTED = Node(id="sources", kind="", children=[
    Node(id="somewhere", kind="source", children=[
        Node(id="said", kind="clause", payload={"locator": "p. 1"})])])

COUNTER_EXAMPLES = [
    CounterExample(rule="a-clause-quotes-its-source", nodes=[_UNQUOTED],
                   because="a clause with no quote states nothing anyone can check"),
    CounterExample(rule="a-requirement-rests-on-clauses",
                   nodes=[Node(id="requirements", kind="", children=[
                       Node(id="a-wish", kind="requirement", payload={"measure": "overturning"})])],
                   because="a requirement that rests on no clause is an opinion"),
    CounterExample(rule="a-material-rests-on-clauses",
                   nodes=[Node(id="materials", kind="", children=[
                       Node(id="mystery-wood", kind="material",
                            params={"density": _target(600, "kg/m3", "a guess")})])],
                   because="a material whose properties come from nowhere"),
    CounterExample(rule="a-load-acts-on-a-part",
                   nodes=[Node(id="pieces", kind="", children=[
                       Node(id="books", kind="load", params={"mass": _target(30, "kg", "")})])],
                   because="a load on nothing is counted nowhere"),
    CounterExample(rule="a-piece-is-held-to-what-applies-to-it",
                   nodes=_world(chest=_chest(links={})),
                   because="a chest in the clothing-storage-unit scope that links to neither "
                           "stability test, so neither is run"),
    CounterExample(rule="a-piece-stands-in-its-stability-cases",
                   nodes=_world(chest=Node(**{**_chest().model_dump(), "children": [
                       Node(id="carcass", kind="part",
                            params={"mass": _target(15, "kg", "a light carcass")},
                            payload={"shape": {"op": "box", "size": [1000, 400, 1200]}}),
                       Node(id="drawer", kind="part",
                            params={"mass": _target(5, "kg", ""),
                                    "storage_volume": _target(60e6, "mm3", "")},
                            payload={"extends": 380,
                                     "shape": {"op": "box", "size": [900, 380, 200]},
                                     "transform": {"translate": [50, 0, 1000]}})]})),
                   because="a light, tall chest whose top drawer, open, carries 60 pounds "
                           "well in front of its feet: it tips"),
    CounterExample(rule="a-beam-sags-within-its-limit", nodes=_world(sag_limit=1.0),
                   because="the oak shelf deflects about 1.1 mm at once, more than two-thirds "
                           "of a 1 mm longtime limit"),
    CounterExample(rule="a-moving-part-stays-where-its-equation-holds", nodes=_world(rh_max=0.90),
                   because="at 90% relative humidity oak settles near 20.5% moisture, beyond the "
                           "14% where the movement equation holds"),
    CounterExample(rule="a-moving-part-has-room-to-move", nodes=_world(clearance=4.0),
                   because="400 mm of flat-sawn oak moves about 7.1 mm between 30% and 65% "
                           "humidity, and the groove leaves it 4"),
]

PACKAGE = Package(
    name="furniture-design",
    version="0.2.0",
    description=(
        "Furniture designs and the published knowledge they are judged against. Kinds: "
        "source and clause (a publication and its verbatim, located statements, with the "
        "quantities they state), material (properties derived from clauses), requirement "
        "(a demand resting on clauses, with its limits and test conditions), piece, part and "
        "load. Rules: every clause quotes its source; requirements and materials rest on "
        "clauses; a piece in a requirement's scope is held to it; a piece stands in its "
        "stability cases (furniture/tipping_cases); a part bends within its longtime sag "
        "limit (Wood Handbook Eq. 9-2 to 9-4 and its creep guidance); a part that swells and "
        "shrinks with the air has room to (Eq. 13-3, the moisture content of its climate from "
        "Eq. 4-5, kind climate), and is judged only where that equation holds. The rules carry no "
        "number a source states: limits and properties are read from the knowledge base."),
    publisher="xag/furniture-design",
    vocabulary=VOCABULARY,
    rules=RULES,
    solvers=SOLVERS,
    examples=EXAMPLES,
    counter_examples=COUNTER_EXAMPLES,
)
