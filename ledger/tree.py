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
        Node(
            id="a-shops-cutting-service-is-a-saw-with-its-rules", kind="decision",
            name="A shop's cutting service is a tool a part links sawn_with, like a saw: besides its cut and depth it "
                 "states the narrowest part it cuts (min_part_width) and links refuses to the materials it does "
                 "not cut. Rules: a part is no narrower than its saws cut (furniture/narrow_margin: the part's "
                 "cut width, the middle of its box sides, less the largest min_part_width its saws state), and no "
                 "saw it names refuses its material. The service's rules are a shop's package's data",
            links={"rests_on": ["a-part-names-the-saw-that-cuts-it-out",
                                "what-the-grammar-cannot-sum-is-a-calculation-with-cases"]},
            payload={"decided_on": "2026-11-14",
                     "the_owner": "Ça peut valoir le coup aussi de modéliser les règles de découpe dans le pack "
                                  "Leroy Merlin unofficial. Par exemple j'ai appris sur place qu'ils ne pouvaient "
                                  "pas faire une découpe de moins de 10 cm de large.",
                     "why": "The cutting sheet is handed to a shop's service, whose rules decide whether a part "
                            "can be cut there at all. A part's cut width is read from its box, which the rule "
                            "grammar cannot sort, and most saws state no narrowest part, which a rule reading "
                            "the param would turn into an absent check on every part: so a calculation, which "
                            "takes a saw that states none as no limit.",
                     "the_rule": "rules a-part-is-no-narrower-than-its-saw-cuts and "
                                 "a-part-is-cut-by-a-saw-that-cuts-its-material; natives.narrow_margin."},
            children=[
                _alt("a-service-kind", "A kind of its own for a shop's cutting service",
                     "It cuts parts out of boards as a saw does and is laid out the same way on the sheet; a "
                     "new kind would double every rule about saws."),
                _alt("min-width-in-the-grammar", "Read the part's width param in the rule",
                     "A part states width only when a joint needs it, and a param the saw does not state "
                     "leaves the check absent everywhere."),
            ],
        ),
        Node(
            id="a-step-closes-a-joint-the-way-its-connector-engages", kind="decision",
            name="A connector says how its two parts come together (payload engages; square: pushed "
                 "straight together, square to the face they meet on), as its maker shows it, and the "
                 "assembly steps are judged by it: a part a step brings in (direction) to close a joint whose "
                 "connector engages square comes straight at that face from its own side, never slid along it "
                 "nor brought from the far side (furniture/misfit_closings, rule "
                 "a-step-closes-each-joint-the-way-its-connector-engages). A connector that does not say "
                 "leaves the check absent",
            links={"rests_on": ["the-rules-read-the-knowledge", "the-documents-are-for-the-people-who-build",
                                "what-the-grammar-cannot-sum-is-a-calculation-with-cases"]},
            payload={"decided_on": "2026-11-14",
                     "the_owner": "if you know Clamex, you know that sliding a piece like that on the image is "
                                  "not possible or not a god practice because it implied torsion. The "
                                  "instructions are incorrect. [...] Adding this check should have been the fix",
                     "why": "A design's assembly instructions told its builder to slide a shelf in from the front "
                            "between two sides already joined, on Clamex P-14 connectors, which close square "
                            "across the joint line; the rules let it through because nothing read the steps. "
                            "Fixing the one design left the next one free to say the same. Which face a joint's "
                            "parts meet on is read from their boxes, which the rule grammar cannot do: a "
                            "calculation, with cases worked by hand.",
                     "the_rule": "rule a-step-closes-each-joint-the-way-its-connector-engages; "
                                 "natives.misfit_closings; spec furniture/misfit_closings."},
            children=[
                _alt("fix-the-design-only", "Correct the steps of the one design that slid a shelf in",
                     "The next design, or the next edit of this one, could slide a part in again and no rule "
                     "would say so."),
                _alt("engagement-in-the-rule", "Hold every connector to square engagement in the rule itself",
                     "How a connector closes is its maker's statement, knowledge like its limits; a rule that "
                     "assumed it would judge a sliding connector wrongly and rest on no source."),
                _alt("unstated-passes", "Let a connector that does not say how it engages pass",
                     "The check would read as passed on a design no one has judged; absent says it was not."),
            ],
        ),
        Node(
            id="a-joints-grooves-are-cut-from-one-reference-the-card-names", kind="decision",
            meta={"expected:what-a-decision-rests-on-still-stands":
                  "superseded by the-grooving-step-is-drawn-to-ikeas-rules, and the cut decision it rests on "
                  "by a-cut-is-drawn-to-ikeas-rules; each restates what of the two still binds"},
            name="A preparation step that cuts the grooves of joints gives, after its picture, the "
                 "method of the joints' tools on a page and a card per part: the part's face drawn square to "
                 "it with every groove and access hole, and sentences saying for each joint the surface "
                 "grooved, each groove's middle measured from an edge of that part, and the one reference both "
                 "parts are cut from, so the two grooves of a connector meet: the face where the parts are "
                 "flush (an edge groove registers on it, a face groove on the edge flush with it), else for a "
                 "part whose edge meets the other's face away from its edges (a shelf) the line of that part's "
                 "top face, drawn on the other. The groove's middle is the machine's groove_offset from the "
                 "reference less the spacer that brings it nearest the middle of the edge-grooved part, the "
                 "thinner of two as near. A connector closed through a hole has it drilled in the part grooved "
                 "in its edge, from the face away from the reference (so the hole is on the hidden side of a "
                 "flush corner and under a shelf), at access_hole_offset from the joint face, in the middle "
                 "of each groove",
            links={"rests_on": ["a-cut-is-explained-from-its-shape-and-its-tools-clauses",
                                "the-documents-are-for-the-people-who-build"]},
            payload={"decided_on": "2026-11-15", "the_owner": "Je voudrais que les plans de montage détaillent les actions de perçage avec la lamello zeta P2. Tout ça doit reposer sur une excellente compréhension de l'outil et des techniques pour l'utiliser, notamment pour l'alignement des trous",
                     "why": "The jointer's makers and woodworking authors agree that the two grooves of a joint "
                            "meet only when both are cut from the same reference face (Woodsmith; DeWalt DW682 "
                            "p. 2; Fine Woodworking), and a shelf is set by the line of its top face with both "
                            "cuts made from one clamping (DeWalt p. 3; Makita PJ7000 p. 7; Popular "
                            "Woodworking). The instructions said one sentence per step and no position. "
                            "Lamello's 20 mm panel is centred with no spacer and its 16 mm corner drawn with the "
                            "2 mm one, which the spacer rule gives. Which part takes the hole is not said in "
                            "words by Lamello: its drawings put it 7.5 mm from the joint face in one half, drilled "
                            "square into a face with the jig hooked over the edge the groove opens into, which "
                            "only the edge-grooved part has.",
                     "falsified_by": "a builder who follows a card and finds a connector's two grooves do not "
                                     "meet, or a hole the key cannot reach once assembled"},
            children=[
                _alt("one-sentence-per-step", "Keep one sentence per step naming the machine and its setting",
                     "It said neither where the grooves go nor from what they are cut, which is where a joint "
                     "goes wrong."),
                _alt("positions-without-reference", "Give the positions along the joint and nothing across it",
                     "Two grooves at the right place along a joint but cut from different faces leave the "
                     "parts out of flush."),
                _alt("centre-in-the-thickness", "Put every groove in the middle of the thickness, as the joint "
                                                "layout draws it",
                     "A jointer cuts at a fixed distance from its reference, and the card must say what the "
                     "machine does: 10 mm, or 8 with a spacer, is within the connector's 1 mm radial tolerance "
                     "of the middle of 18 mm."),
            ],
        ),
        Node(
            id="a-makers-machine-follows-the-general-method-of-its-kind", kind="decision",
            meta={"expected:what-a-decision-rests-on-still-stands":
                  "superseded with the card decision it rests on by the-grooving-step-is-drawn-to-ikeas-rules, "
                  "which restates what of both still binds"},
            name="How any biscuit or plate jointer is used is one general tool, tools/plate-jointer, here, its "
                 "method in sentences resting on makers' manuals and woodworking articles, cited by locator; "
                 "a maker's machine (in its maker's package) links follows to it and says only what is its own "
                 "(its settings, stops and depth), and states groove_offset and spacers_mm. A connector closed "
                 "through a hole states access_hole_diameter and access_hole_offset and links drilled_with to "
                 "the tool that drills it. The documents print the general method, then the machine's, then "
                 "the drilling tool's",
            links={"rests_on": ["the-method-is-public-and-names-no-home",
                                "a-joints-grooves-are-cut-from-one-reference-the-card-names"]},
            payload={"decided_on": "2026-11-15", "the_owner": "Les spécificités de Lamello et de ses modèles vont dans lamello-unofficial mais ce qui est générique pour ce genre de machine reste dans un paquet générique",
                     "why": "What is true of every jointer (marking across both parts, one reference face, a "
                            "shelf on its line, a test cut) would otherwise be copied into every maker's "
                            "package, or missing from the next one."},
            children=[
                _alt("all-in-the-makers-package", "Write the whole method in each maker's package",
                     "The general method would be written again, and differently, for every maker."),
                _alt("all-here", "Write the maker's settings here too",
                     "A maker's settings are its own, and the general method names no maker."),
            ],
        ),
        Node(
            id="a-source-says-who-stands-behind-it", kind="decision",
            name="Every source says its authority: maker (on its own product or service), standard, "
                 "research, editorial (an edited publication) or none (a person's video, page or post). "
                 "A clause of a source with no authority is in the knowledge only verified: a check the "
                 "knowledge already holds, run on a case, confirms it, and the clause says which check, "
                 "the clauses with authority it reads, the case, the result and the date (payload "
                 "verified). Rules a-source-says-its-authority and a-clause-with-no-authority-is-verified",
            links={"rests_on": ["the-rules-read-the-knowledge"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "Et on source notre modèle de connaissances sur les tutos. Mais il faut "
                                  "des tutos authoritatifs. En tout cas il faut conserver une notion "
                                  "d'autorité. Si on a un moyen de vérifier des approches proposées par "
                                  "des tutos non authoritatifs, cad qu'on teste l'idée sur les règles "
                                  "qu'on a par ailleurs et ça nous confirme que ça marche, c'est bien, "
                                  "et il faut le loguer sur le modèle",
                     "why": "Tutorials show how a machine is used better than a manual's text, but anyone "
                            "can publish one; the knowledge grounds instructions people follow at the "
                            "machine, so what it says has to be weighed by who says it, and what no one "
                            "stands behind has to be shown to work by what someone does.",
                     "falsified_by": "a clause with authority none whose verification, run again, no "
                                     "longer gives its result"},
            children=[
                _alt("authoritative-only", "Take nothing from a source with no authority",
                     "The owner asked that an approach from such a tutorial be kept when a check "
                     "confirms it."),
                _alt("a-score", "Grade each source on a scale of trust",
                     "A number between two sources says nothing a reader can check; who published "
                     "it can be."),
                _alt("authority-by-default", "Count a source that says nothing as authoritative",
                     "A tutorial added without the field would pass as a maker's word."),
            ],
        ),
        Node(
            id="a-video-is-cited-from-the-account-gemini-gave", kind="decision",
            name="A tutorial video is a source like a document: cited by locator (its timestamps) and "
                 "the words each clause rests on, its authority stated. Nobody here watches it: the copy "
                 "is the account Gemini gives of it (what is said and what is shown, with timestamps), "
                 "kept byte for byte in the private repo, its sha256 on the source, and payload read_by "
                 "names Gemini and the date. A test finds each clause's words in that account",
            links={"rests_on": ["a-reported-source-is-the-persons-words-never-the-makers",
                                "a-copyrighted-source-is-cited-by-locator-and-values"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "Dans ce cas il faut aller chercher des tutoriels. Je sais que youtube ne "
                                  "donne pas le texte de ses vidéos mais il suffit de le demander à Gemini, "
                                  "il le donne direct",
                     "why": "YouTube's robots.txt forbids robots its transcripts (/timedtext_video), the "
                            "player's requests (/youtubei/) and its preview frames (i.ytimg.com/sb/); "
                            "Gemini reads the video on Google's side. Its account can be wrong: on two "
                            "videos it answered that it could not watch them after describing them, so a "
                            "clause rests only on what a document with authority also says, and the "
                            "source says who read it.",
                     "falsified_by": "a passage of an account that the video, watched, does not show or say"},
            children=[
                _alt("frames", "Take frames of the video as the copy",
                     "The player's requests and the preview frames are forbidden to robots."),
                _alt("captions", "Fetch YouTube's captions",
                     "/timedtext_video is forbidden to robots, and the Lamello videos have no speech."),
            ],
        ),
        Node(
            id="a-screen-takes-its-drawing-from-the-instructions-and-its-words-from-the-piece", kind="decision",
            name="The assembly instructions come as screens for an app, one step or one block of a step at a time: "
                 "each screen's drawing is cut from the instructions' PDF where they drew it (the drawing notes each "
                 "picture's place: the cover, each board, each step's picture, each block drawn on its own and its "
                 "frames), and its words (the step's text, tools and connectors, the boards' letters, counts and "
                 "sizes, the hardware, a cut card's sentences and method) are read from the piece and set by the app. "
                 "A frame or block added to the instructions reaches the screens by noting its place, never by a "
                 "second drawing of it",
            links={"rests_on": ["the-grooving-step-is-drawn-to-ikeas-rules",
                                "the-documents-are-for-the-people-who-build"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "I think we should have a new card with user friendly display of the assembly "
                                  "instructions; Right now they're only in a pdf. That's fine, but since we're in an "
                                  "app... Prototype; then, of the prototype: deploy",
                     "why": "A whole A4 page on a phone draws a step at about 2 px per mm, its words 5 to 7 px high. "
                            "Cutting the drawings from the PDF keeps one drawing of each; the prototype "
                            "(furniture's prototypes/assembly-card) read well at 320 and 390 px and on a desktop."},
            children=[
                _alt("pages-as-images", "Show the PDF's pages as images, one a screen",
                     "On a phone the words are 5 to 7 px high and half pages are empty."),
                _alt("a-second-drawing", "Draw each screen again from the scene, apart from the PDF",
                     "Two drawings of each step drift apart."),
            ],
        ),
        Node(
            id="a-pieces-instructions-are-full-or-short", kind="decision",
            name="A piece says in its payload instructions how much its assembly instructions show of the tools "
                 "in use: full, when it says nothing, or short, for someone who knows their tools. Short leaves "
                 "out the tools' methods beside each cut, the jointer drawn at work and its test groove, and "
                 "keeps what the piece needs: the cuts and where to mark them, the joints' marks and positions, "
                 "the machine's settings, the holes. The choice is the piece's, made for each design, never a "
                 "tool's or a person's",
            links={"rests_on": ["the-grooving-step-is-drawn-to-ikeas-rules",
                                "the-documents-are-for-the-people-who-build"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "some people are so used to their tools that they won't need to include "
                                  "detailed instructions. How do we make this optional?; then: \"I know this "
                                  "tool\" is naive. The choice should be per design",
                     "why": "Full is the default because the costs are uneven: a page someone does not need "
                            "costs a page turn, a page missing costs a wrong groove in a part already cut; and "
                            "the documents are read by whoever builds the piece, not only by who designed it. "
                            "What a person knows of a tool does not settle what one design asks of it."},
            children=[
                _alt("per-tool", "A mark 'I know this tool' on each tool of the person's list",
                     "The owner: naive; the choice is per design."),
                _alt("short-by-default", "Short unless the piece asks for full",
                     "A missing page costs more than an extra one, and others build from the same documents."),
            ],
        ),
        Node(
            id="a-tools-pages-are-the-blocks-that-show-it-at-work", kind="decision",
            name="A tool's pages (drawings.tool_pages) are the blocks of a piece's assembly instructions that show "
                 "it at work, drawn with it at work, as a PDF of their pages and as screens: each block names the "
                 "tool it shows (by path), and each block screen carries its step and its place among the step's "
                 "blocks, which is its place in the instructions drawn with or without any tool at work, so a "
                 "reader sets a tool's blocks in the place of the ones that leave it out",
            links={"rests_on": ["a-caller-names-the-tools-drawn-at-work",
                                "a-screen-takes-its-drawing-from-the-instructions-and-its-words-from-the-piece"]},
            payload={"decided_on": "2026-11-16",
                     "why": "Instructions already drawn are not drawn again to add one tool: the tool's pages come "
                            "beside them, and a block's place in its step does not change with what it shows."},
            children=[
                _alt("draw-all-again", "Draw the whole instructions again with the tool at work",
                     "The instructions already made would change, and every page be drawn again for a few."),
            ],
        ),
        Node(
            id="a-question-to-the-person-asks-one-thing-and-names-its-answers", kind="decision",
            name="A rule of furniture-standards@ that waits on what only the person knows checks one thing, so "
                 "its question (messages ask) is put only when that thing is missing: what a part is cut from "
                 "(a-pieces-parts-say-what-they-are-cut-from, Which boards do you buy?) and what cuts it out "
                 "(a-pieces-parts-say-how-they-are-cut, What do you cut the boards with, or which shop cuts "
                 "them?) are two rules. When the person's tools answer a question, the rule says which "
                 "(messages offers: the payload key such a tool states, saw_kind for what cuts a part); whoever "
                 "shows the question offers only those tools, and none when the rule names none",
            links={"rests_on": ["a-part-names-the-saw-that-cuts-it-out",
                                "a-shops-cutting-service-is-a-saw-with-its-rules",
                                "a-pieces-instructions-have-a-level-to-reach"]},
            payload={"decided_on": "2026-11-16",
                     "why": "One rule held both links and asked both questions: a bench whose parts all named "
                            "their board was still asked which boards the person buys, and the person's sander, "
                            "clamps, tape and vacuum were offered as what they cut with. A reader may not "
                            "recognise a rule by its name, so which tools answer is the rule's to say."},
            children=[
                _alt("one-rule-two-questions", "Keep one rule for both links, its question asking both",
                     "The person is asked what the model already says."),
                _alt("reader-filters-by-rule", "The app offers saws when it sees the cutting rule",
                     "A reader would then name a rule of the standard, which whoever shows a certificate does not."),
                _alt("no-tools-offered", "Offer no tools as answers, only a line to type",
                     "The person's tools are the answer most of the time, and ticking one names it as the "
                     "piece links it."),
            ],
        ),
        Node(
            id="a-caller-names-the-tools-drawn-at-work", kind="decision",
            name="Whoever draws a piece's documents may name the tools its assembly instructions draw at work "
                 "(at_work, by path), overriding the payload's full or short tool by tool: a block draws its tool "
                 "at work when it is named and leaves it out otherwise, an empty set drawing none; and may draw "
                 "one document at a time (drawings.document), told how far the instructions have got as they "
                 "draw their steps then cut their screens",
            links={"rests_on": ["a-pieces-instructions-are-full-or-short"]},
            payload={"decided_on": "2026-11-16",
                     "why": "A reader of the documents may want the method of one tool drawn and not another's, "
                            "and the documents may be drawn where a person waits for them, one at a time, on a "
                            "slower machine than a server: the payload's one choice for every tool cannot say "
                            "the first, and drawing the four together with no word of progress cannot serve "
                            "the second. The payload's choice stays the default, so a piece drawn without "
                            "at_work is drawn as before."},
            children=[
                _alt("payload-per-tool", "A list of tools in the piece's payload",
                     "Which tools are drawn at work is a reader's choice made after the design is saved, and a "
                     "saved version's piece.json never changes."),
            ],
        ),
        Node(
            id="the-grooving-step-is-drawn-to-ikeas-rules", kind="decision",
            name="A preparation step that cuts the grooves of joints is drawn, not written: after its picture, "
                 "pages of their own with the settings drawn on the machine (its depth adjusters, the spacer, "
                 "crossed out when none is used, a test groove), then per kind of joint four frames: the two "
                 "parts as assembled, seen from their reference face, a tick across the joint at each groove, "
                 "the positions from the edge they start at, a blue triangle on the reference face; the "
                 "edge-grooved part with the machine's front stop on its reference face; the face-grooved part "
                 "with the machine standing, its base plate flush with the reference edge; the edge-grooved "
                 "part turned over with the jig and a drill. Lines only, in the instructions' one viewpoint, the "
                 "machine and the jig drawn from the 3D models their makers' packages give (payload model) by "
                 "a hidden-line renderer, the groove's distance in a close-up circle, counts as '4 ×'. Still "
                 "binding from the decisions it replaces: both grooves of a connector are cut from one "
                 "reference (the face where the parts are flush, else the line of a shelf's top face), at the "
                 "machine's groove_offset less the spacer that centres them; the access hole in the "
                 "edge-grooved part from the face away from the reference; a maker's machine follows the "
                 "general jointer tool and states its own settings, whose sentences stay knowledge",
            links={"rests_on": ["the-documents-are-for-the-people-who-build"],
                   "supersedes": ["a-joints-grooves-are-cut-from-one-reference-the-card-names",
                                  "a-makers-machine-follows-the-general-method-of-its-kind"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "C'est horrible à lire tu as dumpé toutes tes connaissances dans les "
                                  "instructions. C'est le contraire de ce que je te demande, je te demande des "
                                  "instructions à la Ikea; then: You need a realistic model of the Lamello, not "
                                  "just a few understandable grey strokes. Simple doesn't mean bad. To the "
                                  "contrary. Simple is a lot of work. Fetch Ikea drawing rules",
                     "why": "IKEA tests its instructions on people who assemble the product without any text "
                            "(its manual for assembly instructions, as Schumacher 2011 reports it); action "
                            "diagrams one per step cut assembly time and errors (Heiser 2004); a stylised tool "
                            "is recognised least, so the machine is modelled from its maker's printed sizes and "
                            "drawings. Three blind readers named the sequence, the reference face and the counts "
                            "from the pages alone.",
                     "falsified_by": "a builder who cannot cut a joint's grooves from the frames without "
                                     "reading anything else"},
            children=[
                _alt("sentences-per-part", "Keep a card per part with sentences and a method page",
                     "The owner found it unreadable: knowledge dumped into instructions."),
                _alt("sections", "Draw the machine as grey blocks in section",
                     "The owner: not clear at all; IKEA and Lamello draw the real tool in perspective."),
                _alt("one-page", "All the frames of all the joints on one page",
                     "Sixteen frames on an A4 page leave each too small to read the machine."),
            ],
        ),
        Node(
            id="a-cut-is-drawn-to-ikeas-rules", kind="decision",
            name="A part's cut is drawn, not written, by the rules the grooving step is drawn to: frames of "
                 "its own after its step's picture, the board with the marks drawn where they go and their "
                 "distances from the edges they start at, the saw lines numbered in the order they are sawn, "
                 "and the saw drawn at work from a model of it, one action per frame, no sentence. Still "
                 "binding from the decision it replaces: how a cut is made is never typed into a piece; where "
                 "to mark it, the edges it is measured from and the saw lines and their order are read from "
                 "the cut's box against its board; the kind of cut is stored nowhere; the tools' methods stay "
                 "knowledge, sentences resting on clauses, which the frames draw and the instructions do not "
                 "print",
            links={"rests_on": ["the-documents-are-for-the-people-who-build",
                                "the-grooving-step-is-drawn-to-ikeas-rules"],
                   "supersedes": ["a-cut-is-explained-from-its-shape-and-its-tools-clauses"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "We have another case of assembly intructions that break the rules and still "
                                  "pass: [the cut card of the bench's side, 'Tracer : 25 depuis le chant "
                                  "arrière, 115 depuis le chant du bas' and the hand saw's four sentences] I "
                                  "need Ikea style instructions for these too. Why wheren't they made this way?",
                     "why": "The owner's complaint that made the grooving pages drawn was about the "
                            "instructions as a whole ('tu as dumpé toutes tes connaissances dans les "
                            "instructions ... je te demande des instructions à la Ikea'), but the decision "
                            "was written for the grooving step only, so the cut card kept the form it had "
                            "rejected there (a card per part with sentences and a method page), and the "
                            "tests asserted those sentences. The same reasons hold for a cut: IKEA tests its "
                            "instructions on people who use no text, and one action diagram per step cuts "
                            "time and errors (Heiser 2004).",
                     "falsified_by": "a builder who cannot mark and saw a part's cut from the frames without "
                                     "reading anything else"},
            children=[
                _alt("sentences-per-cut", "Keep the cut card's sentences and the saw's method beside it",
                     "The owner: assembly instructions that break the rules; the grooving step already turned "
                     "this form down."),
                _alt("short-only", "Leave the sentences to the full instructions and draw only in short ones",
                     "Short still prints where to mark as a sentence, and full is the default most people get."),
            ],
        ),
        Node(
            id="every-page-of-the-instructions-is-drawn-to-ikeas-rules", kind="decision",
            name="IKEA's rules reach every page of the assembly instructions, not only the grooving step and "
                 "the cuts: what a page says in words it draws instead. Still written, and owed: each step's "
                 "sentence under its picture, and the hardware and tools named in words on the page of what is "
                 "needed",
            links={"rests_on": ["the-grooving-step-is-drawn-to-ikeas-rules", "a-cut-is-drawn-to-ikeas-rules"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "C'est horrible à lire tu as dumpé toutes tes connaissances dans les "
                                  "instructions ... je te demande des instructions à la Ikea; then: We have "
                                  "another case of assembly intructions that break the rules and still pass",
                     "why": "The owner's correction was about the instructions as a whole and was recorded for "
                            "one step, so the next written part was found by the owner, not by the ledger. "
                            "IKEA tests its instructions on people who use no text (the grooving decision's "
                            "source); the parts still written are named here so the next change finds them.",
                     "falsified_by": "a builder who cannot build the piece from the instructions' drawings "
                                     "without reading a word"},
            children=[
                _alt("one-part-at-a-time", "Record each part when the owner finds it",
                     "That is how the cut card was missed: the owner found it, the ledger did not."),
            ],
        ),
        Node(
            id="a-tools-steps-are-drawn-from-its-node", kind="decision",
            name="The assembly instructions draw a tool at work only as its node in a package states it: the "
                 "tools drawn are those the piece's parts and joints name (which the assistant chooses from the "
                 "person's tools), each drawn from its model, and each step it is drawn doing (where it sits "
                 "against the line or the part, its angle, its stroke, the close-up, the hand) is data on the "
                 "tool's node beside its method's sentences, resting on the same clauses. The drawing code knows "
                 "no tool and no step of its own. Still scripted in code, and owed: the sawing frames "
                 "(drawn-cut-card branch, sawing.py: one push saw's start, 45 degree stroke and end, given to any "
                 "saw with a model) and the grooving pages (grooving.py: the jointer's frames)",
            links={"rests_on": ["a-cut-is-drawn-to-ikeas-rules", "the-grooving-step-is-drawn-to-ikeas-rules"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "Is it a hardcoded card? In fact I didn't ask for a cut card. I want those to "
                                  "be part of the assembly instructions. Are you hardcoding stuff? They should be "
                                  "based on the tools selected by the assistant for the piece, and the drawings "
                                  "should be based on tool models stored in the packages, not on app code",
                     "why": "The drawn cut took its saw's shape from the tool's model but its actions from code "
                            "written for one push saw, so the owner's pull saw would be drawn pushed at 45 "
                            "degrees. A tool's use is knowledge, as its sentences are: it belongs to the tool "
                            "in its package, sourced, where a maker's package can state its own."},
            children=[
                _alt("frames-per-kind-in-code", "Keep a drawing function per kind of tool in the instructions' code",
                     "Every new tool needs code, its steps rest on no source, and a tool of a kind the code "
                     "did not foresee is drawn doing another tool's steps."),
            ],
        ),
        Node(
            id="a-tool-is-drawn-as-the-lamello-is", kind="decision",
            name="A tool at work is drawn as the Zeta P2 is: furniture-design holds the general tool (its method "
                 "in sentences resting on clauses, and the drawing of that method's steps, one function per "
                 "general tool), a maker's package holds the maker's tool, which follows the general one and "
                 "gives its own model (payload model, sized from the maker's print and drawings) and settings; "
                 "the instructions draw the tool the piece names (chosen by the assistant from the person's "
                 "tools) from its model, doing the steps of the general tool it follows, and a tool that follows "
                 "none drawn gets no step it does not do. The sawing frames draw a saw that follows "
                 "tools/crosscut-saw; the Bahco ERGO Superior 2600-22 in the saws package carries its model",
            links={"rests_on": ["a-cut-is-drawn-to-ikeas-rules", "the-grooving-step-is-drawn-to-ikeas-rules"],
                   "supersedes": ["a-tools-steps-are-drawn-from-its-node"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "Add to the model (the packages) a standard saw or a precise model close to "
                                  "the saw you draw and fix this: do like for the lamello.",
                     "why": "The superseded decision went beyond the owner's words (\"the drawings should be "
                            "based on tool models stored in the packages, not on app code\") into steps as data "
                            "on every tool; the owner pointed to the Lamello, whose model is its maker's package's "
                            "and whose steps are drawn by furniture-design for the general jointer. The fault "
                            "the owner found was a model on the general saw and any saw drawn pushing: a maker's "
                            "saw gives the model, and only one that follows the general push saw is drawn doing "
                            "its steps."},
            children=[
                _alt("steps-as-data", "Each tool's steps as data on its node, the drawing code knowing no tool",
                     "Not what the owner asked; the owner pointed to the Lamello's way."),
            ],
        ),
        Node(
            id="a-tool-is-certified-by-a-standard-that-is-a-package", kind="decision",
            name="What a tool's entry is held to is a package of its own, furniture-standards@ "
                 "(furniture_design/standards.py), beside furniture-design@: rules that grade and refuse nothing, "
                 "criteria that group them (identified, drawn, drawing true to the figures, said in every "
                 "language, a saw's cut and depth, figures consistent, each found printed, each resting on two "
                 "observations that agree) and levels that say which criteria a use requires (shown in a "
                 "person's tools, cuts the parts of a piece, drawn at work in instructions, taken into the "
                 "shared packages). A tool is certified by running quern.certify on it; a better standard is a "
                 "new version of the package, and nothing that reads certificates changes. Its rules are not "
                 "among those every design and every node of the knowledge is held to",
            payload={"decided_on": "2026-11-15",
                     "the_owner": "Rething the whole certification process based on that idea, that certification "
                                  "is based on a set of standards and rules enforced by other knowledge models. "
                                  "This way, knowledge models can improve and certification with it, without "
                                  "changing the code",
                     "why": "The app had written a tool's grade in its own code. As rules of furniture-design@ "
                            "they would have judged every tool of the knowledge and turned its own examples red "
                            "(a hand saw has no model), so the standard is a package of its own, proved by its "
                            "own example and counter-examples.",
                     "not_yet": "The standards for a buildable piece and for assembly instructions; the rules' "
                                "sentences per language (messages)."},
            links={"rests_on": ["the-rules-read-the-knowledge", "makers-products-are-in-packages-outside-furniture-design"]},
            children=[
                _alt("rules-of-furniture-design", "Add the grading rules to furniture-design@",
                     "Every tool of the knowledge would be judged by them in every check, and the package's own "
                     "examples would not pass."),
                _alt("in-the-apps-code", "Leave the grade in the app that keeps people's tools",
                     "Turned down by the owner: the standard must improve without the code."),
            ],
        ),
        Node(
            id="furniture-standards-requires-certification", kind="decision",
            name="furniture-standards@ requires certification@ (exact version, pinned by digest) and defines neither "
                 "kind criterion nor level, nor the rules that keep them well formed: it gets certification@ from "
                 "the public registry by its pin with quern.library.require, and carries no copy. What a reader "
                 "judges a tree with, standards.VOCABULARY and standards.RULES, is certification@'s then this "
                 "package's. That a criterion measures completeness, reliability, consistency or presentation is "
                 "this package's own rule (a-criterion-measures-one-of-the-four-qualities), since certification@ "
                 "leaves the word free",
            payload={"decided_on": "2026-11-16",
                     "the_owner": "remove the stupid comment and solve the issue (xag/furniture-design#2). Then, of a "
                                  "copy carried here: If it's generic, why insist on putting it in furniture design?",
                     "why": "certification@0.1.0 is in the public registry (xag/quern-registry) since 2026-11-16. "
                            "The kinds and rules declared here were a copy of it, and the copies had already "
                            "drifted: four words for measures against any word, another expression for a level's "
                            "criteria, no sentences per language."},
            links={"rests_on": ["a-tool-is-certified-by-a-standard-that-is-a-package", "the-package-is-in-the-open-registry"]},
            children=[
                _alt("keep-the-copy", "Keep criterion, level and their rules declared here",
                     "Two definitions of one name drift, and a tree pinning both packages is refused for the clash."),
                _alt("taken-from-quern", "Import certification@ from quern (quern.certification)",
                     "quern authors no package; the owner: \"only keep it in quern registry\"."),
                _alt("a-copy-in-the-wheel", "Carry certification@ as the registry holds it under furniture_design/registry/",
                     "Done first. The owner: \"If it's generic, why insist on putting it in furniture design?\""),
            ],
        ),
        Node(
            id="a-piece-is-walked-by-its-assemblies", kind="decision",
            name="A piece groups its parts in assemblies (kind assembly: a door, a rail, a drawer), to any depth; an "
                 "assembly places and weighs nothing, so the checks and the other documents read the parts as before. "
                 "The 3D view's parts list is the assembly shown: its assemblies, then its own parts; picking an "
                 "assembly shows it alone, fitted, with a line leading back up to the piece. One whose longest side is "
                 "over eight times its next is shown from its end, close enough to read its section. A double tap on "
                 "the piece turns the view around the point touched and brings it close; beside the piece it shows the "
                 "whole of what is shown again",
            links={"rests_on": ["the-documents-are-for-the-people-who-build"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "In the 3D view we need to be able to navigate through the design tree in order to "
                                  "get a closer look at smaller elements. For instance in the portes des penderies, "
                                  "to view just one rail. Also this wont suffice to look closely at a specific part, "
                                  "so find something for that too.",
                     "why": "A rail 1156 mm long and 20 mm across, fitted by its length, is a line: a first blind "
                            "tester said it could not be examined. The double tap is Sketchfab's (Navigation and "
                            "Controls: double-click on the model sets the camera pivot there and zooms on it, on the "
                            "background re-centres); showing a group alone is Onshape's Hide other instances."},
            children=[
                _alt("a-section-view", "A control that cuts the shown assembly across its length",
                     "A profile is the same all along: its end already shows its section."),
                _alt("groups-read-from-the-parts-ids", "Groups worked out from a shared prefix of the parts' ids",
                     "A name is not structure; the tree holds it."),
                _alt("the-others-left-faint", "The parts outside the assembly left faint (Onshape's Isolate)",
                     "The owner asked to view just one rail; a door standing in a rail hides its section."),
            ],
        ),
        Node(
            id="a-profile-is-one-part-with-its-section", kind="decision",
            name="A part that is a profile (an angle, a channel) states payload section, the outline of what it is "
                 "across its length, in mm from its minimum corner; its box stays the whole it fits in, by which it "
                 "is placed, listed and cut to length. The 3D view and the documents' pictures draw the section, and "
                 "its mass, when not stated, is its density times the section's area times its length. One profile "
                 "is one part, never one part per face. In the 3D view, parts whose middles are close are pulled "
                 "apart by at least most of the second side of what is shown",
            links={"rests_on": ["the-tree-leads-the-3d-views-panel", "a-dimension-is-stated-once-and-parts-follow-it"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "Ecarter les pièces est incorrect. Il y a deux pièces sur le rail, pas cinq.",
                     "why": "Only boxes were modelled, so a piece's rails were written as five flat strips, two for "
                            "the angle and three for the channel, each a part in the list, the pulled-apart view and "
                            "the cutting sheet."},
            children=[
                _alt("a-shape-of-its-own", "A shape op profile beside box, with no box",
                     "Placement, the cut list and every rule read a part's box; the box a profile fits in serves "
                     "them unchanged."),
                _alt("named-sections", "Named sections (angle, channel) with a wall thickness and a way they open",
                     "An outline says any section and its way round at once, with nothing to learn per shape."),
            ],
        ),
        Node(
            id="a-pieces-design-is-certified-against-its-ledger-and-its-mechanisms", kind="decision",
            name="furniture-standards@ also says what a piece's design is held to (furniture_design/standards_piece.py): "
                 "every sentence of its purpose is answered by a decision of its ledger that quotes it and names "
                 "what in the piece realises it; every quantity the ledger states in words is a figure the model "
                 "is held to; every part is fixed by a joint or moved by a motion; and what slides (a new kind, "
                 "motion: axis, travel, what moves, what guides) is held on both sides by its guides and crosses "
                 "nothing along its travel, judged on the parts' outlines across the axis. Two levels: the design "
                 "says what the person asked for; it holds together and what moves in it works. The piece's ledger "
                 "is read at ledgers/<piece id>, where whoever certifies mounts it",
            payload={"decided_on": "2026-11-15",
                     "the_owner": "tous les rails sont faux: le U dans lequel glisse un panneau est coll\u00e9 dans "
                                  "l'angle de sorte qu'il n'y a pas de place pour que l'autre panneau glisse entre "
                                  "le U et l'angle \u2014 donc, il faut aussi un process de certification costaud "
                                  "pour le design des meubles \u2014 consistence entre le ledger et le design "
                                  "peut-\u00eatre, et s'assurer que les r\u00e8gles du ledger sont couvrantes",
                     "why": "A piece of sliding doors passed every rule with rails that could not work: its ledger "
                            "held its purpose and no decision, its doors were boxes that nothing said moved, no "
                            "part was joined to anything, and the 5 cm of overlap its purpose states was 47 and "
                            "52 mm in the model with nothing comparing them.",
                     "not_yet": "Motions other than a slide; a part cut from what was bought, by a tool the person "
                                "has; hardware counted; the surroundings as parts; the assembly instructions' own "
                                "standard."},
            links={"rests_on": ["a-tool-is-certified-by-a-standard-that-is-a-package", "a-profile-is-one-part-with-its-section",
                                "the-tree-leads-the-3d-views-panel"]},
            children=[
                _alt("rules-of-furniture-design", "Make them rules every piece must pass to be built",
                     "A draft is built to be looked at before it is settled; these grade it and say what is left."),
                _alt("free-text-coverage", "Leave it to the assistant to judge whether the ledger covers the purpose",
                     "The party graded would grade itself; a quoted sentence and a named part are checked."),
            ],
        ),
        Node(
            id="a-pieces-instructions-have-a-level-to-reach", kind="decision",
            name="furniture-standards@ has a level a piece's assembly instructions are shown at "
                 "(standards/piece-instructions): the design is explained, agrees with its ledger, holds together, "
                 "its mechanisms work, and its steps build it: every part is brought in by a step, and every "
                 "joint is closed by a step, no sooner than the one that brings in the last part it joins. "
                 "Whoever shows instructions reads the level; what it requires is this package's to raise",
            payload={"decided_on": "2026-11-15",
                     "the_owner": "il faut certifier la notive, et ne pas l'afficher tant qu'elle n'est pas au "
                                  "niveau",
                     "why": "A piece's instructions were three steps that showed parts arriving, with what fixed "
                            "them said in a sentence or not at all, for a design whose rails could not work; "
                            "they were shown like any other.",
                     "not_yet": "The level reads the piece's steps, not the pages drawn: no sentence on a page, "
                                "what a part is fixed to shown in the step's picture, a close-up per fixing, the "
                                "hardware counted on the parts page, each part cut from what was bought, the "
                                "rules read from sources on IKEA's instructions, and the step order computed "
                                "from the joints, are to be added to it."},
            links={"rests_on": ["a-pieces-design-is-certified-against-its-ledger-and-its-mechanisms",
                                "every-page-of-the-instructions-is-drawn-to-ikeas-rules"]},
            children=[
                _alt("always-shown", "Show the instructions of any piece that builds",
                     "Turned down by the owner: not until they are at the level."),
                _alt("no-sentence-now", "Require now that no step carries a sentence",
                     "The drawing code still owes the pictures that replace them (every-page-of-the-instructions-"
                     "is-drawn-to-ikeas-rules): no piece could reach the level, and it would say nothing."),
            ],
        ),
        Node(
            id="the-tree-leads-the-3d-views-panel", kind="decision",
            name="A piece groups its parts in assemblies (kind assembly: a door, a rail, a drawer), to any depth; an "
                 "assembly places and weighs nothing, so the checks and the other documents read the parts as before. "
                 "In the 3D view the parts list stands at the head of the panel and is the assembly shown: its "
                 "assemblies, then its own parts; picking an assembly shows it alone, fitted. The panel's title is the "
                 "way back up (the piece, then each assembly down to the one shown), over the size of what is shown. "
                 "The assembly steps followed are those that bring a part of what is shown; with fewer than two the "
                 "slider is not drawn. An assembly whose longest side is over eight times its next is shown from its "
                 "end, close enough to read its section. A double tap on the piece turns the view around the point "
                 "touched and brings it close; beside the piece it shows the whole of what is shown again",
            links={"rests_on": ["the-documents-are-for-the-people-who-build"],
                   "supersedes": ["a-piece-is-walked-by-its-assemblies"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "Maintenant qu'on navigue dans l'arbre, il faudrait le mettre un peu plus en avant; "
                                  "Sur le téléphone, l'expérience utilisateur n'est pas terrible. [...] B. Et l'étape "
                                  "de montage doit soit avoir du sens soit être enlevé.",
                     "why": "On a phone the list sat under the sliders, out of sight, and the line leading back up "
                            "with it. Inside a rail the step slider emptied the view until the rail's own step. The "
                            "owner chose the list at the head of the panel (B) over a bar of buttons under the model "
                            "(A), both tried on a playable prototype."},
            children=[
                _alt("a-bar-under-the-model", "A bar between the model and the panel: the way back up and a button "
                     "per assembly in what is shown", "Shown as A and turned down by the owner for B."),
                _alt("the-steps-of-the-whole-piece-everywhere", "The step slider kept as it was inside an assembly",
                     "Its steps that bring nothing of what is shown leave the view empty or unchanged."),
            ],
        ),
        Node(
            id="on-a-narrow-screen-the-tree-stands-above-the-model", kind="decision",
            name="On a narrow screen (a phone) the 3D view reads from the top: the tree (the title that leads back "
                 "up, the size of what is shown, the list), then the model, then the tools (the assembly steps, "
                 "pulling apart, the connectors, reset). The tree takes at most 38% of the height; a list longer "
                 "than its place scrolls and fades at its foot. On a wide screen the tree stands over the tools, "
                 "beside the model",
            links={"rests_on": ["the-tree-leads-the-3d-views-panel"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "J'attendais la navigation dans les pièces au dessus de la vue 3D",
                     "why": "With the list at the head of the panel, a phone still showed it under the model: one "
                            "looks at the model, then down for the list, then up again."},
            children=[
                _alt("the-whole-panel-under-the-model", "The tree at the head of one panel under the model",
                     "Built first and turned down by the owner, who expected it above the model."),
            ],
        ),
        Node(
            id="what-an-assistant-is-told-is-guidance-in-the-packages", kind="decision",
            name="What whoever designs with a package must be told before reading its nodes is a node of kind "
                 "guidance in that package's knowledge (branch guidance: a name, payload text, the link about to "
                 "the nodes it speaks of), held by the rule a-guidance-speaks-of-what-exists. A reader (a "
                 "connector, a skill) gives its assistant every guidance of the tree it works in and writes "
                 "none of its own: its own instructions say how its tools work and nothing about furniture, "
                 "shops, tools or standards. A package that adds a shop, a tool, a rule or a level adds what "
                 "must be said of it. furniture-design's are in furniture_design/guidance.py, the standards' "
                 "in standards.guidance(); a level says what reaching it allows (payload allows), so a reader "
                 "asks the tree which level allows the assembly instructions and names none",
            payload={"decided_on": "2026-11-15",
                     "the_owner": "attention \u00e0 n'\u00e9crire aucune connaissance dans le code. Tout ce qui est "
                                  "connaissance est dans quern \u2014 V\u00e9rifie partout, d'ailleurs, qu'aucune "
                                  "connaissance n'est hardcod\u00e9e dans l'appli \u2014 ok je n'avais pas en t\u00eate "
                                  "l'\u00e9tendue de la catastrophe. Sans h\u00e9siter pour tout 1",
                     "why": "The app's connector carried some 250 lines of instructions to assistants that "
                            "restated the packages: the shops and their prefixes, a default cut, the tools of "
                            "three packages by path, panel classes, sag limits, how a tool and a piece are "
                            "certified. A package that changed left them false, and a new shop was not in them.",
                     "not_yet": "The text is in English only, as assistants read it. furniture-standards@ still "
                                "defines criterion and level itself; certification@ (the ledger repository) is "
                                "written and not yet published or required."},
            links={"rests_on": ["a-tool-is-certified-by-a-standard-that-is-a-package"]},
            children=[
                _alt("in-the-kinds-descriptions", "Say it all in the kinds' descriptions",
                     "A kind says what its nodes take, to someone who already reached for it; when to reach for "
                     "one, and what to do where the knowledge stops, belongs to no one kind."),
                _alt("served-on-request", "Serve the guidance only when the assistant asks for it",
                     "An assistant that does the minimum does not ask; what it must know before it starts is "
                     "given unasked. A reader may still shorten what it gives."),
                _alt("in-each-reader", "Leave each reader to write its own instructions",
                     "What the owner found: the reader's copy goes stale and no rule sees it."),
            ],
        ),
        Node(
            id="a-held-part-is-pulled-apart-the-way-its-holder-opens", kind="decision",
            name="In the 3D view, pulling the parts apart separates a part that sits in another's box (a channel "
                 "in its angle, a frame's bar along its panel) from that holder the way the holder opens: from the "
                 "middle of the holder's section to the middle of its box, out of an angle's corner or a channel's "
                 "mouth; a solid holder parts along the line between the two middles. The two move away from each "
                 "other half each, nearly clear at a tenth of the slider, and a holder of several moves by the mean "
                 "of what they push it",
            links={"rests_on": ["a-profile-is-one-part-with-its-section"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "L'écartement des deux pièces U et angle est pesant. Lent, et dans la direction "
                                  "d'une face de l'angle. On s'attend à ce que ça s'écarte dans le deux directions. "
                                  "Trouve un meilleur algo",
                     "why": "The channel alone slid out along one face of the angle, found by casting rays, while "
                            "the angle stayed, and needed most of the slider to clear it."},
            children=[
                _alt("rays-along-the-axes", "The held part alone leaves along the first axis whose rays meet "
                     "nothing of its holder", "Turned down by the owner: slow, along one face, one part moving."),
                _alt("between-the-two-middles", "The two part along the line between their sections' middles",
                     "For a channel set in an angle's corner the middles are nearly level, so it slides along a "
                     "face again."),
            ],
        ),
        Node(
            id="a-part-row-opens-the-part-alone", kind="decision",
            name="In the 3D view a part's row opens it alone, as a group's row opens the group: the parts of its "
                 "letter in the group shown, fitted, the title leading back up through the groups to the piece. A "
                 "piece whose parts stand in no group is walked the same way, one level deep",
            links={"rests_on": ["the-tree-leads-the-3d-views-panel"]},
            payload={"decided_on": "2026-11-15",
                     "the_owner": "The banc à chaussures doesn't have the new 3D view. I don't see the navigatoin "
                                  "throught the tree",
                     "why": "The banc's parts stand in no group, so its list had nothing to open; a part's row "
                            "only coloured it, which a blind tester read as nothing happening."},
            children=[
                _alt("groups-made-up-for-the-banc", "Groups added to the banc's model",
                     "They would be a design choice nobody made; opening a part needs none."),
            ],
        ),
        Node(
            id="a-pieces-instructions-are-judged-on-the-pages-drawn", kind="decision",
            name="The level that allows a piece's assembly instructions also requires three criteria judged on "
                 "the pages as they were drawn, each resting on clauses of the knowledge: no page carries a "
                 "sentence (IKEA's own account of why its instructions are pictures); each step attaches one "
                 "kind of part, drawn apart with a line to where it goes, and shows what fastens each joint it "
                 "closes; each step's picture shows the parts it brings in and enough of those already there "
                 "(Agrawala et al. 2003, whose planner's shares, 50 % of a new part and 10 % of the earlier "
                 "ones, are params of a clause the rules read). The drawing notes what each page shows "
                 "(sheets.Pen.note and Pen.text, pages.model: a branch instructions/<piece id> of pages and "
                 "frames), written beside the screens as pages.json; a tree that judges mounts it. "
                 "Instructions not drawn in the tree judged are not at the level, and say so",
            payload={"decided_on": "2026-11-16",
                     "the_owner": "il faut certifier la notive, et ne pas l'afficher tant qu'elle n'est pas au "
                                  "niveau. Fait tout ce qui manque \u2014 attention \u00e0 n'\u00e9crire aucune "
                                  "connaissance dans le code. Tout ce qui est connaissance est dans quern",
                     "why": "The level read the piece's steps, not what was printed: instructions whose steps "
                            "named every part and joint reached it while their pages said in sentences what "
                            "they did not draw, and showed parts arriving with nothing that fixed them.",
                     "sources_not_used": "Schumacher's guidelines for pictorial assembly instructions "
                                         "(Information Design Journal 15(2), 2007; grooving.py cites them as "
                                         "2011) are behind a paywall and were not read: no clause rests on them.",
                     "not_yet": "No piece reaches the level: the drawing still sets each step's sentence, the "
                                "headings and the tools' and hardware's names (every-page-of-the-instructions-"
                                "is-drawn-to-ikeas-rules owes their pictures). The parts page's hardware is "
                                "not compared with the joints' counts. The step order is still the piece's to "
                                "state, held by a-pieces-instructions-have-a-level-to-reach, and not computed."},
            links={"rests_on": ["a-pieces-instructions-have-a-level-to-reach",
                                "every-page-of-the-instructions-is-drawn-to-ikeas-rules",
                                "what-an-assistant-is-told-is-guidance-in-the-packages"]},
            children=[
                _alt("judge-the-steps-only", "Keep judging the piece's steps, and trust the drawing",
                     "The drawing is what the person reads; what it prints was held by nothing."),
                _alt("thresholds-in-the-code", "Write the shares a part must show as constants of the drawing",
                     "Turned down by the owner: knowledge is in quern. They are a clause's params."),
                _alt("wait-for-the-pictures", "Add the criteria once the drawing meets them",
                     "The owner asked for instructions not to be shown until at the level; the criteria say "
                     "what is left."),
            ],
        ),
        Node(
            id="a-package-module-makes-its-examples-when-asked", kind="decision",
            name="A package module makes its PACKAGE, EXAMPLES and COUNTER_EXAMPLES the first time one is asked for; "
                 "what a reader judges a tree with (VOCABULARY, RULES, SOLVERS, VERSION) is made at import",
            payload={"decided_on": "2026-11-16",
                     "the_owner": "Still this is a lot of memory. [...] Yes, don't hesitate to aggressively make quern "
                                  "more efficient",
                     "why": "The examples are the whole knowledge base several times over (each counter-example is a "
                            "world of its own): importing furniture_design.package held 25 MB, in every process "
                            "that only reads its kinds and rules, among them a web server on a 512 MB machine. Made "
                            "when asked, the import holds 0.1 MB."},
            children=[
                _alt("examples-shared-between-counter-examples", "Counter-examples sharing one world",
                     "A counter-example changes its world; sharing them would let one case leak into another, and "
                     "it would still be made by every reader of the kinds."),
                _alt("examples-in-a-file", "Examples read from a JSON file beside the module",
                     "They are made by the same functions the tests call with other arguments; a file would be a "
                     "second copy to keep in step."),
            ],
        ),
        Node(
            id="two-parts-touch-where-their-material-meets", kind="decision",
            name="Where two parts touch is read from what they are made of: a part is its box, or a profile whose "
                 "section's sides run square to its box is the cells of the grid its section's corners draw that "
                 "lie inside it (natives.cells). Two parts touch on the largest plane their cells meet on, and run "
                 "into each other when any two cells do. A section with a slanted side stays its box",
            links={"rests_on": ["a-profile-is-one-part-with-its-section"]},
            payload={"decided_on": "2026-11-17",
                     "the_owner": "Now fix the identified issues",
                     "why": "A channel laid on an angle's flange sits inside the angle's box, so read by boxes the "
                            "two ran into each other and a joint between them 'joins parts that do not touch'; a "
                            "person's rail had to be joined twice with the same screws, and its hardware counted "
                            "twice. The standards' own door rail glues its channel the same way.",
                     "the_rule": "natives.contact; tests/test_contact.py.",
                     "not_yet": "A section with a slanted or curved side is still read as its box."},
            children=[
                _alt("polygons-in-shapely", "Intersect the sections as polygons (shapely) when the two run along "
                     "one axis", "Only parallel profiles; the cells take any two parts in any direction, boxes "
                     "included, by the one test boxes already had."),
            ],
        ),
        Node(
            id="a-connectors-rules-judge-only-the-joints-it-fastens", kind="decision",
            name="The rules on a joint's seat (a-joined-part-is-thick-enough-for-the-cut, a-joined-part-is-wide-"
                 "enough, a-joint-is-cut-with-a-tool-its-connector-takes) judge each connector the joint uses "
                 "(where(c, linked(self, 'uses'), kind(c) == 'connector')) and read its limits on it: a joint held "
                 "by screws or a glue, which the knowledge holds as materials, is not judged by them",
            links={"rests_on": ["the-rules-read-the-knowledge"]},
            payload={"decided_on": "2026-11-17",
                     "the_owner": "Now fix the identified issues",
                     "why": "a-pieces-joints-say-what-fastens-them names screws and a glue among what a joint "
                            "uses, and these rules read min_thickness_<cut>, min_width and needs, which only a "
                            "connector states: a screwed rail came out absent or broken and the piece non-compliant. "
                            "A guard written with `or` cannot pass such a joint over, both sides being evaluated "
                            "(quern's the-grammar-is-an-object-not-a-private-parser), so quern 0.1.10 added where.",
                     "the_rule": "package.RULES; tests/test_joints.py.",
                     "not_yet": "Screws have no kind and no rules of their own (diameter, length, pilot hole, "
                                "countersink, the thickness they hold in): each limit needs a clause a maker or a "
                                "standard prints (the-rules-read-the-knowledge), and none is captured yet."},
            children=[
                _alt("screws-as-connectors", "Hold screws as connectors, so the rules apply to them",
                     "A screw states no seat, no cut and no machine; it would carry invented limits to pass."),
                _alt("guard-in-or", "Guard each rule with `kind(c) != 'connector' or ...`",
                     "Both sides of `or` are evaluated: the guarded side still reads what screws lack."),
            ],
        ),
        Node(
            id="a-part-bought-cut-to-its-size-names-who-sells-it", kind="decision",
            name="A part bought already cut to its size (a panel its maker cuts to order) states payload "
                 "bought_to_size, who sells it so, and links no saw: a-pieces-parts-say-how-they-are-cut does not "
                 "ask what cuts it out, and the cutting sheet leaves it out",
            links={"rests_on": ["a-part-names-the-saw-that-cuts-it-out", "a-piece-has-a-cutting-sheet-for-the-shop"]},
            payload={"decided_on": "2026-11-17",
                     "the_owner": "Now fix the identified issues",
                     "why": "Twin-wall polycarbonate door panels came cut to size from their maker: no board, no "
                            "kerf, no place on the sheet, yet every part had to name a saw for the piece to reach "
                            "the level its assembly instructions need. a-part-names-the-saw-that-cuts-it-out was "
                            "made to know the cut left between parts drawn from one board, which such a part is not.",
                     "the_rule": "standards_piece.parts_unsawn; cutting.cuts; tests/test_cutting.py."},
            children=[
                _alt("the-maker-as-a-cutting-service", "Link sawn_with to the maker as a shop's cutting service",
                     "A cutting service cuts boards the person buys from the shop, and states a cut the sheet "
                     "leaves between parts; this part is bought finished and on no sheet."),
            ],
        ),
        Node(
            id="a-rule-says-where-it-is-written", kind="decision",
            name="Every rule and calculation of furniture@ and furniture-standards@ says where it is written "
                 "(package.written_at: furniture_design/<file>.py:<line> in package.REPOSITORY), and a guidance "
                 "(where-the-rules-are-written) tells whoever designs with the packages to read a rule there when "
                 "it holds a piece back for a reason its description does not give",
            links={"rests_on": ["what-an-assistant-is-told-is-guidance-in-the-packages"]},
            payload={"decided_on": "2026-11-17",
                     "the_owner": "Now fix the identified issues",
                     "why": "An assistant blocked by three rules (contact between profiles, a saw asked of a part "
                            "bought cut to size, a connector's rules applied to screws) found the cause only because "
                            "the person told it where the code was; told by the packages, it reads the rule and "
                            "reports the line without being asked.",
                     "the_rule": "package.written_at; tests/test_written_at.py."},
            children=[
                _alt("the-connector-says-it", "Write the repository's address in the connector's instructions",
                     "What an assistant is told of the packages is the packages' guidance, not a reader's own "
                     "words (what-an-assistant-is-told-is-guidance-in-the-packages)."),
            ],
        ),
        Node(
            id="a-page-names-things-and-says-what-it-cannot-draw", kind="decision",
            name="The level that allows a piece's assembly instructions also requires three criteria judged on "
                 "the pages as they were drawn, each resting on clauses of the knowledge: no page says in a "
                 "sentence what it could draw (IKEA's own account of why its instructions are pictures), the "
                 "piece's name, the headings the drawing sets, the names of tools and hardware, sizes and counts "
                 "excepted, and the sentence of a step that brings in, cuts and closes nothing (finishing, a "
                 "check), which no picture says yet; each step attaches one kind of part, drawn apart with a "
                 "line to where it goes, and shows what fastens each joint it closes; each step's picture shows "
                 "the parts it brings in and enough of those already there (Agrawala et al. 2003, whose "
                 "planner's shares, 50 % of a new part and 10 % of the earlier ones, are params of a clause the "
                 "rules read). The drawing notes what each page shows and what each text is (sheets.Pen.note, "
                 "Pen.text and its role: name, heading, label, note; pages.model), written beside the screens as "
                 "pages.json; a tree that judges mounts it. A step's text may be left out. Instructions not "
                 "drawn in the tree judged are not at the level, and say so",
            payload={"decided_on": "2026-11-17",
                     "the_owner": "Relax \"No page of the instructions carries a sentence\" [...] The rule does "
                                  "make sense for drawn assembly, but it's too strict for a notice someone builds "
                                  "from at home [...] Suggestions: allow short labels such as tool and material "
                                  "names, plus the app's own headings. Allow a written note for a step that has "
                                  "no drawable form yet (finishing, glue, checks), or let it print elsewhere, for "
                                  "example in the plans. Make `text` optional in the builder. (report "
                                  "0YCjjggePEYXC2soG1Fb; on being shown it: \"So?\")",
                     "why": "On the shoe bench every step's text had to go to meet the rule: the finishing, the "
                            "check that the diagonals are equal and the tools no package draws (glue, clamps, "
                            "hex key, tape measure, sander, paint) left the notice, and the headings the drawing "
                            "sets kept it red whatever the design said. A notice that drops its finishing to be "
                            "certified is a worse notice.",
                     "not_yet": "Gluing two panels face to face is a step that brings in a part: its sentence "
                                "still counts, and what draws a glue is owed. Instructions drawn before this "
                                "noted no roles, and are judged as before until drawn again."},
            links={"supersedes": ["a-pieces-instructions-are-judged-on-the-pages-drawn"],
                   "rests_on": ["a-pieces-instructions-have-a-level-to-reach",
                                "every-page-of-the-instructions-is-drawn-to-ikeas-rules",
                                "what-an-assistant-is-told-is-guidance-in-the-packages"]},
            children=[
                _alt("print-it-in-the-plans", "Print a step that cannot be drawn in the plans instead",
                     "The person builds from the notice; finishing and checks printed elsewhere are steps they "
                     "do not see when they reach them."),
                _alt("any-short-text", "Let any text under a number of words through",
                     "A short sentence still says in words what the picture should show; what a text is "
                     "is known where it is set, so the drawing says it."),
            ],
        ),
        Node(
            id="a-reported-source-is-the-persons-words-never-the-makers", kind="decision",
            name="Every source says its authority: maker (what it publishes on its own product or service), "
                 "standard, research, editorial (an edited publication), none (a person's video, page or post) "
                 "or reported (a person's own account of what they saw or were told, what a shop's staff said "
                 "to them included). A clause of a source with no authority is in the knowledge only verified: "
                 "a check the knowledge already holds, run on a case, confirms it, and the clause says which "
                 "check, the clauses with authority it reads, the case, the result and the date (payload "
                 "verified). A clause of a reported source is the person's words, quoted from where they said "
                 "them, and every value it gives is ungrounded. Rules a-source-says-its-authority, "
                 "a-clause-with-no-authority-is-verified and a-reported-clause-quotes-the-person",
            payload={"decided_on": "2026-11-17",
                     "the_owner": "Le paquet commun a accepté sources/leroy-merlin-store-visit-2026-11-14 : "
                                  "présentée comme le récit d'un client, avec l'autorité « maker », alors que la "
                                  "clause no-glulam reprend les mots du modèle, pas ceux du client. → Une source "
                                  "« rapportée par l'utilisateur » ne doit contenir que ses mots, cités depuis la "
                                  "conversation, et n'a jamais l'autorité du fabricant. (report YpKoBk2o4SwgpMAklcus)",
                     "why": "A customer's account of what a store said passed as the maker's word, and a clause "
                            "of it was a model's conclusion rather than the customer's words: the cutting "
                            "service then refused every glulam board, which the customer says it never did, "
                            "and the certificate asked the person questions resting on it."},
            links={"supersedes": ["a-source-says-who-stands-behind-it"],
                   "rests_on": ["the-rules-read-the-knowledge"]},
            children=[
                _alt("reported-is-none", "File a person's account under none",
                     "None enters only through a check the knowledge holds, and what a store will cut is "
                     "checked by nothing here: the narrowest cut a customer was told would be lost."),
                _alt("staff-words-are-the-makers", "Keep what a shop's staff said under maker",
                     "Those words reach the knowledge only through someone who reports them; that is "
                     "how a model's summary passed as the shop's rule."),
            ],
        ),
        Node(
            id="what-a-person-only-said-is-checked-and-shown", kind="decision",
            name="What a person only said reaches a rule checked and shown. Checked: a reported source states the "
                 "sha256 of a copy of the person's message as the session's transcript holds it (rule "
                 "a-reported-source-keeps-the-persons-message), kept privately under reported/<source id>.json, "
                 "and a package's test runs furniture_design.reported.check on it: every quote is in the copy, "
                 "and the copy is the message the transcript names, which the person typed. Shown: every "
                 "verdict that is not a pass names the clauses of sources of authority reported or none behind "
                 "the values it read, with their words and their source (evidence.unestablished, in "
                 "drawings.checks' detail)",
            payload={"decided_on": "2026-11-17",
                     "the_owner": "Then the question is how to prevent incorrect rules",
                     "why": "The glulam refusal came from a sentence a model wrote and a commit called the "
                            "customer's words; nothing compared it with what the customer said, and the person "
                            "met it only as a refusal with no source, then as questions resting on it. A quote "
                            "found in the person's own message cannot be invented; a refusal that quotes what it "
                            "rests on is caught by the one person who knows it is wrong.",
                     "not_yet": "In a claude.ai chat the server never sees the person's message, so a reported "
                                "source can be added only where a transcript holds their words (a Claude Code "
                                "session). The standards' certificate lines (quern.certify) do not carry the "
                                "evidence yet; the reds a build lists do."},
            links={"rests_on": ["a-reported-source-is-the-persons-words-never-the-makers"]},
            children=[
                _alt("declare-every-payload-field", "Declare every payload field in its kind, and refuse "
                     "an undeclared one",
                     "It would have given cut_to_size a meaning to read, but it reaches quern and every "
                     "package, and a declared field can still be misread; the quote check stops the "
                     "invented sentence itself."),
                _alt("trust-the-author", "Trust the quote the author of a package writes",
                     "That is how the glulam clause passed: its commit said it quoted the customer."),
            ],
        ),
        Node(
            id="a-piece-is-buildable-only-with-certified-saws", kind="decision",
            name="The knowledge a piece's checks read is held to its certificate, starting with the saws: a piece "
                 "reaches \"It can be cut and fastened from what it states\" only when every saw or shop's cutting "
                 "service a part is cut with (sawn_with) reaches \"Its figures are read by a piece's checks\" "
                 "(standards/tool-cuts-parts: identified, its cut and depth stated, its figures consistent and each "
                 "found printed). Criterion piece-saws-are-certified, rule a-pieces-saws-are-certified-to-cut-parts "
                 "(furniture/parts_cut_by_uncertified_saws, which says for each part which criteria its saw lacks)",
            payload={"decided_on": "2026-11-17",
                     "the_owner": "Then the question is how to prevent incorrect rules / Maybe we need to use "
                                  "certification@ on our knowledge",
                     "why": "The tools' certificate already said which figures a piece's checks may read, and "
                            "nothing held the checks to it: of the 70 tools in the shared packages on 2026-11-17, "
                            "61 did not reach that level, Leroy Merlin's cutting service none at all, and its "
                            "refusal of glulam, which nobody said, refused a person's parts.",
                     "not_yet": "Materials, connectors and sources have no certificate: their criteria (each "
                                "value resting on a clause of a source with authority, each quote found in its "
                                "copy) are owed, and the checks that read them are not yet held to one. A shared "
                                "package still admits a tool below \"Taken into the shared packages\": none of the "
                                "70 reaches it."},
            links={"rests_on": ["a-tool-is-certified-by-a-standard-that-is-a-package",
                                "what-a-person-only-said-is-checked-and-shown"]},
            children=[
                _alt("rules-skip-uncertified-figures", "Let each check skip a figure its tool is not certified "
                     "for, as absent",
                     "Every check would carry the certificate in its expression, and a piece would still look "
                     "buildable with figures nobody read; one criterion on the level says it once."),
                _alt("gate-the-shared-packages-first", "Refuse a shared package whose tools are below its level",
                     "Every shared package would fail today; the piece's level is where a wrong figure reaches "
                     "a person."),
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
