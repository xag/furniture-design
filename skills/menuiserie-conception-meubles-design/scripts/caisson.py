#!/usr/bin/env python3
"""Débit géométrique uniquement, en mm. Aucun calcul de résistance."""
import argparse
import json
import math

def calculate(w, h, d, t, back, shelves, gap):
    vals = [w, h, d, t, back, gap]
    if any(not math.isfinite(v) for v in vals):
        raise ValueError("Toutes les dimensions doivent être finies.")
    if min(w, h, d, t) <= 0 or min(back, gap) < 0:
        raise ValueError("Dimensions positives requises ; fond et jeu peuvent être nuls.")
    if not isinstance(shelves, int) or shelves < 0:
        raise ValueError("Nombre de tablettes entier positif ou nul requis.")
    iw, depth = w - 2*t, d - back
    clear_height = (h - (shelves + 2)*t)/(shelves + 1)
    if min(iw - 2*gap, depth, clear_height) <= 0:
        raise ValueError("Épaisseur, fond, jeux ou tablettes incompatibles avec l'enveloppe.")
    parts = [
        dict(rep="A", piece="Côté", quantite=2, longueur=h, largeur=depth, epaisseur=t),
        dict(rep="B", piece="Dessus / dessous entre côtés", quantite=2,
             longueur=iw, largeur=depth, epaisseur=t)]
    if shelves:
        parts.append(dict(rep="C", piece="Tablette mobile", quantite=shelves,
                          longueur=iw-2*gap, largeur=depth, epaisseur=t))
    if back:
        parts.append(dict(rep="D", piece="Fond rapporté", quantite=1,
                          longueur=h, largeur=w, epaisseur=back))
    return dict(unite="mm", modele="Côtés toute hauteur ; fond rapporté inclus dans profondeur totale ; sans portes, pieds ni divisions",
                hors_tout=dict(largeur=w, hauteur=h, profondeur=d),
                hauteur_libre_par_niveau=clear_height,
                jeu_lateral_par_cote=gap,
                pieces=parts,
                limite="Géométrie uniquement. Vérifier appuis de tablettes, fixations, stabilité et résistance. Aucun trait de scie ajouté aux cotes finies.")

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["largeur", "hauteur", "profondeur", "epaisseur"]:
        p.add_argument("--"+name, type=float, required=True)
    p.add_argument("--fond", type=float, default=0, help="Épaisseur du fond rapporté, inclus dans profondeur (défaut 0)")
    p.add_argument("--tablettes", type=int, default=0)
    p.add_argument("--jeu", type=float, default=1, help="Jeu latéral par côté de tablette mobile, à confirmer (défaut 1 mm)")
    a = p.parse_args()
    try:
        result = calculate(a.largeur, a.hauteur, a.profondeur, a.epaisseur, a.fond, a.tablettes, a.jeu)
    except ValueError as e:
        p.error(str(e))
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
