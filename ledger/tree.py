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
            id="makers-products-are-outside-furniture-design", kind="decision",
            name="Knowledge of makers' products is not in furniture-design@: it is in unofficial packages that "
                 "require furniture-design@ and add the products as data on its kinds, one per maker "
                 "(lamello-unofficial) or one for the makers of one kind of product (wood-panels-unofficial, with "
                 "the standard classes their boards declare). furniture-design names no maker",
            payload={"decided_on": "2026-11-13",
                     "the_owner": "We need to keep the makers too but not necessarily as specific packages.",
                     "why": "furniture-design is the general method, and a maker's catalogue changes when the maker "
                            "changes it. Panel makers declare the same classes, and one package per maker would be "
                            "fourteen packages of a few declarations each, all needing those classes."},
            links={"supersedes": ["a-makers-products-are-their-own-package"],
                   "rests_on": ["the-rules-read-the-knowledge"]},
            children=[
                _alt("always-a-package-per-maker", "Keep one package per maker for panels too",
                     "Fourteen packages for a few declarations each, all needing the same classes."),
            ],
        ),
        Node(
            id="makers-products-are-in-packages-outside-furniture-design", kind="decision",
            name="Knowledge of makers' products is not in furniture-design@: it is in packages that require "
                 "furniture-design@ and add the products as data on its kinds, one per maker (lamello-unofficial) "
                 "or one for the makers of one kind of product (wood-panels, with the standard classes their "
                 "boards declare). furniture-design names no maker",
            payload={"decided_on": "2026-11-13",
                     "the_owner": "Why unofficial on wood panels?",
                     "why": "The same claim as before without 'unofficial packages': whether a package's name says "
                            "unofficial is a-name-says-unofficial-only-when-it-names-a-maker-or-shop's to settle."},
            links={"supersedes": ["makers-products-are-outside-furniture-design"],
                   "rests_on": ["the-rules-read-the-knowledge"]},
            children=[
                _alt("always-a-package-per-maker", "Keep one package per maker for panels too",
                     "Fourteen packages for a few declarations each, all needing the same classes."),
            ],
        ),
        Node(
            id="a-name-says-unofficial-only-when-it-names-a-maker-or-shop", kind="decision",
            name="A package of makers' or shops' data is named <name>-unofficial when its name is a maker's or a "
                 "shop's (lamello-unofficial, leroy-merlin-unofficial), and without the suffix when its name is "
                 "a kind of product (wood-panels); its README says in either case that the makers did not write "
                 "or endorse it",
            payload={"decided_on": "2026-11-13",
                     "the_owner": "Why unofficial on wood panels?",
                     "why": "The suffix stops a package named after a maker or a shop being taken for that maker's "
                            "or shop's own (a-makers-products-are-their-own-package). A name like wood-panels "
                            "names no one, so the suffix says nothing; the README's disclaimer covers the makers' "
                            "data inside."},
            links={"rests_on": ["makers-products-are-in-packages-outside-furniture-design"]},
            children=[
                _alt("unofficial-on-every-package", "Name every package of makers' data <name>-unofficial",
                     "On a name that names no maker or shop it says nothing a reader could have got wrong."),
                _alt("never-unofficial", "Drop the suffix everywhere and rely on the README",
                     "lamello would read as Lamello's own package wherever only its name is seen: a pin, a "
                     "dependency list, a search result."),
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
            id="a-stated-strength-is-read-the-way-its-source-labels-it", kind="decision",
            name="A panel maker's bending strength is read the way its document labels it: a characteristic "
                 "value (a 5th percentile, as EN 12369-1 gives it) is the near-minimum and only takes the "
                 "Handbook's 2.1; a mean, a value printed as a lower bound on a mean, and a value whose "
                 "document says neither are read as a mean and brought down with Table 5-6's coefficient of "
                 "variation first. A panel tested flat states which way it bent: face grain, flat; across "
                 "face grain, flat; major axis, flat; minor axis, flat; or flat for a board with no grain in "
                 "its plane",
            payload={"decided_on": "2026-11-12",
                     "the_owner": "we're going to choose the wood at leroy merlin. Make sure we have all the "
                                  "knowledge in the quern tree about every type of wood panels that can be "
                                  "found there",
                     "why": "The makers of the panels on sale publish their values in Declarations of "
                            "Performance and data sheets that label them differently: OSB/3 declarations give "
                            "EN 12369-1's characteristic strengths, Finsa heads its tables 'average values' and "
                            "prints '≥ 11', Valchromat and Betanzos print bare numbers. Reading a mean as a "
                            "5th percentile would overstate the board by about a third (1 − 1.645 × 0.16); "
                            "reading a 5th percentile as a mean only understates it. A board with no grain "
                            "(particleboard, MDF, hardboard) bends the same either way in its plane, and EN 310 "
                            "tests it flat, so `flat` is what its part spans as."},
            links={"rests_on": ["a-design-stress-is-the-near-minimum-strength-over-the-handbooks-factor",
                                "a-material-says-which-way-its-values-were-measured"]},
            children=[
                _alt("every-value-a-mean", "Read every stated value as a mean, characteristic ones included",
                     "Takes a third off strengths that are already near-minimum, so OSB would be judged weaker "
                     "than its maker declares for no reason a source gives."),
                _alt("unlabelled-as-near-minimum", "Read an unlabelled value as a near-minimum, the way the EN "
                     "product standards set their requirements",
                     "The standards are not here to say so, and the side it errs on is the unsafe one."),
            ],
        ),
        Node(
            id="a-european-species-is-read-from-tropix", kind="decision",
            name="The clear-wood values of a species sold in Europe (oak, beech, fir, spruce, Scots and maritime "
                 "pine, ash, robinia, Acacia mangium, teak, okoumé, poplar, Eucalyptus grandis) come from its "
                 "CIRAD Tropix sheet, "
                 "its means at 12% moisture content; black alder, which Tropix lacks, from LWF Wissen 42's "
                 "ranges, the low end of each; shrinkage per percent of moisture from LWF Wissen 42's Tab. 3 "
                 "where it gives the species, and from nowhere where it does not",
            payload={"decided_on": "2026-11-12",
                     "the_owner": "Make sure we have all the knowledge in the quern tree about every type of "
                                  "wood panels that can be found there",
                     "why": "The Wood Handbook gives the North American species (yellow birch, northern red "
                            "oak) and, of the European woods sold as glued boards, only teak and okoumé, from "
                            "world literature. Tropix gives every one but alder from one publisher, one table "
                            "and one moisture content. Its sheets give shrinkage as totals and a volumetric "
                            "coefficient, not the radial and tangential coefficients the movement rule reads, "
                            "and turning a total into a coefficient would need a fibre saturation point no "
                            "source here states."},
            links={"rests_on": ["the-rules-read-the-knowledge", "a-copyrighted-source-is-cited-by-locator-and-values"]},
            meta={"amended": "441e2122ff04 Eucalyptus grandis added to the species named; the rule is the "
                             "same and covers it"},
            children=[
                _alt("north-american-relatives", "Use the Handbook's American relatives (American beech, white "
                     "oak) for the European species", "Another species, with other values."),
                _alt("shrinkage-from-totals", "Derive a per-percent coefficient from Tropix's total shrinkage "
                     "over an assumed fibre saturation point", "The 30% it would need is assumed, not stated."),
            ],
        ),
        Node(
            id="a-species-mean-modulus-is-taken-as-apparent", kind="decision",
            name="A species' longitudinal modulus whose source names no test method is divided by 1.1 (Table "
                 "5-3a footnote c's shear correction) and used as an apparent modulus, with no shear term",
            payload={"decided_on": "2026-11-12",
                     "why": "Tropix's sheets say the modulus is a mean at 12% and nothing of how it was "
                            "measured. If it was measured on a center-loaded beam it is already apparent and "
                            "dividing by 1.1 understates it; if it is a true modulus, over 1.1 it is the "
                            "apparent one of footnote c's 14-to-1 beam. Either way the part is judged no "
                            "stiffer than it is, and no shear modulus is needed, which Tropix does not give."},
            links={"rests_on": ["a-panels-tested-modulus-takes-no-shear-term", "a-european-species-is-read-from-tropix"]},
            children=[
                _alt("as-true-with-handbook-ratios", "Read it as true and add a shear term with the Handbook's "
                     "GLR/EL of a related species", "Borrows another species' ratio for a correction of a "
                     "few percent."),
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
        Node(
            id="a-cut-is-explained-from-its-shape-and-its-tools-clauses", kind="decision",
            name="How a part's cut is made is never typed into a piece. The documents read it: where "
                 "to mark it, measured from the edges the cut touches, and which saw lines make it in "
                 "which order, from the cut's box against its board; how each tool is used, from the "
                 "tools the part links made_with, each saying it in sentences that rest on clauses "
                 "(a rule refuses a part with cuts and no such tool). The kind of cut (notch, slot, "
                 "cutout, rebate) is read from the geometry and stored nowhere",
            payload={"decided_on": "2026-11-12",
                     "the_owner": "we should add in the instructions how to cut the part for the "
                                  "plinthe. How should that go in a generic way ... Are we defining new "
                                  "terms for cutting out pieces? ... ok great",
                     "why": "The shoe bench's cutting step was a sentence typed in the piece that said "
                            "where the notch was and repeated two of its params, and nothing said how "
                            "to cut it. The package's part kind did not mention cuts at all, so no rule "
                            "could reach one and an assistant reading the vocabulary could not learn "
                            "of them. The joint already names the tools it is cut with; a part's cut "
                            "follows it, and the knowledge base gains the hand tools and the public "
                            "manuals (TM 9-243, FM 5-426) that say how they are used."},
            links={"rests_on": ["the-documents-are-for-the-people-who-build",
                                "a-dimension-is-stated-once-and-parts-follow-it"]},
            children=[
                _alt("typed-per-piece", "Keep the cutting instructions as text in each piece",
                     "Every piece types the same method again, its numbers drift from its params, "
                     "and nothing says where the method comes from."),
                _alt("store-the-kind-of-cut", "Store the kind of cut (notch, slot, cutout, rebate) "
                     "on each cut, with a method per kind",
                     "The box already says it; a stored kind can disagree with the box, and it adds "
                     "terms to the vocabulary that nothing needs."),
                _alt("a-cut-kind", "A new kind for a cut, beside part and joint",
                     "A cut is part of one board's shape and has no links of its own to carry; the "
                     "tools it needs hang off the part as a joint's hang off the joint."),
            ],
        ),
        Node(
            id="the-knowledge-is-shared-unchanged-and-improved-only-here", kind="decision",
            name="The knowledge base, the database knowledge() returns, is licensed CC BY-NC-ND 4.0 with one "
                 "added permission (designing, building and selling furniture with it): anyone may use it and "
                 "share it unchanged for a non-commercial purpose, and adapt it for their own use, but no "
                 "adapted version and no database built on a substantial part of it may be shared, so an "
                 "improvement is published here, under the contributor agreement, or not at all. Commercial use "
                 "needs a commercial licence. The code stays AGPL-3.0-or-later",
            payload={"decided_on": "2026-11-12",
                     "the_owner": "je pense que j'ai intérêt à laisser ouvert, et à interdire de dupliquer le "
                                  "contenu ... c'est exactement ce qu'il faut",
                     "why": "Under CC BY-NC-SA a copy could grow on its own, with people contributing to it "
                            "under terms that give the owner no commercial right to what they add. CC BY-NC-ND "
                            "4.0 lets copies be shared but never an adapted one (2(a)(1), 3(a)), and treats a "
                            "database holding a substantial part of this one as adapted (4(b)). Keeping the base "
                            "open is what draws people to use and improve it; closing it would leave nobody "
                            "building on it."},
            links={"supersedes": ["only-the-owner-earns-from-the-knowledge"]},
            children=[
                _alt("keep-share-alike", "Keep CC BY-NC-SA",
                     "A copy could grow elsewhere, and what people add there could not be sold by the owner."),
                _alt("close-the-base", "Move the base to a private repo and take contributions through a platform",
                     "Turned down by the owner: people would neither build on it nor improve it."),
                _alt("no-redistribution", "A licence that forbids sharing even unchanged copies",
                     "No standard licence does, GitHub lets anyone fork a public repo, and an unchanged copy "
                     "cannot grow."),
            ],
        ),
        Node(
            id="a-document-is-one-source-in-the-tree", kind="decision",
            name="A document is one source node in the tree a design mounts: when two packages read the same "
                 "document, the more general one holds it, with every clause either reads, and the other links "
                 "to its clauses (EN 1995-1-1's creep factors kdef, Table 9.1 of Swedish Wood's Design of timber "
                 "structures Vol. 2, are clauses of furniture-design's source, which wood-panels reads)",
            payload={"decided_on": "2026-11-13",
                     "the_owner": "Now source lots of data from authoritative sources to answer any relevant "
                                  "question about the bench for any choice of wood panel",
                     "why": "Two packages that each define a source by the same id are refused when their knowledge "
                            "is merged; under two ids, one book reads as two sources and its clauses split "
                            "between them, so a reader asking what the book says finds half of it."},
            children=[
                _alt("each-package-its-own-copy", "Each package keeps its own source node for the document, under "
                     "its own id", "The same book twice, each with part of what it says."),
                _alt("merge-same-id", "Let the merge join two packages' nodes of the same id",
                     "A clause could then be changed by a package that does not own it, and a clash between two "
                     "definitions would pass silently."),
            ],
        ),
        Node(
            id="a-published-sag-limit-is-a-source-a-piece-chooses-from", kind="decision",
            name="A published limit on how far a shelf, a beam or a seat may sag is a clause under its "
                 "source, never a requirement every part is held to: a piece that wants one authors its own "
                 "requirement (measure longtime_sag, param limit in mm) per the clause it chooses. Every "
                 "limit found is kept, one clause each, saying what it applies to, under which load, for "
                 "how long, and whether the deflection is initial, measured after that time or final",
            payload={"decided_on": "2026-11-13",
                     "why": "None of the limits found is written for the seats and shelves of a home: EN "
                            "16121 is for non-domestic storage furniture, UNI 11663 for domestic storage "
                            "units in Italy, KCMA A161.1 for kitchen cabinets, the AWS for architectural "
                            "casework, SEFA 8-PL for laboratory casework, NIH for laboratory wall shelving, "
                            "GSA for metal library shelves, ICC 300 for bleachers, Eurocode 5 for timber "
                            "structures, CPA and EWPAA for panel shelving. They run from span/144 to "
                            "span/500, under loads from 0.7 to 2.0 kg/dm2, measured at once, after ten "
                            "minutes, after a week or at the end of a structure's life. A requirement every "
                            "part were held to would pick one and apply it where it was not written; kept as "
                            "knowledge, a designer sees them all and states which one the piece follows. The seating "
                            "standards set none either: EN 12520's Table 1, an EN 16139 test report, "
                            "ANSI/BIFMA X5.4's tests and an X5.1 report load a seat (1300 N, a bag dropped "
                            "100,000 times) and pass it when it still serves or has not given way, and "
                            "measure no sag (sources/en-12520-2015-preview and the three beside it)."},
            links={"rests_on": ["the-rules-read-the-knowledge", "a-check-reads-its-requirement-over-its-own-link"]},
            meta={"amended": "400c53a9d5a5 the seating standards added to the sources searched; they set no "
                             "sag limit, so the decision is the same"},
            children=[
                _alt("one-limit-for-every-shelf", "Hold every shelf and seat to EN 16121's 0.5% of the span, "
                     "the limit most often cited", "It is written for non-domestic storage shelves under "
                     "1.5 kg/dm2 for a week; no source says a home bench seat should meet it."),
                _alt("a-requirement-per-standard", "A requirement per standard, in scope of a category of "
                     "piece as the clothing-storage-unit tests are", "No category of home furniture is in "
                     "any of their scopes; the categories would be made up to fit."),
                _alt("design-targets-only", "Keep sag limits as targets a design sets with no source",
                     "A designer asking how much a seat or a shelf may sag finds nothing to choose from."),
            ],
        ),
        Node(
            id="a-deflection-limit-is-stated-as-a-share-of-the-span", kind="decision",
            name="A deflection limit is stated in SI as share_of_span (the deflection over the span: span/180 "
                 "is 1/180, 0.5% is 0.005), max_deflection (mm), surface_load (kg/m2), load_duration (h) and "
                 "creep_factor (final over initial deflection); each value carries a row naming the words "
                 "it follows in the copy, the value as printed, the number and how it becomes SI, and a "
                 "test finds it there in the copy kept by sha256",
            payload={"decided_on": "2026-11-13",
                     "why": "The sources write a limit as span/180, L/144, 1/16 inch per foot or 0.5% of the "
                            "span; one share reads them all, and times a part's span it gives millimetres. A "
                            "load is a mass in this package, so a load per area is kg/m2, not a pressure "
                            "that needs gravity to compare. A conversion done once in code and checked "
                            "against the printed number leaves no value typed by hand."},
            links={"rests_on": ["a-published-sag-limit-is-a-source-a-piece-chooses-from"]},
            children=[
                _alt("span-divisor", "Store the divisor (180 for span/180)",
                     "0.5% of the span and 1/16 inch per foot are not divisors, and a divisor is "
                     "inverted before every use."),
                _alt("millimetres-for-a-span", "Store the limit in mm for a typical span",
                     "The limit depends on the part's span; any one span is an assumption."),
                _alt("pascals", "State surface loads in Pa, as KCMA prints them",
                     "The package's loads are masses; Pa would be divided by gravity to be used."),
            ],
        ),
        Node(
            id="an-open-licensed-source-is-quoted-like-a-public-domain-one", kind="decision",
            name="A source under CC BY 4.0 (an open-access paper) is quoted, and the pages quoted kept under "
                 "sources/, as a public-domain one is; its source says licence cc-by-4.0, names the authors "
                 "and the DOI, and says the quoted words keep their CC BY licence. Its values are also found "
                 "after their labels in the whole copy kept privately, by sha256",
            payload={"decided_on": "2026-11-13",
                     "why": "CC BY lets anyone copy the words with credit, and a quote lets anyone check a "
                            "value without the private copy. CC BY 4.0 forbids putting further terms on the "
                            "licensed material (2(a)(5)(B)), so the quoted words stay CC BY inside a CC "
                            "BY-NC-ND knowledge base, and the source says so. Only the pages quoted are kept, "
                            "as for the Wood Handbook: a paper's PDF can be tens of MB."},
            links={"rests_on": ["a-copyrighted-standard-is-cited-never-copied-here",
                                "the-knowledge-is-shared-unchanged-and-improved-only-here"]},
            children=[
                _alt("cite-cc-by-like-copyrighted", "Cite a CC BY source by locator and values only",
                     "Gives up what the licence allows, and a value can then be checked only by whoever "
                     "holds the private copy."),
                _alt("keep-the-whole-pdf", "Keep the whole PDF in the repo", "Tens of MB for a few pages "
                     "quoted."),
            ],
        ),
        Node(
            id="a-thermally-modified-wood-is-read-from-a-study-of-its-treatment", kind="decision",
            name="A thermally modified wood is a material of its own, read from a study of wood treated the "
                 "stated way, never from the untreated species. Beech thermally modified is Schmidtová et "
                 "al.'s (2026) structural boards treated at 190 °C for 3.5 h: its design stress their "
                 "characteristic bending strength (EN 384) over the Handbook's 2.1, its modulus their mean "
                 "Em,0,mean (EN 384) taken as apparent, its density their treated mean (Table 2). The "
                 "material says the temperature its values hold for and that a board on sale's is unknown",
            payload={"decided_on": "2026-11-13",
                     "why": "The treatment changes the wood, and how much depends on its temperature: "
                            "Schmidtová's treated boards lost 17% of their mean bending strength and "
                            "scattered three times as much (coefficient of variation 45% against 14%); "
                            "Borůvka et al.'s (2018) clear beech kept its strength at 165 °C (108.8 MPa "
                            "against 102.7) and lost 59% of it at 210 °C (42.0). The study gives a "
                            "characteristic value, which takes only the 2.1. Em,0,mean, 13.62 GPa, is below "
                            "the boards' global modulus measured with the shear deflection in it, 14.92 GPa, "
                            "so taken as apparent it judges no part stiffer than the boards were."},
            links={"rests_on": ["a-stated-strength-is-read-the-way-its-source-labels-it",
                                "a-panels-tested-modulus-takes-no-shear-term",
                                "an-open-licensed-source-is-quoted-like-a-public-domain-one"]},
            children=[
                _alt("untreated-beech", "Use Tropix's beech for thermally modified beech",
                     "Untreated wood; the treatment lowers the strength and widens its scatter."),
                _alt("clear-wood-at-165", "Use Borůvka et al.'s clear-wood means at 165 °C",
                     "Small clear specimens at the mildest treatment: a board of unknown treatment may "
                     "be far weaker, and a mean takes no account of a 45% scatter."),
                _alt("global-modulus", "Use Table 2's global modulus, 14.92 GPa", "The higher of the two "
                     "moduli the study gives."),
                _alt("table-3-density", "Use Table 3's mean density, 632.3 kg/m3", "The lighter of the two "
                     "means: a part's own weight, and so its sag, would be understated."),
            ],
        ),
        Node(
            id="the-birch-laminate-borrows-plywoods-kdef", kind="decision",
            name="The Wood Handbook's yellow birch laminate, flat and on edge, carries EN 1995-1-1's creep for "
                 "plywood in service class 1, 1/(1 + 0.80), read from Swedish Wood's Table 9.1 and not grounded: "
                 "Eurocode 5 rates EN 636 plywood, and the Handbook does not say its laminate is one",
            payload={"decided_on": "2026-11-13",
                     "the_owner": "If I like a panel in Leroy Merlin would it be able to adapt the design for the "
                                  "panel to be used while keeping the desired qualities? ... Ok do it",
                     "why": "A part is held to a longtime sag limit through its material's initial_share_of_longtime; "
                            "without one the bench's seat, in this laminate, could not be held to a limit at all. The "
                            "boards it is compared with, Leroy Merlin's plywoods, carry EN 1995-1-1's plywood figure "
                            "(wood-panels: creep-is-ec5s-kdef-for-service-class-1), so the laminate takes the same, "
                            "and a seat judged in either is judged on one basis."},
            links={"rests_on": ["a-document-is-one-source-in-the-tree"]},
            children=[
                _alt("handbook-two-thirds", "The Handbook's two-thirds for initially dry timber (Chapter 9, p. 9-4)",
                     "Written for timber beams, not panels; and the plywoods on sale take Eurocode 5's figure, so "
                     "the laminate would sag less over the years than a board of the same stiffness."),
                _alt("no-creep", "Leave the laminate without a creep share",
                     "A part in it could not be held to a longtime sag limit."),
            ],
        ),
        Node(
            id="a-pieces-checks-are-the-rules-under-it", kind="decision",
            name="The checks a piece's documents print (drawings.checks, report.checks) run the rules on the piece "
                 "and the nodes beneath it only, and keep the verdicts whose path is the piece's or beneath it, id "
                 "by id; the knowledge's own verdicts are this package's tests', not each build's",
            payload={"decided_on": "2026-11-13",
                     "why": "Run over the whole tree, each check judged every source, clause and material again: "
                            "7.5 s of a check on the bench, twice a build, for verdicts the checks then threw away. "
                            "Under the piece, the bench's 62 verdicts are the same in 0.03 s, which is what makes "
                            "judging a draft in many boards in one call possible. quern before 061f79d bound a run "
                            "under pieces/bench to pieces/bench-side as well, so the checks keep only the piece's "
                            "paths themselves; a test holds the checks to the whole tree's verdicts in every world "
                            "the package states."},
            children=[
                _alt("whole-tree", "Run the rules over the whole tree and keep the piece's verdicts",
                     "Seconds per check spent on verdicts nobody reads."),
                _alt("verdict-cache", "Keep the whole-tree run, with a verdict cache across builds",
                     "Each build is a process of its own, so the cache would have to live on disk, and the first "
                     "build after a package moves would pay the whole run again."),
            ],
        ),
        Node(
            id="the-design-notes-are-the-callers", kind="decision",
            name="The design document prints the notes its caller gives, sections of a heading and their "
                 "paragraphs, under the checks or on a fourth sheet when they would run into the title block; "
                 "the piece's payload description is printed only when the caller gives none",
            payload={"decided_on": "2026-11-13",
                     "the_owner": "Was it a good idea to replace the assistant authored notes with notes generated "
                                  "from a ledger? ... Ok go do the work in full",
                     "why": "A piece's design notes were a description written by hand in its model, beside a "
                            "ledger that says the same decisions and open points as entries a rule can check: the "
                            "plans printed the copy nothing checks. Whoever builds the documents knows where its "
                            "notes are kept, so it hands them over; this package knows no ledger format, and a "
                            "caller with none keeps the description."},
            children=[
                _alt("read-a-ledger-here", "Read the piece's ledger in furniture-design",
                     "The package would carry one consumer's ledger format and its words."),
                _alt("drop-description", "Drop the description and print no notes unless given",
                     "A caller with no ledger would lose the notes it has."),
                _alt("cut-the-notes", "Print what fits under the checks and leave the rest out",
                     "A note left out of the plans is one the people who build never read."),
            ],
        ),
        Node(
            id="the-design-notes-flow-on-from-the-checks", kind="decision",
            name="The design document prints the notes its caller gives (sections of a heading and their "
                 "paragraphs, a paragraph with the lines under it) starting under the checks, and goes on over "
                 "as many sheets of their own as they need, a heading never left at the foot of a sheet; the "
                 "piece's payload description is printed only when the caller gives none",
            payload={"decided_on": "2026-11-14",
                     "why": "Moved whole to a fourth sheet when they did not all fit, the bench's notes left half "
                            "of the third sheet, titled checks and notes, empty and the notes on the next; and a "
                            "ledger longer than one sheet had nowhere to go."},
            links={"supersedes": ["the-design-notes-are-the-callers"]},
            children=[
                _alt("a-fourth-sheet-whole", "Put the notes whole on a fourth sheet when they do not fit under the "
                     "checks", "Half a sheet left empty under a title that says notes, and no room past one sheet."),
                _alt("cut-what-does-not-fit", "Print what fits and leave the rest out",
                     "A note left out of the plans is one the people who build never read."),
            ],
        ),
        Node(
            id="a-piece-has-a-cutting-sheet-for-the-shop", kind="decision",
            name="Every piece's documents include a cutting sheet (A4) to hand a shop's cutting service: the "
                 "rectangles the saw cuts, length along the grain; then for each material and thickness the "
                 "panels to buy, the smallest sheet sold that takes the parts, and where each part sits on it, "
                 "in strips across the panel and end to end along its grain, drawn to scale with the grain of "
                 "panel and parts. What can be bought is the caller's (`stock`, per material); a material with "
                 "none is listed with its parts. A part's grain runs along its length unless its span_along bends "
                 "it across the face grain. A part's own cuts are made afterwards, as the assembly instructions say",
            payload={"decided_on": "2026-11-14",
                     "the_owner": "Dans les documents ajoute un document de découpe. Notamment avec le sens de "
                                  "découpe. ... Pour donner a l'atelier à Leroy Merlin par exemple ... Build it",
                     "why": "The plans' cut list gave the grain for one part in four and no panel: a cutting "
                            "service cuts from a panel bought in the shop, and the grain of a plywood part is the "
                            "panel's. The shop is not this package's: a caller passes the sheets it sells, and "
                            "the lib knows no shop.",
                     "the_rule": "furniture_design/cutting.py; drawings.documents gives it as 'cutting'."},
            children=[
                _alt("cut-list-on-the-plans", "Fill the plans' cut list's grain column and stop there",
                     "A cutting service needs the panels to buy and where the parts sit on them."),
                _alt("the-lib-reads-a-shops-range", "furniture-design reads a shop's range itself",
                     "A lib knows nothing of who uses it; the shop's range is a package of its own."),
            ],
        ),
        Node(
            id="a-part-names-the-saw-that-cuts-it-out", kind="decision",
            name="A part links sawn_with the saws that cut it out of its board. A saw is a tool whose params, each "
                 "derived from a clause its maker printed, are the width its blade takes out (kerf), else the widest "
                 "blade it takes (max_kerf), and the thickest board it cuts through square (max_cut_depth). The "
                 "cutting sheet leaves between a material's parts the widest cut of their saws and says whose; a "
                 "part whose saws state none counts the caller's allowance (4 mm) and the sheet says it is one. "
                 "Rules: every saw a part names states its cut and rests on clauses; each sheet of a part is no "
                 "thicker than its saws cut",
            links={"rests_on": ["the-rules-read-the-knowledge", "a-piece-has-a-cutting-sheet-for-the-shop",
                                "makers-products-are-in-packages-outside-furniture-design"]},
            payload={"decided_on": "2026-11-14",
                     "the_owner": "le plan de découpe prend il en compte l'épaisseur de la scie? ... Source les "
                                  "différents types de scies et les solvers et règles associés",
                     "why": "The sheet left 4 mm between parts, a figure from no source, the same for a pull saw "
                            "that takes out under 1 mm and a table saw blade that takes out 2.6. Makers print the "
                            "cut of the blade a saw comes with (a plunge saw's 1.8 mm, a table saw's 2.6) or the "
                            "widest blade it takes; a jigsaw's, a portable circular saw's and a panel saw's makers "
                            "print neither, so such a saw is measured and stated on a saw of the design's own. "
                            "The saws themselves, being makers' products, are a package of their own.",
                     "the_rule": "rules a-part-is-sawn-with-a-saw-that-states-its-cut and "
                                 "a-part-is-no-thicker-than-its-saw-cuts; cutting.group_kerf."},
            children=[
                _alt("a-kerf-per-piece", "The piece states one kerf as a number in its payload",
                     "A number typed into a piece rests on nothing, and a piece cut with two saws has two."),
                _alt("a-kerf-per-saw-kind", "One kerf per kind of saw (hand saw, circular saw, panel saw)",
                     "The cut is the blade's: within one kind, makers' blades range from 0.46 to 1.07 mm for pull "
                     "saws and 1.8 to 2.6 mm for the blades one plunge saw takes."),
                _alt("a-saw-solver", "A furniture/* calculation for the cut and the depth",
                     "The grammar states both checks (a param read through a link, a quotient and a comparison), "
                     "and a calculation is only for what it cannot sum."),
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
