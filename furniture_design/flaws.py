"""What the standards know of a piece's design flaws, for whoever shows them to a person: the family each
check of the design is in, how critical a rule that does not hold is, and what each check of the piece's
own rules (furniture-design's package, report.checks) says to people when it does not hold.

A check belongs to the asset it reads. The criteria judged on the assembly instructions as they were drawn
(standards.ON_THE_PAGES) are the instructions' own; every other criterion of a piece, and every rule of
the package that judges a piece, its parts or its joints, reads the design (the model and its notes), and
each is in one family here, in the order a person reads them:

- answers-the-notes: the model gives what the piece's notes ask and decide;
- strength: the piece and its parts take their loads;
- fits-and-moves: the parts fit, are held, and what moves works;
- can-be-made: each part and joint says what it is cut and fastened from and with, within what they allow;
- can-be-assembled: the steps bring the parts together.

How critical a rule that does not hold is, its level, is set by what its failure means for the piece:
fails (the piece will not work as drawn), may_fail (a rule whose failure means that could not tell, a
value it reads being unknown), incomplete (the model or the notes do not say something the piece needs
said). A rule's consequence is the level it has when it is settled; one whose consequence is fails is at
may_fail when it could not tell.

Whoever shows them reads these and writes no word of its own: a standards rule says itself (its messages,
standards_words); a rule of the package says itself here (RED; UNSETTLED when it could not tell).
"""
from __future__ import annotations

FAMILIES = (
    ("answers-the-notes", {"en": "Answers the notes", "fr": "Répond aux notes"}),
    ("strength", {"en": "Strength", "fr": "Solidité"}),
    ("fits-and-moves", {"en": "Fits and moves", "fr": "Ajustement et mouvement"}),
    ("can-be-made", {"en": "Can be made", "fr": "Fabrication"}),
    ("can-be-assembled", {"en": "Can be assembled", "fr": "Montage"}),
)

LEVELS = (
    ("fails", {"en": "Fails", "fr": "Échoue"}),
    ("may_fail", {"en": "May fail", "fr": "Peut échouer"}),
    ("incomplete", {"en": "Incomplete", "fr": "Incomplet"}),
)

# the design's criteria of a piece (every criterion of a piece but those on the pages), each in its family
CRITERIA = {
    "piece-is-explained": "answers-the-notes",
    "piece-agrees-with-its-ledger": "answers-the-notes",
    "piece-holds-together": "fits-and-moves",
    "piece-mechanisms-work": "fits-and-moves",
    "piece-parts-fit": "fits-and-moves",
    "piece-can-be-made": "can-be-made",
    "piece-steps-build-it": "can-be-assembled",
}

F, I = "fails", "incomplete"

# every rule that reads a piece's design: (its family, its consequence), in the order a family lists them
RULES = {
    # the standards' rules of the design's criteria
    "a-pieces-purpose-is-answered": ("answers-the-notes", I),
    "a-pieces-decisions-name-what-realises-them": ("answers-the-notes", I),
    "a-pieces-stated-numbers-are-checked": ("answers-the-notes", I),
    "a-pieces-figures-are-those-of-its-model": ("answers-the-notes", F),
    "a-beam-is-strong-enough": ("strength", F),
    "a-beam-sags-within-its-limit": ("strength", F),
    "a-part-bends-the-way-its-material-was-tested": ("strength", F),
    "a-piece-takes-its-sideways-load": ("strength", F),
    "a-piece-stands-in-its-stability-cases": ("strength", F),
    "a-piece-is-held-to-what-applies-to-it": ("strength", I),
    "a-load-acts-on-a-part": ("strength", I),
    "a-pieces-parts-are-fixed-or-guided": ("fits-and-moves", F),
    "a-pieces-joints-join-what-is-modelled": ("fits-and-moves", I),
    "a-pieces-parts-fill-their-own-space": ("fits-and-moves", F),
    "a-pieces-front-is-clear-of-what-is-there": ("fits-and-moves", F),
    "a-pieces-motions-are-stated": ("fits-and-moves", I),
    "a-pieces-sliding-parts-are-held": ("fits-and-moves", F),
    "a-pieces-sliding-parts-have-room": ("fits-and-moves", F),
    "a-pieces-turning-parts-are-carried": ("fits-and-moves", F),
    "a-pieces-turning-parts-have-room": ("fits-and-moves", F),
    "a-moving-part-stays-where-its-equation-holds": ("fits-and-moves", F),
    "a-moving-part-has-room-to-move": ("fits-and-moves", F),
    "a-pieces-parts-say-what-they-are-cut-from": ("can-be-made", I),
    "a-pieces-parts-say-how-they-are-cut": ("can-be-made", I),
    "a-pieces-joints-say-what-fastens-them": ("can-be-made", I),
    "a-joined-part-is-thick-enough-for-the-cut": ("can-be-made", F),
    "a-joined-part-is-wide-enough": ("can-be-made", F),
    "a-joint-is-cut-with-a-tool-its-connector-takes": ("can-be-made", I),
    "a-joint-is-cut-at-its-connectors-setting": ("can-be-made", I),
    "a-part-with-cuts-is-cut-with-tools-that-rest-on-clauses": ("can-be-made", I),
    "a-part-is-sawn-with-a-saw-that-states-its-cut": ("can-be-made", I),
    "a-part-is-no-thicker-than-its-saw-cuts": ("can-be-made", F),
    "a-part-is-no-narrower-than-its-saw-cuts": ("can-be-made", F),
    "a-part-is-cut-by-a-saw-that-cuts-its-material": ("can-be-made", F),
    "a-pieces-steps-bring-in-every-part": ("can-be-assembled", I),
    "a-pieces-steps-close-every-joint": ("can-be-assembled", I),
    "a-pieces-parts-reach-their-place": ("can-be-assembled", F),
    "a-step-closes-each-joint-the-way-its-connector-engages": ("can-be-assembled", F),
}

# a rule of the package (not of the standards, whose rules say themselves): what is wrong when it does not
# hold, per language
RED = {
    "a-beam-is-strong-enough": {"en": "A part breaks under the load it carries.",
                                "fr": "Une pièce casse sous la charge qu'elle porte."},
    "a-beam-sags-within-its-limit": {"en": "A part sags more than its limit.",
                                     "fr": "Une pièce fléchit plus que sa limite."},
    "a-part-bends-the-way-its-material-was-tested": {
        "en": "A part spans a way its material's values were not measured in.",
        "fr": "Une pièce porte dans un sens où les valeurs de son matériau n'ont pas été mesurées."},
    "a-piece-takes-its-sideways-load": {"en": "The piece does not take a push from the side.",
                                        "fr": "Le meuble ne tient pas une poussée de côté."},
    "a-piece-stands-in-its-stability-cases": {"en": "The piece tips over where it must stay standing.",
                                              "fr": "Le meuble bascule là où il doit rester debout."},
    "a-piece-is-held-to-what-applies-to-it": {"en": "A requirement that applies to the piece is not checked on it.",
                                              "fr": "Une exigence qui s'applique au meuble n'y est pas vérifiée."},
    "a-load-acts-on-a-part": {"en": "A load does not say which part it acts on.",
                              "fr": "Une charge ne dit pas sur quelle pièce elle s'exerce."},
    "a-moving-part-stays-where-its-equation-holds": {
        "en": "A part's wood moves outside what its movement can be worked out for.",
        "fr": "Le bois d'une pièce travaille hors de ce que son calcul de mouvement couvre."},
    "a-moving-part-has-room-to-move": {"en": "A part has too little room for its wood to swell.",
                                       "fr": "Une pièce n'a pas assez de jeu pour que son bois gonfle."},
    "a-joined-part-is-thick-enough-for-the-cut": {"en": "A joined part is thinner than its connector allows.",
                                                  "fr": "Une pièce assemblée est plus mince que son connecteur ne "
                                                        "le permet."},
    "a-joined-part-is-wide-enough": {"en": "A joined part is narrower than its connector allows.",
                                     "fr": "Une pièce assemblée est plus étroite que son connecteur ne le permet."},
    "a-joint-is-cut-with-a-tool-its-connector-takes": {
        "en": "A joint names no tool its connector's seat can be cut with.",
        "fr": "Un assemblage ne nomme aucun outil qui puisse fraiser le logement de son connecteur."},
    "a-joint-is-cut-at-its-connectors-setting": {
        "en": "A joint does not say the machine setting its connector is cut at.",
        "fr": "Un assemblage ne dit pas le réglage auquel le logement de son connecteur est fraisé."},
    "a-part-with-cuts-is-cut-with-tools-that-rest-on-clauses": {
        "en": "A part's cuts name no tools that say how they are used.",
        "fr": "Les découpes d'une pièce ne nomment pas d'outils qui disent comment s'en servir."},
    "a-part-is-sawn-with-a-saw-that-states-its-cut": {
        "en": "A saw a part is cut with does not state the width its blade takes out.",
        "fr": "Une scie qui coupe une pièce ne dit pas la largeur que sa lame enlève."},
    "a-part-is-no-thicker-than-its-saw-cuts": {"en": "A part is thicker than its saw cuts through.",
                                               "fr": "Une pièce est plus épaisse que ce que sa scie traverse."},
    "a-part-is-no-narrower-than-its-saw-cuts": {"en": "A part is narrower than its saw can cut.",
                                                "fr": "Une pièce est plus étroite que ce que sa scie peut couper."},
    "a-part-is-cut-by-a-saw-that-cuts-its-material": {
        "en": "A part is cut by a saw or a shop that does not cut its material.",
        "fr": "Une pièce est coupée par une scie ou un magasin qui ne coupe pas son matériau."},
    "a-step-closes-each-joint-the-way-its-connector-engages": {
        "en": "A part does not come straight at the connectors it closes.",
        "fr": "Une pièce n'arrive pas droit sur les connecteurs qu'elle ferme."},
}

# a rule of the package whose consequence is fails: what it says when it could not tell, per language
UNSETTLED = {
    "a-beam-is-strong-enough": {"en": "Whether a part takes the load it carries is not known.",
                                "fr": "On ne sait pas si une pièce tient la charge qu'elle porte."},
    "a-beam-sags-within-its-limit": {"en": "Whether a part sags within its limit is not known.",
                                     "fr": "On ne sait pas si une pièce fléchit moins que sa limite."},
    "a-part-bends-the-way-its-material-was-tested": {
        "en": "Whether a part spans the way its material was tested is not known.",
        "fr": "On ne sait pas si une pièce porte dans le sens où son matériau a été testé."},
    "a-piece-takes-its-sideways-load": {"en": "Whether the piece takes a push from the side is not known.",
                                        "fr": "On ne sait pas si le meuble tient une poussée de côté."},
    "a-piece-stands-in-its-stability-cases": {"en": "Whether the piece stays standing is not known.",
                                              "fr": "On ne sait pas si le meuble reste debout."},
    "a-moving-part-stays-where-its-equation-holds": {
        "en": "Whether a part's wood movement can be worked out is not known.",
        "fr": "On ne sait pas si le jeu du bois d'une pièce peut être calculé."},
    "a-moving-part-has-room-to-move": {"en": "Whether a part has room for its wood to swell is not known.",
                                       "fr": "On ne sait pas si une pièce a assez de jeu pour que son bois gonfle."},
    "a-joined-part-is-thick-enough-for-the-cut": {
        "en": "Whether a joined part is thick enough for its connector is not known.",
        "fr": "On ne sait pas si une pièce assemblée est assez épaisse pour son connecteur."},
    "a-joined-part-is-wide-enough": {"en": "Whether a joined part is wide enough for its connector is not known.",
                                     "fr": "On ne sait pas si une pièce assemblée est assez large pour son connecteur."},
    "a-part-is-no-thicker-than-its-saw-cuts": {"en": "Whether its saw cuts through a part is not known.",
                                               "fr": "On ne sait pas si sa scie traverse une pièce."},
    "a-part-is-no-narrower-than-its-saw-cuts": {"en": "Whether its saw can cut a part this narrow is not known.",
                                                "fr": "On ne sait pas si sa scie peut couper une pièce aussi étroite."},
    "a-part-is-cut-by-a-saw-that-cuts-its-material": {
        "en": "Whether its saw cuts a part's material is not known.",
        "fr": "On ne sait pas si sa scie coupe le matériau d'une pièce."},
    "a-step-closes-each-joint-the-way-its-connector-engages": {
        "en": "Whether each part comes straight at its connectors is not known.",
        "fr": "On ne sait pas si chaque pièce arrive droit sur ses connecteurs."},
}


def family(rule: str) -> str | None:
    """The family a rule of the design is in, None for a rule that does not read the design."""
    return RULES[rule][0] if rule in RULES else None


def level(rule: str, settled: bool = True) -> str:
    """How critical `rule` not holding is: its consequence, and may_fail for a rule whose consequence is
    fails that could not tell (settled False). A rule this module does not know is incomplete."""
    consequence = RULES[rule][1] if rule in RULES else I
    return "may_fail" if consequence == F and not settled else consequence


def words(rule: str, settled: bool = True) -> dict | None:
    """What a rule of the package says when it does not hold, per language (when it could not tell, the
    words for that); None for a rule that says itself (a standards rule: its messages red)."""
    return (UNSETTLED.get(rule) if not settled else None) or RED.get(rule)


def order(rule: str, settled: bool = True) -> tuple[int, int, int]:
    """Where a flaw of `rule` comes in a list of them: by level, then by family, then as RULES lists it."""
    levels, families, rules = [lv for lv, _ in LEVELS], [f for f, _ in FAMILIES], list(RULES)
    return (levels.index(level(rule, settled)), families.index(family(rule)) if rule in RULES else len(families),
            rules.index(rule) if rule in RULES else len(rules))
