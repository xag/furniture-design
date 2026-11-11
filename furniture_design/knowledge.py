"""The knowledge base: published sources, the clauses quoted from them, and what is derived
from those clauses (materials, requirements), as quern nodes a design tree mounts beside
its pieces.

Three branches, each a top-level node of the tree that uses them:

    sources/        one `source` per publication, its `clause`s beneath it. A clause
                    quotes the publication verbatim (`quote`, checked against the
                    capture under sources/ in this repo) and carries, as params, the
                    quantities it states, converted to SI. What a clause states in a
                    form text extraction cannot read (an equation, a table row) is
                    given as `transcribed`, read from the page and marked as such.
    materials/      one `material` per material, its properties as params, each derived
                    from clauses (`derived_from`). A part made of a material links to
                    it with `uses` and reads its properties as its own.
    requirements/   one `requirement` per checkable demand, linked `per` the clauses it
                    rests on, its limits and test conditions as params.

Nothing here is shaped by one check. A new check reads what is here, and a new source adds
a source, its clauses and what they let us derive; neither changes the kinds.

Only public-domain sources are captured and quoted in this repo (ledger:
a-copyrighted-standard-is-cited-never-copied-here).
"""

from __future__ import annotations

from quern.provenance import Quantity
from quern.tree import Node

from .units import CUBIC_FOOT_MM3, INCH_MM, POUND_KG, POUND_PER_CUBIC_FOOT_KG_M3

SOURCES = "sources"
MATERIALS = "materials"
REQUIREMENTS = "requirements"

WOOD_HANDBOOK = f"{SOURCES}/wood-handbook"
FEDERAL_REGISTER = f"{SOURCES}/federal-register-2023-08997"


def published(value: float, unit: str, where: str, note: str | None = None) -> Quantity:
    """A quantity a clause states, grounded because a publication states it."""
    return Quantity(value=value, unit=unit, provenance="published", grounded=True,
                    source=where, note=note)


def derived(value: float, unit: str, refs: list[str], note: str) -> Quantity:
    """A quantity computed from clauses; `derived_from` names every one it used."""
    return Quantity(value=value, unit=unit, provenance="derived", grounded=True,
                    derived_from=refs, note=note)


def _clause(id_: str, locator: str, quote: str, *, transcribed: str | None = None,
            params: dict[str, Quantity] | None = None, **payload) -> Node:
    body = {"locator": locator, "quote": quote, **payload}
    if transcribed:
        body["transcribed"] = transcribed
    return Node(id=id_, kind="clause", payload=body, params=params or {})


# --- the Wood Handbook ------------------------------------------------------------------

# One table row of Table 5-3a (12% moisture content) and of Table 5-1, per species:
# (id, name, Table 5-3a quote, specific gravity at 12%, modulus of elasticity MPa,
#  Table 5-1 quote, G_LR/E_L, G_LT/E_L)
SPECIES = [
    ("birch-yellow", "Birch, yellow",
     "Yellow Green 0.55 57,000 10,300 111 1,220 23,300 3,000 7,700 3,000 3,600 "
     "12% 0.62 114,000 13,900 143 1,400 56,300 6,700 13,000 6,300 5,600", 0.62, 13_900,
     "Birch, yellow 0.050 0.078 0.074 0.068 0.017", 0.074, 0.068),
    ("cherry-black", "Cherry, black",
     "Cherry, black Green 0.47 55,000 9,000 88 840 24,400 2,500 7,800 3,900 2,900 "
     "12% 0.50 85,000 10,300 79 740 49,000 4,800 11,700 3,900 4,200", 0.50, 10_300,
     "Cherry, black 0.086 0.197 0.147 0.097 —", 0.147, 0.097),
    ("maple-sugar", "Maple, sugar",
     "Sugar Green 0.56 65,000 10,700 92 1,020 27,700 4,400 10,100 — 4,300 "
     "12% 0.63 109,000 12,600 114 990 54,000 10,100 16,100 — 6,400", 0.63, 12_600,
     "Maple, sugar 0.065 0.132 0.111 0.063 —", 0.111, 0.063),
    ("oak-northern-red", "Oak, northern red",
     "Northern red Green 0.56 57,000 9,300 91 1,120 23,700 4,200 8,300 5,200 4,400 "
     "12% 0.63 99,000 12,500 100 1,090 46,600 7,000 12,300 5,500 5,700", 0.63, 12_500,
     "Oak, red 0.082 0.154 0.089 0.081 —", 0.089, 0.081),
    ("walnut-black", "Walnut, black",
     "Walnut, black Green 0.51 66,000 9,800 101 940 29,600 3,400 8,400 3,900 4,000 "
     "12% 0.55 101,000 11,600 74 860 52,300 7,000 9,400 4,800 4,500", 0.55, 11_600,
     "Walnut, black 0.056 0.106 0.085 0.062 0.021", 0.085, 0.062),
    ("yellow-poplar", "Yellow-poplar",
     "Yellow-poplar Green 0.40 41,000 8,400 52 660 18,300 1,900 5,400 3,500 2,000 "
     "12% 0.42 70,000 10,900 61 610 38,200 3,400 8,200 3,700 2,400", 0.42, 10_900,
     "Yellow-poplar 0.043 0.092 0.075 0.069 0.011", 0.075, 0.069),
]

# Table 9-1: (id, loading, supports, deflection at, kb, ks, row as printed)
BEAM_CASES = [
    ("uniform-simply-supported", "uniform", "both simply supported", "midspan", 5 / 384, 1 / 8,
     "Uniformly distributed | Both simply supported | Midspan | 5/384 | 1/8"),
    ("uniform-clamped", "uniform", "both clamped", "midspan", 1 / 384, 1 / 8,
     "Uniformly distributed | Both clamped | Midspan | 1/384 | 1/8"),
    ("midspan-point-simply-supported", "point at midspan", "both simply supported", "midspan",
     1 / 48, 1 / 4, "Concentrated at midspan | Both simply supported | Midspan | 1/48 | 1/4"),
    ("midspan-point-clamped", "point at midspan", "both clamped", "midspan", 1 / 192, 1 / 4,
     "Concentrated at midspan | Both clamped | Midspan | 1/192 | 1/4"),
    ("quarter-points-simply-supported", "points at outer quarter spans", "both simply supported",
     "midspan", 11 / 768, 1 / 8,
     "Concentrated at outer quarter span points | Both simply supported | Midspan | 11/768 | 1/8"),
    ("quarter-points-clamped", "points at outer quarter spans", "both clamped", "load point",
     1 / 96, 1 / 8,
     "Concentrated at outer quarter span points | Both clamped | Load point | 1/96 | 1/8"),
    ("uniform-cantilever", "uniform", "cantilever, one free, one clamped", "free end", 1 / 8, 1 / 2,
     "Uniformly distributed | Cantilever, one free, one clamped | Free end | 1/8 | 1/2"),
    ("end-point-cantilever", "point at free end", "cantilever, one free, one clamped", "free end",
     1 / 3, 1.0,
     "Concentrated at free end | Cantilever, one free, one clamped | Free end | 1/3 | 1"),
]


def wood_handbook() -> Node:
    wh = WOOD_HANDBOOK
    clauses = [
        _clause("density-4-14", "Chapter 4, Equation (4–14), p. 4–12",
                "Density is then calculated by",
                transcribed="ρx = ρw Gx (1 + x/100), with ρw the density of water, "
                            "1,000 kg m–3 (p. 4–11)",
                params={"water_density": published(1000.0, "kg/m3", "p. 4–11")}),
        _clause("water-density", "Chapter 4, p. 4–11",
                "1.000 g cm–3 (1,000 kg m–3 or 62.43 lb ft"),
        _clause("table-5-3a-note-b", "Chapter 5, Table 5–3a, footnote b, p. 5–8",
                "Specific gravity is based on weight when ovendry and volume when green or at "
                "12% moisture content."),
        _clause("table-5-3a-note-c", "Chapter 5, Table 5–3a, footnote c, p. 5–8",
                "Modulus of elasticity measured from a simply supported, center-loaded beam, on "
                "a span depth ratio of 14/1. To correct for shear deflection, the modulus can be "
                "increased by 10%.",
                params={"shear_correction": published(1.10, "", "Table 5–3a footnote c",
                                                      "increased by 10%")}),
        _clause("table-5-1-note-a", "Chapter 5, Table 5–1, footnote a, p. 5–3",
                "may be approximated by increasing modulus of elasticity values in Table 5–3 by "
                "10%."),
        _clause("creep-chapter-5", "Chapter 5, Creep and Relaxation, p. 5–39",
                "At typical design levels and use environments, after several years the "
                "additional deformation caused by creep may approximately equal the initial, "
                "instantaneous elastic deformation."),
        _clause("creep-chapter-9", "Chapter 9, Effect of Time: Creep Deflections, p. 9–4",
                "If deflection under longtime load with initially green timber is to be limited, "
                "it has been customary to design for an initial deflection of about half the "
                "value permitted for longtime deflection. If deflection under longtime load with "
                "initially dry timber is to be limited, it has been customary to design for an "
                "initial deflection of about two-thirds the value permitted for longtime "
                "deflection.",
                params={"initial_share_dry": published(2 / 3, "", "p. 9–4", "about two-thirds"),
                        "initial_share_green": published(0.5, "", "p. 9–4", "about half")}),
        _clause("deflection-9-2", "Chapter 9, Equation (9–2), p. 9–2",
                "Values of kb and ks for several cases of loading and support are given in "
                "Table 9–1.",
                transcribed="δ = kb W L³/(E I) + ks W L/(G A′), where W is the total beam load "
                            "acting perpendicular to the neutral axis, L the span, E the modulus "
                            "of elasticity (E = EL when the grain runs along the beam), G the "
                            "shear modulus (G = GLT for flat-grained vertical faces, G = GLR for "
                            "edge-grained vertical faces)"),
        _clause("inertia-9-3", "Chapter 9, Equation (9–3), p. 9–2",
                "the moment of inertia I of the beams is given by",
                transcribed="I = b h³ / 12 for a beam of rectangular cross section, b its width "
                            "and h its depth"),
        _clause("modified-area-9-4", "Chapter 9, Equation (9–4), p. 9–2",
                "The modified area A′ is given by",
                transcribed="A′ = (5/6) b h for a beam of rectangular cross section"),
    ]
    for id_, loading, supports, at, kb, ks, row in BEAM_CASES:
        clauses.append(_clause(
            f"table-9-1-{id_}", "Chapter 9, Table 9–1, p. 9–3",
            "Table 9–1. Values of kb and ks for several beam loadings",
            transcribed=row, loading=loading, supports=supports, deflection_at=at,
            params={"kb": published(kb, "", "Table 9–1"), "ks": published(ks, "", "Table 9–1")}))
    for id_, name, row, g12, e, row51, glr, glt in SPECIES:
        clauses.append(_clause(
            f"table-5-3a-{id_}", "Chapter 5, Table 5–3a, 12% moisture content row",
            row, species=name,
            params={"specific_gravity_12": published(g12, "", "Table 5–3a"),
                    "modulus_of_elasticity_table": published(float(e), "MPa", "Table 5–3a")}))
        clauses.append(_clause(
            f"table-5-1-{id_}", "Chapter 5, Table 5–1, p. 5–3", row51, species=name,
            params={"glr_ratio": published(glr, "", "Table 5–1 GLR/EL"),
                    "glt_ratio": published(glt, "", "Table 5–1 GLT/EL")}))
    return Node(id="wood-handbook", kind="source",
                name="Wood Handbook: Wood as an Engineering Material (FPL-GTR-282)",
                payload={"publisher": "USDA Forest Service, Forest Products Laboratory",
                         "year": 2021, "identifier": "FPL-GTR-282",
                         "url": "https://research.fs.usda.gov/download/treesearch/62200.pdf",
                         "sha256": "f0b488c5637614d8e69a07abf796f9e32d7a8df956ee75ab5cc5f64f3bd5ee6f",
                         "licence": "public-domain",
                         "capture": "sources/wood-handbook-fpl-gtr-282/pages.txt",
                         "capture_note": "text extracted from the pages quoted; the whole PDF "
                                         "is 104 MB and is identified by its sha256"},
                children=clauses)


def materials() -> Node:
    """Air-dried solid wood at 12% moisture content, one material per species."""
    wh = WOOD_HANDBOOK
    out = []
    for id_, name, _row, g12, e, _row51, glr, glt in SPECIES:
        row, row51 = f"{wh}/table-5-3a-{id_}", f"{wh}/table-5-1-{id_}"
        el = 1.10 * e
        out.append(Node(
            id=id_, kind="material", name=f"{name}, air-dried, 12% moisture content",
            payload={"form": "solid wood", "moisture_content_percent": 12, "dried": True},
            params={
                "density": derived(1000.0 * g12 * 1.12, "kg/m3",
                                   [f"{row}/specific_gravity_12", f"{wh}/density-4-14/water_density"],
                                   "ρ12 = ρw G12 (1 + 12/100), Equation (4–14)"),
                "modulus_of_elasticity": derived(el, "MPa",
                                                 [f"{row}/modulus_of_elasticity_table",
                                                  f"{wh}/table-5-3a-note-c/shear_correction"],
                                                 "EL: Table 5–3a's value increased by 10% "
                                                 "(footnote c, Table 5–1 footnote a)"),
                "shear_modulus_lr": derived(glr * el, "MPa", [f"{row51}/glr_ratio"],
                                            "GLR = (GLR/EL) EL, Table 5–1"),
                "shear_modulus_lt": derived(glt * el, "MPa", [f"{row51}/glt_ratio"],
                                            "GLT = (GLT/EL) EL, Table 5–1"),
                "initial_share_of_longtime": derived(2 / 3, "",
                                                     [f"{wh}/creep-chapter-9/initial_share_dry"],
                                                     "initially dry timber: design for an "
                                                     "initial deflection of about two-thirds "
                                                     "the permitted longtime deflection"),
            },
            links={"per": [row, row51]}))
    return Node(id="materials", kind="", children=out)


# --- the Federal Register: 16 CFR 1261, adopting ASTM F2057-23 ---------------------------

def federal_register() -> Node:
    clauses = [
        _clause("1261-1-b", "16 CFR 1261.1(b), 88 FR 28408",
                "Clothing storage unit means any free-standing furniture item manufactured in the "
                "United States or imported for use in the United States that is intended for the "
                "storage of clothing, typical of bedroom furniture."),
        _clause("1261-2", "16 CFR 1261.2, 88 FR 28408",
                "Each clothing storage unit that is subject to ASTM F2057-23, Standard Safety "
                "Specification for Clothing Storage Units, approved on February 1, 2023, shall "
                "comply with ASTM F2057-23."),
        _clause("scope-height", "Preamble II.B, STURDY sec. 201(c)(2), 88 FR 28405",
                "Testing of all clothing storage units as specified by the Commission, including "
                "those 27 inches and above in height",
                params={"height": published(27 * INCH_MM, "mm", "88 FR 28405", "27 inches")}),
        _clause("scope-mass", "Preamble II.B, 88 FR 28405",
                "The ASTM standard excludes units weighing less than 30 pounds empty.",
                params={"mass": published(30 * POUND_KG, "kg", "88 FR 28405", "30 pounds")}),
        _clause("scope-storage-volume", "Preamble II.B, 88 FR 28405",
                "Staff therefore concluded that the Commission could find that, based on tip-over "
                "data, testing units having a storage volume less than 3.2 cubic feet is not "
                "``reasonably necessary'' to protect children from injury or death.",
                params={"storage_volume": published(3.2 * CUBIC_FOOT_MM3, "mm3", "88 FR 28405",
                                                    "3.2 cubic feet")}),
        _clause("test-9-2-1", "Preamble II.B, describing ASTM F2057-23 section 9.2.1, 88 FR 28405",
                "Section 9.2.1 of the ASTM standard, Simulated Clothing Load, is a test conducted "
                "on a hard, level, and flat test surface with extendible elements and doors open "
                "and, if 50 percent or more of the storage volume is extended, the unit is to be "
                "filled with a ``simulated clothing load.'' The fill weight in extendible elements "
                "is calculated using a density of 8.5 pounds per cubic foot of volume",
                params={"fill_share": published(0.5, "", "88 FR 28405", "50 percent"),
                        "fill_density": published(8.5 * POUND_PER_CUBIC_FOOT_KG_M3, "kg/m3",
                                                  "88 FR 28405", "8.5 pounds per cubic foot")}),
        _clause("test-9-2-1-duration", "Preamble II.B, 88 FR 28405",
                "All extendible elements are opened and must remain open for 30 seconds without "
                "tip over."),
        _clause("test-9-2-3", "Preamble II.B, describing ASTM F2057-23 section 9.2.3, 88 FR 28405",
                "The third stability test, Section 9.2.3 Simulating a Reaction on Carpet with "
                "Child Weight, uses 60 pounds of weight placed on the edge of an open drawer or "
                "pull-out shelf, while the CSU is tilted forward using a 0.43 inch test block to "
                "simulate placement on a carpeted surface, with all doors and extendible elements "
                "open.",
                params={"point_mass": published(60 * POUND_KG, "kg", "88 FR 28405", "60 pounds"),
                        "tilt_block": published(0.43 * INCH_MM, "mm", "88 FR 28405",
                                                "0.43 inch")}),
    ]
    return Node(id="federal-register-2023-08997", kind="source",
                name="Safety Standard for Clothing Storage Units, direct final rule, "
                     "88 FR 28403 (16 CFR part 1261)",
                payload={"publisher": "U.S. Consumer Product Safety Commission, Federal Register",
                         "year": 2023, "identifier": "FR Doc. 2023-08997",
                         "url": "https://www.govinfo.gov/content/pkg/FR-2023-05-04/html/2023-08997.htm",
                         "sha256": "a7115d8ddab5916aa5eca3146f9a12d535dac1a796679e524cd08de1a0e48e5f",
                         "licence": "public-domain",
                         "capture": "sources/federal-register-2023-08997/2023-08997.txt",
                         "note": "The rule adopts ASTM F2057-23 by reference; its test methods "
                                 "are ASTM's and copyrighted. What is quoted here is the "
                                 "Commission's public description of them."},
                children=clauses)


def requirements() -> Node:
    fr = FEDERAL_REGISTER

    def scope_params() -> dict[str, Quantity]:
        return {
            "min_height": derived(27 * INCH_MM, "mm", [f"{fr}/scope-height/height"], "27 inches"),
            "min_mass": derived(30 * POUND_KG, "kg", [f"{fr}/scope-mass/mass"], "30 pounds empty"),
            "min_storage_volume": derived(3.2 * CUBIC_FOOT_MM3, "mm3",
                                          [f"{fr}/scope-storage-volume/storage_volume"],
                                          "3.2 cubic feet"),
        }

    scope = {"category": "clothing-storage-unit"}
    prediction = ("A static calculation predicts this physical test from the design's masses "
                  "and positions; passing it is not compliance, which is the test itself.")
    clothing = Node(
        id="csu-simulated-clothing-load", kind="requirement",
        name="A clothing storage unit does not tip with every extendible element open and, when "
             "half or more of its storage volume extends, filled with the simulated clothing load",
        payload={"measure": "overturning", "scope": scope, "extendibles": "open",
                 "prediction": prediction},
        params={**scope_params(),
                "tilt_block": derived(0.0, "mm", [f"{fr}/test-9-2-1"], "a hard, level, and flat "
                                      "test surface"),
                "point_mass": derived(0.0, "kg", [f"{fr}/test-9-2-1"], "no added weight"),
                "fill_share": derived(0.5, "", [f"{fr}/test-9-2-1/fill_share"], "50 percent"),
                "fill_density": derived(8.5 * POUND_PER_CUBIC_FOOT_KG_M3, "kg/m3",
                                        [f"{fr}/test-9-2-1/fill_density"],
                                        "8.5 pounds per cubic foot")},
        links={"per": [f"{fr}/test-9-2-1", f"{fr}/test-9-2-1-duration", f"{fr}/1261-1-b",
                       f"{fr}/1261-2", f"{fr}/scope-height", f"{fr}/scope-mass",
                       f"{fr}/scope-storage-volume"]})
    carpet = Node(
        id="csu-carpet-child-weight", kind="requirement",
        name="A clothing storage unit tilted forward on the carpet block, every extendible "
             "element open, does not tip with 60 pounds on the edge of an open drawer or "
             "pull-out shelf",
        payload={"measure": "overturning", "scope": scope, "extendibles": "open",
                 "point_load_at": "front top edge of each open extendible element, one at a time",
                 "tilt": "the rear supports raised by the block, so the unit leans forward",
                 "prediction": prediction},
        params={**scope_params(),
                "tilt_block": derived(0.43 * INCH_MM, "mm", [f"{fr}/test-9-2-3/tilt_block"],
                                      "0.43 inch"),
                "point_mass": derived(60 * POUND_KG, "kg", [f"{fr}/test-9-2-3/point_mass"],
                                      "60 pounds")},
        links={"per": [f"{fr}/test-9-2-3", f"{fr}/1261-1-b", f"{fr}/1261-2",
                       f"{fr}/scope-height", f"{fr}/scope-mass", f"{fr}/scope-storage-volume"]})
    return Node(id="requirements", kind="", children=[clothing, carpet])


def knowledge() -> list[Node]:
    """The three top-level branches a design tree mounts: sources, materials, requirements."""
    return [Node(id="sources", kind="", children=[wood_handbook(), federal_register()]),
            materials(), requirements()]
