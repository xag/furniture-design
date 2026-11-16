# 3D view display settings: stage 1, round 1 (sound, simple, standard)

What was checked: the written design (`DESIGN.md`) against the viewer's code (`furniture_design/viewer.py`), the plans' dimensioning (`furniture_design/sheets.py`), the app that embeds the viewer (`furniture/app/web/app.js`, `app.css`, `index.html`, `overlay3d.html`), both ledgers (`quern brief` in furniture-design-proto3d and in furniture), the prototype's real piece (the wardrobe doors' scene data inside `mock/before.html`), and seventeen published sources (in `research/`, one file each).

Words used below, as the design uses them: a *branch* is an assembly or a part opened from the tree (the view then shows it alone, `go()` / `under()`, viewer.py lines 151–154, 319–325); *the rest* is every part outside the open branch; the *strip* is the tools area at the foot of the view on a narrow screen (viewer.py line 63); a *chain* is the row of distances between neighbouring part edges along one axis (sheets.py lines 401–436).

Each finding has three parts: what was read, what the need or the person requires there, and the gap. Heights marked "estimated" are added up from the CSS values cited, not measured in a browser.

## E1. The display settings block

### F1. Checkboxes for settings that act at once

- **Read.** DESIGN.md lines 46–47: Connectors and Dimensions are checkboxes. viewer.py line 84: Connectors is a checkbox today, and line 226 applies it on `input`, at once. research/04 (NN/g): "Toggle switches should take immediate effect"; the article's table gives a checkbox's moment as "After a user clicks a submit button". research/16 (model-viewer): its dimensions are shown by `<input id="show-dimensions" type="checkbox">` labelled "Show Dimensions:". research/06: SketchUp's dimension options are checkboxes too.
- **Need.** DESIGN.md line 62: "each setting takes effect as it is changed".
- **Gap.** Small. NN/g's guidance points to a switch for a setting that acts at once; the page's own Connectors control and model-viewer's dimension control use a checkbox. Keeping the checkbox keeps the block consistent with the existing row. The design does not say the choice was weighed; it should, in one line.

### F2. The rows inherit the captions' style

- **Read.** viewer.py line 41: `label { font-size:13px; color:var(--muted); display:block; margin:14px 0 4px; }`, the style of the slider captions ("Écarter les pièces"). DESIGN.md line 36: Connectors "becomes a `<label>` around its checkbox, as the two new rows are". DESIGN.md line 50: each row at least 44 px tall, the whole row the target.
- **Need.** A row the person taps must read as a control, not as a caption over the next control.
- **Gap.** The design does not say how a row looks (ink or muted text, box left or right, padding). Built as written, each row picks up the muted caption style and its 14 px top margin, so the three rows read as three headings. The design should give the rows their own style and say it.

### F3. The third row appears and disappears above the sliders

- **Read.** DESIGN.md line 48: the "Rest of the piece" row is drawn only while a branch is open. viewer.py line 201 and ledger entry `the-tree-leads-the-3d-views-panel` ("with fewer than two the slider is not drawn"): the product already hides a control that can change nothing. research/14 (Unity Editor guidelines): "Hide input controls … when the value shown is currently irrelevant and not used" and "always place the hidden control somewhere below the control that triggers the hiding".
- **Need.** The owner: "display unselected elements (when a branch of the tree is selected)". Hiding the row at the piece itself follows that and follows the product's own rule for the assembly slider.
- **Gap.** On a wide screen the block sits above the sliders (DESIGN.md line 54), so every time the person opens a branch or goes back to the piece, the sliders under it move down or up by the height of that row (a label over a 44 px control: about 65 px, estimated). The assembly block already moves them the same way, so this adds to an existing shift rather than creating one. The design does not mention it.

### F4. Settings are lost every time the view is opened on a phone

- **Read.** DESIGN.md line 50: "Settings are not remembered across page loads". app.js lines 716–720: each opening of the 3D view card on a phone makes a new `<iframe>`. app.js lines 1167–1176: on a wide screen the iframe is kept only while its address is unchanged, so another version reloads it. app.js lines 1190–1194: crossing the 1200 px width rebuilds the page and its iframe.
- **Need.** The record does not say whether the person expects the settings to last. The owner's words name the options, not their lifetime.
- **Gap.** An open question, not a defect: a person who always wants dimensions will tick them each time they open the view on a phone. Ask the owner whether that matters before choosing either way.

## E2. Wide screen: where the block stands

### F5. On a short window the block pushes the sliders out of view, and a phone held sideways gets the wide layout

- **Read.** DESIGN.md line 54: the block at the head of `#tools`, before the sliders. viewer.py line 34: the tree takes up to 60 % of the view's height; line 33: `#tools` scrolls (`overflow:auto`); line 43: the step text is at least 3.5 lines tall; line 59: the narrow layout depends on width alone (720 px). app.js line 1130: the app's page layout with the view beside the column starts at 1200 × 600.
- **Need.** The owner put the block "just below the tree on desktop". The sliders already there must stay within reach.
- **Gap.** The design gives no rule for height. Two cases it was not built for:
  - A laptop window near 600 px tall: the view's iframe is a few hundred pixels tall, the tree takes up to 60 % of it, and the block (two 44 px rows and a captioned 44 px control, about 160 px, estimated) takes most of what is left, so the sliders sit under it, scrolled out of sight.
  - A 390 × 844 phone held sideways: the iframe is about 844 px wide, so the viewer draws its wide layout (model left, 300 px column right) on a view about 340 px tall (390 less the app's sheet head, estimated). The tree takes up to about 204 px, leaving about 136 px for the block and both sliders.

## E3. Narrow screen: the button

### F6. The "layers" icon, the owner's "settings button", and no visible label

- **Read.** DESIGN.md line 58: a 44 × 44 round button, the Material Symbols "layers" glyph, accessible name "Affichage" / "Display". The owner: "small settings button above or over (right hand corner) the view". research/12 (Google Maps): "At the top right, tap Layers", which opens "Map type" and "Map details", the same kind of choice (what is drawn). research/13 (NN/g): only home, print and search icons are recognised everywhere; "a text label must be present alongside an icon to clarify its meaning in that particular context".
- **Need.** The person must find the display options from the button alone, on a phone.
- **Gap.** The layers glyph follows the best-known button for the same job (Google Maps, same corner); a gear would follow the owner's word "settings". The design does not record why it chose one over the other. Neither has a visible label, which NN/g says leaves any icon but three ambiguous. The blind testers in stage 2 should be asked to find dimensions from the button with no hint; that answers it better than a choice made here.

### F7. Where the glyph comes from

- **Read.** viewer.py lines 6–7: the page loads three.js from cdnjs and OrbitControls from jsDelivr, by exact version, and nothing else. DESIGN.md line 58: "the Material Symbols 'layers' glyph".
- **Need.** The page stays one self-contained HTML file with only the two script loads it has.
- **Gap.** The design does not say the glyph is drawn as inline SVG. Loading the Material Symbols font would add a third outside load. One line in the design settles it.

### F8. Two "Close" buttons on one screen, one of which throws the view away

- **Read.** index.html lines 59–64: the app's sheet has a ✕ button, `aria-label="Close"`, at the right of its head. app.css lines 315–319: on a phone the 3D view's sheet fills the screen with that head on top. DESIGN.md line 62: the viewer's sheet has its own ×, "Fermer" / "Close", at its top right. research/01 (NN/g): bottom sheets "should not be used on top of other bottom sheets".
- **Need.** The person closes the display settings and keeps the model, with the settings they chose.
- **Gap.** In a piece written in English both buttons are named "Close", both drawn as a cross at the top right of their area. The app's one closes the whole 3D view, and since settings are not remembered (F4) the choice is lost with it. The viewer's sheet is a sheet inside the app's full-screen sheet; the app's sheet does not look like a sheet on a phone, which softens NN/g's warning but does not remove the naming clash. The design should either drop the viewer's × (the layers button already toggles the sheet, and Escape closes it) or name it for what it closes ("Fermer l'affichage" / "Close display").

## E4. Narrow screen: the sheet

### F9. The phone's Back gesture closes the whole 3D view, not the sheet

- **Read.** app.js lines 1535–1545: the app's sheet is a step in the browser history, and Back (`popstate`) closes it. DESIGN.md line 62: the viewer's sheet closes by its ×, the layers button and Escape; Back is not mentioned. research/01 (NN/g): "supporting the use of Back for dismissing the bottom sheet" "(such as the phone's Back button or the Back gesture)".
- **Need.** On a phone, Back undoes the last thing opened, which here is the settings sheet.
- **Gap.** As designed, Back closes the app's 3D view sheet with the model in it. The design should say what Back does. Whether a history entry pushed inside the iframe reaches the app's `popstate` handler first or the iframe's needs a check in a real browser before anyone relies on it.

### F10. No swipe down to close

- **Read.** research/03 (Apple): "Support swiping to dismiss a sheet. People expect to swipe vertically to dismiss a sheet instead of tapping a dismiss button." research/02 (Material): a drag handle that taps through states and hides on double tap. DESIGN.md line 62: no swipe, no handle.
- **Need.** A phone person closes a sheet the way phone sheets close.
- **Gap.** Small. The sheet sits over the strip, not over the model's canvas, so a swipe on it would not fight the orbit controls; the design can add it or say why not.

### F11. The sheet is tallest exactly where the strip is shortest

- **Read.** DESIGN.md line 62: "as tall as its rows (the three rows fit in the strip's height on a 390 × 844 phone)". viewer.py line 63: the strip is as tall as its content, at most 30 % of the view; line 201: the assembly step slider is not drawn when the branch has fewer than two steps. The wardrobe's scene data (`mock/before.html`): three assembly steps; a door, a rail or a frame branch is brought in by one step, so none of them draws the step slider.
- **Need.** DESIGN.md line 32: the sheet rises "over the strip of sliders, leaving the model in view".
- **Gap.** The third row exists only inside a branch, and in this piece the branches where the rest of the piece matters most (a door, a rail, a frame) have no step slider. There the strip, once Connectors leaves it, holds the pull-apart caption and slider and Reset: about 106 px (estimated: caption 34, slider 21, Reset row 39, padding 12). The sheet holds two 44 px rows and a captioned 44 px control: at least about 152 px before padding. So the sheet covers roughly the bottom 50 px of the model or more, which is where the dimensions along the bottom of the box would be drawn (E5). The claim on line 62 holds at the piece itself (three steps, slider drawn, two rows in the sheet) and fails in the branches. The design also does not say whether the sheet lies over the strip (the model's area unchanged) or takes the strip's place in the layout (the model's area changes, `fit()` runs, viewer.py line 184, and the model jumps); it should say which, and what happens when the third row appears while the sheet is open.

## E5. Dimensions on the model

### F12. In a turned 3D view, a chain's tick no longer points at the part edge it measures

- **Read.** DESIGN.md lines 66–71: a chain of every distinct part edge along each axis, on one edge of the box of what is shown, "extension lines back to the box". sheets.py lines 405–436: the plans draw chains on first-angle front and left views, where every part edge projects to a straight line meeting its tick; the top view gets no chain (line 464). viewer.py line 97: the 3D view uses a perspective camera that the person turns freely. Ledger `the-documents-are-for-the-people-who-build`. The wardrobe's data: along its width, 26 edge positions, 25 distances, 18 of them under 20 mm; for one wardrobe (Grande penderie) the distances are 1, 7, 545, 1, 7, 31, 7, 1, 545, 7, 1, 3.
- **Need.** A person reading a number needs to know which parts it is between.
- **Gap.** In an orthographic plan view, each tick lines up with the edge it marks. In a turned perspective view, the extension line runs to the box, not to the part: a tick at 553 mm on the box's bottom front edge has nothing drawn between it and the back door's edge, which sits 29 mm back and 2 mm up. The design takes the plans' method without the axis-aligned view that makes it readable. It also adds a chain along the depth that the plans do not draw: 14 distances of 1 to 7 mm for this piece.

### F13. Zooming in on a detail shows no dimension

- **Read.** DESIGN.md line 71: every dimension is drawn outside the box of what is shown, offset from it. viewer.py lines 341–350: a double tap brings the view close to the point touched (to 0.3 of the distance). The owner: "display measurements (only those readable at current zoom level)".
- **Need.** Zooming in should bring in the short measurements that were too small to read.
- **Gap.** Close up on the middle of a door, the edges of the box are off screen, so nothing is drawn, even though the short distances now pass the length test. The design does not say what happens to a dimension whose line runs partly off screen, or whose number's place is off screen. Alternative B (each part's own size on its own edges) answers this case, since a part's edges are near what the person zoomed on; A does not.

### F14. The overlap test makes numbers appear, vanish and come back while zooming

- **Read.** DESIGN.md line 73: a dimension is drawn when its line on screen is longer than its number's width plus 16 px and its number does not overlap a number already drawn; numbers are placed overall first, then the chain "from the longest down". research/10 (Been et al.): "(D1) Except for sliding in or out of the view area, labels should not vanish when zooming in or appear when zooming out", and "imposing a global priority order on the labels doesn't help", with the case "C disappears because it conflicts with B. Then C reappears when B disappears because of its conflict with A."
- **Need.** The design's own promise on line 73: "zooming in brings the short ones in and zooming out drops them".
- **Gap.** With the overlap test run each frame, a short number already drawn can vanish while zooming in, when a longer neighbour passes its length test and takes the space, and come back later: Been et al.'s figure 1. "Longest" is also undefined: in millimetres the order is fixed; in screen pixels it changes as the view turns, and numbers swap. The design should order by millimetres and should state the case of two neighbours on one line, whose overlap can be decided from their millimetre lengths and the scale alone.

### F15. The dimension line jumps from one box edge to another as the view turns

- **Read.** DESIGN.md line 71: for each axis, of the four box edges parallel to it, the one on the outline nearest the bottom of the screen (or the leftmost, for the vertical axis), "projected to the screen every frame". research/10: "(D2) As long as a label is visible, its position and size should change continuously". viewer.py line 181: the home view looks from about 45° to the side, where two box edges are close to level on screen.
- **Need.** A number the person is reading stays put while they turn the model slightly.
- **Gap.** When two edges pass each other in height on screen, every dimension of that axis jumps to the other edge in one frame. The design gives no margin (keep the current edge until the other is lower by some pixels). The length test does cover dimensions seen end-on, which SketchUp handles with a separate "Hide When Foreshortened" option (research/06): a dimension seen from its end is short on screen and so is not drawn. That part holds.

### F16. Drawn over the model or hidden behind it

- **Read.** DESIGN.md line 71: "dimension lines are drawn in 3D projected to the screen". research/16 (model-viewer): lines drawn on an overlay "cannot support occlusion in the 3D scene, as it always draws on top of the model", and "because the text is not part of the 3D rendering it is easier to read".
- **Need.** A dimension the rule draws is seen.
- **Gap.** The design does not say whether the lines are hidden by parts in front of them. With the rest drawn solid (E6), lines along the branch's box can fall behind grey parts. The design should say they are drawn on top.

### F17. The overall size repeats the line under the title

- **Read.** viewer.py lines 257–258: the line under the title already gives the size of what is shown ("V7 · 2402 × 40 × 1153 mm"). DESIGN.md line 68: the overall size of what is shown, on each axis.
- **Need.** Simplicity: each number on the model should tell the person something the panel does not.
- **Gap.** Small. On the model, the overall sizes add which axis each number belongs to, which the line under the title does not show. Keep them, but the information that only the 3D view can now give is the chain (positions), which F12 says is hard to read there.

### Alternative B: each part's own size

### F18. B repeats the list and the tap box, and answers F12 and F13

- **Read.** DESIGN.md line 91. viewer.py lines 244–245: each part's row already gives its three sizes; lines 361–362: a tap on a part shows its size. The wardrobe's data: one wardrobe (Grande penderie, 18 parts) gives 54 candidate numbers, many identical (the frame bars E and F each come four times), and parts nest (a U inside its angle), so their numbers overlap.
- **Need.** Measurements readable at the current zoom, for people who build.
- **Gap.** B's numbers are all in the list and the tap box already; what B adds is their place on the model, which solves F12 (each number sits on its part) and F13 (a close view shows the sizes of the parts in it). A's chains give positions, which nothing else in the viewer gives (they are only in the plans), but read badly in a turned view (F12). The design sets A and B as exclusive. Neither alone serves both "where" and "how big" at a close zoom; that trade is the owner's to make, and the design should put it to him in those terms.

## E6. The rest of the piece

### F19. Solid rest hides the branch, and a tap on it picks the part hidden behind it

- **Read.** DESIGN.md lines 82–84: the rest drawn opaque in grey, the view fitted to the branch, "a tap never picks a part of the rest (taps pass through it)". viewer.py lines 166–178: a bar is shown from its end, from the front and to the left, at five times its section. The wardrobe's data: the back bottom rail (y 20–40 mm) lies directly behind the front bottom rail (y 0–20 mm), same height, same length. research/11 (Elmqvist and Tsigas): "Make targets visible through intervening distractors by turning occluding surfaces invisible or semi-transparent." research/09 (Onshape): "When unchecked, only non-transparent geometry can be selected", so a solid part catches the tap.
- **Need.** The owner asked for the rest "solid"; the person must still see and touch the branch.
- **Gap.** Opening the back rail with the rest solid puts the grey front rail between the eye and the branch, at the very view the design fits to the branch. And because taps pass through, a tap on the grey front rail selects the back rail's hidden part and opens its tip: the person touched one thing and got another. The design does not address hiding by the solid rest. The simpler rule, and the one Onshape follows, is that a tap acts on what it touches: in Solid, a tap on the rest selects nothing and passes nowhere; in See-through it passes through.

### F20. Light grey and pale wood differ by colour only

- **Read.** DESIGN.md line 82: the rest "in a light grey instead of the wood colour, so the branch stays the one thing in wood". viewer.py line 109: wood `#e6cfa4`. Relative luminance computed: wood 0.641; `#d9d9d9` 0.694, contrast 1.08 : 1; `#bfbfbf` 1.21 : 1; `#8a8a8a` 2.27 : 1; reaching 3 : 1 against the wood needs a grey near `#767676` or darker. research/17 (WCAG 1.4.1): colour "is not used as the only visual means of … distinguishing a visual element", unless the difference in luminance reaches 3 : 1.
- **Need.** The person tells the branch from the rest at a glance, including people who see colour poorly.
- **Gap.** A light grey has about the wood's luminance, so the two differ by saturation alone. The design gives no value for the grey. Lighting shades both, so 3 : 1 is a guide here rather than a computed guarantee, but a light grey is far below it.

### F21. A second see-through look and a second word for it in one product

- **Read.** DESIGN.md line 81: the rest at 15 % opacity, edges at 25 %, colour not stated. overlay3d.html lines 44–46: Compare draws the other version's boards in the accent colour at 30 %, without depth writing. app.js lines 1611–1612 and ledger entry `a-version-is-compared-with-another-on-its-figures-and-in-3d`: those boards are "drawn see-through in the accent, with Faint buttons". research/07 and research/09: SolidWorks and Onshape call this "Transparent". DESIGN.md line 48: "Transparent" in French, "See-through" in English.
- **Need.** One way of drawing "less present" parts and one word for it across Soban's 3D views.
- **Gap.** The design adds a second look (15 %, in an unstated colour) and a third word: Compare says "Faint", the CAD tools and the design's own French say "Transparent", the design's English says "See-through". The viewer belongs to a public library that must not refer to the app (ledger `the-method-is-public-and-names-no-home`), so it cannot borrow the app's code, but the words and the look can agree. The design should state the see-through colour, and pick one English word ("Transparent" matches the French and the CAD tools).

### F22. The branch moves inside a rest that does not move

- **Read.** DESIGN.md line 84: the assembly steps and pulling apart act on the branch only; the rest stays finished and in its place. viewer.py line 215: each part moves from the middle of what is shown by the slider's share, plus its own split from its holder (lines 288–318).
- **Need.** What the person sees while pulling apart or stepping through stays readable.
- **Gap.** Small, and to be checked in the prototype: with the rest drawn solid and still, pulled-apart branch parts can travel into rest parts and vanish inside them; and at an early assembly step the finished rest stands around a half-built branch, a state that never exists on the bench. The design could hide the rest while the slider is above 0, as it already hides dimensions then (line 75).

## Element by element: the design beside the research and the code

| Element | What holds | What the research and code add |
|---|---|---|
| E1 block | Serves both requested options; Masqué default changes nothing for whoever never touches it; the third row's visibility follows the product's own rule for the assembly slider (ledger `the-tree-leads-the-3d-views-panel`) and Unity's hide-when-irrelevant rule; "Cotes" / "Dimensions" are the plans' words (sheets.py lines 49, 80); Connectors moving to a 44 px row fixes its 13 px target (WCAG 2.5.8, research/05). Concepts to learn: two new ones (dimensions, the rest) and three mode words. | Checkbox kept against NN/g's switch advice, defensibly (F1); row style unspecified (F2); the third row shifts the sliders (F3); settings lost on every phone opening, a question for the owner (F4). |
| E2 wide | Where the owner put it. | No height rule: short windows and phones held sideways bury the sliders (F5). |
| E3 button | Corner and size follow the owner and Google Maps' layers button (research/12); 44 px meets the thumb-size law the design cites; the tip box (left, at most 70 % wide, viewer.py lines 54–55) and the button do not meet on a 390 px view (12 + 273 px against 334 px). | Layers glyph against the owner's "settings button", no visible label (F6); glyph's delivery unstated (F7); a second "Close" beside the app's (F8). |
| E4 sheet | Non-modal is what NN/g, Material and Apple recommend for options acting on the view behind (research/01, 02, 03); the × and Escape match NN/g and Onshape. | Back closes the whole view (F9); no swipe (F10); the height claim fails in branches, and overlay against in-flow is unstated (F11). |
| E5 dimensions, A | Measuring only what is shown, only the parts drawn at the step, and nothing while pulled apart, is sound and consistent with the code; the length test matches SketchUp's "Hide When Too Small" and covers "Hide When Foreshortened" (research/06); model-viewer shows dimensions on bounding-box edges facing the camera (research/16), as A's overall sizes do. | Chains lose their parts in a turned view (F12); nothing at a close zoom (F13); appear-vanish-return from the overlap test, "longest" undefined (F14); jumps between box edges (F15); on top or hidden, unstated (F16); overall sizes repeat the subtitle (F17). |
| E5, B | Each number on its own part; works close up. | Repeats the list and the tap box; many overlapping numbers; trade against A is the owner's (F18). |
| E6 rest | "Rest of the piece" is SketchUp's own phrase ("Rest of Model", research/08); hidden / transparent as SolidWorks and Onshape offer (research/07, 09); taps passing through a see-through rest match Onshape's default; connectors and fit limited to the branch keep the existing code paths. | Solid hides the branch and passes taps to what is hidden (F19); grey too close to the wood (F20); a second see-through look and word (F21); branch moving inside a still rest (F22). |
