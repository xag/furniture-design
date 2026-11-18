"""furniture-standards@ (furniture_design/standards.py): a tool is certified by running the package's
criteria and levels on it (quern.certify), and the package passes quern's publish gate."""

from quern import Quern
from quern.certify import certificate
from quern.library import validate_package

from furniture_design import standards
from furniture_design.standards import PACKAGE, _document, _world, example_tool

TOOL = "tools/example-sander"


def cert(*args, **kw) -> dict:
    t = Quern(vocabulary=standards.VOCABULARY, rules=standards.RULES, solvers=standards.SOLVERS)
    t.root.children = _world(*args, **kw)
    return certificate(t, TOOL)


def reached(c: dict) -> list[str]:
    return [p.rpartition("/")[2] for p in c["reached"]]


def test_the_package_passes_the_publish_gate(tmp_path):
    log = validate_package(PACKAGE, tmp_path, standards.library())
    assert any("a-tools-figures-each-rest-on-two-observations" in line for line in log)


def test_a_tool_read_from_two_documents_with_a_true_model_reaches_every_level():
    assert reached(cert()) == ["tool-listed", "tool-cuts-parts", "tool-in-instructions", "tool-shared"]


def test_a_tool_read_from_one_manual_is_used_where_it_is_fit_and_told_what_closes_it():
    """One document vouches for each figure: it cuts parts and is drawn, and is not taken into the shared
    packages; the red is the rule's own sentence and the figures it counted."""
    c = cert(example_tool(documents=("manual",)))
    assert reached(c) == ["tool-listed", "tool-cuts-parts", "tool-in-instructions"]
    [closed] = [k for k in c["criteria"] if k["criterion"] == "standards/tool-figures-are-closed"]
    [red] = closed["reds"]
    assert red["says"].startswith("Close every figure") and "pad_diameter: 1 of 2 (sources/manual)" in red["why"]


def test_a_tool_without_a_model_is_not_drawn_and_still_cuts_parts():
    c = cert(example_tool(model={}))
    assert reached(c) == ["tool-cuts-parts"]
    [listed] = [lv for lv in c["levels"] if lv["level"] == "standards/tool-listed"]
    assert listed["blocked_by"] == ["standards/tool-is-drawn"]


def test_figures_nobody_found_printed_reach_no_level_that_reads_them():
    c = cert(documents=[_document("manual", grounded=False), _document("page", grounded=False)])
    assert reached(c) == ["tool-listed", "tool-in-instructions"]


def test_a_document_that_prints_another_value_is_named():
    c = cert(documents=[_document("manual"), _document("page", 150.0)])
    whys = [w for k in c["criteria"] for r in k["reds"] for w in r["why"]]
    assert "pad_diameter: 125 here, 150 at sources/page/data/pad_diameter" in whys


def test_the_levels_are_data_a_tree_may_replace():
    """A stricter standard, the same runner: the list level now asks for closed figures too."""
    [branch] = standards.knowledge()
    for node in branch.children:
        if node.id == "tool-listed":
            node.links["requires"].append("standards/tool-figures-are-closed")
    assert "tool-listed" not in reached(cert(example_tool(documents=("manual",)), standards=branch))


# --- a piece's design -------------------------------------------------------------------------

from furniture_design import standards_piece as sp  # noqa: E402

PIECE = "pieces/doors"


def piece_cert(pages: dict | None = None, **kw) -> dict:
    from furniture_design.standards_pages import example_pages

    t = Quern(vocabulary=standards.VOCABULARY, rules=standards.RULES, solvers=standards.SOLVERS)
    t.root.children = _world() + sp.piece_world(**kw) + [example_pages(**(pages or {}))]
    return certificate(t, PIECE)


def whys(c: dict) -> str:
    return " | ".join(w for k in c["criteria"] for r in k["reds"] for w in r["why"])


def test_two_doors_in_one_rail_as_designed_reach_both_levels():
    assert reached(piece_cert()) == ["piece-settled", "piece-works", "piece-buildable", "piece-instructions"]


def test_a_channel_glued_in_the_angle_leaves_the_back_door_no_room():
    """The owner: the channel a panel slides in is glued in the angle, so that there is no room for the other
    panel to slide between the channel and the angle. The design still says what was asked; it does not work."""
    c = piece_cert(piece=sp.example_piece(channel_at=7.0))
    assert reached(c) == ["piece-settled"]
    assert "pieces/doors/back-slides: along its travel it crosses pieces/doors/channel" in whys(c)


def test_a_piece_whose_ledger_says_only_its_purpose_is_not_settled():
    """Doors modelled with no decision on how they slide: every sentence of the purpose is unanswered."""
    bare = sp.example_ledger()
    bare.children[0].children = bare.children[0].children[:1]
    c = piece_cert(ledger=bare)
    assert reached(c) == [] and "no decision answers: “Two doors slide in one rail, one behind the other.”" in whys(c)


def test_a_number_the_ledger_states_is_compared_with_the_model():
    c = piece_cert(piece=sp.example_piece(overlap=47.0))
    assert reached(c) == [] and "“overlap by 50 mm” is 50 in the ledger and 47 in the model (2 * 600 - width)" in whys(c)


def test_parts_nothing_holds_and_doors_nothing_moves_are_named():
    c = piece_cert(piece=sp.example_piece(joints=False, motions=False))
    assert "pieces/doors/angle: no joint joins it, and no motion moves it" in whys(c)
    assert "pieces/doors/front-door/front-panel: no joint joins it, and no motion moves it" in whys(c)


def test_instructions_are_not_at_the_level_until_the_steps_build_the_piece():
    """The design works, and its steps say nothing of what fixes the rail: the piece holds together and its
    assembly instructions are not to be shown."""
    c = piece_cert(piece=sp.example_piece(steps=[{"add": ["angle", "channel", "back-panel", "front-panel"]}]))
    assert reached(c) == ["piece-settled", "piece-works", "piece-buildable"]
    assert "angle-to-lintel: no assembly step closes it" in whys(c)


def test_a_design_that_does_not_work_has_no_instructions_to_show():
    assert "piece-instructions" not in reached(piece_cert(piece=sp.example_piece(channel_at=7.0)))


def test_the_piece_ledgers_package_passes_the_publish_gate(tmp_path):
    """The purpose of a piece and its two rules are a package (they were written in the app that reads
    ledgers): its rules hold on a purpose and the one that replaced it, and each is refuted."""
    from furniture_design.piece_ledger import PACKAGE as LEDGER

    log = validate_package(LEDGER, tmp_path)
    assert any("2 rule(s) exercised" in line and "all pass" in line for line in log), log
    assert any("2 rule(s) refuted" in line for line in log), log
    assert any("in en, fr" in line for line in log), log


def test_instructions_are_judged_on_the_pages_as_drawn():
    """The owner: "il faut certifier la notice". A design that works, whose steps build it, is not at the
    level while a page says in a sentence what it should draw, or a step shows a rail arriving and nothing
    that fixes it; instructions that were not drawn are not at the level either, and say so."""
    c = piece_cert(pages={"sentence": "Glue the channel to the angle.", "fastened": ()})
    assert reached(c) == ["piece-settled", "piece-works", "piece-buildable"]
    assert 'page 3: "Glue the channel to the angle."' in whys(c)
    assert "step 1 closes angle-to-lintel and draws nothing of what fastens it" in whys(c)
    undrawn = piece_cert(pages={"drawn": False})
    assert reached(undrawn) == ["piece-settled", "piece-works", "piece-buildable"] and "were not drawn in this build" in whys(undrawn)


def test_how_much_of_a_part_must_show_is_read_from_the_paper():
    """The share of a part that must show is the clause's, not the code's: half shown passes at the paper's
    50 %, and a tree whose clause asks for more refuses the same pages."""
    from quern.tree import get_node

    assert "piece-instructions" in reached(piece_cert(pages={"door_shows": 0.5}))
    assert "piece-instructions" not in reached(piece_cert(pages={"door_shows": 0.49}))
    t = Quern(vocabulary=standards.VOCABULARY, rules=standards.RULES, solvers=standards.SOLVERS)
    from furniture_design.standards_pages import example_pages
    t.root.children = _world() + sp.piece_world() + [example_pages(door_shows=0.5)]
    get_node(t, "sources/agrawala-2003/visibility-scores").params["current_parts"].value = 0.75
    assert "piece-instructions" not in reached(certificate(t, PIECE))


def test_the_pages_drawn_are_the_pages_judged(tmp_path):
    """What the drawing notes is what the standard reads: the bench's instructions, drawn, say in words
    what each step does, and the record of its pages names those sentences."""
    import json

    from furniture_design.drawings import documents
    from furniture_design.package import EXAMPLES as WORLD, PACKAGE as DESIGN
    from furniture_design.standards_pages import _worded
    from quern.tree import Node

    t = Quern(vocabulary=DESIGN.vocabulary, rules=DESIGN.rules, solvers=DESIGN.solvers)
    t.root.children = WORLD
    out = documents(t, "pieces/bench", tmp_path)
    t.root.children = t.root.children + [Node.model_validate(json.loads(out["pages"].read_text(encoding="utf-8")))]
    lines = _worded(t, "pieces/bench")
    assert any("Push the back onto the left side." in line for line in lines), lines
    assert not any('"bench"' in line or "450 × 300" in line for line in lines), lines


def test_a_hinged_part_is_carried_where_it_turns_and_swings_clear():
    """A flap hinged on the rail's top front edge lifts outwards and the design still works; said to open
    inwards, it goes through the rail and the door behind it, and the certificate names each."""
    assert "piece-works" in reached(piece_cert(piece=sp.example_piece(flap={})))
    inwards = piece_cert(piece=sp.example_piece(flap={"travel": [0, 90]}))
    assert "piece-works" not in reached(inwards)
    assert "it crosses pieces/doors/front-door/front-panel" in whys(inwards)
    adrift = piece_cert(piece=sp.example_piece(flap={"pivot": [-108, 1200]}))
    assert "piece-works" not in reached(adrift) and "from what carries it" in whys(adrift)


def test_a_piece_is_buildable_once_it_says_what_cuts_and_fastens_it():
    """A design that works is not yet one that can be made: a rail fixed by nothing anyone named, a
    channel nobody said what to cut from, keep it from the level, and from its instructions."""
    c = piece_cert(piece=sp.example_piece(fastened=False, made=False))
    assert reached(c) == ["piece-settled", "piece-works"]
    assert "angle-to-lintel: it does not say what fastens it" in whys(c)
    assert "channel: it does not say what cuts it out (sawn_with)" in whys(c)


def test_a_rule_that_waits_on_the_person_says_the_question_in_every_language():
    """Whoever shows a certificate asks the person only what the person alone knows, in the standard's
    words: the rules on what cuts and fastens a piece say a question beside what is wrong, in each
    language they speak; a rule whoever edits the model can put right alone asks nothing."""
    by = {r.name: r.messages for r in standards.RULES}
    for name in ("a-pieces-parts-say-what-they-are-cut-from", "a-pieces-parts-say-how-they-are-cut",
                 "a-pieces-joints-say-what-fastens-them"):
        assert set(by[name]) == {"en", "fr"} and all(m["ask"].rstrip().endswith("?") for m in by[name].values())
    assert all("ask" not in m for m in by["a-pieces-pages-carry-no-sentence"].values())


def test_only_the_persons_saws_answer_what_they_cut_with():
    """The question on what cuts the parts is answered by a saw (sawn_with), so it offers the person's
    tools that state a saw kind, and not their sander, clamps or tape; nothing the person holds as a
    tool fastens a joint, so that question offers none of them."""
    by = {r.name: r.messages for r in standards.RULES}
    assert all(m["offers"] == "saw_kind" for m in by["a-pieces-parts-say-how-they-are-cut"].values())
    assert all("offers" not in m for m in by["a-pieces-joints-say-what-fastens-them"].values())
    assert all("offers" not in m for m in by["a-pieces-parts-say-what-they-are-cut-from"].values())


def test_a_part_that_names_its_board_is_not_asked_which_board():
    """A part that names the board it is cut from and not the saw is asked only what cuts it: the
    person is not asked again what the model already says."""
    c = piece_cert(piece=sp.example_piece(unsaid=("sawn_with",)))
    assert "channel: it does not say what cuts it out (sawn_with)" in whys(c)
    assert "(uses)" not in whys(c)
    asked = [m["ask"] for cr in c["criteria"] for red in cr["reds"] for m in (red["messages"] or {}).values()
             if "ask" in m]
    assert asked and not any("buy" in q or "achetez" in q for q in asked)


def test_with_no_pages_drawn_only_the_criteria_judged_on_the_pages_fail():
    """A design at the instructions' level, judged before its instructions are drawn, holds every criterion of
    the level but those standards.ON_THE_PAGES names, which are criteria of that level."""
    t = Quern(vocabulary=standards.VOCABULARY, rules=standards.RULES, solvers=standards.SOLVERS)
    t.root.children = _world() + sp.piece_world()
    c = certificate(t, PIECE)
    level = next(lv for lv in c["levels"] if lv["level"].endswith("piece-instructions"))
    failing = {k["criterion"].rpartition("/")[2] for k in c["criteria"] if not k["held"]}
    assert failing == set(standards.ON_THE_PAGES)
    assert {f"{standards.STANDARDS}/{x}" for x in standards.ON_THE_PAGES} <= set(level["requires"])


def test_a_piece_whose_steps_and_parts_contradict_each_other_is_refused_its_instructions():
    """The model is held to agree with itself: doors lowered through a rail already up, a bar modelled as a
    full box over the panel edge it holds, and a door whose panel and bar nothing joins each keep the piece
    from the level its instructions are shown at, and the certificate names the parts."""
    through = piece_cert(piece=sp.example_piece(doors_from="up"))
    assert "piece-instructions" not in reached(through)
    assert "front-panel, brought in from above, crosses pieces/doors/channel" in whys(through)
    solid = piece_cert(piece=sp.example_piece(bar="solid"))
    assert "piece-works" not in reached(solid)
    assert "front-panel and pieces/doors/front-door/front-bar fill the same space" in whys(solid)
    unjoined = piece_cert(piece=sp.example_piece(bar="channel", bar_joined=False))
    assert "piece-works" not in reached(unjoined)
    assert "it moves with pieces/doors/front-door, and no joint joins it to another part of it" in whys(unjoined)
    assert "piece-works" in reached(piece_cert(piece=sp.example_piece(bar="channel")))
