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
from furniture_design.knowledge import REQUIREMENTS, WOOD_HANDBOOK, knowledge, merge

VOCABULARY = [
    KindDef(kind="source", description=(
        "A publication the knowledge base quotes: payload title-like name, publisher, year, "
        "identifier, url, sha256 of what was fetched, licence (public-domain or copyrighted) "
        "and, when the licence allows, capture (the path of the text kept in the repo). Its "
        "children are the clauses quoted from it.")),
    KindDef(kind="clause", description=(
        "A located statement of its parent source: payload locator (chapter, table, page) "
        "and quote (verbatim); transcribed when the statement is an equation or a table row "
        "text extraction cannot read, read from the page and marked as transcription. A "
        "clause of a copyrighted source carries its locator and no quote: the words are the "
        "publisher's, and the copy they can be checked against is kept where it may be. Its "
        "params are the quantities it states, converted to SI, provenance published."),
        params={"(any)": "a quantity the clause states, in SI, its original wording in note"}),
    KindDef(kind="material", description=(
        "A material a part is made of. Its params are its properties, each derived_from the "
        "clauses it was computed from; a part links to it with `uses` and reads them as its "
        "own. payload form (solid wood, plywood, ...), measured_along (the direction its "
        "bending values were measured in: grain, face grain, or unstated when the source does "
        "not say) and modulus (true: corrected for shear deflection, so a shear term is added; "
        "apparent: measured on the panel with its shear deflection in it)."),
        params={"density": "kg/m3", "modulus_of_elasticity": "EL, MPa (for a panel, its "
                "bending modulus as tested on the panel)",
                "modulus_of_rupture": "MPa, the mean bending strength the source states",
                "design_bending_stress": "MPa, the bending stress a part may be designed to",
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
        links={"stability_case": "the overturning requirements it is held to",
               "sideways_case": "the sideways-force requirements it is held to",
               "braced_by": "the panels standing in the plane of a sideways force (a back), "
                            "joined along their top and side edges, that carry it to the "
                            "floor"}),
    KindDef(kind="part", description=(
        "A component to make. payload shape {op: box, size: [x, y, z]} in mm, transform "
        "{translate} placing its minimum corner relative to the enclosing part or piece "
        "(geometry@'s convention), each entry a number or an expression over params (the "
        "part's own, then those of the parts and piece holding it, nearest first), so a "
        "dimension the piece states once moves every part that depends on it; extends (mm it "
        "opens towards the front) for a drawer or pull-out shelf; hinged for a door "
        "(not modelled yet); span_along (grain, face grain) for a part that bends: the way "
        "its grain runs along its span; shear_modulus naming the material property that is G for it "
        "(shear_modulus_lr for a board whose vertical faces are edge-grained, the common "
        "flat-sawn board lying flat; shear_modulus_lt for flat-grained vertical faces). "
        "A part that bends names its span, depth and thickness params and its Table 9-1 "
        "case. A part that swells and shrinks with the air (a floating panel) links the "
        "climate it lives in and its movement equation, names in payload across_grain the "
        "param that is its width across the grain and in dimensional_change the material "
        "property that moves it (dimensional_change_tangential for a flat-sawn face, "
        "dimensional_change_radial for a quartersawn one), and states the clearance it "
        "has. payload cuts: what is taken out of the board, a list of boxes {at, size} in "
        "the part's own frame (each entry a number or an expression over params, as for its "
        "size), such as a notch for a skirting board; a part's cuts are not a joint's `cut`, "
        "which names the kind of connector seat. A part with cuts links made_with the tools "
        "that cut them, each saying how it is used and resting on clauses; the documents "
        "draw each cut measured from the edges it touches and number its saw lines in order."),
        params={"mass": "kg, when it is not its volume times its material's density",
                "span": "mm between supports", "depth": "mm, the beam's width b",
                "thickness": "mm, the beam's depth h, and a joined panel's thickness",
                "width": "mm, a joined panel's width", "storage_volume": "mm3",
                "clearance": "mm the part may grow across the grain before it is stopped"},
        links={"uses": "its material", "bends_as": "the Table 9-1 clause for its loading "
               "and supports", "sag_limit": "the longtime-sag requirements it is held to",
               "moves_in": "the climates it lives in",
               "moves_per": "the clause of the movement equation it is judged by",
               "made_with": "the tools that cut its cuts"}),
    KindDef(kind="tool", description=(
        "A machine or jig that cuts or drills what a joint needs: payload maker and what it "
        "does. A design names the tools it is made with; a connector names the tools that "
        "can cut its seat."),
        links={"per": "the clauses that say what it does"}),
    KindDef(kind="connector", description=(
        "A manufactured element that joins parts (a knock-down fitting, a biscuit, a dowel): "
        "payload maker and setting (the machine setting its seat is cut at, when it has "
        "one); params its limits — min_width (mm, the narrowest part it may join), "
        "min_thickness_<cut> (mm, per kind of cut: edge, surface, intermediate, mitre), "
        "pull_out_<material> and shear_<material> (N), moment_opening_<material> and "
        "moment_closing_<material> (N mm: one connector's share of what a corner joint "
        "resists being bent open or shut) — each derived from a clause; and its size as its "
        "maker states it, length (mm, along the joint) and thickness (mm, across it), which "
        "the documents draw it at."),
        params={"min_width": "mm", "min_thickness_<cut>": "mm", "pull_out_<material>": "N",
                "shear_<material>": "N",
                "moment_opening_<material>": "N mm, one connector's share of what a corner "
                                             "joint resists being bent open",
                "moment_closing_<material>": "N mm, the same, bent shut",
                "length": "mm, the connector's length along the joint",
                "thickness": "mm, its thickness across the joint"},
        links={"needs": "the tools that can cut its seat; any one of them will do",
               "per": "the clauses its limits come from"}),
    KindDef(kind="joint", description=(
        "Where parts are joined. Links joins (the parts), uses (the connector it is made "
        "with, whose limits it reads as its own) and made_with (the tools that cut it); "
        "payload cut (edge, surface, intermediate or mitre: which of the connector's "
        "min_thickness_<cut> applies), setting (the machine setting it is cut at) and, when "
        "the design places its connectors, positions (mm along the longer side of the face "
        "the parts meet on; otherwise they are spread evenly, for the checks and the "
        "documents alike); param count (connectors in it). A joined part states its width "
        "and thickness."),
        params={"count": "connectors in the joint"},
        links={"joins": "the parts it joins", "uses": "its connector",
               "made_with": "the tools it is cut with"}),
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
         expr="some(s, nodes('source'), s == parent(self)) "
              "and len(payload(self, 'locator', '')) > 0 "
              "and (len(payload(self, 'quote', '')) > 0 "
              "or payload(parent(self), 'licence', '') == 'copyrighted' "
              "or payload(parent(self), 'licence', '') == 'unstated')",
         description="A clause sits under the source it comes from, says where in it, and "
                     "quotes it, unless the source is copyrighted, or its licence could not "
                     "be established (unstated): then it carries the values and the locator, "
                     "and the words stay with their publisher."),
    Rule(name="a-connector-rests-on-clauses", kind="connector",
         expr="len(linked(self, 'per')) > 0 and "
              "every(c, linked(self, 'per'), some(k, nodes('clause'), k == c))",
         description="A connector links `per` to the clauses its limits come from."),
    Rule(name="a-joined-part-is-thick-enough-for-the-cut", kind="joint",
         expr="every(p, linked(self, 'joins'), "
              "param(p, 'thickness') >= param(self, 'min_thickness_' + payload(self, 'cut')))",
         description="Every part a joint joins is at least as thick as its connector allows "
                     "for the kind of cut the joint is (the connector's min_thickness_<cut>, "
                     "read through `uses`)."),
    Rule(name="a-joined-part-is-wide-enough", kind="joint",
         expr="every(p, linked(self, 'joins'), param(p, 'width') >= param(self, 'min_width'))",
         description="Every part a joint joins is at least as wide as its connector allows."),
    Rule(name="a-joint-is-cut-with-a-tool-its-connector-takes", kind="joint",
         expr="len(linked(self, 'made_with')) > 0 and every(c, linked(self, 'uses'), "
              "some(t, linked(c, 'needs'), some(m, linked(self, 'made_with'), m == t)))",
         description="A joint names the tools it is cut with, and one of them is a tool its "
                     "connector's seat can be cut with."),
    Rule(name="a-joint-is-cut-at-its-connectors-setting", kind="joint",
         expr="every(c, linked(self, 'uses'), payload(c, 'setting', '') == '' "
              "or payload(self, 'setting', '') == payload(c, 'setting', ''))",
         description="When a connector's seat is cut at a machine setting, the joint says it "
                     "is cut at that setting."),
    Rule(name="a-part-with-cuts-is-cut-with-tools-that-rest-on-clauses", kind="part",
         expr="len(payload(self, 'cuts', '')) == 0 or (len(linked(self, 'made_with')) > 0 and "
              "every(t, linked(self, 'made_with'), len(linked(t, 'per')) > 0))",
         description="A part with cuts names the tools that cut them, and each of those tools "
                     "rests on clauses that say how it is used, so the instructions tell how "
                     "to make the cut and not only where it is."),
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
    Rule(name="a-piece-takes-its-sideways-load", kind="piece",
         expr="every(r, linked(self, 'sideways_case'), "
              "solve('furniture/sideways_margin', self, r) >= 0)",
         description="Under every sideways requirement a piece links as sideways_case, the "
                     "panels it is braced_by carry the side force: the connectors along each "
                     "panel's top edge take the force in shear, those along each side edge "
                     "take it in pull-out and the force times the panel's height over its "
                     "width in shear, each connector good for its strength in the weaker "
                     "joined material, no bearing credited "
                     "(furniture/sideways_margin). A piece with no such panel is not judged "
                     "to stand: its joints would have to resist bending, and no source here "
                     "rates that."),
    Rule(name="a-beam-sags-within-its-limit", kind="part",
         expr="every(r, linked(self, 'sag_limit'), solve('furniture/deflection', self) "
              "<= param(self, 'initial_share_of_longtime') * param(r, 'limit'))",
         description="Wood Handbook Equation (9-2) with (9-3) and (9-4), through "
                     "furniture/deflection: the initial deflection of a part under its own "
                     "weight and the loads on it is at most the share of each sag_limit's "
                     "longtime limit that creep leaves (Chapter 9, Creep Deflections)."),
    Rule(name="a-beam-is-strong-enough", kind="part",
         expr="every(c, linked(self, 'bends_as'), "
              "param(c, 'km') * 9.80665 * (solve('furniture/mass', self) "
              "+ sum(params_of(backlinked(self, 'on'), 'mass'))) * param(self, 'span') * 6 "
              "/ (param(self, 'depth') * param(self, 'thickness') * param(self, 'thickness')) "
              "<= param(self, 'design_bending_stress'))",
         description="Wood Handbook Equation (9-13): the largest bending stress M/S in a part, "
                     "M = km W L for its Table 9-1 case and S = b h^2/6, under its own weight "
                     "and the loads on it, is at most its material's design bending stress "
                     "(the near-minimum modulus of rupture over the factor for duration of "
                     "load and safety). W in N, lengths in mm, stresses in MPa."),
    Rule(name="a-part-bends-the-way-its-material-was-tested", kind="part",
         expr="every(c, linked(self, 'bends_as'), every(m, linked(self, 'uses'), "
              "payload(self, 'span_along', '') == payload(m, 'measured_along', 'unstated')))",
         description="A part that bends spans the way its material's bending values were "
                     "measured (along the grain for solid wood, face grain along the span for "
                     "plywood). A material whose source does not say which way it was bent "
                     "(measured_along: unstated) judges no part's bending."),
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


def _shelf(limit_mm: float, books_kg: float = 30, span_along: str = "grain") -> list[Node]:
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
                          "shear_modulus": "shear_modulus_lr", "span_along": span_along},
                 links={"uses": ["materials/oak-northern-red"],
                        "bends_as": [f"{WOOD_HANDBOOK}/table-9-1-uniform-simply-supported"],
                        "sag_limit": [f"{REQUIREMENTS}/bookshelf-sag"]})
    books = Node(id="books", kind="load", params={"mass": _target(books_kg, "kg", "a row of books")},
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


def _joinery(*, thickness: float = 18, width: float = 300, tool: str = "tools/groove-cutter",
             setting: str = "S-1", cited: bool = True) -> tuple[Node, list[Node], Node]:
    """An invented maker's catalogue (copyrighted: cited, not quoted), the connector and the
    tool it describes, and a box whose two sides it joins at the corner, surface cut."""
    catalogue = Node(id="example-catalogue", kind="source", name="An example maker's catalogue",
                     payload={"publisher": "an example maker", "licence": "copyrighted",
                              "url": "https://example.com/connector"},
                     children=[Node(id="technical-data", kind="clause",
                                    payload={"locator": "technical data table"},
                                    params={"min_thickness_surface": Quantity(
                                        value=15, unit="mm", provenance="published"),
                                            "min_width": Quantity(value=75, unit="mm",
                                                                  provenance="published"),
                                            "shear_birch-yellow": Quantity(
                                        value=600, unit="N", provenance="published"),
                                            "pull_out_birch-yellow": Quantity(
                                        value=1000, unit="N", provenance="published"),
                                            "moment_opening_birch-yellow": Quantity(
                                        value=5000, unit="N mm", provenance="published"),
                                            "moment_closing_birch-yellow": Quantity(
                                        value=5000, unit="N mm", provenance="published"),
                                            "length": Quantity(value=60, unit="mm",
                                                               provenance="published"),
                                            "thickness": Quantity(value=8, unit="mm",
                                                                  provenance="published")})])
    per = ["sources/example-catalogue/technical-data"] if cited else []
    connector = Node(id="example-connector", kind="connector",
                     payload={"maker": "an example maker", "setting": "S-1"},
                     params={"min_thickness_surface": Quantity(
                                 value=15, unit="mm", provenance="derived",
                                 derived_from=["sources/example-catalogue/technical-data"]),
                             "min_width": Quantity(value=75, unit="mm", provenance="derived",
                                                   derived_from=["sources/example-catalogue/technical-data"]),
                             "shear_birch-yellow": Quantity(
                                 value=600, unit="N", provenance="derived",
                                 derived_from=["sources/example-catalogue/technical-data"]),
                             "pull_out_birch-yellow": Quantity(
                                 value=1000, unit="N", provenance="derived",
                                 derived_from=["sources/example-catalogue/technical-data"]),
                             "moment_opening_birch-yellow": Quantity(
                                 value=5000, unit="N mm", provenance="derived",
                                 derived_from=["sources/example-catalogue/technical-data"]),
                             "moment_closing_birch-yellow": Quantity(
                                 value=5000, unit="N mm", provenance="derived",
                                 derived_from=["sources/example-catalogue/technical-data"]),
                             "length": Quantity(value=60, unit="mm", provenance="derived",
                                                derived_from=["sources/example-catalogue/technical-data"]),
                             "thickness": Quantity(value=8, unit="mm", provenance="derived",
                                                   derived_from=["sources/example-catalogue/technical-data"])},
                     links={"needs": ["tools/groove-cutter"], "per": per})
    tools = [Node(id="groove-cutter", kind="tool", payload={"maker": "an example maker"}),
             Node(id="drill", kind="tool", payload={"maker": "any"})]

    def side(id_: str) -> Node:
        return Node(id=id_, kind="part", links={"uses": ["materials/birch-yellow"]},
                    params={"width": _target(width, "mm", ""), "thickness": _target(thickness, "mm", "")},
                    payload={"shape": {"op": "box", "size": ["thickness", "width", 400]}})
    joint = Node(id="corner", kind="joint", payload={"cut": "surface", "setting": setting},
                 params={"count": _target(2, "", "two connectors")},
                 links={"joins": ["pieces/box/left", "pieces/box/top"],
                        "uses": ["connectors/example-connector"], "made_with": [tool]})
    box = Node(id="box", kind="piece", children=[side("left"), side("top"), joint])
    return catalogue, [Node(id="connectors", kind="", children=[connector]),
                       Node(id="tools", kind="", children=tools)], box


def _seat(back_count: float = 4) -> Node:
    """A bench of yellow birch boards on the example maker's connectors: two sides, a top
    and a back panel joined to the top and to each side, held to the light sidethrust."""
    def board(id_: str, size: list, at: list) -> Node:
        return Node(id=id_, kind="part", links={"uses": ["materials/birch-yellow"]},
                    params={"thickness": _target(20, "mm", ""), "width": _target(300, "mm", "")},
                    payload={"shape": {"op": "box", "size": size}, "transform": {"translate": at}})

    def joint(id_: str, other: str, count: float) -> Node:
        return Node(id=id_, kind="joint", payload={"cut": "surface", "setting": "S-1"},
                    params={"count": _target(count, "", "connectors in the joint")},
                    links={"joins": ["pieces/bench/back", f"pieces/bench/{other}"],
                           "uses": ["connectors/example-connector"],
                           "made_with": ["tools/groove-cutter"]})
    return Node(id="bench", kind="piece", payload={"category": "seating"},
                links={"sideways_case": [f"{REQUIREMENTS}/seating-sidethrust-light"],
                       "braced_by": ["pieces/bench/back"]},
                children=[board("left", [20, 300, 450], [0, 0, 0]),
                          board("right", [20, 300, 450], [980, 0, 0]),
                          board("top", [1000, 300, 20], [0, 0, 450]),
                          board("back", [960, 20, 350], [20, 280, 100]),
                          joint("back-top", "top", back_count), joint("back-left", "left", 2),
                          joint("back-right", "right", 2)])


def _notched(cut_with: str) -> Node:
    """A bench's side standing against a wall, notched at its bottom back corner for the
    skirting board, sawn with `cut_with`."""
    side = Node(id="side", kind="part", links={"uses": ["materials/birch-yellow"],
                                               "made_with": [cut_with]},
                params={"skirting_height": _target(115, "mm", "the skirting's height, and room"),
                        "skirting_depth": _target(25, "mm", "the skirting's depth, and room")},
                payload={"shape": {"op": "box", "size": [18, 300, 450]},
                         "cuts": [{"at": [0, "300 - skirting_depth", 0],
                                   "size": [18, "skirting_depth", "skirting_height"]}]})
    return Node(id="bench-side", kind="piece", children=[side])


def _world(*, chest: Node | None = None, sag_limit: float = 4.0, clearance: float = 8.0,
           rh_max: float = 0.65, books_kg: float = 30, span_along: str = "grain",
           back_count: float = 4, cut_with: str = "tools/crosscut-saw",
           **joinery) -> list[Node]:
    kb = knowledge()
    sag, bookshelf = _shelf(sag_limit, books_kg, span_along)
    kb[2].children.append(sag)
    climates, cabinet = _cabinet(clearance, rh_max)
    catalogue, hardware, box = _joinery(**joinery)
    kb[0].children.append(catalogue)
    return merge(kb, hardware) + [climates, Node(id="pieces", kind="", children=[
        chest or _chest(), bookshelf, cabinet, box, _seat(back_count), _notched(cut_with)])]


EXAMPLES = _world()

_UNQUOTED = Node(id="sources", kind="", children=[
    Node(id="somewhere", kind="source", children=[
        Node(id="said", kind="clause", payload={"locator": "p. 1"})])])

COUNTER_EXAMPLES = [
    CounterExample(rule="a-clause-quotes-its-source", nodes=[_UNQUOTED],
                   because="a clause with no quote states nothing anyone can check"),
    CounterExample(rule="a-part-with-cuts-is-cut-with-tools-that-rest-on-clauses",
                   nodes=_world(cut_with="tools/drill"),
                   because="a notch said to be cut with a drill no clause says how to use: the "
                           "instructions could say where the notch is, not how to make it"),
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
    CounterExample(rule="a-piece-takes-its-sideways-load", nodes=_world(back_count=1),
                   because="one connector along the back's top edge, good for 600 N in "
                           "birch, takes the whole 890 N of the light sidethrust"),
    CounterExample(rule="a-beam-is-strong-enough", nodes=_world(books_kg=600),
                   because="600 kg on the oak shelf bends it to about 39 MPa, past oak's design "
                           "stress of about 34.7"),
    CounterExample(rule="a-part-bends-the-way-its-material-was-tested",
                   nodes=_world(span_along="across the grain"),
                   because="a board spanning across its grain, judged with values measured "
                           "along it"),
    CounterExample(rule="a-moving-part-stays-where-its-equation-holds", nodes=_world(rh_max=0.90),
                   because="at 90% relative humidity oak settles near 20.5% moisture, beyond the "
                           "14% where the movement equation holds"),
    CounterExample(rule="a-moving-part-has-room-to-move", nodes=_world(clearance=4.0),
                   because="400 mm of flat-sawn oak moves about 7.1 mm between 30% and 65% "
                           "humidity, and the groove leaves it 4"),
    CounterExample(rule="a-connector-rests-on-clauses", nodes=_world(cited=False),
                   because="a connector whose limits come from no clause"),
    CounterExample(rule="a-joined-part-is-thick-enough-for-the-cut", nodes=_world(thickness=12),
                   because="12 mm sides joined with a surface cut that needs 15"),
    CounterExample(rule="a-joined-part-is-wide-enough", nodes=_world(width=60),
                   because="60 mm wide sides, where the connector needs 75"),
    CounterExample(rule="a-joint-is-cut-with-a-tool-its-connector-takes",
                   nodes=_world(tool="tools/drill"),
                   because="a joint cut with a drill, for a connector whose seat only the "
                           "groove cutter makes"),
    CounterExample(rule="a-joint-is-cut-at-its-connectors-setting", nodes=_world(setting="S-2"),
                   because="the seat cut at the wrong machine setting"),
]

PACKAGE = Package(
    name="furniture-design",
    version="0.6.0",
    description=(
        "Furniture designs and the published knowledge they are judged against. Kinds: "
        "source and clause (a publication and its verbatim, located statements, with the "
        "quantities they state), material (properties derived from clauses), requirement "
        "(a demand resting on clauses, with its limits and test conditions), piece, part and "
        "load. Rules: every clause quotes its source; requirements and materials rest on "
        "clauses; a piece in a requirement's scope is held to it; a piece stands in its "
        "stability cases (furniture/tipping_cases); a part bends within its longtime sag "
        "limit (Wood Handbook Eq. 9-2 to 9-4 and its creep guidance, furniture/deflection, with no shear term for a panel whose modulus was measured on the panel); a part is strong enough (Eq. 9-13 against the near-minimum modulus of rupture over the Handbook's factor for 10-year duration of load and safety); a part bends the way its material's values were measured; a seat carries the light-service sidethrust of GSA's FNAE-80-214A through a panel in the push's plane (furniture/sideways_margin); a part that swells and "
        "shrinks with the air has room to (Eq. 13-3, the moisture content of its climate from "
        "Eq. 4-5, kind climate), and is judged only where that equation holds; a joint is cut with a tool its connector takes, at its setting, in parts thick and wide enough for it (kinds tool, connector, joint; a maker's products are data in a package of their own); a part with cuts is cut with tools that rest on clauses saying how they are used. The rules carry no "
        "number a source states: limits and properties are read from the knowledge base."),
    publisher="xag/furniture-design",
    vocabulary=VOCABULARY,
    rules=RULES,
    solvers=SOLVERS,
    examples=EXAMPLES,
    counter_examples=COUNTER_EXAMPLES,
)
