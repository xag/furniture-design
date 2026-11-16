# Been, Daiches, Yap: Dynamic Map Labeling (IEEE TVCG 12(5), 2006, InfoVis 2006)

https://cs.nyu.edu/visual/home/pub/infovis06.pdf (text extracted from the PDF)

> This consists of two interrelated issues. The first is to avoid label popping and other artifacts that cause confusion and interrupt navigation, and the second is to label at interactive speed.

> (D1) Except for sliding in or out of the view area, labels should not vanish when zooming in or appear when zooming out.

> (D2) As long as a label is visible, its position and size should change continuously under the pan and zoom operations.

> (D3) Except for sliding in or out of the view area, labels should not vanish or appear during panning.

> (D4) The placement and selection of any label is a function of the current map state (scale and view area). In particular, it does not depend on the history of how we arrived at that state.

On labelling each frame afresh with a priority order:

> (D1) and (D3) can be violated with this approach. Notice that imposing a global priority order on the labels doesn't help. The source of the problem—the fundamental stumbling block for dynamic labeling—is that from frame to frame the labeling is done on a different set of labels

> Fig. 1. Violations of (D1) under zooming in (a), and (D3) under panning in (b). In both cases, label priority is A > B > C. Initially C is visible. As we zoom out/pan left, C disappears because it conflicts with B. Then C reappears when B disappears because of its conflict with A.

Their remedy:

> It means that each label must be selected precisely within a single scale interval; we call the selected interval for each label its active range
