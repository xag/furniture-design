# furniture-design

Skills and tooling for designing furniture as a beginner: from what you want, to a piece that stands up, fits where it goes, and can be cut and assembled.

This repo holds only the general method. It names no home, no piece and nobody's furniture. A project that designs real furniture keeps that in its own repo and pins this one.

## What is here

- **A skill that designs furniture a beginner can build** (`skills/menuiserie-conception-meubles-design/`, in French, by Joohee): it takes an agent from an idea, a photo or an existing piece to dimensioned drawings, a cut list, a shopping list and assembly steps. It favours panels cut in the shop and joints a drill-driver can make, checks the design with this package's rules, and comes with a cut-list calculator for simple cabinets (geometry only).
- **A knowledge base** (`furniture_design/knowledge.py`): published sources, the clauses quoted from them word for word, and what those clauses let us derive. `sources/` holds each source and its clauses, with the quantities a clause states converted to SI (mm, kg, N, MPa). `materials/` holds six air-dried hardwoods (yellow birch, black cherry, sugar maple, northern red oak, black walnut, yellow-poplar): density, stiffness, shear moduli and how much they swell and shrink across the grain per percent of moisture, each derived from the Wood Handbook's tables. `requirements/` holds the two clothing-storage-unit stability tests the Federal Register describes, with their scope.
- **The furniture-design@ quern package** (`furniture_design/package.py`): the kinds a design and its knowledge are made of (source, clause, material, requirement, piece, part, load, climate, tool, connector, joint) and seventeen rules. Every clause quotes its source. Requirements and materials rest on clauses. A load acts on a part. A piece in a requirement's scope is held to it. A piece stands in its stability tests. A shelf sags within its long-term limit. A seat carries a sideways push (GSA's light-service sidethrust, 890 N) through a panel standing in the push's plane, such as a back, whose connectors take it in shear and pull-out; a piece with no such panel is not judged to stand. A part that bends is strong enough: its largest bending stress (Equation 9–13) stays under its material's design stress, which is the near-minimum strength divided by the Handbook's factor of 2.1 for 10-year loads and safety. A part spans the way its material's values were measured (along the grain, or with plywood's face grain along the span); a material whose source does not say which way it was bent judges no part's bending. A part that swells and shrinks with the air, such as a floating panel, has the clearance to, in the climate it lives in (a `climate` states its temperature and its driest and dampest humidity). That check refuses to answer for a climate where the Handbook's movement equation does not hold (outside 6% to 14% moisture content). A joint is cut with a tool its connector takes, at the connector's machine setting, in parts at least as thick (for its kind of cut) and as wide as the connector allows. No maker is named here: a maker's connectors and tools are data in a package of their own (for Lamello's, `xag/lamello-unofficial`). The rules carry no number a source states: they read limits, test loads and material properties from the knowledge base, so a new source adds knowledge, not rules.
- **Drawings from the tree** (`furniture_design/drawings.py`): for any piece, the cut list, the joints, dimensioned front and top views and a section at mid-width (SVG), 3D views (PNG, through geometry@'s renderer) and a build document that puts them together with the piece's assembly steps and the rules' verdicts.
- **The calculations the rules call** (`furniture_design/natives.py`): the deflection of a part (Equation 9–2, with no shear term for a panel whose stiffness was measured on the panel), mass, height, the tipping margin about the front edge, which requirements apply to a piece, and the moisture content wood settles at in a climate (Equation 4–5, which a test holds to the Handbook's printed Table 4–2). Each comes with cases worked by hand (`furniture_design/spec.py`) that quern runs before the package can be published.

## Sources

A rule enters here from a published source, cited by name and clause. Copies of public-domain sources are kept under `sources/` so every quote can be checked, and a test checks it:

- USDA Forest Products Laboratory, *Wood Handbook: Wood as an Engineering Material*, FPL-GTR-282 (2021). Beam deflection (Equations 9–2 to 9–4, Table 9–1), creep (Chapters 5 and 9), density (Equation 4–14), the stiffness tables (Tables 5–1 and 5–3a), equilibrium moisture content (Equation 4–5) and dimensional change (Equation 13–3, Table 13–5). The whole PDF is 104 MB, so only the pages quoted are kept, as text, with the PDF's sha256.
- U.S. Consumer Product Safety Commission, *Safety Standard for Clothing Storage Units*, 88 FR 28403 (2023), the rule that makes ASTM F2057-23 mandatory (16 CFR 1261). ASTM's own text is copyrighted; what is quoted here is the Commission's public description of its tests.

Copyrighted standards (EN 14749, EN 16121 and EN 16122, ASTM F2057, ANSI/BIFMA X5.9, ANSI/AWI 0641) are cited here and never copied in. A clause from a copyrighted source carries its locator and the values it states, never a quote; its source records the url and the sha256 of what was fetched, and the copy is kept in a private repo. A test holds that no such clause here carries a quote.

## What the checks do not do yet

- The tipping check predicts the physical tests. Passing it is not compliance: compliance is the test itself, run as ASTM F2057-23 says.
- Doors are not modelled, nor the 10-pound pull of test 9.2.2: the public text does not say where the hand-hold is or whether the drawers are open.
- Neither source gives a sag limit for a furniture shelf, and no search for a public one has been made yet. A design states its own limit, as a requirement with provenance `design-target`, and the check holds the initial deflection to the share of that limit the Wood Handbook's creep guidance leaves (two-thirds for dry wood).

## Using it

A design tree pins the package and mounts the knowledge beside its pieces:

```sh
uv add "furniture-design @ git+https://github.com/xag/furniture-design"
uv run quern --registry <checkout of xag/quern-registry> pin furniture-design@0.3.0
uv run quern --registry <checkout of xag/quern-registry> --natives furniture_design sync
```

```python
import furniture_design                     # registers the calculations
from furniture_design import knowledge

tree.root.children = knowledge() + [pieces]   # sources/, materials/, requirements/ beside your designs

# or, beside a tree's own requirements/, under one branch with every link rewritten:
from furniture_design.knowledge import merge, mount
tree.root.children.append(mount(merge(knowledge(), other_knowledge), "knowledge"))
```

A part made of oak links `uses: ["materials/oak-northern-red"]` and reads its properties as its own. A chest of drawers with `category: "clothing-storage-unit"` must link both stability tests as `stability_case` once it is tall, heavy and large enough for their scope. A shelf links its Table 9–1 case as `bends_as` and its limit as `sag_limit`, and says `span_along: "grain"` (or `"face grain"` for plywood). The materials are six hardwoods (Table 5–3a), a yellow birch plywood flat and the same plywood on its edge (Table 19–2, the one plywood whose test direction the Handbook states), six plywood sheathing species (Table 12–2), MDF and particleboard (the low end of Table 12–1's ranges). The package's examples (`EXAMPLES` in `package.py`) are a worked chest and bookshelf.

To publish a new version, bump `PACKAGE.version` and:

```sh
uv run quern --registry <checkout of xag/quern-registry> --natives furniture_design publish furniture_design/package.py:PACKAGE
```

## Design ledger

The decisions this repo is bound by, with the alternatives turned down, are a quern ledger in `ledger/tree.py`. Read it with the brief, not the source:

```sh
uv sync
uv run quern brief .
uv run quern check     # exits 1 on a red nobody expected
```

There is no flight-recorder boundary: nothing here touches storage, the network, the clock or randomness.

## Tests

`uv run pytest --testmon` runs the tests that failed last time or whose code changed, then `uv run pytest` runs the whole suite. Both stop at the first failure.
