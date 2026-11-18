# 3D view display settings: stage 1, round 3 (sound, simple, standard)

What was checked: only the five elements added since round 2, as `furniture_design/viewer.py` stands at commit 0839441 in the worktree `furniture-design-proto3d` (branch proto-3d-display), with the stills in `stills/c/` whose names start with `_dims-` and the composite sheets `dims-*.png` beside them:

1. "Cotes" becomes a three-way segmented choice, Masquées · Positions · Tailles (en: Hidden · Positions · Sizes), in place of a checkbox (viewer.py lines 109–115, 470, 575);
2. Tailles: each part's own size, in rows outward from the outline, shortest nearest, one size per span, on the nearer of two opposite edges (lines 546–560, 601–613);
3. for both kinds, no line passes through a number and no number lies under a line already drawn (lines 578–590, 622–625);
4. with a mouse (`pointer: fine`) the settings' rows are 32 px tall instead of 44 px (lines 83–86);
5. on a phone, the open settings take the height they need and the tree gives it up (line 81).

Sources 26 to 32 are new, in `research/`; earlier sources are cited by their numbers.

Measurements: three scripts open the prototype's own state pages (`mock/states/C-*.html`) in Chromium through Playwright, kept outside the repo in the session's scratch folder: `C:\Users\trans\AppData\Local\Temp\claude\cecbfd0848c6c6bd\b067cca8-78c6-4694-aca9-16a1c32ff886\scratchpad\m3.mjs` (layout, phone, and every dimension candidate with its row and whether it was drawn, in five views: as captured, from the front, from the right side, from above, from behind), `m4.mjs` (a phone held sideways) and `m5.mjs` (the 3D view at the sizes Soban's wide page gives it). Its output is `m3.json` beside them. A size given for "Soban's wide page" is an estimate from app.css lines 201–214: the page is the window's height (`100dvh`) less 16 px of padding above, the prompt bar and 16 px below it (`--ask-h`, 80 px when unset, line 204), the title row (about 40 px) and a 16 px gap; the 3D view's width is the window less 48 px of padding, a 20 px gap and the side column (`clamp(320px, 24vw, 480px)`). A window's height is the screen less about 48 px of Windows taskbar and about 87 px of Chrome's tabs and address bar, also an estimate.

Each finding has three parts: what was read or done, what the need or the person requires there, and the gap.

## The design record

### F35. DESIGN.md still describes the design before these five elements

- **Read.** `DESIGN.md` line 48: "`☐ Cotes` (en: Dimensions), unchecked by default"; line 51: "The two settings that are on or off stay checkboxes … Each row … at least 44 px tall"; line 67: "On a phone, Connecteurs and Cotes share one row; on the smallest screens … the strip still scrolls by a little"; line 80: the readability rule without the rule about lines and numbers; lines 95–98: "what the dimensions show is the open question", A or B. The code: Cotes is a radio group of three (viewer.py lines 109–115); the row that put Connecteurs and Cotes side by side is gone (the `.pair` rule was removed in 0839441); rows are 32 px with a mouse (lines 83–86); the lines-through-numbers rule is in `marks()` (lines 622–624). The commit message of 0839441 is the only description of the change.
- **Need.** The task: the design record is the claims the code is checked against, and the owner reads it to decide.
- **Gap.** None of the five elements is in the record, and four of its sentences are now false. The record needs E1, E5 and the alternatives rewritten before the next stage: Cotes as a choice of three, Tailles' rule (rows, the side a size stands on, one size per span), the rule about lines and numbers, the 32 px rows with a mouse, and what the phone's settings do to the tree and the model.

## Element 1: Cotes, Masquées · Positions · Tailles

### F36. "Positions" and "Tailles" are drafting's two kinds of dimension; what Positions draws is the gaps between neighbouring edges, not positions

- **Read.** research/27: "Size dimensions are necessary so that the material size of the object can be determined"; "Location dimensions are necessary so that parts, holes, or other features can be positioned". research/28: dimensions from one origin, where "all dimensions start from the same origin". research/15 (Apple): a segmented control is for "closely related choices that affect an object, state, or view", "no more than about five segments on iPhone". viewer.py lines 561–564: Positions draws the overall size and the distance between each pair of neighbouring edge values along each axis. Measured on the wardrobe (`C-s12-wardrobe-chain`, 1280 × 800): the edges along the width are at 0, 8, 553, 600, 1145, 1153 and 1156 mm; the numbers drawn are 1156 and two 545s (8 to 553, 600 to 1145). The plans dimension the same way (sheets.py lines 419–436). The design record: the owner said "So we need both options" only once told "that one kind gives where parts are and the other each part's own size".
- **Need.** The person picks the kind of dimension by its word alone and reads from it what it promises.
- **Gap.** The control itself is sound: three choices in one segmented control, as "Reste du meuble" already is, and "Masquées" keeps the old default. The two words match drafting's size and location dimensions. But a chain gives where a part is only by adding up: the 545 says the back door starts 545 mm after the front door's 8 mm bar, so to know where the back door is from the end a person adds 8 and 545. Dimensions from one origin would give the 553 directly. Either the word should promise what a chain gives, or Positions should measure from one end; keeping the chain has the plans on its side. The owner himself told the two kinds apart only after an explanation, so the two words are for stage two: ask testers to find "how wide is this part" and "where does this part start".

## Element 2: Tailles

### F37. Shortest nearest, as drafting does; a size dropped later still keeps its row

- **Read.** research/26: "the larger dimensions are correctly placed outside, or beyond the shorter dimensions"; the first line "approximately 1/2″ away", the others "approximately 3/8″ apart". research/27: "Keep the smallest dimensions nearest to the object outline". viewer.py lines 604–613: rows per axis and side, the shortest first into the first row where it overlaps no other in mm, the first row 18 px off, the next ones a step apart equal to the number's depth across its line, at least 22 px. Measured, wardrobe at 1280 × 800 as captured: along the width below the outline, 598 at 18 px, 600 (0 to 600) at 52 px, 600 (553 to 1153, overlapping the first by 47 mm) at 86 px, 1156 at 120 px; all drawn. Lines 614–625: the checks that a number is on screen, meets no number and meets no line run after the rows are assigned.
- **Need.** The owner on the first B: "B is unreadable as prototyped"; each size must be readable.
- **Gap.** The order and the spacing follow drafting. One case is left: because the rows are assigned before the drawing checks, a size that is then dropped (its number off screen, or on another) keeps its row, and the rows outside it stay one step farther out over an empty row. It did not occur in the five views measured; assigning rows only among the sizes that pass the checks would remove it.

### F38. Equal sizes are drawn once per part, not once per value

- **Read.** viewer.py lines 551–554: one size per span, the key being the two ends' positions, so only parts that cover the same stretch merge. Measured at the piece (`C-s03-dims-part`, 1280 × 800, as captured): 14 numbers drawn for 8 values: 600, 598, 500 and 498 each twice, besides 1156, 1153, 949, 948, 1141.5 and 1127.5. research/26: "Show each dimension only once"; research/27: "no dimension should be repeated twice", with "ø20 – 2 holes" for identical features; research/28: repeated elements take one dimension with "the number of times the value is repeated, the multiplicative sign X". The parts list already counts identical parts with "× n" (viewer.py line 334).
- **Need.** The person reads each part's size; repeated numbers cost room that shorter sizes need.
- **Gap.** The merge covers parts stacked one behind the other (the front and back rails) but not identical parts side by side (the two doors' bars and sheets). Drafting writes such a size once with its count. Here the two 600s also take two rows (F37), so the 1156 stands four rows out, 120 px off the outline; at 390 × 844 the 1156 and both 600s are dropped while the two 598s stay. Whether one 600 with its count would keep the 1156 on a phone was not measured.

### F39. A full-height part's size goes above or below by its depth, and turning to the back swaps it

- **Read.** viewer.py lines 532–536 and 555: a size stands on the far edge when the part's nearest corner is closer to it than to the near edge, distance measured across the axis in mm, depth and height together. Measured on the wardrobe: the front door's sheet (598 mm, 10 to 16 mm deep) is dimensioned below and the back door's sheet (598 mm, 30 to 36 mm deep) above, as captured and from above; seen from behind the two swap; seen from the front both go below. The code comment: "as an elevation dimensions a top rail above the view and a bottom rail below".
- **Need.** A size stands where the person looks for it, next to its part, and does not jump when nothing about the part has changed on screen.
- **Gap.** The rule does what the comment says for rails, which sit at the top or the bottom. For a part as tall as what is shown, the height difference is nil and 20 mm of depth decides, which the person cannot see from the front: two identical sheets get their sizes 1.1 m apart, and turning the view swaps them. When the part's distances to the two edges differ by little compared with the height shown, it could take the near edge, as the design's other sizes do.

### F40. Tailles measures the parts two levels below the list, so its numbers cannot be found in the list; the standard shows one element's sizes on selection

- **Read.** Stills `_dims-C-s12-wardrobe-part-1280-light.png` and `dims-390-light.png`: in the wardrobe the list shows its rows as Rail bas avant 1156 × 20 × 20, Rail haut avant 1153 × 20 × 20, Porte avant 1143.5 × 600 × 8 (an assembly). The model shows 1141.5 (the polycarbonate sheet), 1127.5 (the frame's upright bars), 600 (the frame's cross bars) and 598 (the sheet's width), from `measured()` (viewer.py lines 480–483), which takes every part under the branch, whatever its depth. 1143.5, the door's height the list gives, is never drawn. Each size names its part only by extension lines from the part's corner to the row, up to 120 px off the outline at 1280 px (F37), and drawn over the model (round 2, F31). research/32 (Revit): "To view the temporary dimensions of an element, click Modify and select the element"; "When you place another element, the temporary dimensions for the previous element no longer display". The tip already gives a tapped part's size (viewer.py lines 453–458).
- **Need.** The owner: "each part's own size". The tree leads the 3D view (ledger `the-tree-leads-the-3d-views-panel`): the rows shown are what the person reads as "the parts".
- **Gap.** At the piece and in a wardrobe the person sees sizes of parts that are not rows of the list, and does not see the size of a row that is (the door, 1143.5). Two ways would make each number findable: measure the rows of the list at this level (an assembly as its box, as its row's size is given), or draw the sizes of the selected row only, beside it, as Revit does for a selected element, which also removes the rows, the side rule (F39) and the repeats (F38). Which of the two "each part's own size" means is the owner's to say; stage two should ask testers which part a chosen number belongs to.

## Element 3: no line through a number

### F41. The rule follows drafting; Positions keeps fixed offsets, so a vertical chain number is always dropped beside the overall

- **Read.** viewer.py lines 622–625: a dimension is skipped when its extension or dimension lines pass through a number already drawn, or a line already drawn passes through its number. research/28: "Dimension lines must not cross anything"; research/26: "the dimension line is usually broken near the middle to provide open space for the dimension numerals", and numbers read from the bottom ("unidirectional … is usually best"), as here (always upright). Lines 563–564: Positions puts its chain 18 px off and the overall 40 px off on every axis. Lines 604–607: Tailles spaces its rows by the number's width across a vertical line. Measured on the wardrobe in Positions: along the height the overall 1153 is drawn, and the chain's 1113 (between the bottom rail and the top rail) never is, in all five views, though its line is 156 to 616 px long. Its upright number, about 36 px wide, stands 22 px from the overall's, at the same height, and the two overlap.
- **Need.** Both kinds readable, as the owner asked "only those readable at current zoom level", and a longer line is readable.
- **Gap.** The new rule itself matches drafting. The fix that keeps a number clear of the next row was made for Tailles only. On the vertical axis Positions loses the middle of every chain whose number falls level with the overall's; spacing Positions' two rows the way Tailles spaces its rows would keep it.

## Element 4: 32 px rows with a mouse

### F42. A denser layout for a mouse is standard; the media query reads the primary pointer only

- **Read.** viewer.py lines 83–86: `@media (pointer: fine)` sets the checkbox row and the segments to 32 px. research/30: "Compact - designed primarily to accommodate pointer input"; research/31: "Targets should have more precise sizing", "Pointer targets can be smaller than the standard 48 x 48 dp touch target". research/05: WCAG 2.5.8's floor is 24 px. research/29 (MDN): `pointer` tests "how accurate the _primary_ pointing device is"; "use `any-pointer`" to test any. Measured: the checkbox row and the segments are 32 px in a mouse context and 44 px in a touch context; the Display and Reset buttons were already 32 px (round 2, F26).
- **Need.** The settings fit under the tree on a laptop (the commit message), and stay easy to hit.
- **Gap.** Sound and standard, and the rows now match the buttons beside them. A laptop with a touch screen and a trackpad reports its primary pointer, most often fine, so its finger gets 32 px rows: above the 24 px floor, under the 44 px the design set for touch. That is small; `(any-pointer: coarse)` would keep 44 px for it if the owner wants that.

### F43. The settings fit under the tree at a 1280 × 800 view, not on a 1280 × 800 screen, and not in Soban's wide page

- **Read.** mock/capture.mjs line 16: the wide cell is a 1280 × 800 viewport, the whole screen with no browser bars. viewer.py lines 313–317: the block goes behind the Display button when the tools do not fit their place. Measured, with a mouse, whether the block stands under the tree:

| 3D view size (what it stands for) | Piece | Branch Porte avant | Wardrobe |
|---|---|---|---|
| 1280 × 800 (the captures) | under | under | under |
| 1366 × 768 | under | under | button |
| 1280 × 665 (a 1280 × 800 screen in Chrome, estimate) | under | under | button |
| 1026 × 597 (Soban's wide page on a 1440 × 900 screen, estimate) | under | under | button |
| 970 × 465 (Soban's wide page on a 1366 × 768 screen, estimate) | button | button | button |
| 892 × 495 (Soban's wide page on a 1280 × 800 screen, estimate) | button | button | button |

  In the wardrobe the tree takes 398 px (two title lines and six rows) and the tools need 401 px; with 44 px rows the wardrobe needed the button even at 1280 × 800. Soban's wide page applies from a window 1200 px wide and 600 px tall (app.js line 1147).
- **Need.** The owner: "I'd say it goes just below the tree on desktop".
- **Gap.** The 32 px rows bought the wardrobe at exactly the captures' 1280 × 800 view, which is a full screen with no browser. On a laptop the 3D view lives in Soban's wide page, where it is 465 to 600 px tall: there the block is behind the button for every state on a 1280 × 800 or 1366 × 768 screen, and in the wardrobe on a 1440 × 900 screen. Only Soban's "Full screen" (app.js line 1204) gives the view a laptop's height. The fallback works, but the placement the owner asked for is what a laptop user will rarely see. The claim should say this, and the captures should include the size Soban's wide page gives on a common laptop; making the tree give up height on a wide screen too (as element 5 does on a phone) is what would keep the block under it.

## Element 5: on a phone, the open settings take their height

### F44. The model gives up its height first, and the tree only once the model is at its floor

- **Read.** viewer.py line 81: while open, the tools are `max-height: none; flex: none`; lines 78–79: the tree has at most 38 %, the model `flex: 1` with at least 34 %. In a column, the model grows from nothing into whatever the tree and the tools leave, and the tree shrinks only when the model would go under 34 %. Measured with the block opened (touch, heights less Soban's sheet head where marked):

| Phone, state | Tree before → after | Model before → after | Tools after (content) |
|---|---|---|---|
| 390 × 788, branch Porte avant | 214 → 214 | 461 → 316 | 256 (256) |
| 375 × 611, branch Porte avant | 214 → 145 | 284 → 208 | 256 (256) |
| 320 × 584, branch Porte avant | 221 → 127 | 250 → 199 | 256 (256) |
| 390 × 788, wardrobe | 298 → 262 | 268 → 268 | 256 (256) |
| 320 × 584, wardrobe | 221 → 127 | 199 → 199 | 256 (256) |

  At 127 px the tree still shows the title that leads back up and the size line (they end 79 px down), and about one row. Ledger `on-a-narrow-screen-the-tree-stands-above-the-model`: "The tree takes at most 38% of the height". research/01 (NN/g): a nonmodal sheet presents options "in parallel with the main information on the screen".
- **Need.** The person changes what the model shows and watches the model change.
- **Gap.** The settings no longer scroll on a phone in portrait: round 2's F25 is answered there. But the model gives up first: on a 390 px phone in a branch it loses 31 % of its height while the tree keeps all of its own, and the dimensions drawn change with the scale (round 2, F24). The sentence "the tree gives it up" holds only on the smallest phones. Giving the tree a lower floor (its title and size line, about 80 px) and letting it shrink before the model would match the sentence and the need.

### F45. A phone held sideways is not covered, and its settings now scroll by 127 px

- **Read.** viewer.py line 76: element 5 is inside `@media (max-width: 720px)`; a phone held sideways is wider and takes the wide layout, where the tree keeps up to 60 % (line 34). Measured at 844 × 334 (a 390 × 844 phone sideways in Soban's sheet), touch, block open, branch Porte avant and wardrobe: the tree 200 px, the tools 133 px tall for 260 px of content. Round 2 measured 52 px of scroll there; the Cotes row is now a label over three 44 px segments, taller than the checkbox it replaced. The bottom row stays pinned (line 94).
- **Need.** Opening the settings shows all of them (round 2, F25).
- **Gap.** On a phone held sideways the "Reste du meuble" row is wholly out of view until the strip is scrolled, and the tree keeps 200 px that the settings need. Applying element 5's rule wherever the block opens from the button (`.tight`), not only under 720 px wide, would cover it.

## Element by element: the design beside the research and the code

| Element | What holds | What the research, the code and the measurements add |
|---|---|---|
| Record | | DESIGN.md describes none of the five elements, and four of its sentences are now false (F35). |
| 1. Cotes, three choices | One segmented control of three, as the rest row (research/15); the old default kept; the words are drafting's size and location (research/27). | Positions draws the gaps between neighbouring edges, which give where a part is only by adding up (research/28); both words for stage two (F36). |
| 2. Tailles | Shortest nearest, rows spaced by the number's depth, as drafting stacks dimensions (research/26, 27); measured four rows clear of each other. | A dropped size keeps its row (F37). Equal sizes side by side are drawn twice, where drafting writes them once with a count (F38). Full-height parts go above or below by their depth and swap when turned (F39). The numbers are of parts two levels below the list, so they cannot be matched to a row; the standard shows the selected element's own sizes (research/32) (F40). |
| 3. No line through a number | Matches "Dimension lines must not cross anything" (research/28). | Positions kept its fixed 18 and 40 px offsets: on the vertical axis the chain's middle number is always dropped (F41). |
| 4. 32 px with a mouse | Compact sizing for a pointer is standard (research/30, 31), above WCAG's 24 px (research/05); the rows now match the buttons. | The primary pointer only (research/29): a touch laptop's finger gets 32 px (F42). Fits under the tree only at a full-screen 1280 × 800 view, not in Soban's wide page on common laptops (F43). |
| 5. Phone, settings take their height | No scroll on a phone in portrait (round 2's F25 answered there); the title and size line stay. | The model gives up first, the tree only at the model's floor (F44). A phone held sideways is not covered and scrolls by 127 px (F45). |
