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

Only public-domain sources are captured and quoted in this repo (ledger:
a-copyrighted-standard-is-cited-never-copied-here).
"""

from __future__ import annotations

from quern.provenance import Quantity
from quern.tree import Node

from .units import CUBIC_FOOT_MM3, INCH_MM, POUND_FORCE_N, POUND_KG, POUND_PER_CUBIC_FOOT_KG_M3

SOURCES = "sources"
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


def _panel(id_: str, name: str, *, form: str, sg: float, sg_ref: str, e: float, e_ref: str,
           mor: float, mor_ref: str, bent: str, per: list[str], note: str = "",
           connector_key: str = "plywood") -> Node:
    """A panel product: its bending modulus is the one measured on the panel (shear
    deflection included, so no shear term is added to it), and its values hold only bent the
    way the source says it bent them (`measured_along`; 'unstated' when it does not say)."""
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
        },
        links={"per": per})


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
        },
        links={"per": [edge, f"{wh}/table-19-2-note-a", f"{wh}/table-19-2-note-b",
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
             "panel with other ply thicknesses or another glue is near it, not it.")]
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
    return Node(id="materials", kind="", children=out + panels())


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
                                                  tm_9_243(), fm_5_426()]),
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
