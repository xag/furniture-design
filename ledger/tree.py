"""The decisions furniture-design is bound by, as a ledger: what the skills and tooling must
and must not do, with the alternatives turned down. Read it with `uv run quern brief .`,
never whole.

Vocabulary: ledger@0.7.0 and grounding@1.2.0, pinned in quern.lock.
"""

from __future__ import annotations

import os
from pathlib import Path

import quern.grounding  # noqa: F401
from quern import Node, Quern
from quern.library import consume


def _alt(id_: str, name: str, why: str) -> Node:
    return Node(id=id_, kind="alternative", name=name, payload={"why": why})


def entries() -> list[Node]:
    return [
        Node(
            id="the-method-is-public-and-names-no-home", kind="decision",
            name="This repo is public and holds only the general method, skills and tooling; it names no home, "
                 "no piece and nobody's furniture. Real furniture lives in its own repo, which pins this one, "
                 "and nothing here refers back to it",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "Would you suggest a public repo with only the tooling and skills, or a private "
                                  "repo with also the content? ... Do it.",
                     "why": "A design is fitted to a survey of a home: room sizes, layout, photos. That stays "
                            "private. The method is the same for every home, so it can be public, and keeping it "
                            "apart is what stops it from quietly coming to depend on one home."},
            children=[
                _alt("one-private-repo-with-everything", "One private repo holding the method and the furniture",
                     "The method ends up written against one home, and nobody else can use it."),
                _alt("one-public-repo-with-everything", "One public repo holding the method and the furniture",
                     "Publishes the survey of a home."),
            ],
        ),
        Node(
            id="a-copyrighted-standard-is-cited-never-copied-here", kind="decision",
            name="A rule taken from a copyrighted standard (EN 14749, EN 16121/16122, ASTM F2057, ANSI/BIFMA X5.9, "
                 "ANSI/AWI 0641) is cited here by number and clause and its text is never committed here; a "
                 "public-domain source (the Wood Handbook FPL-GTR-282, 16 CFR 1261 in the Federal Register) may "
                 "be copied in whole so its quotes can be checked",
            payload={"decided_on": "2026-11-11",
                     "why": "A rule enters from a fetched source quoted verbatim, so a reader can refute it from "
                            "the file. A public repo cannot hold a paywalled text; a private repo that pins this "
                            "one can, and is where such a copy goes."},
            links={"rests_on": ["the-method-is-public-and-names-no-home"]},
            children=[
                _alt("copy-every-source-here", "Keep every source's text here, as for public-domain ones",
                     "Republishes copyrighted standards."),
                _alt("copy-no-source-anywhere", "Cite every source and copy none",
                     "Leaves the quotes behind the paywalled rules uncheckable by anyone who has not bought them."),
            ],
        ),
        Node(
            id="the-rules-read-the-knowledge", kind="decision",
            name="A rule carries no number a source states: every limit, test condition, material property "
                 "and coefficient is a param on a knowledge node (a clause quoted verbatim from a captured "
                 "source, or a material or requirement derived from clauses), and the rule reads it there. "
                 "A new source adds nodes, not kinds or rules",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "Create rules you suggested from public sources and do that by building a smart "
                                  "knowledge base and implement rules on the knowledge with a quern package. Don't "
                                  "hardcode the knowledge base structure from these rules; more will come.",
                     "why": "A number written into a rule hides where it came from and has to be found and edited "
                            "when its source changes; on a node it carries its clause, its unit and its "
                            "derivation, and every check that needs it reads the same one."},
            links={"rests_on": ["a-copyrighted-standard-is-cited-never-copied-here"]},
            children=[
                _alt("constants-in-rules", "Write each limit and test load into the rule that uses it",
                     "The rule then states the source's number without the source, and two rules that need "
                     "it state it twice."),
                _alt("a-table-per-check", "One table per check (a sag table, a tip-over table)",
                     "Shapes the knowledge around the first checks; the next check would need a new table "
                     "for facts the existing ones already hold."),
            ],
        ),
        Node(
            id="a-check-reads-its-requirement-over-its-own-link", kind="decision",
            name="A design names the requirement a check reads over that check's own link (stability_case, "
                 "sag_limit), not over one shared link filtered by a field of the requirement",
            payload={"decided_on": "2026-11-11",
                     "why": "quern's rules evaluate both sides of `or`, and a value a node does not carry is a "
                            "red. A shared link filtered by `measure` makes every check read the params of every "
                            "other check's requirements, and go red on their absence."},
            links={"rests_on": ["the-rules-read-the-knowledge"]},
            children=[
                _alt("one-held-to-link", "One `held_to` link, each rule keeping the requirements whose "
                     "measure it checks",
                     "Reds that mean only that a sag requirement has no tilt block."),
            ],
        ),
        Node(
            id="what-the-grammar-cannot-sum-is-a-calculation-with-cases", kind="decision",
            name="A check that needs more than quern's rule grammar (a sum of products over parts, an opened "
                 "drawer, a tilt) is a furniture/* calculation registered beside its code, with cases worked "
                 "by hand in spec.py that quern's publish gate runs; a check the grammar can state stays a rule",
            payload={"decided_on": "2026-11-11",
                     "why": "The grammar sums one list at a time, so mass times lever arm over the parts of a "
                            "piece has no expression; shelf sag is arithmetic over params and stays a rule."},
            links={"rests_on": ["the-rules-read-the-knowledge"]},
            children=[
                _alt("a-weighted-sum-verb-in-quern", "Add a weighted sum to quern's grammar",
                     "Covers mass times arm, not opening the drawers, tilting the piece or the fill share."),
                _alt("a-wasm-solver", "Ship the calculation as a wasm solver inside the package",
                     "It would travel as data, but needs a toolchain this repo does not have, for a "
                     "calculation every consumer already installs as Python."),
            ],
        ),
        Node(
            id="the-static-margin-predicts-the-stability-tests", kind="hypothesis",
            name="The static moment about the front edge, with every extendible element open and the "
                 "conditions a requirement states, predicts whether a built piece passes ASTM F2057-23's "
                 "stability tests 9.2.1 and 9.2.3",
            payload={"stated_on": "2026-11-11",
                     "basis": "The Federal Register's description of the tests (88 FR 28405): loads, block, "
                              "open elements. Not modelled: doors, the dynamic pull of 9.2.2, the test's own "
                              "procedure, which is ASTM's."},
            links={"rests_on": ["what-the-grammar-cannot-sum-is-a-calculation-with-cases"]},
            children=[
                Node(id="a-built-piece-disagrees", kind="falsification",
                     name="A built piece the calculation passes tips in the physical test, or one it fails "
                          "stands"),
            ],
        ),
        Node(
            id="an-equation-is-applied-only-where-its-source-says-it-holds", kind="decision",
            name="A rule that applies a source's equation also checks the range the source says it holds "
                 "over (Eq. 13-3: 6% to 14% moisture content), with the range as params on the equation's "
                 "clause, and goes red outside it rather than extrapolating",
            payload={"decided_on": "2026-11-11",
                     "why": "A limit the source states is part of what it states; a check that uses the "
                            "equation and drops the limit claims more than the source does, and gives a "
                            "confident number where the source gives none."},
            links={"rests_on": ["the-rules-read-the-knowledge"]},
            children=[
                _alt("apply-everywhere", "Apply the equation to whatever moisture content the climate gives",
                     "At 90% humidity oak settles near 20.5%, and the movement the equation predicts "
                     "there is a number the Handbook does not back."),
            ],
        ),
        Node(
            id="a-copyrighted-source-is-cited-by-locator-and-values", kind="decision",
            name="A clause from a copyrighted source (a maker's page, a paywalled standard) carries its "
                 "locator and the values it states, and no quote; its source records the url and the sha256 "
                 "of what was fetched, and the copy the values can be checked against is kept in a private "
                 "repo. The clause rule accepts a clause without a quote only when its source says "
                 "licence: copyrighted",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "Public, cite without quote",
                     "why": "The values are facts a rule needs; the words are the publisher's. A test holds "
                            "that no clause of a copyrighted source in this repo carries a quote."},
            links={"rests_on": ["a-copyrighted-standard-is-cited-never-copied-here"]},
            children=[
                _alt("private-maker-packages", "Keep a maker's package private, with its quotes",
                     "A collaborator could not sync it from the private registry."),
                _alt("short-quotes-as-facts", "Quote the short specification lines publicly as facts",
                     "Weakens the rule that copyrighted text is never copied in, one line at a time."),
            ],
        ),
        Node(
            id="a-makers-products-are-their-own-package", kind="decision",
            name="Knowledge of one maker's products (Lamello's connectors and machines) is not in "
                 "furniture-design@: it is an unofficial package of its own, which requires furniture-design@ "
                 "and adds that maker's products as data on furniture-design's kinds. furniture-design names "
                 "no maker",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "lamello specific should not be in furniture design package, they should be in "
                                  "a lamello unofficial package.",
                     "why": "furniture-design is the general method. A maker's catalogue changes when the maker "
                            "changes it, its pages are the maker's copyrighted text, and 'unofficial' says the "
                            "maker neither wrote nor endorsed the package."},
            links={"rests_on": ["the-rules-read-the-knowledge"]},
            children=[
                _alt("makers-in-the-knowledge-base", "Add Lamello's connectors to furniture-design's knowledge base",
                     "Ties the general method's releases to one maker's catalogue, and puts a maker's name in a "
                     "package meant for every maker."),
            ],
        ),
        Node(
            id="the-package-is-in-the-open-registry", kind="decision",
            name="furniture-design@ is published to the public registry (xag/quern-registry), not the "
                 "private fleet registry",
            payload={"decided_on": "2026-11-11",
                     "why": "A collaborator on this public repo must be able to pin and sync the package; the "
                            "fleet registry is private."},
            links={"rests_on": ["the-method-is-public-and-names-no-home"]},
            children=[
                _alt("the-fleet-registry", "Publish beside the estate's other packages in xag/fleet-registry",
                     "Nobody outside the owner's account could sync it."),
            ],
        ),
        Node(
            id="a-design-stress-is-the-near-minimum-strength-over-the-handbooks-factor", kind="decision",
            name="A part's bending stress is held to its material's design_bending_stress: the mean modulus "
                 "of rupture the source states, brought down to its 5% exclusion limit as MOR (1 - 1.645 x "
                 "COV) with Table 5-6's coefficient of variation (16%), then divided by the 2.1 the Wood "
                 "Handbook applies for 10-year duration of load and safety (p. 7-10). Every load is treated "
                 "as a 10-year load, a sitter included",
            payload={"decided_on": "2026-11-11",
                     "why": "The Handbook designs to a strength at least 95% of pieces exceed (p. 7-6), then "
                            "divides by 2.1 for duration and safety (p. 7-10), and both are public. ASTM "
                            "D2555's method for the 5% limit is copyrighted and not here, so the limit is "
                            "estimated as the 5% point of a normal distribution. A load that is short is "
                            "carried better than the tables say (p. 5-40), so taking every load as a 10-year "
                            "one errs safe. Panels are given the clear-wood coefficient of variation: the "
                            "Handbook says composites perform more uniformly than solid wood (p. 12-2), so "
                            "the clear-wood spread is the wider one.",
                     "caveat": "The 2.1 was derived for structural lumber. Clear-wood values hold for clear "
                               "boards: a knot in a solid part is not modelled."},
            links={"rests_on": ["the-rules-read-the-knowledge"]},
            children=[
                _alt("a-safety-factor-of-our-own", "Divide the mean strength by a round safety factor",
                     "A number nobody published."),
                _alt("figure-7-9", "Raise the stress for a short load with Figure 7-9",
                     "It is a curve, read by eye; the 10-year factor errs safe without it."),
                _alt("lumber-grade-values", "Use the design values of lumber grades",
                     "Furniture boards are not stress-graded, and those tables are not public."),
            ],
        ),
        Node(
            id="a-material-says-which-way-its-values-were-measured", kind="decision",
            name="A material states the direction its bending values were measured in (measured_along: "
                 "grain, face grain, or unstated), a part that bends states how its grain runs along its "
                 "span (span_along), and the two must match; values whose source does not say which way it "
                 "bent the panel (Table 12-2's plywood, Table 12-1's MDF and particleboard) judge no part's "
                 "bending",
            payload={"decided_on": "2026-11-11",
                     "why": "Plywood is much weaker and less stiff with its face grain across the span, and "
                            "Table 12-2 does not say which way its panels were tested. Table 19-2 does (face "
                            "grain parallel to span), so its yellow birch laminate is the plywood a bending "
                            "check can use until a maker's data sheet says more."},
            links={"rests_on": ["an-equation-is-applied-only-where-its-source-says-it-holds"]},
            children=[
                _alt("assume-along-the-face-grain", "Assume Table 12-2 was measured along the face grain",
                     "The common test, but the table does not say so, and the error would be unsafe."),
            ],
        ),
        Node(
            id="a-panels-tested-modulus-takes-no-shear-term", kind="decision",
            name="Deflection is a calculation (furniture/deflection), not a rule's expression: solid wood "
                 "takes Equation 9-2's bending and shear terms with its shear-corrected modulus, a panel "
                 "whose modulus was measured on the panel (modulus: apparent) takes the bending term alone",
            payload={"decided_on": "2026-11-11",
                     "why": "The Handbook gives no shear modulus for plywood, and a modulus measured by "
                            "bending the panel already holds its shear deflection. Choosing the equation by "
                            "the material needs a branch the rule grammar does not have, which is a "
                            "calculation with cases (what-the-grammar-cannot-sum-is-a-calculation-with-cases)."},
            links={"rests_on": ["what-the-grammar-cannot-sum-is-a-calculation-with-cases"]},
            children=[
                _alt("a-shear-modulus-for-plywood", "Give plywood a shear modulus",
                     "No public source here states one."),
                _alt("two-sag-rules", "One sag rule for solid wood and one for panels",
                     "Each would read a param the other's parts do not carry and answer 'absent' there."),
            ],
        ),
        Node(
            id="a-sideways-push-goes-through-a-panel-across", kind="decision",
            name="A seat is held to the light-service sidethrust of GSA's leg test (890 N across, at seat "
                 "height), and the push must reach the sides through a panel standing in its plane (a "
                 "back): its top-edge connectors take it in shear, each side edge's connectors take it in "
                 "pull-out and the force times height over width in shear, no bearing of one part on "
                 "another credited. A piece with no such panel is short the whole force; a connector not "
                 "rated in the joined material leaves the check absent",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "check the sideway wobble.",
                     "why": "Nothing public here rates how much a knock-down joint resists bending, so a "
                            "box held square only by its corner joints cannot be shown to stand; a panel "
                            "in the plane of the push turns it into forces along the joints, which a "
                            "connector maker does rate. FNAE-80-214A is the only public seating test found "
                            "that states a sideways force; it is written for upholstered sofas and chairs, "
                            "and its licence could not be established, so it is cited by locator and values.",
                     "caveat": "A strength check, not a stiffness one: how far the piece moves under the push "
                               "is not computed, and the sides bending out of their plane on the way to the "
                               "floor are not checked."},
            links={"rests_on": ["the-rules-read-the-knowledge",
                                "what-the-grammar-cannot-sum-is-a-calculation-with-cases"]},
            children=[
                _alt("corner-joint-moments", "Let the corner joints carry the push by resisting bending",
                     "No public source here rates a connector's bending resistance."),
                _alt("credit-bearing", "Credit the panel bearing on the side it is pushed against",
                     "Pushed the other way, the connectors are pulled; the check takes the worse way."),
            ],
        ),
        Node(
            id="a-panel-bent-two-ways-is-two-materials", kind="decision",
            name="A panel used both flat and on its edge is two material nodes naming the same panel "
                 "(same_panel_as), each with the values measured the way it is bent: on edge, the in-plane "
                 "moduli of Table 19-2 (the lower, 8.9 GPa), the species' GLT as in-plane shear modulus, and "
                 "the edgewise compressive strength as the limit of the bending stress",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "We use the same material everywhere.",
                     "why": "A rail or a back is plywood standing on its edge, and its flatwise bending "
                            "values do not describe it. Table 19-2 gives the crossband laminate's strengths "
                            "and moduli edgewise and lengthwise; plies of rotary-cut veneer have their "
                            "annual rings in the plane of the sheet (Table 19-3 footnote b), so the in-plane "
                            "shear modulus is the species' GLT, crossed or not. Of the two edgewise "
                            "strengths, compression (40 MPa) is the lower, so limiting the bending stress "
                            "to it is the safe side."},
            links={"rests_on": ["a-material-says-which-way-its-values-were-measured"]},
            children=[
                _alt("one-material-with-orientation-params", "One material with flat and on-edge params",
                     "Every rule would have to pick the param by orientation; two nodes keep the rules as "
                     "they are."),
            ],
        ),
        Node(
            id="drawings-are-generated-from-the-tree", kind="decision",
            name="A piece's plans, cut list, joint list, 3D views and build document are generated from its "
                 "quern nodes (furniture_design.drawings), the 3D views through geometry@'s renderer; nothing "
                 "is drawn or typed a second time",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "Can you generate 3D views and 2D plans and how to build doc from it?",
                     "why": "A dimension typed into a drawing drifts from the model the rules judged; "
                            "generated, the plans show what was checked."},
            children=[
                _alt("a-cad-file", "Export to a CAD program and draw there",
                     "The drawing would leave the tree the rules judge."),
                _alt("our-own-3d-renderer", "Render 3D in furniture-design",
                     "geometry@ already realizes and renders the same boxes."),
            ],
        ),
        Node(
            id="the-documents-are-for-the-people-who-build", kind="decision",
            name="What a piece is built from is generated from its quern nodes, for the people who build it, "
                 "not for programmers: an interactive 3D view (one HTML page: turn, pull apart, step through "
                 "the assembly, touch a part), a design document (PDF, A3: first-angle views dimensioned, a "
                 "three-quarter view with the part letters, the parts list and one drawing per board with its "
                 "grooves, the checks in plain words, a title block) and picture-first assembly instructions "
                 "(PDF, A4: the boards and hardware, then one picture per step). Nothing is drawn or typed a "
                 "second time",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "Ce n'est pas un MD qu'il faut. On ne parle pas à des informaticiens. "
                                  "Premièrement, je veux une visualisation 3D, pas juste des vues 3D. Ca vient "
                                  "dans furniture design. Deuxièmement, je veux un document de design, dans un "
                                  "format standard, pdf par exemple, avec des vues 2D clean, pro. Enfin, une vue "
                                  "PDF simple comme Ikea, pour le montage",
                     "why": "A dimension typed into a drawing drifts from the model the rules judged; generated, "
                            "the documents show what was checked. Print needs vector line work, so the boxes "
                            "are projected and ordered here (linework.py) and drawn with reportlab."},
            links={"supersedes": ["drawings-are-generated-from-the-tree"]},
            children=[
                _alt("a-cad-file", "Export to a CAD program and draw there",
                     "The drawing would leave the tree the rules judge."),
                _alt("a-markdown-build-document", "A Markdown document with SVG plans and PNG views",
                     "Turned down by the owner: the readers are the people building, not programmers.",),
                _alt("geometry-raster-views", "3D views through geometry@'s PNG renderer",
                     "Raster, coloured by kind, no line work for print, and not interactive."),
            ],
        ),
        Node(
            id="a-brace-passes-the-bend-of-the-sides-below-it", kind="decision",
            name="The sideways check follows the push down to the floor: below a brace that stops above "
                 "the floor, each side bends by F/2 times the brace's height above the floor, and that "
                 "moment passes into the brace as a pair of forces on its outermost side-edge connectors, "
                 "added to their pull-out; the side itself is held to its design bending stress there; a "
                 "side edge with one connector passes no moment, so the piece is short F/2 whatever the "
                 "connector's rating, and that is answered before any missing rating is asked for",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "Le panneau de derrière va beaucoup trop bas, on veut juste une traverse "
                                  "de taille minimum suffisante pour mettre des clamex.",
                     "why": "The first form of the check took a brace's side edges only in pull-out and "
                            "vertical shear, as if the push stopped at the brace: it would have passed a "
                            "75 mm rail held by one connector at each end, which cannot keep a box square. "
                            "The push has to reach the floor, and the sides below the brace carry it there "
                            "in bending."},
            links={"supersedes": ["a-sideways-push-goes-through-a-panel-across"],
                   "rests_on": ["the-rules-read-the-knowledge",
                                "what-the-grammar-cannot-sum-is-a-calculation-with-cases"]},
            children=[
                _alt("brace-as-a-wall-on-a-base", "Keep treating a brace as a wall standing on a base",
                     "A back or a rail between the sides stands on nothing; the sides carry it."),
            ],
        ),
        Node(
            id="the-frame-holds-by-every-joint-between-uprights-and-cross-parts", kind="decision",
            name="A piece takes a sideways push by its braces or by its frame, the better answering: for "
                 "the frame, the check walks the joints and counts every one between an upright (a side) "
                 "and a part across it (top, shelf, rail), each resisting with its connectors' rated "
                 "moment, bent open at one end of a cross part and shut at the other; together they hold "
                 "the top against the sum of those moments over the piece's height. A way that cannot be "
                 "judged leaves the check absent unless the other holds",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "Il y a les contraintes apportées par les autres pièces. La traverse seule "
                                  "ne fait pas tout le job. C'est peut-être un cas de règle qui traversent le "
                                  "graphe",
                     "why": "Counting only braces called a piece short of the whole push the moment it had "
                            "no panel across, as if its other joints did nothing. Every corner joint has to "
                            "turn for the piece to lean, and a published test of the Clamex P-14 as a "
                            "corner joint (Janíková et al. 2025, CC BY) rates how much each resists."},
            links={"rests_on": ["a-brace-passes-the-bend-of-the-sides-below-it"]},
            children=[
                _alt("braces-only", "Count only panels in the plane of the push",
                     "Turned down by the owner: the other parts' joints hold the piece too."),
                _alt("sum-both-ways", "Add the braces' and the frame's resistance",
                     "They stiffen the piece in different ways; the better one alone is the safe side."),
            ],
        ),
        Node(
            id="this-repos-own-work-is-agpl", kind="decision",
            name="This repo's own work is licensed AGPL-3.0-or-later, its copyright held by Xavier Grehant "
                 "and, for the skill menuiserie-conception-meubles-design, by Joohee; a source copied under "
                 "sources/ keeps its own terms. A contribution from anyone else is merged only with an "
                 "agreement that lets the copyright holders license it under other terms as well",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "je pourrais le monétiser via un service hébergé",
                     "why": "Public with no licence, the repo could be read but not lawfully reused. The AGPL "
                            "keeps it open source and obliges anyone who runs a modified copy as a service "
                            "to publish their code, so nobody can host it closed against the owner's hosted "
                            "service; the copyright holders are not bound by their own licence and may "
                            "still sell other terms. That freedom lasts only while they hold the copyright "
                            "of everything here, hence the agreement on outside contributions."},
            links={"rests_on": ["the-method-is-public-and-names-no-home"]},
            children=[
                _alt("apache-2.0", "Apache-2.0, as quern is",
                     "Lets anyone host it in a closed paid service."),
                _alt("source-available", "A source-available licence (FSL, BSL)",
                     "Not open source until it converts, and a reader cannot tell what they may do."),
                _alt("non-commercial", "A non-commercial licence",
                     "Would forbid a maker to sell a piece designed with it."),
            ],
        ),
        Node(
            id="the-skill-holds-only-the-conversation", kind="decision",
            name="The skill menuiserie-conception-meubles-design leads the conversation with a beginner (use, "
                 "space, tools, concept, plain-words verdicts, assembly) and links to the repo's tools; it "
                 "holds no check, no calculator and no instruction to draw or type a plan, a cut list or "
                 "assembly steps, which the rules and documents() produce",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "réduis la skill à la partie conversation et mets les liens vers les outils du repo",
                     "why": "Its geometry checklist and cabinet calculator repeated what the model and "
                            "cut_list do, and its delivery step had the agent write by hand the documents "
                            "documents() generates."},
            links={"rests_on": ["the-documents-are-for-the-people-who-build"]},
            children=[
                _alt("delete-the-skill", "Delete the skill",
                     "The conversation with a beginner (what to ask, how to explain a red rule) is in no tool."),
            ],
        ),
        Node(
            id="the-code-is-agpl-and-the-knowledge-odbl", kind="decision",
            name="The code is licensed AGPL-3.0-or-later and the knowledge base, the database knowledge() "
                 "returns, ODbL-1.0; a contribution is merged only once its author grants the "
                 "maintainer the right to license it under other terms as well (CONTRIBUTING.md)",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "il faut que ça reste élégant et standard pour ne pas perdre la confiance "
                                  "des utilisateurs et contributeurs",
                     "why": "The AGPL is a copyright licence, and the values in the base are facts copyright "
                            "does not cover. The ODbL rests on copyright, the database right and a contract "
                            "(section 2.1): a database derived from this one and used publicly must stay "
                            "under the ODbL (4.4), and so must one behind an app (4.6). A package independent "
                            "of the base, loaded beside it unmodified, is a Collective Database it does not "
                            "reach; that is the line standard licences draw, and the owner's own private "
                            "packages sit on the same side of it."},
            links={"supersedes": ["this-repos-own-work-is-agpl"]},
            children=[
                _alt("agpl-for-everything", "Keep the AGPL on the data too",
                     "It leaves the values and the database right uncovered."),
                _alt("a-licence-of-our-own", "Write a licence that also reaches independent packages, as the SSPL does",
                     "Not standard; the owner wants to keep users' and contributors' trust."),
                _alt("cc-by-sa", "CC BY-SA 4.0 for the data",
                     "It has no clause making an app publish the database behind it."),
            ],
        ),
        Node(
            id="only-the-owner-earns-from-the-knowledge", kind="decision",
            name="The knowledge base, the database knowledge() returns, is licensed CC BY-NC-SA 4.0 with one "
                 "added permission (designing, building and selling furniture with it); any other commercial "
                 "use of the data needs a commercial licence from the copyright holder. The code stays "
                 "AGPL-3.0-or-later",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "Je voudrais être le seul à pouvoir gagner de l'argent avec ces données",
                     "why": "Under the ODbL anyone could sell an app on the data once they published the "
                            "database behind it. CC BY-NC-SA 4.0 is a standard licence that also licenses "
                            "database rights (section 4) for non-commercial use only, and lets the licensor "
                            "offer separate terms (6(c)): commercial licences, and the added permission "
                            "for makers. Single values a reader takes from the base are facts and stay "
                            "outside any licence; extracting a substantial part is not."},
            links={"supersedes": ["the-code-is-agpl-and-the-knowledge-odbl"]},
            children=[
                _alt("keep-the-odbl", "Keep the ODbL",
                     "Lets anyone earn from the data once they publish their derived database."),
                _alt("no-maker-permission", "CC BY-NC-SA with no added permission",
                     "Leaves a maker who sells a piece designed with it unsure they may."),
            ],
        ),
        Node(
            id="a-dimension-is-stated-once-and-parts-follow-it", kind="decision",
            name="Each entry of a part's size, position and cuts is a number or an expression in "
                 "quern's rule grammar over params, the part's own and then those of the parts and "
                 "piece holding it, nearest first; a piece states a dimension once as a param and "
                 "every part that depends on it is written in terms of it. A design is data, not a "
                 "program that computes its numbers",
            payload={"decided_on": "2026-11-11",
                     "the_owner": "3 est-il une bonne pratique? ... et les autres points?",
                     "why": "The shoe bench was a Python file that computed each part's size and "
                            "place from constants: every number lived in the code and again in the "
                            "nodes, and the app that edits it had to run the code an assistant "
                            "wrote. A part could only name its own params, and a position took "
                            "numbers only, so a stored tree would have had to write every derived "
                            "number down. quern's grammar already evaluates arithmetic over names, "
                            "safely."},
            links={"rests_on": ["the-documents-are-for-the-people-who-build"]},
            children=[
                _alt("a-program-per-design", "Keep writing a design as Python that builds its nodes",
                     "Each number is written twice, and editing a design means running code."),
                _alt("own-params-only", "Let a size name only the part's own params",
                     "A position derived from the piece's dimensions still has to be computed elsewhere."),
                _alt("mates-and-a-solver", "Place parts by constraints between them (mates) and a solver",
                     "Far more than boxes placed in one frame need."),
            ],
        ),
    ]


def build() -> Quern:
    root = Path(__file__).resolve().parents[1]
    lib, refs = consume(root, os.environ.get("QUERN_REGISTRY", root.parent / "quern-registry"))
    quern = Quern(packages=list(refs))
    quern = lib.effective(quern)
    quern.root.children = entries()
    return quern
