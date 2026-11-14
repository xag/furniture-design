"""What the checks found on a piece, in plain words, for the design document: one row per
requirement a person cares about (does the top hold a sitter, how much does it give, does
the piece take a push from the side, do the joints fit their connectors), each with its
numbers and a verdict: ok, fail, or open (the rule could not answer, and why).

The numbers come from the same calculations the rules run (furniture/deflection,
furniture/sideways_margin, the strength rule's M/S); the words are in TEXT.
"""

from __future__ import annotations

import re

from quern import Quern, run_rules
from quern.expr import Absent
from quern.tree import get_node

from .natives import _param, closings, deflection, mass, sideways_margin
from .units import STANDARD_GRAVITY

TEXT = {
    "fr": {
        "strength": "Résistance : {part} sous {load}",
        "strength_res": "contrainte {s} MPa pour {a} MPa admissibles (résistance que 95 % des "
                        "pièces dépassent, divisée par 2,1 pour une charge de dix ans et la "
                        "sécurité)",
        "sag": "Flèche : {part} sous {load}",
        "sag_res": "{d} mm au milieu, en appui simple sur ses deux supports",
        "sag_limit": " ; avec le fluage, {f} mm pour une limite fixée à {l} mm",
        "sag_limit_no_creep": " ; limite fixée à {l} mm avec le fluage, que le matériau ne permet pas de vérifier : "
                              "il ne donne pas son fluage",
        "no_strength": "non tranché : le matériau ne donne pas de résistance en flexion",
        "no_stiffness": "non calculée : le matériau ne donne pas de module d'élasticité",
        "no_shear": "non calculée : la pièce ne dit pas quel module de cisaillement de son matériau lire",
        "sideways": "Poussée de côté : {f} N à hauteur d'assise ({src})",
        "sideways_ok": "les connecteurs des panneaux qui la reprennent tiennent, {m} N de marge",
        "sideways_fail": "il manque {m} N : {why}",
        "sideways_unbraced": "aucun panneau dans le plan de la poussée ne la reprend",
        "single": "ni les panneaux dans le plan de la poussée, ni la flexion de tous les "
                  "assemblages entre les côtés et les pièces horizontales ne la reprennent",
        "weak": "les connecteurs ou les côtés ne tiennent pas ce qu'on leur demande",
        "sideways_open": "non tranché : {why}",
        "no_rating": "le connecteur n'a pas de valeur publiée de {mode} dans le {material}",
        "pull_out": "tenue à l'arrachement", "shear": "tenue au cisaillement",
        "moment_opening": "tenue en flexion (assemblage d'angle ouvert)",
        "moment_closing": "tenue en flexion (assemblage d'angle fermé)",
        "joints": "Assemblages : épaisseur et largeur des pièces, outil et réglage du connecteur",
        "joints_ok": "{n} assemblages, tous conformes aux minimums du fabricant",
        "joints_fail": "non conforme : {which}",
        "direction": "Sens du fil : {part}",
        "direction_ok": "le panneau porte dans le sens où ses valeurs ont été mesurées",
        "direction_fail": "les valeurs du matériau ne valent pas dans ce sens",
        "assembly": "Montage : chaque pièce arrive droit sur les connecteurs qu'elle ferme",
        "assembly_ok": "{n} assemblages fermés dans le sens où leurs connecteurs se ferment",
        "assembly_fail": "à l'étape {step}, {part} n'arrive pas droit sur ses connecteurs ({joints}) : "
                         "il faudrait faire glisser la pièce le long de l'assemblage, ou écarter les pièces déjà en place",
        "assembly_open": "non tranché : {why}",
        "no_engagement": "le connecteur de l'assemblage {joint} ne dit pas comment ses pièces se rapprochent",
        "load_point": "{kg} kg au milieu",
        "other": "{rule}",
    },
    "en": {
        "strength": "Strength: {part} under {load}",
        "strength_res": "stress {s} MPa against {a} MPa allowed (the strength 95 % of pieces "
                        "exceed, divided by 2.1 for a ten-year load and safety)",
        "sag": "Sag: {part} under {load}",
        "sag_res": "{d} mm at the middle, simply supported on its two supports",
        "sag_limit": "; with creep, {f} mm against a limit set at {l} mm",
        "sag_limit_no_creep": "; limit set at {l} mm with creep, which the material does not let us check: it "
                              "states no creep",
        "no_strength": "not settled: the material states no bending strength",
        "no_stiffness": "not worked out: the material states no modulus of elasticity",
        "no_shear": "not worked out: the part does not say which of its material's shear moduli to read",
        "sideways": "Sideways push: {f} N at seat height ({src})",
        "sideways_ok": "the connectors of the panels that take it hold, with {m} N to spare",
        "sideways_fail": "{m} N short: {why}",
        "sideways_unbraced": "no panel in the plane of the push takes it",
        "single": "neither the panels in the plane of the push nor the bending of every joint "
                  "between the sides and the horizontal parts take it",
        "weak": "the connectors or the sides do not hold what is asked of them",
        "sideways_open": "not settled: {why}",
        "no_rating": "the connector has no published {mode} in {material}",
        "pull_out": "pull-out strength", "shear": "shear strength",
        "moment_opening": "bending strength (open corner joint)",
        "moment_closing": "bending strength (closed corner joint)",
        "joints": "Joints: thickness and width of the parts, the connector's tool and setting",
        "joints_ok": "{n} joints, all within the maker's minimums",
        "joints_fail": "not within the maker's minimums: {which}",
        "direction": "Grain direction: {part}",
        "direction_ok": "the panel spans the way its values were measured",
        "direction_fail": "the material's values do not hold in this direction",
        "assembly": "Assembly: each part comes straight at the connectors it closes",
        "assembly_ok": "{n} joints closed the way their connectors close",
        "assembly_fail": "at step {step}, {part} does not come straight at its connectors ({joints}): "
                         "it would have to slide along the joint, or spread the parts already in place",
        "assembly_open": "not settled: {why}",
        "no_engagement": "the connector of joint {joint} does not say how its parts come together",
        "load_point": "{kg} kg at the middle",
        "other": "{rule}",
    },
}

JOINT_RULES = {"a-joined-part-is-thick-enough-for-the-cut", "a-joined-part-is-wide-enough",
               "a-joint-is-cut-with-a-tool-its-connector-takes",
               "a-joint-is-cut-at-its-connectors-setting"}
MATERIAL_WORDS = {"fr": {"plywood": "contreplaqué", "mdf": "MDF", "particleboard": "aggloméré"},
                  "en": {"plywood": "plywood", "mdf": "MDF", "particleboard": "particleboard"}}
DECIMAL = {"fr": ",", "en": "."}


def checks(tree: Quern, piece: str, lang: str = "fr") -> list[dict]:
    T = TEXT[lang]

    def _fmt(v: float, nd: int = 1) -> str:
        return f"{v:.{nd}f}".replace(".", DECIMAL[lang])

    prefix = piece.rstrip("/")
    results = [r for r in run_rules(tree, prefix)
               if r.node == prefix or r.node.startswith(prefix + "/")]
    rows = []
    for path, node in tree.walk(prefix):
        if node.kind != "part" or not (node.links or {}).get("bends_as"):
            continue
        name = node.name or node.id
        loads = [(p, n) for p, n in tree.walk("") if n.kind == "load"
                 and path in (n.links or {}).get("on", [])]
        kg = sum(_param(tree, p, "mass") or 0 for p, _ in loads)
        load = T["load_point"].format(kg=_fmt(kg, 0))
        case = node.links["bends_as"][0]
        w = STANDARD_GRAVITY * (mass(tree, path) + kg)
        span, b, h = (_param(tree, path, k) for k in ("span", "depth", "thickness"))
        stress = _param(tree, case, "km") * w * span * 6 / (b * h * h)
        allowed = _param(tree, path, "design_bending_stress")
        rows.append({"requirement": T["strength"].format(part=name, load=load),
                     "result": T["no_strength"] if allowed is None
                     else T["strength_res"].format(s=_fmt(stress), a=_fmt(allowed)),
                     "verdict": "open" if allowed is None else "ok" if stress <= allowed else "fail"})
        limits = [_param(tree, r, "limit") for r in node.links.get("sag_limit", [])]
        try:
            d = deflection(tree, path)
            res, verdict = T["sag_res"].format(d=_fmt(d)), "info"
            if limits:
                share = _param(tree, path, "initial_share_of_longtime")
                res += (T["sag_limit"].format(f=_fmt(d / share, 2), l=_fmt(min(limits), 2)) if share
                        else T["sag_limit_no_creep"].format(l=_fmt(min(limits), 2)))
                verdict = "ok" if all(r.ok for r in results if r.rule == "a-beam-sags-within-its-limit"
                                      and r.node == path) else "fail"
        except (ValueError, Absent) as e:  # a value the material or the part does not give
            res = T["no_shear" if "shear modulus" in str(e) else "no_stiffness"]
            verdict = "open" if limits else "info"
        rows.append({"requirement": T["sag"].format(part=name, load=load), "result": res,
                     "verdict": verdict})
        direction = [r for r in results if r.rule == "a-part-bends-the-way-its-material-was-tested"
                     and r.node == path]
        if direction:
            rows.append({"requirement": T["direction"].format(part=name),
                         "result": T["direction_ok" if direction[0].ok else "direction_fail"],
                         "verdict": "ok" if direction[0].ok else "fail"})
    root = get_node(tree, prefix)
    for case in (root.links or {}).get("sideways_case", []):
        force = _param(tree, case, "side_force")
        req = get_node(tree, case)
        src = ", ".join(t.rsplit("/", 2)[-2].upper().replace("GSA-", "GSA ")
                        for t in (req.links or {}).get("per", [])[:1])
        row = {"requirement": T["sideways"].format(f=_fmt(force, 0), src=src)}
        try:
            m = sideways_margin(tree, prefix, case)
            if not (root.links or {}).get("braced_by"):
                row.update(result=T["sideways_unbraced"], verdict="fail")
            elif m >= 0:
                row.update(result=T["sideways_ok"].format(m=_fmt(m, 0)), verdict="ok")
            else:
                why = T["single"] if abs(m + force / 2) < 1e-6 else T["weak"]
                row.update(result=T["sideways_fail"].format(m=_fmt(-m, 0), why=why), verdict="fail")
        except Absent as e:
            got = re.search(r"states no (\w+) strength in (\S+)", str(e))
            why = T["no_rating"].format(mode=T.get(got.group(1), got.group(1)),
                                        material=MATERIAL_WORDS[lang].get(got.group(2), got.group(2))) \
                if got else str(e)
            row.update(result=T["sideways_open"].format(why=why), verdict="open")
        rows.append(row)
    try:
        closed = closings(tree, prefix)
        if closed:
            bad: dict[tuple[int, str], list[str]] = {}
            for n, j, p, ok in closed:
                if not ok:
                    bad.setdefault((n, p), []).append(j)
            names = {p: (get_node(tree, f"{prefix}/{p}").name or p) for _, _, p, _ in closed}
            rows.append({"requirement": T["assembly"],
                         "result": "; ".join(T["assembly_fail"].format(step=n, part=names[p],
                                                                       joints=", ".join(js))
                                             for (n, p), js in bad.items()) if bad
                         else T["assembly_ok"].format(n=len(closed)),
                         "verdict": "fail" if bad else "ok"})
    except Absent as e:
        got = re.search(r"connector of '([^']+)'", str(e))
        why = T["no_engagement"].format(joint=got.group(1).rsplit("/", 1)[-1]) if got else str(e)
        rows.append({"requirement": T["assembly"], "result": T["assembly_open"].format(why=why),
                     "verdict": "open"})
    joint_results = [r for r in results if r.rule in JOINT_RULES]
    if joint_results:
        bad = sorted({r.node.rsplit("/", 1)[-1] for r in joint_results if not r.ok})
        n = len({r.node for r in joint_results})
        rows.append({"requirement": T["joints"],
                     "result": T["joints_fail"].format(which=", ".join(bad)) if bad
                     else T["joints_ok"].format(n=n),
                     "verdict": "fail" if bad else "ok"})
    return rows
