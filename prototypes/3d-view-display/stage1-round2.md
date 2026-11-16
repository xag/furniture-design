# 3D view display settings: stage 1, round 2 (sound, simple, standard)

What was checked: only the elements that changed after round 1, as `DESIGN.md` and `furniture_design/viewer.py` stand at commit 87fcec6 in the worktree `furniture-design-proto3d` (branch proto-3d-display):

- (a) E2: the block goes behind the Display button when the view is 560 px tall or less, whatever its width;
- (b) E4: the block opens in the sliders' place and the model's area changes, instead of lying over the model;
- (c) E3 and E4: the text button "Affichage" / "Display" with a chevron, at the left of the strip's bottom row, opens and closes the block; Back (through a history step pushed inside the iframe), Escape and a swipe down also close it;
- (d) E5: extension lines from each part's own corner;
- (e) E5: the 12 px margin before a dimension moves to another box edge;
- (f) E6: a solid rest that catches taps, in grey `#8f8b85` without outlines.

The round-1 layers button and the × are gone and are not reviewed. Sources 18 to 25 are new, in `research/`; round 1's sources are cited by their numbers.

Measurements: three scripts run the prototype's own state pages (`mock/states/A-s01-rest.html`, the piece; `mock/states/A-s04-branch-hidden.html`, the branch Grande penderie › Porte avant) in Chromium through Playwright. They are kept outside the repo, in the session's scratch folder: `C:\Users\trans\AppData\Local\Temp\claude\cecbfd0848c6c6bd\b067cca8-78c6-4694-aca9-16a1c32ff886\scratchpad\measure.mjs`, `swipe.mjs` and `backcases.mjs`. A height written "390 × 788" or "320 × 584" is a phone's screen less about 56 px for the head of Soban's full-screen sheet (app.css lines 308–309 and 315–320: 8 px of padding above and below a close button about 40 px tall). That figure is an estimate; a notched phone takes more for its top safe area.

Each finding has three parts: what was read, what the need or the person requires there, and the gap.

## (a) E2: the block behind the button at 560 px tall or less

### F23. The 560 px line fits this piece's short parts list, not the room the list leaves

- **Read.** viewer.py line 84: `@media (max-width: 720px), (max-height: 560px)`. Line 34: the tree takes up to 60 % of the height. DESIGN.md line 57: a low laptop window gets the button. Measured, wide layout, block under the tree: at 1280 × 561 the tools column is 329 px tall and its content (block, step slider, pull-apart slider, Reset) is 329 px: it fits to the pixel. At 1280 × 560 the block goes behind the button, though the column there is 328 px. research/18 (Android window size classes): height is classified on its own, compact height is under 480 dp, "99.78% of phones in landscape".
- **Need.** The owner: "just below the tree on desktop". Round 1's F5: the sliders must stay in reach.
- **Gap.** The wardrobe's parts list is short at every level (two groups, then five rows), so the tree takes little height and the line at 560 px looks exact. For a piece whose list fills its 60 %, the column gets 40 % of the height, and the same 329 px of content needs a view about 823 px tall (329 / 0.4). Between 561 and about 820 px tall, a common laptop height before the browser's own bars are taken off, such a piece shows the block under the tree and its sliders scrolled out of sight beneath it: F5's case remains, hidden by this piece. The rule would follow the need if it compared the tools column's height with the block's and the sliders' heights, rather than the window's height with a fixed number. Separately, a laptop window 560 px tall or less is a desktop in the owner's words and now gets the phone arrangement. That follows from the room it has, but the owner has not been asked.

## (b) E4: the block in the sliders' place

### F24. The model grows at the piece and shrinks in a branch, and its dimensions change with it

- **Read.** DESIGN.md line 67: "the strip grows to the block's height, so the model's area shrinks a little and the model is drawn smaller". Measured at 390 × 844, model area height before and after opening the block: in the branch, 517 to 447 px (14 % smaller); at the piece, 429 to 546 px (27 % larger). At the piece the closed strip holds the assembly step slider with its step text, at least 3.5 lines tall (viewer.py lines 43, 116–120), which is taller than the two-row block (no rest row at the piece). viewer.py lines 136 and 186–189: the camera keeps its vertical field of view, so the model is drawn in proportion to the area's height. research/19 (web.dev): "A layout shift is only bad if the user isn't expecting it", and shifts within 500 ms of the person's input are left out of the measure.
- **Need.** The person opens the block to change what is drawn, and keeps the same model in view.
- **Gap.** The change in size is caused by the person's tap, so by web.dev's measure it is acceptable. The design's sentence is right in a branch and wrong at the piece. And because the rule for drawing a dimension compares its line on screen with its number's width plus 16 px (DESIGN.md line 80), rescaling the model by 0.86 or 1.27 changes which numbers are drawn: a person who ticks Cotes and sees a set of numbers sees a different set once the block closes. The design should say the model grows or shrinks, and that the dimensions follow.

### F25. Inside Soban's sheet the block does not fit at 320 × 640, nor on a phone held sideways

- **Read.** DESIGN.md line 67: "the block fits the strip on a 320 × 640 screen". mock/capture.mjs lines 16–17: the captures use the screen as the view, with no app sheet head. viewer.py line 80: the strip is at most 30 % of the view's height. Measured with the block open in the branch, strip height against content height: 390 × 788, 181 against 181 (fits); 320 × 584, 168 against 181 (13 px scroll); 844 × 334 (a 390 × 844 phone held sideways, which takes the wide layout and the button), 133 against 185 (52 px scroll, the Rest row's three buttons partly out of view). The bottom row is pinned (viewer.py line 91), so the Display button stays in reach in every case.
- **Need.** Opening the block shows all of it.
- **Gap.** The claim was measured on a bare screen. In Soban, the smallest phone scrolls the block by 13 px, and a phone held sideways by 52 px. The captures should be run at the height the 3D view really gets in Soban's sheet.

## (c) E3 and E4: the Display button, and how the block closes

### F26. The Display button is 32 px tall, under the 44 px the design sets for the rows it opens

- **Read.** viewer.py lines 57–58: a button has 6 px of padding around 13 px text; lines 123–124: the Display button and Reset share the bottom row. Measured: Display 92 × 32 px, Reset 87 × 31 px. DESIGN.md line 51: each row "at least 44 px tall". research/05: WCAG 2.5.8 sets 24 px as the floor; the law the design cites also quotes 2.5.5's 44 px.
- **Need.** On a phone this button is the only way to the settings; the owner called the round-1 button "a friction".
- **Gap.** It passes the 24 px floor and falls short of the 44 px the design applies to the rows it opens. Making the bottom row's buttons 44 px tall (Reset too, which has been 31 px since before this design) costs 12 px of strip and brings them in line with the rows.

### F27. The trigger follows the disclosure pattern; its chevron and its word are for the testers

- **Read.** viewer.py lines 73–75 and 123–124: a native `<button>` with `aria-expanded` and `aria-controls="display"`; the chevron's path points up, and it turns 180° while the block is open. DESIGN.md line 61: up while closed, down while open, because the block opens above the row. research/20 (W3C, disclosure pattern): "The element that shows and hides the content has role button", with `aria-expanded` true while shown; Enter and Space toggle it, which a native button does. research/21 (NN/g): "The caret icon most clearly indicated to users that it would open an accordion in place"; the caret tested pointed down, placed right of its label at the screen's edge, and "our results may not generalize to that placement". research/13: a visible text label settles round 1's F6.
- **Need.** The person sees that the button opens something in place, and guesses that dimensions are behind it.
- **Gap.** Nothing in the semantics needs changing. Two things are untested here: a chevron pointing up, which mirrors NN/g's downward caret because the block opens upward; and the word "Affichage" / "Display", which names a category rather than its contents (the owner's own word was "settings"). Both are for stage two: ask the testers to show the dimensions, with no hint.

### F28. A swipe down with a finger does not close the block

- **Read.** viewer.py lines 306–308: the block closes when a `pointerup` arrives 48 px or more below its `pointerdown`. No `touch-action` is set on `#display` or `#tools` (lines 33, 61, 78–80, 87–91), so it is `auto`. research/22 (MDN): "An application using Pointer events will receive a pointercancel event when the browser starts handling a touch gesture"; research/23: no `pointerup` follows. Measured in Chromium with touch emulated (390 × 844 and 320 × 584, block open, an 80 px drag down from the Rest row): the block received `pointerdown` then `pointercancel`, and stayed open. With a mouse the same drag closes it.
- **Need.** DESIGN.md line 69 lists a swipe down among the ways to close the block, and the swipe is a phone gesture.
- **Gap.** On a phone the swipe does nothing: the browser takes the vertical drag as its own scroll and cancels the pointer. Setting `touch-action: none` on the block would make it work, but would also stop the strip from scrolling when the block overflows it (F25). The smallest fix is to take the swipe out of the design: the Display button, which closes the block, is pinned right under it, and Back and Escape remain.

### F29. Closing the 3D view with the block open spends the person's next Back on nothing

- **Read.** app.js lines 1535–1545: closing the app's sheet empties it (removing the iframe), then, when `history.state.sheet` is set, sets `closing = true` and calls `history.back()`; the `popstate` handler returns without doing anything while `closing` is true. viewer.py line 298: opening the block pushes a history step inside the iframe. Measured in Chromium, with a parent page carrying app.js's exact close and `popstate` handlers (`backcases.mjs`): history length 3 with the view open, 4 with the block open. After the app's own Close the parent's `history.state` was still the sheet's and no `popstate` reached the parent: the app's `history.back()` was used up on the iframe's step. The person's next Back then fired the parent's `popstate` with `closing` still true, and the handler swallowed it. That Back press did nothing visible; only the one after it moved on. research/01 (NN/g): Back dismisses the sheet. `mock/backtest.mjs` checks Back and a second Back, not the app's Close with the block open.
- **Need.** Each Back press does one visible thing.
- **Gap.** A case the design's check does not cover, with a step that does nothing. The viewer cannot see the app's Close, so the fix sits on the app's side: when its sheet closes, it can go back by as many steps as were added since it opened, counted by `history.length` at opening, rather than by one. The same leftover step is likely when the wide page replaces the view's iframe (a new version, app.js lines 1167–1176) while the block is open; that case was not run.

### F30. Closing the block calls `history.back()` inside an iframe, which an open WebKit bug turns into a reload of the app

- **Read.** viewer.py line 299: closing by the button, Escape or the swipe calls `history.back()` from inside the iframe. app.js lines 716–720 and 1538: each opening of the 3D view on a phone creates an iframe, and each closing removes it. research/25 (WebKit bug 209753, status NEW, filed against Safari 13): after an iframe is created and removed and another created, `pushState` then `back` inside the new iframe reloads the parent instead of firing `popstate`. mock/backtest.mjs line 15: the design's check ran in Chromium only.
- **Need.** On an iPhone, closing the block leaves Soban as it was.
- **Gap.** The bug's steps are Soban's own sequence the second time a person opens the 3D view on a phone. Whether current Safari still reloads could not be checked here. It needs one run on iOS Safari before landing; if it reloads, closing the block reloads Soban.

## (d) E5: extension lines from each part's own corner

### F31. The extension lines fan out across the model instead of running parallel

- **Read.** viewer.py lines 529–540: each end of a dimension starts at the corner of a part at that position, the one nearest the dimensioned box edge; lines 575–580: the line runs from 3 px off that corner to 4 px past the dimension line, at 55 % opacity, drawn over the model. DESIGN.md line 78. research/24 (LibreTexts): "Usually, the dimension line meets the extension line at right angles", with a gap at the object and an overshoot past the arrowhead.
- **Need.** Round 1's F12: a number names the parts it is between, in a turned view.
- **Gap.** The gap at the corner and the overshoot follow drafting practice, and a part standing on the dimensioned edge gets a short line square to the dimension line, which does name its part. But each line's direction on screen depends on how far its part stands from the box edge across the other two axes. A part set back (at the piece, the back door's frame 29 mm behind the front; along the height, a rail at the top when the edge is at the bottom) gets a long oblique line, so neighbouring ticks of one chain leave in different directions and can cross. Drafting keeps them parallel so the eye can follow each one to its tick. And since everything is drawn over the model (DESIGN.md line 78), a line from a corner hidden behind another part starts on the face of the part in front, which names the wrong part. F12 is answered for parts on or near the dimensioned edge, not for parts set back. Stage two's testers should be asked which parts a chosen number is between.

## (e) E5: the 12 px margin

### F32. The margin keeps numbers still, with two cases it does not cover

- **Read.** viewer.py lines 481–506: the edge in use is remembered per axis and per box (the key is the axis and the box's corners), and kept unless another edge on the outline is lower (or more to the left) by 12 px. DESIGN.md line 78. research/10 (Been et al.): "(D2) As long as a label is visible, its position and size should change continuously", and "(D4) … it does not depend on the history of how we arrived at that state".
- **Need.** DESIGN.md line 78: "turning the model a little never moves a number".
- **Gap.** It meets D2 for small turns, which was round 1's F15. It gives up D4: the same view reached by turning from the left or from the right can put the numbers on different edges, which costs little. Two cases it does not cover: stepping through the assembly changes the box of what is measured, so the key changes, the remembered edge is forgotten, and the numbers can jump at a step; and the margin is 12 px whether the box is 60 px or 600 px tall on screen, so at a far zoom it holds an edge through a larger turn than close up. Both are small.

## (f) E6: a solid rest that catches taps, grey `#8f8b85`, no outlines

### F33. A single tap on the solid rest does nothing, as Onshape does; a double tap still comes close to it

- **Read.** viewer.py line 423: a solid rest is in what a tap can hit; line 443: a hit on the rest hides the tip and selects nothing; lines 428–434: a double tap brings the view close to the point hit, the rest included. DESIGN.md line 89: "a tap on them catches nothing (it neither selects them nor passes to a part they hide)". research/09 (Onshape): non-transparent geometry is what can be selected. Ledger `the-tree-leads-the-3d-views-panel`: "A double tap on the piece turns the view around the point touched and brings it close".
- **Need.** What the person touches is what acts.
- **Gap.** The single tap now does what round 1's F19 asked. A double tap on a solid rest part brings the view close to that part, away from the branch the view was fitted to. That is the double tap's own job, and reasonable, but the design's sentence says the rest "catches nothing". It should say a double tap still comes close.

### F34. Outlines make the difference from the rest; the part new at a step has the grey's luminance

- **Read.** viewer.py line 149: rest `#8f8b85`; line 148: wood `#e6cfa4`, new at this step `#b07a3c`, selected `#f0b45a`; line 171: the branch's outlines `#3b3428`; line 257: the solid rest has no outlines. Contrast against the grey, computed from relative luminance (grey 0.260): wood 2.23 : 1; new at this step 1.09 : 1; selected 1.84 : 1; the branch's outline 3.63 : 1; the light ground `#f6f3ee` 3.06 : 1; the dark ground `#1b1a18` 5.13 : 1. research/17 (WCAG 1.4.1): colour is not the only means of distinguishing an element.
- **Need.** The branch is told apart from the rest, and at an assembly step the part the step brings is told apart too.
- **Gap.** With outlines on the branch and none on the rest, the branch is no longer told apart by colour alone; round 1's F20 holds as answered. One case remains: with the rest solid and the assembly slider on a step, the part the step brings is drawn in `#b07a3c`, which has the grey's luminance (1.09 : 1). Against the rest around it, the step's highlight shows only by hue and outline. This is small, and stage two can show whether it matters.

## Element by element: the changed design beside the research and the code

| Element | What holds | What the research, the code and the measurements add |
|---|---|---|
| (a) E2, the height rule | A height rule at all, as Android's height classes advise for phones held sideways (research/18). At 1280 × 561 the wardrobe's block and sliders fit the column exactly. | The fixed 560 px suits this piece's short list; a piece with a long list buries the sliders up to about 820 px tall. A low laptop window now gets the phone arrangement, which the owner has not been asked about (F23). |
| (b) E4, in the sliders' place | Never covers the model or the dimensions along its foot (round 1's F11 answered). The resize follows the person's tap, so web.dev counts it as expected (research/19). The bottom row stays pinned while the block scrolls. | The model grows at the piece and shrinks in a branch, and the drawn dimensions change with it (F24). Inside Soban's sheet the block scrolls by 13 px on a 320 px phone and by 52 px on a phone held sideways (F25). |
| (c) E3, the Display button | A labelled text button in the strip, nothing over the model: answers the owner's "ugly and a friction" and round 1's F6. A native button with `aria-expanded` and `aria-controls` follows W3C's disclosure pattern (research/20); the chevron turns as NN/g describes (research/21). | 32 px tall against the 44 px of the rows it opens (F26). The upward chevron and the word "Display" are for the testers (F27). |
| (c) E4, closing | Back closes the block and a second Back the view, as checked in Chromium; Escape; the button again. | The finger swipe never closes it (F28). The app's Close with the block open spends the next Back on nothing (F29, measured). An open WebKit bug can turn closing the block into a reload of Soban on iPhone (F30, not checked). |
| (d) E5, extension lines | Gap at the corner and overshoot as drafting does (research/24). Parts on the dimensioned edge are named. | Lines from parts set back fan out and can cross; lines from hidden corners start on the part in front (F31). |
| (e) E5, 12 px margin | Small turns no longer move numbers (D2, round 1's F15 answered). | It depends on the way the view was reached (D4, minor); it forgets the edge at each assembly step; it is fixed in pixels at every zoom (F32). |
| (f) E6, solid rest | A tap on a solid rest selects nothing and passes nowhere, as Onshape does (round 1's F19 answered). Outlines on the branch only, so not colour alone (round 1's F20 answered). | The double tap still comes close to the rest, which the design's sentence does not say (F33). The part new at a step has the grey's luminance (F34). |
