"""What the furniture/* calculations must answer, on cases checkable by hand.

The spec lives beside the implementation, as geometry@'s does: these are host code, and a
proof travelling in the package could be softened by whoever republished it. quern's
publish gate runs every case, and refuses a calculation whose cases all expect one answer.

The world: a carcass 1000 wide, 500 deep, 800 tall, 40 kg, standing on the floor with its
front at y = 0; a drawer 900 x 450 x 200 at height 500, 5 kg, opening 400 mm. Masses are
given as params so the arithmetic below needs no density.
"""

from __future__ import annotations

from quern.provenance import Quantity
from quern.tree import Demonstration, Node

G = 9.80665


def _kg(v: float) -> Quantity:
    return Quantity(value=v, unit="kg", provenance="design-target", grounded=False)


def chest(extends: float = 400, drawer_volume: float | None = None,
          storage_volume: float | None = None) -> Node:
    drawer = Node(id="drawer", kind="part", params={"mass": _kg(5)},
                  payload={"extends": extends,
                           "shape": {"op": "box", "size": [900, 450, 200]},
                           "transform": {"translate": [50, 0, 500]}})
    if drawer_volume is not None:
        drawer.params["storage_volume"] = Quantity(value=drawer_volume, unit="mm3",
                                                   provenance="design-target", grounded=False)
    piece = Node(id="chest", kind="piece", payload={"category": "clothing-storage-unit"},
                 children=[Node(id="carcass", kind="part", params={"mass": _kg(40)},
                                payload={"shape": {"op": "box", "size": [1000, 500, 800]}}),
                           drawer])
    if storage_volume is not None:
        piece.params["storage_volume"] = Quantity(value=storage_volume, unit="mm3",
                                                  provenance="design-target", grounded=False)
    return piece


def case(id_: str, **params: float) -> Node:
    units = {"tilt_block": "mm", "point_mass": "kg", "fill_density": "kg/m3", "fill_share": "",
             "min_height": "mm", "min_mass": "kg", "min_storage_volume": "mm3"}
    return Node(id=id_, kind="requirement",
                payload={"measure": "overturning", "scope": {"category": "clothing-storage-unit"}},
                params={k: Quantity(value=v, unit=units[k], provenance="published", grounded=True)
                        for k, v in params.items()})


def reqs(*cases: Node) -> Node:
    return Node(id="requirements", kind="", children=list(cases))


OAK = Node(id="materials", kind="", children=[
    Node(id="oak", kind="material",
         params={"density": Quantity(value=700, unit="kg/m3", provenance="published")})])
BOARD = Node(id="board", kind="piece", children=[
    Node(id="top", kind="part", links={"uses": ["materials/oak"]},
         payload={"shape": {"op": "box", "size": [1000, 100, 10]}})])
UNWEIGHED = Node(id="board", kind="piece", children=[
    Node(id="top", kind="part", payload={"shape": {"op": "box", "size": [1000, 100, 10]}})])


def climate(temperature: float, rh_min: float, rh_max: float, linked: bool = True) -> list[Node]:
    """The Wood Handbook as a source, and one climate under climates/."""
    from .knowledge import wood_handbook

    def q(v: float, unit: str = "") -> Quantity:
        return Quantity(value=v, unit=unit, provenance="design-target", grounded=False)
    c = Node(id="room", kind="climate",
             params={"temperature": q(temperature, "degC"), "rh_min": q(rh_min), "rh_max": q(rh_max)},
             links={"emc_per": ["sources/wood-handbook/emc-4-5"]} if linked else {})
    return [Node(id="sources", kind="", children=[wood_handbook()]),
            Node(id="climates", kind="", children=[c])]


def d(contract: str, nodes: list[Node], args: list, because: str, **expect) -> Demonstration:
    return Demonstration(contract=f"furniture/{contract}", nodes=nodes, args=args,
                         because=because, **expect)


# The chest, every drawer open: the carcass's centre is 250 behind the front edge; the
# drawer's centre is at y = 225 - 400 = -175; a point load on the open drawer's front top
# edge is at y = -400, z = 700.
STANDING = 40 * 250 + 5 * -175

def beam(modulus: str = "true", shear: str | None = "shear_modulus_lr", cases: int = 1,
         load: float = 10) -> list[Node]:
    """A 1000 mm board, 100 deep and 10 thick, weightless (mass 0), simply supported, with
    `load` kg spread on it; its material has E 10,000 MPa and G 700 MPa."""
    def q(v: float, unit: str = "") -> Quantity:
        return Quantity(value=v, unit=unit, provenance="design-target", grounded=False)
    case = Node(id="uniform", kind="clause", params={"kb": q(5 / 384), "ks": q(1 / 8)})
    wood = Node(id="wood", kind="material", payload={"modulus": modulus},
                params={"modulus_of_elasticity": q(10_000, "MPa"),
                        "shear_modulus_lr": q(700, "MPa")})
    board = Node(id="board", kind="part", links={"uses": ["materials/wood"],
                                                 "bends_as": ["cases/uniform"] * cases},
                 params={"mass": q(0, "kg"), "span": q(1000, "mm"), "depth": q(100, "mm"),
                         "thickness": q(10, "mm")},
                 payload={"shape": {"op": "box", "size": ["span", "depth", "thickness"]},
                          **({"shear_modulus": shear} if shear else {})})
    books = Node(id="books", kind="load", params={"mass": q(load, "kg")},
                 links={"on": ["shelf/board"]})
    return [Node(id="cases", kind="", children=[case]),
            Node(id="materials", kind="", children=[wood]),
            Node(id="shelf", kind="piece", children=[board, books])]


# The beam above: W = 10 kg x g; bending 5/384 W L^3 12/(E b h^3), shear 1/8 W L 6/(5 G b h)
_W = 10 * G
_BENDING = 5 / 384 * _W * 1000 ** 3 * 12 / (10_000 * 100 * 10 ** 3)
_SHEAR = 1 / 8 * _W * 1000 * 6 / (5 * 700 * 100 * 10)

def braced(top_count: float = 4, side_count: float = 2, brace: bool = True,
            key: str = "wood") -> list[Node]:
    """A seat 1040 wide: two 20 mm sides 600 tall, a top on them, and a back panel 1000 wide
    and 500 tall between the sides, under the top, joined to the top and to each side. The
    connector carries 500 N in shear and 1000 N in pull-out in `wood`; the case asks for
    900 N across."""
    def q(v: float, unit: str = "") -> Quantity:
        return Quantity(value=v, unit=unit, provenance="design-target", grounded=False)

    def part(id_: str, size: list, at: list) -> Node:
        return Node(id=id_, kind="part", links={"uses": ["materials/panel"]},
                    params={"mass": q(5, "kg")},
                    payload={"shape": {"op": "box", "size": size}, "transform": {"translate": at}})

    def joint(id_: str, a: str, count: float) -> Node:
        return Node(id=id_, kind="joint", params={"count": q(count)},
                    links={"joins": ["seat/back", f"seat/{a}"], "uses": ["connectors/c"]})
    parts = [part("left", [20, 300, 600], [0, 0, 0]), part("right", [20, 300, 600], [1020, 0, 0]),
             part("top", [1040, 300, 20], [0, 0, 600]), part("back", [1000, 20, 500], [20, 280, 100]),
             joint("back-top", "top", top_count), joint("back-left", "left", side_count),
             joint("back-right", "right", side_count)]
    seat = Node(id="seat", kind="piece", children=parts,
                links={"braced_by": ["seat/back"]} if brace else {})
    panel = Node(id="panel", kind="material", payload={"connector_key": key})
    c = Node(id="c", kind="connector", params={"shear_wood": q(500, "N"),
                                               "pull_out_wood": q(1000, "N")})
    case = Node(id="across", kind="requirement", params={"side_force": q(900, "N")})
    return [seat, Node(id="materials", kind="", children=[panel]),
            Node(id="connectors", kind="", children=[c]),
            Node(id="requirements", kind="", children=[case])]


SPEC = {
    "furniture/sideways_margin": [
        d("sideways_margin", braced(), ["seat", "requirements/across"], expect=550,
          because="top edge: 4 x 500 - 900 = 1100 in shear; each side edge: 2 x 500 - "
                  "900 x 500/1000 = 550 in shear, 2 x 1000 - 900 = 1100 in pull-out: the "
                  "side edges' shear governs, 550 N to spare"),
        d("sideways_margin", braced(side_count=1), ["seat", "requirements/across"], expect=50,
          because="one connector per side edge: 500 - 450 in shear, 1000 - 900 = 100 in "
                  "pull-out: shear governs"),
        d("sideways_margin", braced(top_count=1), ["seat", "requirements/across"], expect=-400,
          because="one connector along the top edge takes the whole 900 N against 500"),
        d("sideways_margin", braced(brace=False), ["seat", "requirements/across"],
          expect=-900,
          because="an unbraced piece would rely on joints resisting bending, which nothing "
                  "here rates: the whole force is its shortfall"),
        d("sideways_margin", braced(key="plywood"), ["seat", "requirements/across"],
          expect_error="states no shear strength in plywood",
          because="a connector rated only in other materials says nothing about this one"),
    ],
    "furniture/deflection": [
        d("deflection", beam(), ["shelf/board"], expect=_BENDING + _SHEAR,
          because="solid wood: the bending term with the true modulus, plus the shear term "
                  "with the G the part names"),
        d("deflection", beam(modulus="apparent", shear=None), ["shelf/board"], expect=_BENDING,
          because="a panel whose modulus was measured on the panel already holds its shear "
                  "deflection: the bending term alone"),
        d("deflection", beam(shear=None), ["shelf/board"], expect_error="names no shear modulus",
          because="solid wood with no G named is refused, never judged without its shear term"),
        d("deflection", beam(cases=2), ["shelf/board"], expect_error="must link one",
          because="a part bent two ways at once is refused"),
        d("deflection", beam(load=20), ["shelf/board"], expect=2 * (_BENDING + _SHEAR),
          because="twice the load, twice the deflection: the equation is linear in W"),
    ],
    # Equation (4-5) evaluated by hand; Table 4-2 prints these as 9.2, 16.0 and 6.2
    # (tests/test_knowledge.py holds the equation to the table across its range).
    "furniture/emc": [
        d("emc", climate(21.1, 0.3, 0.5), ["climates/room", "max"], expect=9.242582321706546,
          because="21.1 °C at 50% relative humidity: Table 4-2 says 9.2%"),
        d("emc", climate(21.1, 0.3, 0.8), ["climates/room", "max"], expect=15.98957591023807,
          because="21.1 °C at 80%: Table 4-2 says 16.0%"),
        d("emc", climate(21.1, 0.3, 0.8), ["climates/room", "min"], expect=6.169754722200033,
          because="the dry end of the same climate, 30%: Table 4-2 says 6.2%"),
        d("emc", climate(21.1, 0.3, 0.8, linked=False), ["climates/room", "max"],
          expect_error="must link one equation",
          because="a climate that names no equation is refused, never given a moisture content"),
    ],
    "furniture/mass": [
        d("mass", [chest()], ["chest"], expect=45, because="the parts' own masses, summed"),
        d("mass", [OAK, BOARD], ["board"], expect=700 * 1000 * 100 * 10 * 1e-9,
          because="a part with no mass of its own weighs its volume times the density of "
                  "the material it uses"),
        d("mass", [UNWEIGHED], ["board"], expect_error="no mass and no density",
          because="a part with neither a mass nor a material is refused, never weighed 0"),
    ],
    "furniture/height": [
        d("height", [chest()], ["chest"], expect=800, because="the carcass is the tallest part"),
        d("height", [OAK, BOARD], ["board"], expect=10, because="a board lying flat"),
    ],
    "furniture/overturning_margin": [
        d("overturning_margin", [chest(), reqs(case("open"))], ["chest", "requirements/open"],
          expect=G * STANDING, because="every drawer open and nothing on it: it stands"),
        d("overturning_margin", [chest(), reqs(case("heavy", point_mass=27))],
          ["chest", "requirements/heavy"], expect=G * (STANDING + 27 * -400),
          because="27 kg on the open drawer's front edge tips it"),
        d("overturning_margin", [chest(), reqs(case("tilted", tilt_block=50))],
          ["chest", "requirements/tilted"],
          expect=G * (40 * (250 * 500 / 502.4937810560445 - 400 * 50 / 502.4937810560445)
                      + 5 * (-175 * 500 / 502.4937810560445 - 600 * 50 / 502.4937810560445)),
          because="a 50 mm block under the rear supports leans it forward: each lever arm is "
                  "y cos θ - z sin θ, with tan θ = 50/500"),
        d("overturning_margin",
          [chest(drawer_volume=60e6, storage_volume=100e6),
           reqs(case("filled", fill_density=1000, fill_share=0.5))],
          ["chest", "requirements/filled"], expect=G * (STANDING + 1000 * 60e6 * 1e-9 * -175),
          because="the drawer holds 60% of the storage volume, so it is filled at the "
                  "density the case states"),
        d("overturning_margin",
          [chest(drawer_volume=40e6, storage_volume=100e6),
           reqs(case("unfilled", fill_density=1000, fill_share=0.5))],
          ["chest", "requirements/unfilled"], expect=G * STANDING,
          because="the drawer holds 40% of the storage volume, under the share, so no fill"),
        d("overturning_margin", [chest(), reqs()], ["chest", "requirements/ghost"],
          expect_error="no requirement at",
          because="a case that is not in the tree is refused"),
    ],
    "furniture/tipping_cases": [
        d("tipping_cases",
          [Node(id="chest", kind="piece", children=chest().children,
                links={"stability_case": ["requirements/open", "requirements/heavy"]}),
           reqs(case("open"), case("heavy", point_mass=27))],
          ["chest"], expect=1, because="it stands open and tips under 27 kg: one case of two"),
        d("tipping_cases",
          [Node(id="chest", kind="piece", children=chest().children,
                links={"stability_case": ["requirements/open"]}),
           reqs(case("open"))],
          ["chest"], expect=0, because="held only to the case it passes"),
    ],
    "furniture/unheld": [
        d("unheld", [chest(storage_volume=100e6),
                     reqs(case("csu", min_height=686, min_mass=13.6, min_storage_volume=90e6))],
          ["chest"], expect=1,
          because="800 tall, 45 kg, 100 litres: in scope, and it links to no requirement"),
        d("unheld", [chest(storage_volume=50e6),
                     reqs(case("csu", min_height=686, min_mass=13.6, min_storage_volume=90e6))],
          ["chest"], expect=0, because="50 litres is under the scope's storage volume"),
        d("unheld", [chest(), reqs(case("csu", min_storage_volume=90e6))], ["chest"],
          expect_error="states no storage_volume",
          because="a piece that does not say what it holds cannot be judged out of scope"),
    ],
}
