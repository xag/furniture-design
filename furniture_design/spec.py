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

SPEC = {
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
