"""The knowledge base: published sources, the clauses quoted from them, and what is derived
from those clauses (materials, requirements), as quern nodes a design tree mounts beside
its pieces.

Four branches, each a top-level node of the tree that uses them (the fourth, tools/, holds
the hand tools that cut a part's cuts, each saying how it is used and linked `per` the
clauses that say so):

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

Only public-domain and CC BY sources are captured and quoted in this repo (ledger:
a-copyrighted-standard-is-cited-never-copied-here,
an-open-licensed-source-is-quoted-like-a-public-domain-one).
"""

from __future__ import annotations

from quern.provenance import Quantity
from quern.tree import Node

from .units import (CUBIC_FOOT_MM3, INCH_MM, POUND_FORCE_N, POUND_KG, POUND_PER_CUBIC_FOOT_KG_M3,
                    POUND_PER_FOOT_KG_M, POUND_PER_SQUARE_FOOT_KG_M2)

SOURCES = "sources"
# The licences under which a source's words may be quoted here and its quoted pages kept under
# sources/ (ledger: an-open-licensed-source-is-quoted-like-a-public-domain-one); any other
# source is cited by locator and values
OPEN_LICENCES = ("public-domain", "cc-by-4.0")
MATERIALS = "materials"
REQUIREMENTS = "requirements"

WOOD_HANDBOOK = f"{SOURCES}/wood-handbook"
FEDERAL_REGISTER = f"{SOURCES}/federal-register-2023-08997"
GSA_FNAE = f"{SOURCES}/gsa-fnae-80-214a"

# FNAE-80-214A, Table 1: the acceptance levels of the sidethrust load test on legs (7.4),
# pounds of force, each held for 25,000 cycles
SIDETHRUST_LEG_LBF = {"light": 200, "medium": 250, "heavy": 350}


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

# Table 5-3a, 12% moisture content: the modulus of rupture (kPa), the number after the
# specific gravity in each row quoted above
MOR_KPA = {"birch-yellow": 114_000, "cherry-black": 85_000, "maple-sugar": 109_000,
           "oak-northern-red": 99_000, "walnut-black": 101_000, "yellow-poplar": 70_000}

# Table 12-2, plywood sheathing products: (id, species, row as extracted, specific gravity,
# MOE GPa, MOR MPa). The table does not say which way the panels were bent.
PLYWOOD_SHEATHING = [
    ("baldcypress", "Baldcypress", "Baldcypress 0.50 7.58 (1.10) 39.23 (5,690)", 0.50, 7.58, 39.23),
    ("douglas-fir", "Douglas-fir", "Douglas-fir 0.53 7.45 (1.08) 41.37 (6,000)", 0.53, 7.45, 41.37),
    ("lauan", "Lauan", "Lauan 0.44 7.43 (1.08) 33.72 (4, 890)", 0.44, 7.43, 33.72),
    ("western-redcedar", "Western redcedar", "Western 0.41 8.55 (1.24) 37.37 (5,420)", 0.41,
     8.55, 37.37),
    ("redwood", "Redwood", "Redwood 0.41 6.96 (1.01) 42.61 (6, 180)", 0.41, 6.96, 42.61),
    ("southern-pine", "Southern Pine", "Southern Pine 0.57 7.70 (1.12) 37. 09 (5,380)", 0.57,
     7.70, 37.09),
]

# Table 12-1, panel products with no veneer: (id, name, row as extracted, specific gravity
# low and high, MOE GPa low and high, MOR MPa low and high)
FIBRE_PANELS = [
    ("medium-density-fiberboard", "Medium-density fiberboard",
     "Medium-density fiberboard 0.7–0.9 3.59 (0.52) 35.85 (5,200)", 0.7, 0.9, 3.59, 3.59,
     35.85, 35.85),
    ("particleboard", "Particleboard",
     "Particleboard 0.6–0.8 2.76–4.14 (0.40–0.60) 15.17–24.13 (2,200–3,500)", 0.6, 0.8, 2.76,
     4.14, 15.17, 24.13),
]

# The 5% point of a normal distribution, in standard deviations below the mean: how a near-
# minimum is read off a mean and a coefficient of variation (ledger:
# a-design-stress-is-the-near-minimum-strength-over-the-handbooks-factor)
NORMAL_5_PERCENT = 1.645

# Table 13-5: (Table 13-5 quote, CR, CT), per species id — the change in dimension per
# percent of moisture content, across the grain, radial and tangential
MOVEMENT = {
    "birch-yellow": ("Birch, yellow 0.00256 0.00338", 0.00256, 0.00338),
    "cherry-black": ("Cherry, black 0.00126 0.00248", 0.00126, 0.00248),
    "maple-sugar": ("Maple, sugar 0.00165 0.00353", 0.00165, 0.00353),
    "oak-northern-red": ("Red oak, northern red 0.00137 0.00304", 0.00137, 0.00304),
    "walnut-black": ("Walnut, black 0.00190 0.00274", 0.00190, 0.00274),
    "yellow-poplar": ("Poplar, yellow 0.00158 0.00289", 0.00158, 0.00289),
}

# Equation 4-5's temperature terms, T in °C: (name, constant, × T, × T²)
EMC_TERMS = [("W", 349, 1.29, 0.0135), ("K", 0.805, 0.000736, -0.00000273),
             ("K1", 6.27, -0.00938, -0.000303), ("K2", 1.91, 0.0407, -0.000293)]

# Table 9-1: (id, loading, supports, deflection at, kb, ks, row as printed, km). km is not
# in the table: it is the largest bending moment over W L for that loading and support, by
# statics (equilibrium of the beam; for the clamped cases, the end moments of a beam fixed
# at both ends), and Equation (9-13) turns it into a stress.
BEAM_CASES = [
    ("uniform-simply-supported", "uniform", "both simply supported", "midspan", 5 / 384, 1 / 8,
     "Uniformly distributed | Both simply supported | Midspan | 5/384 | 1/8", 1 / 8),
    ("uniform-clamped", "uniform", "both clamped", "midspan", 1 / 384, 1 / 8,
     "Uniformly distributed | Both clamped | Midspan | 1/384 | 1/8", 1 / 12),
    ("midspan-point-simply-supported", "point at midspan", "both simply supported", "midspan",
     1 / 48, 1 / 4, "Concentrated at midspan | Both simply supported | Midspan | 1/48 | 1/4", 1 / 4),
    ("midspan-point-clamped", "point at midspan", "both clamped", "midspan", 1 / 192, 1 / 4,
     "Concentrated at midspan | Both clamped | Midspan | 1/192 | 1/4", 1 / 8),
    ("quarter-points-simply-supported", "points at outer quarter spans", "both simply supported",
     "midspan", 11 / 768, 1 / 8,
     "Concentrated at outer quarter span points | Both simply supported | Midspan | 11/768 | 1/8",
     1 / 8),
    ("quarter-points-clamped", "points at outer quarter spans", "both clamped", "load point",
     1 / 96, 1 / 8,
     "Concentrated at outer quarter span points | Both clamped | Load point | 1/96 | 1/8", 3 / 32),
    ("uniform-cantilever", "uniform", "cantilever, one free, one clamped", "free end", 1 / 8, 1 / 2,
     "Uniformly distributed | Cantilever, one free, one clamped | Free end | 1/8 | 1/2", 1 / 2),
    ("end-point-cantilever", "point at free end", "cantilever, one free, one clamped", "free end",
     1 / 3, 1.0,
     "Concentrated at free end | Cantilever, one free, one clamped | Free end | 1/3 | 1", 1.0),
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
    emc = {}
    for name, c0, c1, c2 in EMC_TERMS:
        emc[f"{name}_0"] = published(float(c0), "", "Equation (4–5)", f"{name}, constant term")
        emc[f"{name}_1"] = published(c1, "1/degC", "Equation (4–5)", f"{name}, times T")
        emc[f"{name}_2"] = published(c2, "1/degC2", "Equation (4–5)", f"{name}, times T squared")
    clauses += [
        _clause("emc-4-5", "Chapter 4, Equilibrium Moisture Content, Equation (4–5), p. 4–3",
                "For temperature T in °C, W = 349 + 1.29T + 0.0135T2 K = 0.805 + 0.000736T – "
                "0.00000273T2 K1 = 6.27 – 0.00938T – 0.000303T2 K2 = 1.91 + 0.0407T – "
                "0.000293T2",
                transcribed="EMC(%) = (1,800/W) [Kh/(1 − Kh) + (K1Kh + 2K1K2K²h²)/(1 + K1Kh + "
                            "K1K2K²h²)], h the relative humidity as a decimal; Table 4–2 is "
                            "calculated from it",
                params=emc),
        _clause("dimensional-change-13-3", "Chapter 13, Equation (13–3), p. 13–16",
                "The change in dimension within the moisture content limits of 6% to 14% can be "
                "estimated satisfactorily by using a dimensional change coefficient based on the "
                "dimension at 10% moisture content:",
                transcribed="ΔD = DI [CT (MF − MI)], DI the dimension at the start, CT the "
                            "tangential coefficient (CR for radial), MF and MI the moisture "
                            "content (%) at the end and the start",
                params={"mc_min": published(6.0, "%", "p. 13–16", "6%"),
                        "mc_max": published(14.0, "%", "p. 13–16", "14%")}),
    ]
    for id_, (row, cr, ct) in MOVEMENT.items():
        clauses.append(_clause(
            f"table-13-5-{id_}", "Chapter 13, Table 13–5, p. 13–17", row,
            params={"cr": published(cr, "1/%", "Table 13–5 CR"),
                    "ct": published(ct, "1/%", "Table 13–5 CT")}))
    clauses += [
        _clause("bending-stress-9-13", "Chapter 9, Straight Beam Stresses, Equation (9–13), p. 9–7",
                "where fb is bending stress, M bending moment, and S beam section modulus (for a "
                "rectangular cross section, S = bh2/6;",
                transcribed="fb = M / S, S = b h² / 6 for a rectangular cross section"),
        _clause("cov-table-5-6", "Chapter 5, Table 5–6, p. 5–26",
                "Static bending Modulus of rupture 16 Modulus of elasticity 22",
                params={"cov_modulus_of_rupture": published(0.16, "", "Table 5–6", "16%"),
                        "cov_modulus_of_elasticity": published(0.22, "", "Table 5–6", "22%")}),
        _clause("cov-table-5-6-note-a", "Chapter 5, Table 5–6, footnote a, p. 5–26",
                "Values for wood adjusted to 12% moisture content may be assumed to be "
                "approximately of the same magnitude."),
        _clause("near-minimum-7-6", "Chapter 7, Visually Graded Structural Lumber, p. 7–6",
                "it is intended that the actual strength of at least 95% of the pieces in a "
                "grade exceed the design properties (before reduction for duration of load and "
                "safety) assigned to that grade.",
                params={"exclusion": published(0.05, "", "p. 7–6", "at least 95% exceed")}),
        _clause("near-minimum-7-6-name", "Chapter 7, p. 7–6",
                "minimum value is called the 5% exclusion limit.",
                transcribed="The near-minimum value is called the 5% exclusion limit. (The "
                            "page breaks near- across two lines.)"),
        _clause("design-factor-7-10", "Chapter 7, Machine-Graded Structural Lumber, p. 7–10",
                "This value is then adjusted by a factor (2.1) for assumed 10-year duration of "
                "load and safety to obtain Fb.",
                params={"bending_factor": published(2.1, "", "p. 7–10", "a factor (2.1)")}),
        _clause("short-load-5-40", "Chapter 5, Duration of Load, p. 5–40",
                "Conversely, if the duration of load is very short, the load-carrying capacity "
                "may be higher than that determined from strength properties given in the "
                "tables."),
        _clause("panels-uniform-12-2", "Chapter 12, p. 12–2",
                "Although the mechanical properties of most wood composites might not be as "
                "high as those of solid wood, they provide very consistent and uniform "
                "performance."),
        _clause("bending-moe-12-2", "Chapter 12, Modulus of Elasticity, p. 12–2",
                "Bending MOE is a measure of the resistance to bending deflection, which is "
                "relative to the stiffness."),
        _clause("table-19-2-note-a", "Chapter 19, Table 19–2, footnote a, p. 19–8",
                "aLaminates made from 17 plies of 1.6-mm (1/16-in.) rotary-cut yellow birch "
                "veneer."),
        _clause("table-19-2-note-b", "Chapter 19, Table 19–2, footnote b, p. 19–8",
                "with phenol resin film adhesive."),
        _clause("table-19-2-crossband-flexure", "Chapter 19, Table 19–2, Crossband laminates, "
                "Normal laminated wood column, p. 19–8",
                "Flexure—face grain parallel to span (flatwise)",
                transcribed="Crossband laminates, Flexure—face grain parallel to span "
                            "(flatwise), Normal laminated wood: Modulus of rupture 90.3 MPa "
                            "(13,100 lb in–2), Modulus of elasticity 9.0 GPa (1,310 × 1,000 lb "
                            "in–2); read from the page, the extracted text splits the columns",
                bent="face grain parallel to span, load on the face",
                params={"modulus_of_rupture": published(90.3, "MPa", "Table 19–2"),
                        "modulus_of_elasticity": published(9000.0, "MPa", "Table 19–2",
                                                           "9.0 GPa")}),
        _clause("table-19-2-crossband-edgewise", "Chapter 19, Table 19–2, Crossband laminates, "
                "Normal laminated wood column, p. 19–8",
                "Compression parallel to face grain (edgewise)",
                transcribed="Crossband laminates, Normal laminated wood: Compression parallel to "
                            "face grain (edgewise), Ultimate strength 40.0 MPa (5,800 lb in–2), "
                            "Modulus of elasticity 9.4 GPa; Tension parallel to face grain "
                            "(lengthwise), Ultimate strength 84.8 MPa (12,300 lb in–2), Modulus "
                            "of elasticity 8.9 GPa; read from the page",
                params={"compression_strength": published(40.0, "MPa", "Table 19–2"),
                        "compression_modulus": published(9400.0, "MPa", "Table 19–2", "9.4 GPa"),
                        "tension_strength": published(84.8, "MPa", "Table 19–2"),
                        "tension_modulus": published(8900.0, "MPa", "Table 19–2", "8.9 GPa")}),
        _clause("table-19-2-note-f", "Chapter 19, Table 19–2, footnote f, p. 19–8",
                "fForest Products Laboratory (FPL) test procedure: load applied to edge of "
                "laminations (perpendicular to laminating pressure direction)."),
        _clause("table-19-3-note-b", "Chapter 19, Table 19–3, footnote b, p. 19–8",
                "bAll wood laminates made from rotary-cut veneer, annual rings in plane of sheet."),
        _clause("cov-table-5-6-compression", "Chapter 5, Table 5–6, p. 5–26",
                "Compression parallel to grain 18",
                params={"cov_compression_parallel": published(0.18, "", "Table 5–6", "18%")}),
        _clause("table-19-3-birch-laminate", "Chapter 19, Table 19–3, p. 19–8",
                "Yellow birch laminate 0.72 3.1 3.254 40.29 36.64 80.18",
                params={"specific_gravity": published(0.72, "", "Table 19–3",
                                                      "specific gravity of product")}),
    ]
    for id_, name, row, g, e, mor in PLYWOOD_SHEATHING:
        clauses.append(_clause(
            f"table-12-2-{id_}", "Chapter 12, Table 12–2, p. 12–4", row, species=name,
            transcribed=f"{name}: specific gravity {g}, static bending MOE {e} GPa, MOR {mor} "
                        "MPa; the table does not say whether the panels were bent along or "
                        "across the face grain",
            params={"specific_gravity": published(g, "", "Table 12–2"),
                    "modulus_of_elasticity": published(e * 1000, "MPa", "Table 12–2", f"{e} GPa"),
                    "modulus_of_rupture": published(mor, "MPa", "Table 12–2")}))
    for id_, name, row, g0, g1, e0, e1, m0, m1 in FIBRE_PANELS:
        clauses.append(_clause(
            f"table-12-1-{id_}", "Chapter 12, Table 12–1, p. 12–2", row,
            params={"specific_gravity_low": published(g0, "", "Table 12–1"),
                    "specific_gravity_high": published(g1, "", "Table 12–1"),
                    "modulus_of_elasticity_low": published(e0 * 1000, "MPa", "Table 12–1"),
                    "modulus_of_elasticity_high": published(e1 * 1000, "MPa", "Table 12–1"),
                    "modulus_of_rupture_low": published(m0, "MPa", "Table 12–1"),
                    "modulus_of_rupture_high": published(m1, "MPa", "Table 12–1")}))
    for id_, loading, supports, at, kb, ks, row, km in BEAM_CASES:
        clauses.append(_clause(
            f"table-9-1-{id_}", "Chapter 9, Table 9–1, p. 9–3",
            "Table 9–1. Values of kb and ks for several beam loadings",
            transcribed=row, loading=loading, supports=supports, deflection_at=at,
            params={"kb": published(kb, "", "Table 9–1"), "ks": published(ks, "", "Table 9–1"),
                    "km": derived(km, "", [f"{wh}/bending-stress-9-13"],
                                  "largest bending moment over W L for this loading and "
                                  "support, by statics; not printed in Table 9–1")}))
    for id_, name, row, g12, e, row51, glr, glt in SPECIES:
        clauses.append(_clause(
            f"table-5-3a-{id_}", "Chapter 5, Table 5–3a, 12% moisture content row",
            row, species=name,
            params={"specific_gravity_12": published(g12, "", "Table 5–3a"),
                    "modulus_of_elasticity_table": published(float(e), "MPa", "Table 5–3a"),
                    "modulus_of_rupture_table": published(MOR_KPA[id_] / 1000, "MPa",
                                                          "Table 5–3a",
                                                          f"{MOR_KPA[id_]:,} kPa")}))
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


def _design_stress(mor: float, mor_ref: str, cov: float = 0.16,
                   cov_ref: str = "cov-table-5-6/cov_modulus_of_rupture") -> Quantity:
    """The bending stress a part may be designed to: the near-minimum (5% exclusion) modulus
    of rupture, estimated from the mean with Table 5-6's coefficient of variation, divided by
    the factor the Handbook applies for 10-year duration of load and safety."""
    wh = WOOD_HANDBOOK
    return derived(mor * (1 - NORMAL_5_PERCENT * cov) / 2.1, "MPa",
                   [mor_ref, f"{wh}/{cov_ref}",
                    f"{wh}/near-minimum-7-6/exclusion", f"{wh}/design-factor-7-10/bending_factor"],
                   f"strength (1 − 1.645 × {cov}) / 2.1: the 5% point of a normal distribution "
                   "with Table 5–6's coefficient of variation, over the p. 7–10 factor for "
                   "10-year duration of load and safety")


def design_stress(strength: float, ref: str, *, characteristic: bool) -> Quantity:
    """The bending stress a part may be designed to, from a bending strength a source states,
    read the way the source labels it (ledger:
    a-stated-strength-is-read-the-way-its-source-labels-it). A characteristic strength (a 5th
    percentile, as EN 12369-1 gives it) is already the near-minimum the Handbook's 2.1 is
    applied to; any other value, a mean or one whose source does not say, is read as a mean
    and brought down to its near-minimum first, the safe side."""
    if not characteristic:
        return _design_stress(strength, ref)
    wh = WOOD_HANDBOOK
    return derived(strength / 2.1, "MPa",
                   [ref, f"{wh}/near-minimum-7-6/exclusion", f"{wh}/design-factor-7-10/bending_factor"],
                   "characteristic strength / 2.1: already the 5% exclusion limit, over the p. 7–10 "
                   "factor for 10-year duration of load and safety")


# The Handbook's clauses a material derived with design_stress() rests on, beside its own
DESIGN_STRESS_CLAUSES = [f"{WOOD_HANDBOOK}/cov-table-5-6", f"{WOOD_HANDBOOK}/near-minimum-7-6",
                         f"{WOOD_HANDBOOK}/design-factor-7-10"]


def _panel(id_: str, name: str, *, form: str, sg: float, sg_ref: str, e: float, e_ref: str,
           mor: float, mor_ref: str, bent: str, per: list[str], note: str = "",
           connector_key: str = "plywood", creep: Quantity | None = None) -> Node:
    """A panel product: its bending modulus is the one measured on the panel (shear
    deflection included, so no shear term is added to it), and its values hold only bent the
    way the source says it bent them (`measured_along`; 'unstated' when it does not say).
    `creep`, when given, is its initial_share_of_longtime."""
    wh = WOOD_HANDBOOK
    return Node(
        id=id_, kind="material", name=name,
        payload={"form": form, "measured_along": bent, "modulus": "apparent",
                 "connector_key": connector_key, **(
            {"note": note} if note else {})},
        params={
            "density": derived(1000.0 * sg, "kg/m3", [sg_ref, f"{wh}/density-4-14/water_density"],
                               "specific gravity as tabulated times the density of water; "
                               "the table does not state its moisture basis"),
            "modulus_of_elasticity": derived(e, "MPa", [e_ref],
                                             "bending modulus as tested on the panel"),
            "modulus_of_rupture": derived(mor, "MPa", [mor_ref], "as tabulated"),
            "design_bending_stress": _design_stress(mor, mor_ref),
            **({"initial_share_of_longtime": creep} if creep else {}),
        },
        links={"per": per + ([CREEP_PLYWOOD_CLAUSE] if creep else [])})


# EN 1995-1-1, Table 3.2, as Swedish Wood's Table 9.1 prints it: (key, group, row, as printed,
# kdef for service classes 1, 2, 3 where printed)
KDEF_ROWS = [
    ("structural-timber", "Structural timber", "EN 14081-1", "0,60 0,80 2,00", (0.60, 0.80, 2.00)),
    ("glulam", "Glulam", "EN 14080", "0,60 0,80 2,00", (0.60, 0.80, 2.00)),
    ("plywood", "Plywood EN 636", "Type 1", "0,80 - -", (0.80,)),
    ("plywood-type-2", "Plywood EN 636", "Type 2", "0,80 1,00 -", (0.80, 1.00)),
    ("plywood-type-3", "Plywood EN 636", "Type 3", "0,80 1,00 2,50", (0.80, 1.00, 2.50)),
    ("osb-2", "OSB EN 300", "OSB/2", "2,25 - -", (2.25,)),
    ("osb-3", "OSB EN 300", "OSB/3, OSB/4", "1,50 2,25 -", (1.50, 2.25)),
    ("p4", "Particleboard EN 312", "Type P4", "2,25 - -", (2.25,)),
    ("p5", "Particleboard EN 312", "Type P5", "2,25 3,00 -", (2.25, 3.00)),
    ("p6", "Particleboard EN 312", "Type P6", "1,50 - -", (1.50,)),
    ("p7", "Particleboard EN 312", "Type P7", "1,50 2,25 -", (1.50, 2.25)),
    ("hb-la", "Fibreboard, hard EN 622-2", "HB.LA", "2,25 - -", (2.25,)),
    ("hb-hla", "Fibreboard, hard EN 622-2", "HB.HLA1, HB.HLA2", "2,25 3,00 -", (2.25, 3.00)),
    ("mbh-la", "Fibreboard medium EN 622-3", "MBH.LA1, MBH.LA2", "3,00 - -", (3.00,)),
    ("mbh-hls", "Fibreboard medium EN 622-3", "MBH.HLS1, MBH.HLS2", "3,00 4,00 -", (3.00, 4.00)),
    ("mdf-la", "Fibreboard, MDF EN 622-5", "MDF.LA", "2,25 - -", (2.25,)),
    ("mdf-hls", "Fibreboard, MDF EN 622-5", "MDF.HLS", "2,25 3,00 -", (2.25, 3.00)),
]


# Creep of the Handbook's birch laminate: EN 1995-1-1's kdef for plywood in service class 1,
# as 1/(1 + kdef), the share of the final deflection the initial one is. Eurocode 5 rates EN 636
# plywood; the Handbook does not say its laminate is one, so the value is borrowed and not
# grounded (ledger: the-birch-laminate-borrows-plywoods-kdef).
CREEP_PLYWOOD_CLAUSE = "sources/swedish-wood-design-vol-2-2022/table-9-1-plywood"


def _plywood_creep() -> Quantity:
    kdef = next(values[0] for key, *_, values in KDEF_ROWS if key == "plywood")
    return Quantity(value=1 / (1 + kdef), unit="", provenance="derived", grounded=False,
                    derived_from=[f"{CREEP_PLYWOOD_CLAUSE}/kdef_service_class_1"],
                    note="1/(1 + kdef): EN 1995-1-1's kdef for EN 636 plywood in service class 1, "
                         "borrowed, since the Handbook does not say its laminate is EN 636 plywood")


def _birch_on_edge() -> Node:
    """The same yellow birch plywood standing on its edge (a rail, an apron, a back): bent in
    its own plane, so the moduli and strengths that count are the in-plane ones Table 19-2
    measured edgewise and lengthwise, not the flatwise bending ones. Its modulus is an axial
    one, true rather than apparent, so the shear term is added; the in-plane shear modulus
    of plies of rotary-cut veneer, crossed or not, is the species' GLT (Table 19-3 footnote
    b: annual rings in the plane of the sheet)."""
    wh = WOOD_HANDBOOK
    edge = f"{wh}/table-19-2-crossband-edgewise"
    el = 1.10 * 13_900
    return Node(
        id="plywood-birch-yellow-on-edge",
        name="Yellow birch plywood (Table 19–2's crossband laminate) standing on its edge",
        payload={"form": "plywood", "measured_along": "face grain, on edge", "modulus": "true",
                 "connector_key": "plywood",
                 "same_panel_as": "plywood-birch-yellow",
                 "note": "The flatwise and on-edge values are one panel bent two ways; a part "
                         "uses the one that matches how it is bent."},
        kind="material",
        params={
            "density": derived(720.0, "kg/m3", [f"{wh}/table-19-3-birch-laminate/specific_gravity",
                                                f"{wh}/density-4-14/water_density"],
                               "specific gravity 0.72 times the density of water"),
            "modulus_of_elasticity": derived(8900.0, "MPa", [f"{edge}/tension_modulus",
                                                             f"{edge}/compression_modulus"],
                                             "the lower of the in-plane moduli, tension 8.9 GPa "
                                             "and compression 9.4 GPa"),
            "shear_modulus_inplane": derived(0.068 * el, "MPa",
                                             [f"{wh}/table-5-1-birch-yellow/glt_ratio",
                                              f"{wh}/table-5-3a-birch-yellow/modulus_of_elasticity_table",
                                              f"{wh}/table-5-3a-note-c/shear_correction",
                                              f"{wh}/table-19-3-note-b"],
                                             "GLT of yellow birch: (GLT/EL) EL, Table 5–1 and 5–3a"),
            "design_bending_stress": _design_stress(
                40.0, f"{edge}/compression_strength", 0.18,
                "cov-table-5-6-compression/cov_compression_parallel"),
            "initial_share_of_longtime": _plywood_creep(),
        },
        links={"per": [CREEP_PLYWOOD_CLAUSE, edge, f"{wh}/table-19-2-note-a", f"{wh}/table-19-2-note-b",
                       f"{wh}/table-19-2-note-f", f"{wh}/table-19-3-note-b",
                       f"{wh}/table-19-3-birch-laminate", f"{wh}/table-5-1-birch-yellow",
                       f"{wh}/table-5-3a-birch-yellow", f"{wh}/cov-table-5-6-compression",
                       f"{wh}/near-minimum-7-6", f"{wh}/design-factor-7-10"]})


def panels() -> list[Node]:
    """Plywood and fibre panels the Handbook gives bending values for."""
    wh = WOOD_HANDBOOK
    laminate = f"{wh}/table-19-2-crossband-flexure"
    out = [_panel(
        "plywood-birch-yellow", "Yellow birch plywood, 17 plies of 1.6 mm rotary-cut veneer, "
        "phenol resin film", form="plywood", sg=0.72,
        sg_ref=f"{wh}/table-19-3-birch-laminate/specific_gravity", e=9000.0,
        e_ref=f"{laminate}/modulus_of_elasticity", mor=90.3,
        mor_ref=f"{laminate}/modulus_of_rupture", bent="face grain, flat",
        per=[laminate, f"{wh}/table-19-2-note-a", f"{wh}/table-19-2-note-b",
             f"{wh}/table-19-3-birch-laminate", f"{wh}/cov-table-5-6", f"{wh}/near-minimum-7-6",
             f"{wh}/design-factor-7-10", f"{wh}/panels-uniform-12-2"],
        note="Tested as a 27 mm laminate, load on the face, face grain along the span. A "
             "panel with other ply thicknesses or another glue is near it, not it.",
        creep=_plywood_creep())]
    out.append(_birch_on_edge())
    for id_, name, _row, g, e, mor in PLYWOOD_SHEATHING:
        ref = f"{wh}/table-12-2-{id_}"
        out.append(_panel(
            f"plywood-{id_}", f"{name} plywood sheathing", form="plywood", sg=g,
            sg_ref=f"{ref}/specific_gravity", e=e * 1000, e_ref=f"{ref}/modulus_of_elasticity",
            mor=mor, mor_ref=f"{ref}/modulus_of_rupture", bent="unstated",
            per=[ref, f"{wh}/cov-table-5-6", f"{wh}/near-minimum-7-6", f"{wh}/design-factor-7-10",
                 f"{wh}/panels-uniform-12-2"]))
    for id_, name, _row, g0, _g1, e0, _e1, m0, _m1 in FIBRE_PANELS:
        ref = f"{wh}/table-12-1-{id_}"
        out.append(_panel(
            id_, f"{name}, the low end of the Handbook's range", form=name.lower(), sg=g0,
            sg_ref=f"{ref}/specific_gravity_low", e=e0 * 1000,
            e_ref=f"{ref}/modulus_of_elasticity_low", mor=m0, mor_ref=f"{ref}/modulus_of_rupture_low",
            bent="unstated", connector_key={"medium-density-fiberboard": "mdf"}.get(id_, id_),
            per=[ref, f"{wh}/cov-table-5-6", f"{wh}/near-minimum-7-6", f"{wh}/design-factor-7-10",
                 f"{wh}/panels-uniform-12-2"]))
    return out


def materials() -> Node:
    """Air-dried solid wood at 12% moisture content, one material per species, and the
    panels (plywood, fibreboard, particleboard) the Handbook gives bending values for."""
    wh = WOOD_HANDBOOK
    out = []
    for id_, name, _row, g12, e, _row51, glr, glt in SPECIES:
        row, row51 = f"{wh}/table-5-3a-{id_}", f"{wh}/table-5-1-{id_}"
        el = 1.10 * e
        mor = MOR_KPA[id_] / 1000
        out.append(Node(
            id=id_, kind="material", name=f"{name}, air-dried, 12% moisture content",
            payload={"form": "solid wood", "moisture_content_percent": 12, "dried": True,
                     "measured_along": "grain", "modulus": "true", "connector_key": id_},
            params={
                "modulus_of_rupture": derived(mor, "MPa", [f"{row}/modulus_of_rupture_table"],
                                              "Table 5–3a, mean of clear wood"),
                "design_bending_stress": _design_stress(mor, f"{row}/modulus_of_rupture_table"),
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
                "dimensional_change_radial": derived(MOVEMENT[id_][1], "1/%",
                                                     [f"{wh}/table-13-5-{id_}/cr"],
                                                     "CR, Table 13–5"),
                "dimensional_change_tangential": derived(MOVEMENT[id_][2], "1/%",
                                                         [f"{wh}/table-13-5-{id_}/ct"],
                                                         "CT, Table 13–5"),
            },
            links={"per": [row, row51, f"{wh}/table-13-5-{id_}", f"{wh}/cov-table-5-6",
                           f"{wh}/near-minimum-7-6", f"{wh}/design-factor-7-10"]}))
    return Node(id="materials", kind="", children=out + panels() + european_species() + [thermo_beech()])


# --- CIRAD's Tropix: the clear-wood properties of the species sold in Europe ---------------

# Tropix 7 (CIRAD - ITTO) species sheets, as fetched on 2026-11-12. Copyrighted: cited by
# locator and values, never quoted (ledger: a-copyrighted-source-is-cited-by-locator-and-values);
# the copies are kept private and tests/test_captures.py checks every value against them.
# Each sheet's table "Propriétés physiques et mécaniques" has one column, "Valeur moyenne",
# and its footnote ¹ puts the density, the bending strength and the modulus at 12% moisture.
# (material id, name, sheet, botanical name, url path, sha256, last updated,
#  relative density, bending strength MPa, longitudinal modulus MPa, connector_key)
TROPIX_URL = "https://tropix.cirad.fr/FichiersComplementaires/FR/"
TROPIX_SHEETS = [
    ("oak-european", "Oak, European", "Chêne", "Quercus petraea, Quercus robur",
     "Temperees/CHENE%202026_FR.PDF",
     "32250d7cda920cdace293f818838691b6e04b5245fcc4cc34133daf55e957597", "2025-08-30",
     0.74, 105, 13_300, "oak-european"),
    ("beech-european", "Beech, European", "Hêtre", "Fagus sylvatica",
     "Temperees/HETRE%202026_FR.PDF",
     "645c52d52366b949e74dcbeb65d5926be69faa007e9007ebb39c2042872a6cfd", "2024-10-30",
     0.71, 111, 15_300, "beech"),
    ("fir-silver", "Fir, silver", "Sapin", "Abies alba",
     "Temperees/SAPIN%202026_FR.PDF",
     "ddaad250a55f37df05462f096b8fe14f88cd04a7db79b5705c23d85c53f3ca02", "2025-08-30",
     0.49, 80, 14_300, "fir-silver"),
    ("spruce-norway", "Spruce, Norway", "Épicéa", "Picea abies",
     "Temperees/EPICEA%202026_FR.PDF",
     "84e78a6938295c755b8b4a901545f836f13f99758ddc8e59a7155515e3e824bc", "2026-02-25",
     0.45, 78, 11_900, "spruce-norway"),
    ("pine-scots", "Pine, Scots", "Pin sylvestre", "Pinus sylvestris",
     "Temperees/PIN_SYLVESTRE%202026_FR.PDF",
     "3f0738b1aa5d28ed446132ca0207270caff5d2b5da15c2973ab846688b06c5f2", "2025-08-30",
     0.55, 97, 12_900, "pine-scots"),
    ("pine-maritime", "Pine, maritime", "Pin maritime", "Pinus pinaster",
     "Temperees/PIN_MARITIME%202026_FR.PDF",
     "a2649314280b89606f6471c7f62dcd24daeb82e65d4ee5c003ae6ef1c7e0748a", "2025-01-10",
     0.55, 80, 8_800, "pine-maritime"),
    ("ash-european", "Ash, European", "Frêne", "Fraxinus excelsior",
     "Temperees/FRENE%202026_FR.PDF",
     "6d4043876160dd4213308f1916a01725d0c9cbdfd59bcea0a4c07b2953bd338e", "2026-03-30",
     0.68, 113, 12_900, "ash-european"),
    ("robinia", "Robinia (black locust, often sold as acacia)", "Robinier", "Robinia pseudoacacia",
     "Temperees/ROBINIER%202026_FR.PDF",
     "84f64971642be6475c8ebb0775188b63976d7bf517a3f15dd8411576964cbc06", "2025-08-01",
     0.74, 126, 16_900, "robinia"),
    ("acacia-mangium", "Acacia mangium", "Acacia mangium", "Acacia mangium",
     "Asie/ACACIA_MANGIUM%202026_FR.PDF",
     "c32ec916b70fcc2bf651d258b077deae244433719c77fb3a2ad4995a50990208", "2024-10-14",
     0.52, 105, 10_800, "acacia-mangium"),
    ("teak", "Teak", "Teck", "Tectona grandis",
     "Asie/TECK%202026_FR.PDF",
     "15f53148476053b99efe8031435efeb8a0214f57db2632f8ab2d6d5cad384bfa", "2024-05-21",
     0.67, 98, 13_740, "teak"),
    ("okoume", "Okoumé", "Okoumé", "Aucoumea klaineana",
     "Afrique/OKOUME%202026_FR.PDF",
     "79fd53079a56b4f4ade1add5778de081f2f9a0657c185fa414f7f1b8b8ab66f4", "2024-05-22",
     0.44, 62, 9_690, "okoume"),
    ("poplar", "Poplar (cultivars)", "Peuplier", "Populus p.p.",
     "Temperees/PEUPLIER%202026_FR.PDF",
     "6e124c500af6e22c45721a55e1ad0c84f0d1bc5533c3df7bf281f8930ce8123b", "2024-09-11",
     0.45, 62, 9_800, "poplar"),
    ("eucalyptus-grandis", "Eucalyptus grandis (sold as red grandis)", "Red grandis",
     "Eucalyptus grandis", "Amerique/RED_GRANDIS%202026_FR.PDF",
     "cd570770bdf06638d0fd8cf3763a1447cddc3d8dd7bd3522692387e8b2e6ee5b", "2024-10-30",
     0.60, 103, 15_200, "eucalyptus-grandis"),
]
# The day each sheet was fetched, when it is not the day the first twelve were
TROPIX_FETCHED = {"eucalyptus-grandis": "2026-11-13"}
# The rows each Tropix clause reads, as the sheet heads them, and the param each gives
TROPIX_ROWS = [("relative_density", "Densité¹"),
               ("modulus_of_rupture", "Contrainte de rupture en flexion statique¹"),
               ("modulus_of_elasticity", "Module d'élasticité longitudinal¹")]

# LWF Wissen 42 (Bayerische Landesanstalt für Wald und Forstwirtschaft, D. Grosser), p. 52:
# Tab. 1 (density), Tab. 2 (strength, modulus) and Tab. 3 (shrinkage per 1% of moisture
# between 5% and 20%), German names of the species. Copyrighted, cited by locator and values.
LWF = f"{SOURCES}/lwf-wissen-42"
# (material id, German row name, differential shrinkage radial and tangential, % per %, and
#  for each the row heading it is printed after and the cell as printed). Alder's are ranges:
#  the high end is taken, the more a board moves the larger the clearance it needs.
LWF_SHRINKAGE = {
    "oak-european": ("Stieleiche", 0.16, 0.36, ("radial", "0,16"), ("tangential", "0,36")),
    "beech-european": ("Buche", 0.20, 0.41, ("radial", "0,20"), ("tangential", "0,41")),
    "spruce-norway": ("Fichte", 0.19, 0.39, ("Nadelhölzer Fichte", "0,19 0,39"), ("Nadelhölzer Fichte", "0,19 0,39")),
    "pine-scots": ("Kiefer", 0.19, 0.36, ("Kiefer 0,4", "0,19 0,36"), ("Kiefer 0,4", "0,19 0,36")),
    "alder-black": ("Schwarzerle", 0.17, 0.30, ("radial", "0,15-0,17"), ("tangential", "0,24-0,30")),
}
# Black alder has no Tropix sheet; LWF gives ranges, and the low end of each is taken
ALDER = {"density": 0.55, "modulus_of_rupture": 85, "modulus_of_elasticity": 7_700}


def tropix() -> list[Node]:
    out = []
    for id_, _name, sheet, botanical, path, sha, updated, d, mor, moe, _key in TROPIX_SHEETS:
        values = {"relative_density": (d, "", f"{d:.2f}".replace(".", ",")),
                  "modulus_of_rupture": (mor, "MPa", f"{mor} MPa"),
                  "modulus_of_elasticity": (moe, "MPa", f"{moe:,} MPa".replace(",", " "))}
        out.append(Node(
            id=f"tropix-{id_}", kind="source", name=f"CIRAD - ITTO, Tropix 7: {sheet} ({botanical})",
            payload={"publisher": "CIRAD - ITTO", "year": int(updated[:4]), "url": TROPIX_URL + path,
                     "updated": updated, "fetched": TROPIX_FETCHED.get(id_, "2026-11-12"), "sha256": sha,
                     "licence": "copyrighted", "capture": "private copy, identified by its sha256"},
            children=[Node(
                id="properties", kind="clause",
                payload={"locator": "Propriétés physiques et mécaniques, column 'Valeur moyenne', "
                                    "rows " + ", ".join(f"'{label}'" for _, label in TROPIX_ROWS),
                         "rows": [[param, label, values[param][2]] for param, label in TROPIX_ROWS],
                         "in_our_words": "means of clear wood at 12% moisture content (footnote ¹)"},
                params={param: published(v, unit, label, printed)
                        for (param, label), (v, unit, printed) in
                        zip(TROPIX_ROWS, (values[p] for p, _ in TROPIX_ROWS))})]))
    rows = [["relative_density", "Leichtere Laubhölzer Schwarzerle", "0,55"],
            ["modulus_of_elasticity", "Nadelhölzer Fichte Kiefer", "7.700-11.760"],
            ["modulus_of_rupture", "Nadelhölzer Fichte Kiefer", "85-97"]]
    out.append(Node(
        id="lwf-wissen-42", kind="source",
        name="LWF Wissen 42, Das Holz der Schwarzerle (Bayerische Landesanstalt für Wald und "
             "Forstwirtschaft)",
        payload={"publisher": "Bayerische Landesanstalt für Wald und Forstwirtschaft", "year": 2003,
                 "url": "https://lwg.bayern.de/mam/cms04/forsttechnik-holz/dateien/"
                        "w42_das_holz_der_schwarzerle-eigenschaften_verwendung.pdf",
                 "fetched": "2026-11-12",
                 "sha256": "145d3d6734be001e108c2cad5df507b805a2bda80c47895f8da4a7c7b97d81fc",
                 "licence": "copyrighted", "capture": "private copy, identified by its sha256"},
        children=[
            Node(id="tab-1-2-schwarzerle", kind="clause",
                 payload={"locator": "p. 52, Tab. 1 (Rohdichte r_N, mean) and Tab. 2 (E-Modul aus "
                                     "Biegeversuch, Biegefestigkeit), row Schwarzerle",
                          "rows": rows,
                          "in_our_words": "black alder: density 0.55 g/cm3 at 12-15% moisture; "
                                          "bending modulus and strength as ranges, of which the "
                                          "low ends are taken"},
                 params={"relative_density": published(0.55, "", "Tab. 1", "0,55 g/cm3"),
                         "modulus_of_elasticity": published(7700.0, "MPa", "Tab. 2", "7.700-11.760 N/mm2"),
                         "modulus_of_rupture": published(85.0, "MPa", "Tab. 2", "85-97 N/mm2")}),
            *[Node(id=f"tab-3-{german.lower()}", kind="clause",
                   payload={"locator": f"p. 52, Tab. 3 (differentielles Schwindmaß, % per 1% "
                                       f"Holzfeuchte, u = 5% to 20%), row {german}",
                            "rows": [["dimensional_change_radial", *rr], ["dimensional_change_tangential", *tt]]},
                   params={"dimensional_change_radial": published(r / 100, "1/%", "Tab. 3", f"{r} % per %"),
                           "dimensional_change_tangential": published(t / 100, "1/%", "Tab. 3",
                                                                      f"{t} % per %")})
              for _id, (german, r, t, rr, tt) in LWF_SHRINKAGE.items()],
        ]))
    return out


def solid_wood(id_: str, name: str, *, clause: str, connector_key: str,
               shrinkage: str | None = None, per: list[str] | None = None) -> Node:
    """A species' clear wood at 12% moisture content, from a clause stating its relative
    density, bending strength and longitudinal modulus as means. The modulus is read as a
    true one and brought to an apparent one by Table 5-3a footnote c's 10%, since the source
    names no test method: if it was measured on a center-loaded beam it is already apparent
    and this understates it, the safe side (ledger: a-species-mean-modulus-is-taken-as-apparent)."""
    wh = WOOD_HANDBOOK
    params = {
        "density": derived(0.0, "kg/m3", [f"{clause}/relative_density",
                                          f"{wh}/density-4-14/water_density"],
                           "relative density at 12% times the density of water"),
        "modulus_of_rupture": derived(0.0, "MPa", [f"{clause}/modulus_of_rupture"], "mean, 12%"),
        "modulus_of_elasticity": derived(0.0, "MPa", [f"{clause}/modulus_of_elasticity",
                                                      f"{wh}/table-5-3a-note-c/shear_correction"],
                                         "longitudinal modulus / 1.1: an apparent modulus, the "
                                         "shear deflection of footnote c's beam in it"),
        "initial_share_of_longtime": derived(2 / 3, "", [f"{wh}/creep-chapter-9/initial_share_dry"],
                                             "initially dry timber: design for an initial "
                                             "deflection of about two-thirds the permitted "
                                             "longtime deflection"),
    }
    links = [clause, f"{wh}/table-5-3a-note-c", f"{wh}/density-4-14",
             f"{wh}/creep-chapter-9", *DESIGN_STRESS_CLAUSES]
    if shrinkage:
        params["dimensional_change_radial"] = derived(0.0, "1/%", [f"{shrinkage}/dimensional_change_radial"],
                                                      "LWF Tab. 3, radial")
        params["dimensional_change_tangential"] = derived(
            0.0, "1/%", [f"{shrinkage}/dimensional_change_tangential"], "LWF Tab. 3, tangential")
        links.append(shrinkage)
    return Node(id=id_, kind="material", name=name,
                payload={"form": "solid wood", "moisture_content_percent": 12, "dried": True,
                         "measured_along": "grain", "modulus": "apparent",
                         "connector_key": connector_key},
                params=params, links={"per": links + (per or [])})


def _filled(node: Node, values: dict[str, float]) -> Node:
    """Set each derived param from the clause values it names: density from the relative
    density, the modulus over 1.1, the design stress from the mean strength."""
    p = node.params
    p["density"] = p["density"].model_copy(update={"value": 1000.0 * values["relative_density"]})
    p["modulus_of_rupture"] = p["modulus_of_rupture"].model_copy(update={"value": float(values["modulus_of_rupture"])})
    p["modulus_of_elasticity"] = p["modulus_of_elasticity"].model_copy(
        update={"value": values["modulus_of_elasticity"] / 1.10})
    p["design_bending_stress"] = _design_stress(float(values["modulus_of_rupture"]),
                                                p["modulus_of_rupture"].derived_from[0])
    for k in ("dimensional_change_radial", "dimensional_change_tangential"):
        if k in p:
            p[k] = p[k].model_copy(update={"value": values[k]})
    return node


def european_species() -> list[Node]:
    """The species of the solid-wood boards and plywood faces sold in Europe, from Tropix,
    and black alder from LWF Wissen 42, at 12% moisture content."""
    out = []
    for id_, name, sheet, botanical, *_r, d, mor, moe, key in TROPIX_SHEETS:
        shrink = LWF_SHRINKAGE.get(id_)
        values = {"relative_density": d, "modulus_of_rupture": mor, "modulus_of_elasticity": moe}
        if shrink:
            values.update(dimensional_change_radial=shrink[1] / 100,
                          dimensional_change_tangential=shrink[2] / 100)
        out.append(_filled(solid_wood(
            id_, f"{name} ({botanical}), air-dried, 12% moisture content",
            clause=f"{SOURCES}/tropix-{id_}/properties", connector_key=key,
            shrinkage=f"{LWF}/tab-3-{shrink[0].lower()}" if shrink else None), values))
    _g, r, t, *_rows = LWF_SHRINKAGE["alder-black"]
    out.append(_filled(solid_wood(
        "alder-black", "Alder, black (Alnus glutinosa), air-dried, 12-15% moisture content, the "
        "low end of LWF's ranges", clause=f"{LWF}/tab-1-2-schwarzerle", connector_key="alder-black",
        shrinkage=f"{LWF}/tab-3-schwarzerle"),
        {"relative_density": ALDER["density"], "modulus_of_rupture": ALDER["modulus_of_rupture"],
         "modulus_of_elasticity": ALDER["modulus_of_elasticity"],
         "dimensional_change_radial": r / 100, "dimensional_change_tangential": t / 100}))
    return out


# --- values read off a copy, each beside the words it follows ----------------------------

def _si(number: float, how: dict) -> float:
    """A number as printed, in the SI unit a param holds: times a factor (0.01 for a percent,
    24 for days in hours), or a factor over it (span/180 is a share of 1/180 of the span)."""
    return how["over"] / number if "over" in how else number * how.get("times", 1.0)


def _stated(id_: str, locator: str, rows: list[tuple], *, quote: str | None = None,
            **payload) -> Node:
    """A clause whose every value is checked against the copy kept of its source. Each row is
    (param, unit, label, printed, number, how): the value is `number`, as `printed` after
    `label` in the copy, brought to SI by `how` (see _si); tests/test_captures.py finds each
    printed value after its label in the copy whose sha256 the source records. A clause of a
    public-domain or CC BY source also quotes it, checked against the capture under sources/."""
    params = {p: published(_si(n, how), unit, locator, printed) for p, unit, _l, printed, n, how in rows}
    body = {"locator": locator, **({"quote": quote} if quote else {}), **payload,
            "rows": [[p, label, printed, n, how] for p, _u, label, printed, n, how in rows]}
    return Node(id=id_, kind="clause", payload=body, params=params)


def _publication(id_: str, name: str, *, publisher: str, year: int | None, url: str, sha256: str,
                 licence: str, children: list[Node], fetched: str = "2026-11-13",
                 capture: str | None = None, **payload) -> Node:
    return Node(id=id_, kind="source", name=name,
                payload={"publisher": publisher, **({"year": year} if year else {}), "url": url,
                         "fetched": fetched, "sha256": sha256, "licence": licence,
                         "capture": capture or "private copy, identified by its sha256", **payload},
                children=children)


PERCENT = {"times": 0.01}
OVER = {"over": 1.0}
SAME = {"times": 1.0}
KG_PER_DM2 = {"times": 100.0}  # kg/dm2 as kg/m2
LB_PER_FT2 = {"times": POUND_PER_SQUARE_FOOT_KG_M2}
POUNDS = {"times": POUND_KG}
GPA = {"times": 1000.0}


# --- thermally modified beech: two studies under CC BY 4.0 --------------------------------

SCHMIDTOVA = f"{SOURCES}/schmidtova-2026"
BORUVKA = f"{SOURCES}/boruvka-2018"
CC_BY_NOTE = ("© the authors, licensee MDPI; open access under CC BY 4.0, so its words are quoted here "
              "and its quoted pages kept under sources/, and they keep that licence")


def schmidtova() -> Node:
    """Beech boards of structural size, thermally modified by a company at 190 °C: what a
    thermally modified beech board may be designed to, its characteristic strength among it."""
    return _publication(
        "schmidtova-2026",
        "Schmidtová, Andor, Valko, Herdová, Laganà: Stiffness-Based Grading of Thermally Modified "
        "Beech Timber for Structural Applications, Forests 17(2), 174 (2026)",
        publisher="MDPI", year=2026, identifier="doi:10.3390/f17020174",
        url="https://mdpi-res.com/d_attachment/forests/forests-17-00174/article_deploy/forests-17-00174.pdf",
        sha256="cd66762b57e5326219c7327872d49ee97012235cf07ee5bcf5006ffe6a6aacf4",
        licence="cc-by-4.0", licence_note=CC_BY_NOTE, capture="sources/schmidtova-2026/pages.txt",
        children=[
            _stated("method", "Abstract, p. 1", [],
                    quote="All specimens were visually graded according to DIN 4074-5 and assessed "
                          "using acoustic non-destructive methods before testing in four-point bending "
                          "following EN 408. Modulus of elasticity (MOE), modulus of rupture (MOR), and "
                          "density were determined, and characteristic values were calculated according "
                          "to EN 384."),
            _stated("treatment", "2. Materials and Methods, p. 3",
                    [("treatment_temperature", "degC", "industrially treated by", "190 ◦C", 190, SAME),
                     ("treatment_duration", "h", "industrially treated by", "3.5 h", 3.5, SAME)],
                    quote="The boards were industrially treated by the company Designwood at 190 ◦C for "
                          "3.5 h in an oxidative air atmosphere."),
            _stated("boards", "2. Materials and Methods, p. 3",
                    [("board_width", "mm", "final dimensions of", "50 × 150 × 3100 mm", 50, SAME),
                     ("board_depth", "mm", "final dimensions of", "50 × 150 × 3100 mm", 150, SAME),
                     ("board_length", "mm", "final dimensions of", "50 × 150 × 3100 mm", 3100, SAME)],
                    quote="For testing, the boards were re-sized and squared to the final dimensions of "
                          "50 × 150 × 3100 mm (b × h × l)."),
            _stated("table-2-bending-strength", "Table 2, row fm,h150, p. 6",
                    [("modulus_of_rupture", "MPa", "fm,h150 (MPa)", "63.33", 63.33, SAME),
                     ("cov_modulus_of_rupture", "", "fm,h150 (MPa)", "45%", 45, PERCENT),
                     ("modulus_of_rupture_untreated", "MPa", "fm,h150 (MPa)", "76.31", 76.31, SAME),
                     ("cov_modulus_of_rupture_untreated", "", "fm,h150 (MPa)", "14%", 14, PERCENT)],
                    quote="fm,h150 (MPa) 63.33 45% 76.31 14% −17%",
                    transcribed="bending strength brought to a depth of 150 mm, N = 53: thermally "
                                "modified mean 63.33 MPa (coefficient of variation 45%), untreated mean "
                                "76.31 MPa (14%)"),
            _stated("table-2-global-modulus", "Table 2, row MOEg,ref w, p. 6",
                    [("global_modulus", "MPa", "MOEg,ref w (GPa)", "14.92", 14.92, GPA),
                     ("global_modulus_untreated", "MPa", "MOEg,ref w (GPa)", "14.61", 14.61, GPA)],
                    quote="MOEg,ref w (GPa) 14.92 10% 14.61 8% 2%",
                    transcribed="global modulus of elasticity in four-point bending (EN 408), at the "
                                "reference moisture content: thermally modified mean 14.92 GPa, untreated "
                                "14.61 GPa"),
            _stated("table-2-density", "Table 2, row ρ408,ref w, p. 6",
                    [("density", "kg/m3", "ρ408,ref w (kg m−3)", "663.1", 663.1, SAME),
                     ("density_untreated", "kg/m3", "ρ408,ref w (kg m−3)", "694.5", 694.5, SAME)],
                    quote="ρ408,ref w (kg m−3) 663.1 5% 694.5 5% −5%",
                    transcribed="density (EN 408) at the reference moisture content: thermally modified "
                                "mean 663.1 kg/m³, untreated 694.5 kg/m³"),
            _stated("table-2-moisture", "Table 2, row MC, p. 6",
                    [("moisture_content", "%", "MC (%)", "6.09", 6.09, SAME),
                     ("moisture_content_untreated", "%", "MC (%)", "14.93", 14.93, SAME)],
                    quote="MC (%) 6.09 11% 14.93 7% −59%",
                    transcribed="moisture content at the test: thermally modified mean 6.09%, untreated "
                                "14.93%"),
            _stated("characteristic-strength", "3.2, p. 7",
                    [("bending_strength_characteristic", "MPa", "characteristic strength value",
                      "17.27 MPa", 17.27, SAME)],
                    quote="The characteristic strength value of the structural wood made of TMW was "
                          "17.27 MPa (Table 3)."),
            _stated("table-3", "Table 3, p. 7",
                    [("bending_strength_5th_percentile", "MPa", "Characteristic values of TMW timber",
                      "24.68", 24.68, SAME),
                     ("bending_strength_characteristic", "MPa", "Characteristic values of TMW timber",
                      "17.27", 17.27, SAME),
                     ("modulus_of_elasticity_mean", "MPa", "Characteristic values of TMW timber",
                      "13.62", 13.62, GPA),
                     ("modulus_of_elasticity_characteristic", "MPa",
                      "Characteristic values of TMW timber", "11.44", 11.44, GPA),
                     ("density_characteristic", "kg/m3", "Characteristic values of TMW timber",
                      "526.9", 526.9, SAME),
                     ("density_mean", "kg/m3", "Characteristic values of TMW timber", "632.3", 632.3,
                      SAME),
                     ("density_5th_percentile", "kg/m3", "Characteristic values of TMW timber",
                      "598.8", 598.8, SAME)],
                    quote="24.68 17.27 13.62 11.44 526.9 632.3 598.8",
                    transcribed="Characteristic values of TMW timber, columns fm,05 (EN 14358), fm,k "
                                "(EN 384), Em,0,mean (EN 384), Em,0,k (EN 384), ρk, ρmean, ρ05. The table "
                                "prints no units: the strengths are MPa (3.2 gives fm,k as 17.27 MPa), "
                                "the moduli GPa as in Table 2, the densities kg/m³"),
        ])


def boruvka() -> Node:
    """Small clear beech specimens treated at a mild and a severe temperature: how much the
    treatment temperature changes the strength."""
    return _publication(
        "boruvka-2018",
        "Borůvka, Zeidler, Holeček, Dudík: Elastic and Strength Properties of Heat-Treated Beech and "
        "Birch Wood, Forests 9(4), 197 (2018)",
        publisher="MDPI", year=2018, identifier="doi:10.3390/f9040197",
        url="https://mdpi-res.com/d_attachment/forests/forests-09-00197/article_deploy/forests-09-00197.pdf",
        sha256="68d115c85d65d79b9c4d1938c81ed38e25063597a4bde17b5f975e8e810ced31",
        licence="cc-by-4.0", licence_note=CC_BY_NOTE, capture="sources/boruvka-2018/pages.txt",
        children=[
            _stated("specimens", "2.1 Material, p. 3",
                    [("specimen_depth", "mm", "Six test pieces with dimensions of", "20 mm × 20 mm × 300 mm",
                      20, SAME),
                     ("specimen_length", "mm", "Six test pieces with dimensions of",
                      "20 mm × 20 mm × 300 mm", 300, SAME)],
                    quote="Six test pieces with dimensions of 20 mm × 20 mm × 300 mm were prepared from "
                          "each prism"),
            _stated("treatment", "2.1 Material, p. 3",
                    [("treatment_temperature_mild", "degC", "the ﬁrst degree of thermal treatment",
                      "165 ◦C", 165, SAME),
                     ("treatment_temperature_severe", "degC", "the ﬁrst degree of thermal treatment",
                      "210 ◦C", 210, SAME)],
                    quote="One third of the testing samples were subsequently exposed to the ﬁrst degree "
                          "of thermal treatment (an air atmosphere at 165 ◦C), and the second third of the "
                          "testing samples were heat-treated at 210 ◦C, following the Finnish technology "
                          "for the wood heat treatment (Pat. EP-0759137 [25])."),
            _stated("bending-span", "2.2 Methods, p. 5",
                    [("span", "mm", "with support distances of", "240 mm", 240, SAME)],
                    quote="with support distances of 240 mm, i.e., 12-fold greater than the sample height."),
            _stated("table-3-density", "Table 3, Density, p. 8",
                    [("density_untreated", "kg/m3", "Density REF", "622 676 729", 676, SAME),
                     ("density_165", "kg/m3", "Density REF", "615 676 742", 676, SAME),
                     ("density_210", "kg/m3", "Density REF", "579 643 802", 643, SAME)],
                    quote="Density REF 622 676 729 27 4.0 (kg/m3) 165 615 676 742 33 4.8 210 579 643 802 "
                          "53 8.3",
                    transcribed="beech, density, minimum, mean, maximum: untreated mean 676 kg/m³, "
                                "165 °C 676, 210 °C 643"),
            _stated("table-3-static-modulus", "Table 3, Static modulus of elasticity, p. 8",
                    [("modulus_of_elasticity_untreated", "MPa", "Static REF", "8735 10,056 11,142", 10_056,
                      SAME),
                     ("modulus_of_elasticity_165", "MPa", "Static REF", "8909 10,715 12,703", 10_715, SAME),
                     ("modulus_of_elasticity_210", "MPa", "Static REF", "7007 8830 11,072", 8830, SAME)],
                    quote="Static REF 8735 10,056 11,142 740 7.4 modulus of elasticity 165 8909 10,715 "
                          "12,703 1070 10.0 (MPa) 210 7007 8830 11,072 1053 11.9",
                    transcribed="beech, static modulus of elasticity in three-point bending, mean: "
                                "untreated 10,056 MPa, 165 °C 10,715 MPa, 210 °C 8830 MPa"),
            _stated("table-3-modulus-of-rupture", "Table 3, Modulus of rupture, p. 8",
                    [("modulus_of_rupture_untreated", "MPa", "Modulus of rupture- REF", "86.7 102.7 117.3",
                      102.7, SAME),
                     ("modulus_of_rupture_165", "MPa", "Modulus of rupture- REF", "75.4 108.8 130.2",
                      108.8, SAME),
                     ("modulus_of_rupture_210", "MPa", "Modulus of rupture- REF", "27.9 42.0 62.5",
                      42.0, SAME),
                     ("modulus_of_rupture_210_minimum", "MPa", "Modulus of rupture- REF",
                      "27.9 42.0 62.5", 27.9, SAME)],
                    quote="Modulus of rupture- REF 86.7 102.7 117.3 8.1 7.9 bending strength 165 75.4 "
                          "108.8 130.2 14.6 13.5 (MPa) 210 27.9 42.0 62.5 9.0 21.5",
                    transcribed="beech, bending strength, mean: untreated 102.7 MPa, 165 °C 108.8 MPa, "
                                "210 °C 42.0 MPa (minimum 27.9)"),
            _stated("table-3-moisture", "Table 3, Moisture content, p. 8",
                    [("moisture_content_untreated", "%", "Moisture content REF", "11.6 12.0 12.4", 12.0,
                      SAME),
                     ("moisture_content_165", "%", "Moisture content REF", "8.3 9.2 11.0", 9.2, SAME),
                     ("moisture_content_210", "%", "Moisture content REF", "4.5 5.9 7.4", 5.9, SAME)],
                    quote="Moisture content REF 11.6 12.0 12.4 0.2 1.5 (%) 165 8.3 9.2 11.0 0.5 5.9 210 "
                          "4.5 5.9 7.4 0.8 13.0",
                    transcribed="beech, moisture content at the test, mean: untreated 12.0%, 165 °C 9.2%, "
                                "210 °C 5.9%"),
        ])


def thermo_beech() -> Node:
    """Beech thermally modified at 190 °C, from Schmidtová et al.'s structural boards: the
    design stress from their characteristic bending strength, which already is a 5th
    percentile (ledger: a-thermally-modified-wood-is-read-from-a-study-of-its-treatment)."""
    s, wh = SCHMIDTOVA, WOOD_HANDBOOK
    return Node(
        id="beech-thermally-modified",
        name="Beech (Fagus sylvatica), thermally modified at 190 °C for 3.5 h, structural boards",
        kind="material",
        payload={"form": "solid wood", "dried": True, "moisture_content_percent": 6.09,
                 "measured_along": "grain", "modulus": "apparent",
                 "connector_key": "beech-thermally-modified",
                 "treatment": "190 °C for 3.5 h in air, by a company (Designwood), on boards 50 × 150 × "
                              "3100 mm visually graded LS7 or better (DIN 4074-5): these values are those "
                              "boards'. The temperature and time a board on sale was treated at are its "
                              "maker's and are unknown here. Borůvka et al. (2018) measured clear beech at "
                              "102.7 MPa mean bending strength untreated, 108.8 after 165 °C and 42.0 after "
                              "210 °C: a board treated hotter than 190 °C may be much weaker than this.",
                 "note": "Graded boards with knots, not clear wood: a shelf of selected lamellas may be "
                         "stronger. Treated boards scatter far more than untreated ones (coefficient of "
                         "variation 45% against 14%), which the characteristic strength takes in."},
        params={
            "density": derived(663.1, "kg/m3", [f"{s}/table-2-density/density"],
                               "mean of the treated boards (Table 2), at their moisture content when "
                               "tested, 6.09% on average"),
            "modulus_of_rupture": derived(63.33, "MPa", [f"{s}/table-2-bending-strength/modulus_of_rupture"],
                                          "mean of the treated boards, brought to a depth of 150 mm "
                                          "(Table 2)"),
            "design_bending_stress": design_stress(
                17.27, f"{s}/table-3/bending_strength_characteristic", characteristic=True),
            "modulus_of_elasticity": derived(
                13_620.0, "MPa", [f"{s}/table-3/modulus_of_elasticity_mean",
                                  f"{s}/table-2-global-modulus/global_modulus"],
                "Em,0,mean (EN 384) of the treated boards, 13.62 GPa (Table 3): lower than their global "
                "modulus in four-point bending, 14.92 GPa (Table 2), which has the shear deflection in "
                "it, so it is used as an apparent modulus"),
            "initial_share_of_longtime": derived(2 / 3, "", [f"{wh}/creep-chapter-9/initial_share_dry"],
                                                 "initially dry timber: design for an initial deflection "
                                                 "of about two-thirds the permitted longtime deflection"),
        },
        links={"per": [f"{s}/method", f"{s}/treatment", f"{s}/boards", f"{s}/table-2-bending-strength",
                       f"{s}/table-2-global-modulus", f"{s}/table-2-density", f"{s}/table-2-moisture",
                       f"{s}/characteristic-strength", f"{s}/table-3",
                       f"{BORUVKA}/treatment", f"{BORUVKA}/table-3-modulus-of-rupture",
                       f"{wh}/creep-chapter-9", *DESIGN_STRESS_CLAUSES]})


# --- how far a shelf or a beam may sag: every published limit found ----------------------
#
# Knowledge only: no rule reads these. A piece that wants a limit authors its own requirement
# (measure longtime_sag, param limit in mm) per the clause it chooses, since none of them is
# written for the seats and shelves of a home (ledger:
# a-published-sag-limit-is-a-source-a-piece-chooses-from). Each clause states what the limit
# applies to, under which load, and when the deflection is measured: as soon as the load is
# on (initial), after a stated time under it, or at the end of the structure's life (final).

def sag_limits() -> list[Node]:
    copyrighted = {"licence": "copyrighted"}
    return [
        _publication(
            "dti-report-804821-1",
            "Danish Technological Institute, Test Report No. 804821-1 rev. 1: Lammhults "
            "Biblioteksdesign 60/30 Classic Steel Shelving, tested to EN 16121 and EN 16122",
            publisher="Danish Technological Institute, published by SBNL", year=2018,
            identifier="804821-1 rev. 1",
            url="https://sbnl.be/media/24800/804821-1-rev-1-60_30-classic-steel-shelving-en-16121-uk.pdf",
            sha256="464da6228814d51935805ffe496e373d5b9403bf84933a59b6fdd51f1f0dca4d", **copyrighted,
            children=[_stated(
                "en-16121-6-2-e",
                "test 6.1.15 Deflection of shelves (EN 16122 6.1.4, mass per unit area) and requirement "
                "6.2 e), as the report reproduces EN 16121",
                [("share_of_span", "", "There shall be no deflection of", "0.5%", 0.5, PERCENT),
                 ("surface_load_level_1", "kg/m2", "Deflection of shelves", "1.5", 1.5, KG_PER_DM2),
                 ("surface_load_level_2", "kg/m2", "Deflection of shelves", "2.0", 2.0, KG_PER_DM2)],
                standard="EN 16121:2013+A1:2017 (the report prints EN 16121:2017+A1:2017), 6.2 e)",
                applies_to="shelves of non-domestic storage furniture",
                deflection="measured under load at the end of the load period: one week for a shelf "
                           "not of metal, glass or stone (iso-7170-2021-preview/6-1-4-load-duration), "
                           "so a week's creep is in it and not the years' after",
                load="uniform over the shelf, 1.5 kg/dm² at level 1 (general use) or 2.0 kg/dm² at "
                     "level 2 (severe); the 2023 edition lowers them to 1.0 and 1.5 "
                     "(catas-en-16121-2023/deflection-test-loads), and the limit is not restated "
                     "there")]),
        _publication(
            "iso-7170-2021-preview",
            "ISO 7170:2021 Furniture — Storage units — Test methods for the determination of "
            "strength, durability and stability (the preview of its first pages)",
            publisher="ISO, preview served by iTeh Standards", year=2021, identifier="ISO 7170:2021",
            url="https://cdn.standards.iteh.ai/samples/76864/6dd74627d5b54503b585035f49c812ef/ISO-7170-2021.pdf",
            sha256="ac03532af18cfd3f49dee9d05ef579002c9a3d493ee90cb96445771f5276ce54", **copyrighted,
            children=[_stated(
                "6-1-4-load-duration", "6.1.4, shelf deflection",
                [("load_duration", "h", "apply for", "one week for all other shelves", 1, {"times": 168.0}),
                 ("load_duration_metal_glass_stone", "h", "apply for", "one hour for shelves made of metal",
                  1, SAME)],
                applies_to="the shelf deflection test of storage units",
                deflection="measured under load at the end of that time, in mm and as a percentage of "
                           "the distance between the supports; ISO 7170 sets no acceptance level",
                note="EN 16122 6.1.4, the method EN 16121's limit names, was not read; that it loads "
                     "a shelf for the same week rests on this test and on CATAS's tables, which set "
                     "the two side by side")]),
        _publication(
            "catas-warped-shelves-2023",
            "CATAS (P. Tirelli, M. Indovina), Warped furniture and shelves: some considerations "
            "(May 2023)",
            publisher="CATAS", year=2023,
            url="https://catas.com/uploads/media/mobili-e-ripiani-imbarcati-alcune-considerazioni-eng.pdf",
            sha256="4b0a68354c60dc129fe3072c2896e1c76992d2f4e73f9650fc94c68bdbb7b79a", **copyrighted,
            licence_note="all rights reserved; reproduction authorized with the source cited",
            children=[_stated(
                "shelf-deflection-requirement", "p. 1",
                [("share_of_span", "", "If the shelf deflection requirement were", "0.5 per cent", 0.5,
                  PERCENT)],
                applies_to="shelves of storage furniture tested to EN 16122 6.1.4",
                deflection="under the test load at the end of the test; CATAS says EN 16122 sets no "
                           "acceptance level and that most technical specifications require 0.5% of "
                           "the span, and that the measurement includes the panel's warp before loading")]),
        _publication(
            "catas-comparison-table-storage",
            "CATAS, Comparison table of tests on furniture: storage units (undated; it gives EN "
            "16121's loads before the 2023 edition)",
            publisher="CATAS", year=None,
            url="https://catas.com/uploads/media/catas-tabellanormemobilieng.pdf",
            sha256="d3eb25a5bbf873bce3b65595388629ebd529fee0afbeb9268fdbe450524fab2b", **copyrighted,
            children=[
                _stated("deflection-of-shelves-domestic",
                        "row Deflection of shelves, EN 16122 6.1.4, columns UNI 11663 (domestic use)",
                        [("share_of_span", "", "Deflection of shelves EN 16122 6.1.4", "0,5 %", 0.5,
                          PERCENT),
                         ("surface_load_kitchen_bathroom", "kg/m2", "Deflection of shelves EN 16122 6.1.4",
                          "Load: 1,5 kg/dm2", 1.5, KG_PER_DM2),
                         ("surface_load_other_use", "kg/m2", "Deflection of shelves EN 16122 6.1.4",
                          "Load: 1,0 kg/dm2", 1.0, KG_PER_DM2)],
                        standard="UNI 11663 (Italy), strength and durability of domestic storage units",
                        applies_to="shelves of domestic storage units: kitchen and bathroom, other use, "
                                   "small components (1.0 kg/dm²)",
                        deflection="as EN 16122 6.1.4 measures it, under load at the end of the test",
                        load="uniform, 1.5 kg/dm² in a kitchen or bathroom, 1.0 elsewhere",
                        note="the column each value belongs to is read from the table's layout"),
                _stated("deflection-of-shelves-non-domestic",
                        "row Deflection of shelves, EN 16122 6.1.4, columns EN 16121 levels 1 and 2 "
                        "(non-domestic use)",
                        [("share_of_span", "", "Deflection of shelves EN 16122 6.1.4 / Load: 1,5 kg/dm2 "
                          "Max deflection: 0,5 % Load: 2,0", "0,5 %", 0.5, PERCENT),
                         ("surface_load_level_1", "kg/m2", "Deflection of shelves EN 16122 6.1.4 / Load: "
                          "1,5 kg/dm2 Max deflection: 0,5 % Load: 2,0", "Load: 1,5 kg/dm2", 1.5, KG_PER_DM2),
                         ("surface_load_level_2", "kg/m2", "Deflection of shelves EN 16122 6.1.4 / Load: "
                          "1,5 kg/dm2 Max deflection: 0,5 % Load: 2,0", "Load: 2,0 kg/dm2", 2.0, KG_PER_DM2)],
                        standard="EN 16121, before its 2023 edition",
                        applies_to="shelves of non-domestic storage units",
                        deflection="as EN 16122 6.1.4 measures it, under load at the end of the test",
                        load="uniform, 1.5 kg/dm² at level 1, 2.0 at level 2",
                        note="the column each value belongs to is read from the table's layout"),
            ]),
        _publication(
            "catas-en-16121-2023",
            "CATAS (M. Marussi), Storage furniture for non-domestic use: new version of EN 16121 "
            "published (January 2024)",
            publisher="CATAS", year=2024, url="https://catas.com/uploads/media/mobili-non-domestici-eng.pdf",
            sha256="1d3a807af880a5779a1007bcbd1e24abb9e7c9a3ee5e81f0898a57c7bfe0c9f0", **copyrighted,
            licence_note="all rights reserved; reproduction authorized with the source cited",
            children=[_stated(
                "deflection-test-loads", "p. 2, Resistance and Durability Tests",
                [("surface_load_level_1", "kg/m2", "Deflection test of shelves", "from 1.5 to 1.0", 1.0,
                  KG_PER_DM2),
                 ("surface_load_level_2", "kg/m2", "Deflection test of shelves", "from 2.0 to 1.5", 1.5,
                  KG_PER_DM2)],
                standard="EN 16121:2023",
                applies_to="the shelf deflection test of non-domestic storage furniture",
                load="uniform, 1.0 kg/dm² at level 1 (was 1.5) and 1.5 kg/dm² at level 2 (was 2.0)",
                note="CATAS does not restate the acceptance level; whether the 2023 edition keeps "
                     "0.5% of the span was not read")]),
        _publication(
            "kcma-a161-1-2022",
            "ANSI/KCMA A161.1-2022 Performance and Construction Standard for Kitchen and Vanity "
            "Cabinets",
            publisher="Kitchen Cabinet Manufacturers Association", year=2022, identifier="ANSI/KCMA A161.1-2022",
            url="https://kcma.org/sites/default/files/2024-08/KCMA%20A161.1%202022%20High%20Res.pdf",
            sha256="e08477ac528c20ef1c7db5d9c96fc04658577e924078c88246dd9809b65effdf", **copyrighted,
            children=[_stated(
                "5-1-3-shelf-deflection", "5.1.2 D and E (the load test) and 5.1.3, item 2",
                [("share_of_span", "", "shall not deflect more than", "(0.0625 inch) per 305 mm (lineal foot)",
                  0.0625, {"times": 1 / 12}),
                 ("max_deflection", "mm", "shall not deflect more than", "6.4 mm", 6.4, SAME),
                 ("surface_load", "kg/m2", "uniformly at", "(15 lb./ft2)", 15, LB_PER_FT2),
                 ("load_duration", "h", "Maintain loading for", "seven days", 7, {"times": 24.0})],
                applies_to="shelves and bottoms of kitchen and vanity cabinets",
                deflection="measured at the end of seven days under load: a week's creep is in it, not "
                           "the years' after; 1/16 inch per foot of span (span/192) and never more than "
                           "6.4 mm between two supports",
                load="uniform, 718 Pa (15 lb/ft²), arranged so the loads do not bridge")]),
        _publication(
            "aws-2009-section-10",
            "Architectural Woodwork Standards, 1st edition (2009), Section 10: Casework",
            publisher="AWI, AWMAC and WI", year=2009, identifier="AWS 1st edition, Section 10",
            url="https://woodworkinstitute.com/wp-content/uploads/2014/09/WI_AWS_sec10NM.pdf",
            sha256="d18196833cc8d1bd28f5f2441a502803791382816c4617eb78dd1cc98fe347b2", **copyrighted,
            children=[_stated(
                "1-2-21-shelf-deflection", "1.2.21.2 and 1.2.21.3.1.1, p. 253",
                [("share_of_span", "", "1.2.21.3.1.1", "L/144", 144, OVER),
                 ("surface_load", "kg/m2", "1.2.21.2.2", "40 lbs", 40, LB_PER_FT2),
                 ("surface_load_books", "kg/m2", "1.2.21.2.1", "50 lbs", 50, LB_PER_FT2),
                 ("max_load", "kg", "1.2.21.2 LOAD", "200 lbs", 200, POUNDS)],
                applies_to="adjustable shelves of architectural casework",
                deflection="under load; the standard counts creep, the deflection that grows over "
                           "time, as no defect (1.2.21.3.2), so the limit holds without it",
                load="uniform, 40 lb/ft² (50 for school, hospital, library and book shelving), at "
                     "most 200 lb on one shelf")]),
        _publication(
            "sefa-8-pl-2026",
            "SEFA 8-PL-2026 Laboratory Grade Plastic Laminate Casework Standard",
            publisher="Scientific Equipment & Furniture Association", year=2026, identifier="SEFA 8-PL-2026",
            url="https://www.sefalabs.com/assets/docs/Standards/SEFA%208-PL-2026.pdf",
            sha256="3d0eb1932f1b918b8822a1f442a66f4f8a1f9f2bda51f82c9628907588edc604", **copyrighted,
            children=[
                _stated("7-2-3-shelf", "7.2.2 Test Procedure and 7.2.3 Acceptance Level, pp. 11-12",
                        [("share_of_span", "", "allowable maximum deflection of a shelf is", "1/180", 180, OVER),
                         ("max_deflection", "mm", "allowable maximum deflection of a shelf is", "(6.35mm)",
                          6.35, SAME),
                         ("surface_load", "kg/m2", "load the shelf uniformly to", "40 pounds", 40,
                          LB_PER_FT2),
                         ("max_load", "kg", "to a maximum of", "200 pounds", 200, POUNDS)],
                        applies_to="shelves of laboratory casework",
                        deflection="initial: measured once the load is on, then the load is removed",
                        load="uniform, 40 lb/ft² of shelf, at most 200 lb"),
                _stated("10-2-3-apron-rails", "10.2.3 Acceptance Level, p. 17",
                        [("share_of_span", "", "apron rails shall not deflect more than", "1/360", 360, OVER),
                         ("max_deflection", "mm", "apron rails shall not deflect more than", "(3.175mm)",
                          3.175, SAME)],
                        applies_to="the apron rails of laboratory tables",
                        deflection="under the table's full load, as soon as it is on",
                        load="the table's full test load (10.2)"),
            ]),
        _publication(
            "icc-300-2017-public-comment-draft",
            "ICC 300-2017 Standard on Bleachers, Folding and Telescopic Seating, and Grandstands, "
            "public comment draft (October 2017)",
            publisher="International Code Council", year=2017, identifier="ICC 300-2017, public ballot draft",
            url="https://www.iccsafe.org/wp-content/uploads/ICC-300-ANSI-Public-Comment-Draft-pdf.pdf",
            sha256="005b5b43dda428d2db6bec5de00d3b9836ede06365a70bbeddb66eb3c42eb3dd", **copyrighted,
            children=[_stated(
                "303-6-deflections", "303.6 Deflections, p. 4",
                [("share_of_span_2012", "", "303.6 Deflections.", "1/200", 200, OVER),
                 ("share_of_span_proposed", "", "303.6 Deflections.", "1/180", 180, OVER)],
                applies_to="structural members of bleachers and grandstands under live load; members of "
                           "folding and telescopic seating are not limited",
                deflection="under the live load",
                text_status="The draft is in legislative format, struck text deleted and underlined "
                            "text added; on page 4, rendered, 1/200 is struck and 1/180 underlined (the "
                            "text layer prints both). The draft amends ICC 300-2012, so 1/200 of the "
                            "span is the 2012 text and 1/180 the limit proposed in the 2017 draft; "
                            "whether the published ICC 300-2017 kept 1/180 was not checked.")]),
        _publication(
            "swedish-wood-design-vol-2-2022",
            "Design of timber structures, Volume 2: Rules and formulas according to Eurocode 5, UK "
            "edition 1:2022",
            publisher="Swedish Forest Industries Federation (Swedish Wood), with Timber Development UK",
            year=2022,
            url="https://www.universityofgalway.ie/media/timberengineeringresearchgroup/Design-of-timber-"
                "structures_Volume2_Rules-and-formulas-according-to-Eurocode-5.pdf",
            sha256="c8eedc19699307a9f842bd92e86254e7411175cde708c596a0920a823d4da160", **copyrighted,
            licence_note="copying of the content is prohibited; distributed free of charge",
            children=[
                _stated(f"table-9-3-{beam}-{w}", f"Table 9.3, row {row}, column {col}, p. 34",
                        [("share_of_span_lenient", "", "Cantilever beam", printed, lenient, OVER),
                         ("share_of_span_strict", "", "Cantilever beam", printed, strict, OVER)],
                        standard="EN 1995-1-1:2004, 7.2, Table 7.2: recommended ranges, a Nationally "
                                 "Determined Parameter each country's annex may set",
                        applies_to=f"timber beams, {row.lower()}",
                        deflection=what, load="the load combinations of EN 1995-1-1 2.2.3")
                for beam, row, w, col, printed, lenient, strict, what in [
                    ("two-supports", "Beam on two supports", "instantaneous", "winst",
                     "l ⁄300 – l ⁄500", 300, 500,
                     "instantaneous: as soon as the load is on"),
                    ("two-supports", "Beam on two supports", "net-final", "wnet,fin",
                     "l ⁄250 – l ⁄350", 250, 350,
                     "final, creep included, less any precamber"),
                    ("two-supports", "Beam on two supports", "final", "wfin",
                     "l ⁄150 – l ⁄300", 150, 300, "final, creep included"),
                    ("cantilever", "Cantilever beam", "instantaneous", "winst",
                     "l ⁄150 – l ⁄250", 150, 250,
                     "instantaneous: as soon as the load is on"),
                    ("cantilever", "Cantilever beam", "net-final", "wnet,fin",
                     "l ⁄125 – l ⁄175", 125, 175,
                     "final, creep included, less any precamber"),
                    ("cantilever", "Cantilever beam", "final", "wfin",
                     "l ⁄75 – l ⁄150", 75, 150, "final, creep included"),
                ]] + [
                _stated(f"table-9-1-{key}", f"Table 9.1, {group}, row {row}, p. 33",
                        [(f"kdef_service_class_{i + 1}", "", group, f"{row} {printed}", v, SAME)
                         for i, v in enumerate(values)],
                        standard="EN 1995-1-1:2004, 3.1.4, Table 3.2: the deformation factor kdef, the final "
                                 "deflection under a lasting load being the initial one times (1 + kdef)",
                        applies_to=f"{group}, {row}", service_classes="1, 2, 3 as printed; '-' where the "
                                                                    "material may not be used")
                for key, group, row, printed, values in KDEF_ROWS]),
        _publication(
            "cpa-shelving-bulletin",
            "Composite Panel Association, Technical Bulletin: Particleboard and MDF for Shelving "
            "(ANSI A208.1-2016 and A208.2-2016), as hosted by Lowe's",
            publisher="Composite Panel Association", year=None,
            url="https://pdf.lowes.com/productdocuments/f8975c59-6745-4684-bcfd-0b8f0d02c2e5/63115881.pdf",
            sha256="1781c8d5b84e91e14c0abed3448597ad208d990e5211cf07e7ec17ff2119584a", **copyrighted,
            children=[_stated(
                "methodology", "Methodology, p. 8",
                [("share_of_span", "", "allowable shelf deflection of", "span/240", 240, OVER)],
                applies_to="raw particleboard and MDF shelves of the grades ANSI A208.1 and A208.2 "
                           "specify, uniformly loaded, the shelf's own weight not counted",
                deflection="elastic, computed with the standards' minimum modulus; CPA chose the limit "
                           "to keep the long-term deflection small",
                load="uniform")]),
        _publication(
            "ewpaa-shelving-design-manual",
            "Particleboard and MDF Structural Shelving Design Manual, revision 3 (EWPAA), as hosted "
            "by Borg",
            publisher="Engineered Wood Products Association of Australasia", year=2012,
            identifier="revision 3, 06-02-2012",
            url="https://borg.bynder.com/asset/a7644caa-89dc-46ec-83cb-6abd310ef21a/CUSTOMpine-Shelving-load-tables.pdf",
            sha256="57f37feb1f3a186cbd085a1acb8263cef663eb90543cc615e6d3021bf3b0fa8d", **copyrighted,
            children=[
                _stated("design-criteria", "Design Methodology, Design Criteria, p. 4",
                        [("share_of_span", "", "Most industrial shelving designers nominate", "Span/180",
                          180, OVER)],
                        applies_to="industrial shelving of particleboard and MDF (AS/NZS 1859)",
                        deflection="initial: the manual's load tables give initial deflections, creep "
                                   "not included",
                        load="uniformly distributed"),
                _stated("long-term-effects", "Long Term Effects, p. 5",
                        [("creep_factor_temperate", "", "Creep in Particleboard and MDF would be expected to",
                          "double", 2, SAME),
                         ("creep_factor_tropical_interior", "", "the creep factor is", "three times", 3, SAME),
                         ("creep_factor_tropical_exterior", "", "a creep factor of", "four", 4, SAME)],
                        applies_to="particleboard and MDF shelving: temperate climates and "
                                   "air-conditioned interiors; tropical interiors that follow the "
                                   "weather; severe tropical weather under cover outside",
                        deflection="final: the initial deflection times the factor"),
            ]),
        _publication(
            "epf-mdf-shelves",
            "European Panel Federation, mdf-info.eu: Furniture, 11. MDF shelves and storage units "
            "(web page, undated)",
            publisher="European Panel Federation", year=None,
            url="https://mdf-info.eu/applications/mobel/regale-und-stauelemente-aus-mdf",
            sha256="5f2a989c594055763c7066d7487a70116562fa54b73209b9c81d39663fddd19e", **copyrighted,
            children=[_stated(
                "11-creep", "11, the paragraph after the deflection formula",
                [("creep_increase", "", "Creep effects occurring during long term loading", "up to 50%", 50,
                  PERCENT)],
                applies_to="MDF shelves surfaced by direct painting or a thin decorative foil; MDF "
                           "faced on both sides with veneer or laminate deflects and creeps less",
                deflection="long-term: the initial deflection may grow by up to half")]),
        _publication(
            "gsa-3fne-00-589a",
            "Purchase Description 3FNE 00-589A, Test Requirements for Library Bookstacks (2013)",
            publisher="U.S. General Services Administration", year=2013, identifier="3FNE 00-589A",
            url="https://origin-www.gsa.gov/system/files/Test_Requirements_for_Library_Bookstacks_508.pdf",
            sha256="434f2b04c22effbf2e197e1825124fc94ad8e488c3a66ee8abc82a747196513a", licence="unstated",
            licence_note="a GSA document carrying no notice either way, cited as if copyrighted, as "
                         "FNAE-80-214A is",
            children=[
                _stated("4-shelf-deflection", "4. Shelf deflection test",
                        [("max_deflection", "mm", "Deflection in excess of", "4.7 mm", 4.7, SAME),
                         ("load_duration", "h", "the load has been applied for", "ten (10) minutes", 10,
                          {"times": 1 / 60}),
                         ("load_305_mm_shelf", "kg", "A total load of", "54.5 kg placed on the 305 mm",
                          54.5, SAME),
                         ("load_200_mm_shelf", "kg", "A total load of", "43 kg", 43, SAME)],
                        applies_to="adjustable flat shelves of metal cantilever library bookstacks",
                        deflection="under load, ten minutes after it is on",
                        load="43 kg on a 200 mm deep shelf, 54.5 kg on a 305 mm one, 61 and 80 kg on "
                             "280 and 355 mm divider shelves, spread evenly"),
                _stated("4-permanent-deflection", "4. Shelf deflection test",
                        [("max_permanent_deflection", "mm", "Permanent deflection in excess of", "0.78 mm",
                          0.78, SAME)],
                        applies_to="the same shelves",
                        deflection="permanent: five minutes after the load is taken off"),
            ]),
        _publication(
            "nih-drm-news-to-use-2016-02",
            "Design Requirements Manual News to Use, Vol. 01 No. 71: Wall Shelving (February 2016)",
            publisher="National Institutes of Health, Office of Research Facilities", year=2016,
            identifier="Vol. 01, No. 71",
            url="https://orf.od.nih.gov/TechnicalResources/Documents/News%20to%20Use%20PDF%20Files/2016%20NTU/"
                "Wall%20Shelving%20February%20-%202016%20News%20to%20Use_508.pdf",
            sha256="b2baf8b0eb6edef4be48c50dcb51c68c4f91e09a0ce9ab6324b72f3b94d9cd2b",
            licence="public-domain",
            licence_note="a publication of NIH's Office of Research Facilities, a work of the U.S. "
                         "Government",
            capture="sources/nih-drm-news-to-use-2016-02/pages.txt",
            children=[
                _stated("wall-shelving-deflection", "Wall Shelving, sidebar",
                        [("max_deflection", "mm", "there is no more than", "(6mm)", 6, SAME),
                         ("max_support_spacing", "mm", "In no case shall support spacing exceed",
                          "(1200mm)", 1200, SAME)],
                        quote="Shelving material, gauge/thickness and shelf support spacing shall be "
                              "selected so that there is no more than ¼” (6mm) deflection under maximum "
                              "design load. In no case shall support spacing exceed 4’- 0” (1200mm).",
                        applies_to="wall shelving in laboratories, where NIH prohibits wood shelving "
                                   "(wall-shelving-materials)",
                        deflection="under the maximum design load"),
                _stated("wall-shelving-loading", "Wall Shelving, Loading",
                        [("line_load", "kg/m", "Shelving in laboratories shall be designed for a minimum of",
                          "50 pounds", 50, {"times": POUND_PER_FOOT_KG_M}),
                         ("shelf_depth", "mm", "Shelving in laboratories shall be designed for a minimum of",
                          "(300mm)", 300, SAME)],
                        quote="Shelving in laboratories shall be designed for a minimum of 50 pounds "
                              "(23kg) per linear foot for a 12” (300mm) deep shelf, and proportionally "
                              "more for deeper shelves."),
                _stated("wall-shelving-materials", "Wall Shelving, Materials", [],
                        quote="Wood shelving is prohibited."),
            ]),
    ]


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


def gsa_fnae() -> Node:
    """GSA's test method for upholstered seating. Its licence could not be established (GSA
    says most of its site is free of copyright, and that some material on it is a third
    party's), so it is cited by locator and values, never quoted, and the copy it is checked
    against is kept privately."""
    sidethrust = {f"side_force_{level}": published(lbf * POUND_FORCE_N, "N", "Table 1",
                                                     f"{lbf} pounds")
                  for level, lbf in SIDETHRUST_LEG_LBF.items()}
    return Node(
        id="gsa-fnae-80-214a", kind="source",
        name="Upholstered Furniture Test Method, FNAE-80-214A (1998)",
        payload={"publisher": "U.S. General Services Administration", "year": 1998,
                 "identifier": "FNAE-80-214A",
                 "url": "https://www.gsa.gov/system/files/Upholstered_Furniture_Test_Method_508.pdf",
                 "sha256": "6b389ae4b5402dd9617827ad9c79a9101dab3d9c004bea743041e1ad400c86ee",
                 "licence": "unstated",
                 "licence_note": "GSA's site policy: most material on it is free of copyright, "
                                 "some is a third party's; this document carries no notice "
                                 "either way, so it is cited as if copyrighted"},
        children=[
            Node(id="sidethrust-leg-7-4", kind="clause",
                 payload={"locator": "7.4 Sidethrust Load Test on Legs, and Table 1",
                          "in_our_words": "a force parallel to the floor, across the piece, on "
                                          "a side rail at one end midway between its front "
                                          "and back legs, resisted by the legs at the other "
                                          "end; 25,000 cycles at each level; Table 1 gives "
                                          "the levels a light, medium and heavy service "
                                          "piece must reach without disabling damage"},
                 params=sidethrust),
            Node(id="scope-1-0", kind="clause",
                 payload={"locator": "1.0 Scope",
                          "in_our_words": "sofas, dual purpose units, recliners and lounge "
                                          "chairs, whatever their materials and construction"}),
        ])


# --- sawing by hand: two U.S. Army manuals, approved for public release -----------------

def tm_9_243() -> Node:
    clauses = [
        _clause("crosscut-46-4-b-c", "46.4 Using the crosscut saw, b and c, p. 46-7",
                "b. To start the cut, place thumb (3) against the side of the saw blade, being "
                "careful to hold it well above teeth. c. Start the cut by drawing back a few "
                "inches of teeth at the heel of the saw a few times."),
        _clause("crosscut-46-4-d-e", "46.4 Using the crosscut saw, d and e, p. 46-7",
                "d. At approximately a 45 degree angle, saw only on the downward stroke applying "
                "pressure evenly. e. Keep the saw blade at a right angle to the work surface by "
                "checking the saw position occasionally with a try square"),
        _clause("crosscut-46-4-f", "46.4 Using the crosscut saw, f, p. 46-7",
                "f. When nearing end of cut, hold the waste side of the wood to prevent board "
                "breaking off unevenly."),
        _clause("keyhole-46-5-a", "46.5 Using the keyhole saw, a, p. 46-8",
                "a. To make an inside-out cut, first drill a hole (1) large enough to admit the "
                "point of the saw."),
        _clause("keyhole-46-5-b-c", "46.5 Using the keyhole saw, b and c, p. 46-8",
                "b. Insert the saw blade (2) and start to cut slowly, with a minimum of pressure. "
                "c. Be careful not to twist the blade too sharply, as the narrow blade will "
                "easily bend."),
    ]
    return Node(id="tm-9-243", kind="source",
                name="Use and Care of Hand Tools and Measuring Tools, TM 9-243 (TO 32-1-101)",
                payload={"publisher": "U.S. Army, Air Force, Navy and Marine Corps",
                         "year": 2022, "identifier": "TM 9-243, change 2, 8 April 2022",
                         "url": "https://archive.org/download/tm-9-243-use-and-care-of-handtools-"
                                "and-measuring-tools-2022/TM9-243_Use_and_care_of_handtools_and_"
                                "measuring_tools_2022.pdf",
                         "sha256": "728384d64f82336e96af4b67a620af64a0ccee84433ad844e96ddc2b4d684ee0",
                         "licence": "public-domain",
                         "licence_note": "a work of the U.S. Government; Distribution Statement "
                                         "A, approved for public release, distribution unlimited",
                         "capture": "sources/tm-9-243/pages.txt"},
                children=clauses)


def fm_5_426() -> Node:
    return Node(id="fm-5-426", kind="source", name="Carpentry, FM 5-426",
                payload={"publisher": "Headquarters, Department of the Army", "year": 1995,
                         "identifier": "FM 5-426, 3 October 1995",
                         "url": "https://archive.org/download/MManuals/UsArmyEngineerCarpentry1995.pdf",
                         "sha256": "7fd30a1d3468c6debe06a69d4f7b63e773cc3265687161ed794aa396be1e63ee",
                         "licence": "public-domain",
                         "licence_note": "a work of the U.S. Government, approved for public "
                                         "release, distribution unlimited",
                         "capture": "sources/fm-5-426/pages.txt"},
                children=[_clause("waste-side-6", "Chapter 6, Lap Joints, Half-Lap Splice Joint",
                                  "Overlaps should be sawed on the waste side of the gauge line, "
                                  "to avoid cutting laps oversize by the thickness of the cut.")])


def tools() -> Node:
    """Hand tools that cut a part's cuts, each saying, per language, its name and how it is
    used, every sentence resting on the clauses it links `per`. The documents print a
    tool's method beside the cut it makes; the order of the cuts comes from the cut's
    shape, not from here."""
    tm, fm = f"{SOURCES}/tm-9-243", f"{SOURCES}/fm-5-426"
    saw = Node(
        id="crosscut-saw", kind="tool", name="Crosscut saw",
        payload={"does": "saws a straight cut that starts at an edge of the board",
                 "say": {
                     "fr": {"name": "Scie égoïne", "method": [
                         "Scier du côté chute du trait, pour ne pas raccourcir la pièce de "
                         "l'épaisseur de la coupe.",
                         "Amorcer en tirant la scie vers soi quelques fois par le talon, le "
                         "pouce contre la lame, bien au-dessus des dents.",
                         "Scier en poussant seulement, la scie à environ 45°, sans forcer ; "
                         "garder la lame d'équerre à la face, en la vérifiant de temps en "
                         "temps à l'équerre.",
                         "En fin de coupe, tenir la chute pour qu'elle ne casse pas en "
                         "arrachant le bord."]},
                     "en": {"name": "Crosscut saw", "method": [
                         "Saw on the waste side of the line, so the part is not cut short by "
                         "the thickness of the cut.",
                         "Start by drawing the saw back a few times at its heel, your thumb "
                         "against the blade well above the teeth.",
                         "Saw only on the downward stroke, at about 45°, pressing evenly; keep "
                         "the blade at a right angle to the face, checking it now and then "
                         "with a try square.",
                         "Near the end of each cut, hold the waste so it does not break off "
                         "unevenly."]}}},
        links={"per": [f"{fm}/waste-side-6", f"{tm}/crosscut-46-4-b-c",
                       f"{tm}/crosscut-46-4-d-e", f"{tm}/crosscut-46-4-f"]})
    keyhole = Node(
        id="keyhole-saw", kind="tool", name="Keyhole saw",
        payload={"does": "saws a cut that starts inside the board, from a drilled hole",
                 "say": {
                     "fr": {"name": "Scie à guichet", "method": [
                         "Percer dans la chute un trou assez grand pour y engager la pointe de "
                         "la scie.",
                         "Engager la lame et commencer doucement, sans forcer ; ne pas la "
                         "tordre, elle plie facilement.",
                         "Scier du côté chute du trait."]},
                     "en": {"name": "Keyhole saw", "method": [
                         "Drill a hole in the waste large enough to admit the point of the saw.",
                         "Insert the blade and start slowly, with a minimum of pressure; do not "
                         "twist it sharply, the narrow blade bends easily.",
                         "Saw on the waste side of the line."]}}},
        links={"per": [f"{tm}/keyhole-46-5-a", f"{tm}/keyhole-46-5-b-c", f"{fm}/waste-side-6"]})
    return Node(id="tools", kind="", children=[saw, keyhole])


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
    gsa = GSA_FNAE
    sideways = Node(
        id="seating-sidethrust-light", kind="requirement",
        name="A seat carries the light-service sidethrust of GSA's leg test across it at seat "
             "height, without a joint giving way",
        payload={"measure": "sideways", "scope": {"category": "seating"},
                 "applied": "parallel to the floor, across the piece, at seat height",
                 "prediction": "A static check of the force's path predicts a cyclic physical "
                               "test (25,000 cycles); passing it is not passing the test.",
                 "reach": "FNAE-80-214A is written for upholstered sofas and chairs; a bench "
                          "is held to it as the nearest public seating test"},
        params={"side_force": derived(SIDETHRUST_LEG_LBF["light"] * POUND_FORCE_N, "N",
                                      [f"{gsa}/sidethrust-leg-7-4/side_force_light"],
                                      "200 pounds of force")},
        links={"per": [f"{gsa}/sidethrust-leg-7-4", f"{gsa}/scope-1-0"]})
    return Node(id="requirements", kind="", children=[clothing, carpet, sideways])


def knowledge() -> list[Node]:
    """The top-level branches a design tree mounts: sources, materials, requirements, and
    the hand tools that cut a part's cuts."""
    return [Node(id="sources", kind="", children=[wood_handbook(), federal_register(), gsa_fnae(),
                                                  tm_9_243(), fm_5_426(), *tropix(), schmidtova(),
                                                  boruvka(), *sag_limits()]),
            materials(), requirements(), tools()]


def merge(*branches: list[Node]) -> list[Node]:
    """Several knowledge bases as one: top-level branches with the same id (sources,
    materials...) become one branch holding the children of each. A child id two of them
    use is refused, since one path would then name two things."""
    out: dict[str, Node] = {}
    for nodes in branches:
        for node in nodes:
            held = out.setdefault(node.id, Node(id=node.id, kind=node.kind))
            ids = {c.id for c in held.children}
            clash = ids & {c.id for c in node.children}
            if clash:
                raise ValueError(f"'{node.id}/{sorted(clash)[0]}' is defined by two knowledge bases")
            held.children.extend(c.model_copy(deep=True) for c in node.children)
    return list(out.values())


def mount(nodes: list[Node], under: str) -> Node:
    """`nodes` (top-level branches) moved under one branch `under`, every link and every
    `derived_from` that pointed into them rewritten to the new place — so a tree that has
    its own top-level `requirements/` can carry the knowledge beside it as
    `<under>/requirements/...`."""
    tops = {n.id for n in nodes}

    def moved(ref: str) -> str:
        return f"{under}/{ref}" if ref.split("/", 1)[0] in tops else ref

    def walk(node: Node) -> Node:
        node = node.model_copy(deep=True)
        node.links = {rel: [moved(t) for t in targets] for rel, targets in node.links.items()}
        for q in node.params.values():
            q.derived_from = [moved(r) for r in q.derived_from]
        node.children = [walk(c) for c in node.children]
        return node

    return Node(id=under, kind="", children=[walk(n) for n in nodes])
