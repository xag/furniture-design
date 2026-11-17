"""What furniture-standards@ says to people, per language.

A criterion and a level say their name (payload say: {language: name}); a rule says what is wrong
when it does not hold (messages: {language: {"red": sentence}}, quern's messages). They are for the
person who looks at a certificate, in the language their piece is made in; a rule's description
stays what it tells whoever must put it right. A rule that waits on what only the person knows also
says the question to put to them (messages ask), and, when the person's tools answer it, which of
them do (messages offers: the payload key a tool states when it answers, the same in every language,
as saw_kind for what cuts a part). Whoever shows a certificate reads these and writes no word of its
own, and offers as answers only the tools that state that key, none when the rule names none.
"""
from __future__ import annotations

# criterion or level id -> its name, per language
SAY = {
    "tool-is-identified": {"en": "The tool names its maker and the clauses it is read from",
                           "fr": "L'outil nomme son fabricant et les passages d'où il est lu"},
    "tool-is-drawn": {"en": "The tool has a model that draws", "fr": "L'outil a un modèle qui se dessine"},
    "tool-drawing-is-true": {"en": "The model shows the tool's figures",
                             "fr": "Le modèle montre les cotes de l'outil"},
    "tool-is-said": {"en": "The tool says its name and method in every language",
                     "fr": "L'outil dit son nom et sa méthode dans chaque langue"},
    "saw-states-its-cut": {"en": "A saw states its cut and its depth",
                           "fr": "Une scie donne son trait et sa profondeur de coupe"},
    "tool-figures-are-consistent": {"en": "The tool's figures do not contradict each other",
                                    "fr": "Les chiffres de l'outil ne se contredisent pas"},
    "tool-figures-are-observed": {"en": "Every figure was found printed in a document",
                                  "fr": "Chaque chiffre a été trouvé imprimé dans un document"},
    "tool-figures-are-closed": {"en": "Every figure rests on two observations that agree",
                                "fr": "Chaque chiffre repose sur deux observations qui concordent"},
    "tool-listed": {"en": "Shown, drawn, in a person's tools", "fr": "Montré, dessiné, parmi les outils d'une personne"},
    "tool-cuts-parts": {"en": "Its figures are read by a piece's checks",
                        "fr": "Ses chiffres servent aux vérifications d'un meuble"},
    "tool-in-instructions": {"en": "Drawn at work in assembly instructions",
                             "fr": "Dessiné à l'œuvre dans une notice de montage"},
    "tool-shared": {"en": "Taken into the shared packages", "fr": "Repris dans les paquets partagés"},
    "piece-is-explained": {"en": "Every sentence of the piece's purpose is answered by a decision that names what "
                                 "realises it",
                           "fr": "Chaque phrase de ce qu'on attend du meuble a sa décision, qui nomme ce qui la réalise"},
    "piece-agrees-with-its-ledger": {"en": "The model gives the numbers the piece's ledger states",
                                     "fr": "Le modèle donne les chiffres que le registre du meuble énonce"},
    "piece-holds-together": {"en": "Every part is fixed by a joint or moved by a motion",
                             "fr": "Chaque pièce est fixée par un assemblage ou portée par un mouvement"},
    "piece-mechanisms-work": {"en": "What slides is held on both sides, what turns is carried, and each has room "
                                    "along its travel",
                              "fr": "Ce qui coulisse est tenu des deux côtés, ce qui pivote est porté, et chacun a "
                                    "la place de sa course"},
    "piece-steps-build-it": {"en": "The assembly steps bring in every part and close every joint, each once its "
                                   "parts are in",
                             "fr": "Les étapes de montage amènent chaque pièce et ferment chaque assemblage, une "
                                   "fois ses pièces en place"},
    "piece-can-be-made": {"en": "Every part says what it is cut from and with, and every joint what fastens it and "
                                "how many",
                          "fr": "Chaque pièce dit dans quoi et avec quoi elle est coupée, et chaque assemblage ce "
                                "qui le fixe et en quel nombre"},
    "piece-buildable": {"en": "It can be cut and fastened from what it states",
                        "fr": "Il peut être coupé et fixé d'après ce qu'il énonce"},
    "piece-saws-are-certified": {"en": "Every saw a part is cut with may have its figures read by the piece's checks",
                                 "fr": "Chaque scie qui coupe une pièce a des chiffres que les vérifications du meuble "
                                       "peuvent lire"},
    "pages-are-drawn-not-written": {"en": "No page of the instructions says in a sentence what it could draw",
                                    "fr": "Aucune page de la notice ne dit en phrase ce qu'elle pourrait dessiner"},
    "steps-show-how-parts-attach": {"en": "Each step attaches one kind of part, drawn apart with a line to where it "
                                          "goes, and shows what fastens each joint it closes",
                                    "fr": "Chaque étape pose un seul type de pièce, dessiné à l'écart avec un trait "
                                          "vers sa place, et montre ce qui fixe chaque assemblage qu'elle ferme"},
    "steps-show-their-parts": {"en": "Each step's picture shows the parts it brings in, and enough of those already "
                                     "there to place them",
                               "fr": "L'image de chaque étape montre les pièces qu'elle amène, et assez de celles "
                                     "déjà en place pour les situer"},
    "piece-settled": {"en": "Its design says what the person asked for",
                      "fr": "Sa conception dit ce que la personne a demandé"},
    "piece-works": {"en": "It holds together and what moves in it works",
                    "fr": "Il tient ensemble et ce qui y bouge fonctionne"},
    "piece-instructions": {"en": "Its assembly instructions are shown", "fr": "Sa notice de montage est montrée"},
}

# rule name -> what is wrong when it does not hold, per language
RED = {
    "a-criterion-measures-one-of-the-four-qualities": {
        "en": "This criterion measures neither completeness, reliability, consistency nor presentation.",
        "fr": "Ce critère ne mesure ni la complétude, ni la fiabilité, ni la cohérence, ni la présentation."},
    "a-tool-names-its-maker": {"en": "The tool's maker is not named.", "fr": "Le fabricant de l'outil n'est pas nommé."},
    "a-tool-rests-on-clauses": {
        "en": "The tool is read from no passage of its maker's documents.",
        "fr": "L'outil n'est lu d'aucun passage des documents de son fabricant."},
    "a-tool-says-itself-in-every-language": {
        "en": "The tool's name and method are missing in a language the documents are written in.",
        "fr": "Le nom et la méthode de l'outil manquent dans une langue des documents."},
    "a-tool-has-a-model-that-draws": {
        "en": "The tool has no model it can be drawn from.",
        "fr": "L'outil n'a pas de modèle d'après lequel le dessiner."},
    "a-tools-model-shows-its-figures": {
        "en": "The tool's model does not show its figures, or shows one at another size.",
        "fr": "Le modèle de l'outil ne montre pas ses cotes, ou en montre une à une autre taille."},
    "a-tools-figures-are-in-order": {
        "en": "Two of the tool's figures contradict each other.",
        "fr": "Deux chiffres de l'outil se contredisent."},
    "a-tools-figures-each-rest-on-an-observation": {
        "en": "A figure of the tool was not found printed in a document.",
        "fr": "Un chiffre de l'outil n'a été trouvé imprimé dans aucun document."},
    "a-tools-figures-each-rest-on-two-observations": {
        "en": "A figure of the tool rests on one observation only.",
        "fr": "Un chiffre de l'outil ne repose que sur une seule observation."},
    "a-tools-figures-agree-with-what-they-are-read-from": {
        "en": "A figure of the tool differs from the value it is read from.",
        "fr": "Un chiffre de l'outil diffère de la valeur d'où il est lu."},
    "a-saw-states-its-cut": {"en": "The saw does not state the cut of its blade.",
                             "fr": "La scie ne donne pas le trait de sa lame."},
    "a-saw-states-its-depth": {"en": "The saw does not state the thickest board it cuts.",
                               "fr": "La scie ne donne pas l'épaisseur maximale qu'elle coupe."},
    "a-pieces-purpose-is-answered": {
        "en": "A sentence of what the piece is for is answered by no decision.",
        "fr": "Une phrase de ce qu'on attend du meuble n'a pas de décision qui y réponde."},
    "a-pieces-decisions-name-what-realises-them": {
        "en": "A decision does not name the parts, joints or motions that realise it.",
        "fr": "Une décision ne nomme pas les pièces, assemblages ou mouvements qui la réalisent."},
    "a-pieces-stated-numbers-are-checked": {
        "en": "A quantity the ledger states in words is compared with nothing in the model.",
        "fr": "Une quantité que le registre énonce en toutes lettres n'est comparée à rien dans le modèle."},
    "a-pieces-figures-are-those-of-its-model": {
        "en": "The model does not give a number the ledger states.",
        "fr": "Le modèle ne donne pas un chiffre que le registre énonce."},
    "a-pieces-parts-are-fixed-or-guided": {
        "en": "A part is neither fixed by a joint nor moved by a motion.",
        "fr": "Une pièce n'est ni fixée par un assemblage ni portée par un mouvement."},
    "a-pieces-motions-are-stated": {
        "en": "A motion does not say its axis, its travel, its pivot, what moves or what guides it.",
        "fr": "Un mouvement ne dit pas son axe, sa course, son pivot, ce qui bouge ou ce qui le guide."},
    "a-pieces-turning-parts-are-carried": {
        "en": "A turning part turns about a line that is not on it, or not on what carries it.",
        "fr": "Une pièce qui pivote tourne autour d'une ligne qui n'est pas sur elle, ou pas sur ce qui la porte."},
    "a-pieces-turning-parts-have-room": {
        "en": "A turning part crosses another part as it turns.",
        "fr": "Une pièce qui pivote en traverse une autre en tournant."},
    "a-pieces-sliding-parts-are-held": {
        "en": "A sliding part is not held on both sides by what guides it.",
        "fr": "Une pièce qui coulisse n'est pas tenue des deux côtés par ce qui la guide."},
    "a-pieces-sliding-parts-have-room": {
        "en": "A sliding part crosses another part along its travel.",
        "fr": "Une pièce qui coulisse en traverse une autre le long de sa course."},
    "a-pieces-steps-bring-in-every-part": {
        "en": "A part is brought in by no assembly step.",
        "fr": "Une pièce n'est amenée par aucune étape de montage."},
    "a-pieces-steps-close-every-joint": {
        "en": "A joint is closed by no step, or before the parts it joins are in.",
        "fr": "Un assemblage n'est fermé par aucune étape, ou avant que ses pièces soient en place."},
    "a-pieces-parts-say-what-they-are-cut-from": {
        "en": "A part does not say what it is cut from.",
        "fr": "Une pièce ne dit pas dans quoi elle est coupée."},
    "a-pieces-parts-say-how-they-are-cut": {
        "en": "A part does not say what cuts it out.",
        "fr": "Une pièce ne dit pas avec quoi elle est coupée."},
    "a-pieces-saws-are-certified-to-cut-parts": {
        "en": "A part is cut with a saw or a shop whose figures were only said, not found printed.",
        "fr": "Une pièce est coupée avec une scie ou un magasin dont les chiffres ont seulement été dits, pas "
              "trouvés imprimés."},
    "a-pieces-joints-say-what-fastens-them": {
        "en": "A joint does not say what fastens it, or how many it takes.",
        "fr": "Un assemblage ne dit pas ce qui le fixe, ou combien il en faut."},
    "a-pieces-pages-carry-no-sentence": {
        "en": "A page of the instructions says in words what it should draw.",
        "fr": "Une page de la notice dit en mots ce qu'elle devrait dessiner."},
    "a-pieces-steps-attach-one-kind-of-part": {
        "en": "A step brings in parts of several kinds at once.",
        "fr": "Une étape amène des pièces de plusieurs types à la fois."},
    "a-pieces-new-parts-are-drawn-apart-with-a-line": {
        "en": "A part is drawn in place, with no line showing where it comes from.",
        "fr": "Une pièce est dessinée en place, sans trait qui montre d'où elle vient."},
    "a-pieces-fastenings-are-shown": {
        "en": "A step closes a joint and draws nothing of what fastens it.",
        "fr": "Une étape ferme un assemblage sans rien dessiner de ce qui le fixe."},
    "a-pieces-new-parts-are-visible": {
        "en": "A part a step brings in is hidden behind another.",
        "fr": "Une pièce qu'une étape amène est cachée derrière une autre."},
    "a-pieces-steps-keep-their-context": {
        "en": "The parts a step brings in hide those they attach to.",
        "fr": "Les pièces qu'une étape amène cachent celles auxquelles elles se fixent."},
}


# rule name -> the question it puts to the person, per language: only a rule that waits on what the
# person alone knows (what they buy, what they cut and fasten with) asks, each rule one thing, so a
# question is put only when that thing is missing; whoever shows a certificate
# puts the question to them, and what the others need is work for whoever edits the model

# rule name -> which of the person's tools answer its question: the payload key such a tool states. What
# cuts a part out is a saw (sawn_with), so only the person's saws answer what they cut with; nothing
# the person holds as a tool fastens a joint (a connector, screws, a glue do), so that question takes none
OFFERS = {"a-pieces-parts-say-how-they-are-cut": "saw_kind"}

ASK = {
    "a-pieces-parts-say-what-they-are-cut-from": {
        "en": "Which boards do you buy?",
        "fr": "Quelles planches achetez-vous\u00a0?"},
    "a-pieces-parts-say-how-they-are-cut": {
        "en": "What do you cut the boards with, or which shop cuts them?",
        "fr": "Avec quoi coupez-vous les planches, ou quel magasin les coupe\u00a0?"},
    "a-pieces-joints-say-what-fastens-them": {
        "en": "What do you fasten the parts together with?",
        "fr": "Avec quoi fixez-vous les pièces entre elles\u00a0?"},
}


def messages(rule: str) -> dict:
    return {lang: {"red": text} | ({"ask": ASK[rule][lang]} if rule in ASK else {})
            | ({"offers": OFFERS[rule]} if rule in OFFERS else {})
            for lang, text in RED[rule].items()}
