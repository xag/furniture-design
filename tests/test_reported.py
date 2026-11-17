"""A reported source stands on the person's message: its quotes are found in a copy of it, and the copy is
the message the transcript holds (furniture_design.reported)."""
import json

import pytest
from quern.tree import Node

from furniture_design.reported import check, keep

SAID = "Par exemple j'ai appris sur place qu'ils ne pouvaient pas faire une découpe de moins de 10 cm de large."


def _transcripts(tmp_path, text=SAID, kind="user"):
    folder = tmp_path / "transcripts" / "some-project"
    folder.mkdir(parents=True)
    lines = [{"type": kind, "uuid": "m1", "timestamp": "2026-11-14T11:05:34Z", "message": {"content": text}},
             {"type": "assistant", "uuid": "m2", "message": {"content": [{"type": "text", "text": "Noted."}]}}]
    (folder / "s1.jsonl").write_text("\n".join(json.dumps(x) for x in lines), encoding="utf-8")
    return tmp_path / "transcripts"


def _visit(sha: str, *quotes: str) -> Node:
    return Node(id="a-store-visit", kind="source", payload={"authority": "reported", "sha256": sha},
                children=[Node(id=f"c{i}", kind="clause", payload={"locator": "the message", "quote": q})
                          for i, q in enumerate(quotes)])


def test_a_quote_in_the_persons_message_stands(tmp_path):
    transcripts = _transcripts(tmp_path)
    sha = keep(tmp_path / "copies", "a-store-visit", transcripts, "s1", "m1")
    assert check(_visit(sha, "pas faire une découpe de moins de 10 cm de large"), tmp_path / "copies", transcripts) == []


def test_words_the_person_never_said_are_refused(tmp_path):
    transcripts = _transcripts(tmp_path)
    sha = keep(tmp_path / "copies", "a-store-visit", transcripts, "s1", "m1")
    found = check(_visit(sha, "Le magasin ne découpe pas le lamellé-collé"), tmp_path / "copies", transcripts)
    assert len(found) == 1 and "lamellé-collé" in found[0]


def test_a_copy_edited_after_it_was_kept_is_refused(tmp_path):
    transcripts = _transcripts(tmp_path)
    sha = keep(tmp_path / "copies", "a-store-visit", transcripts, "s1", "m1")
    copy = tmp_path / "copies" / "reported" / "a-store-visit.json"
    data = json.loads(copy.read_text(encoding="utf-8"))
    data["text"] += " Ils ne coupent pas le lamellé-collé."
    copy.write_text(json.dumps(data), encoding="utf-8")
    assert "not the one the source states" in check(_visit(sha, "moins de 10 cm"), tmp_path / "copies")[0]


def test_a_summary_of_the_session_is_not_the_persons_message(tmp_path):
    transcripts = _transcripts(tmp_path, text="This session is being continued from a previous conversation. "
                                              "The store does not cut glulam.")
    with pytest.raises(ValueError, match="not one the person typed"):
        keep(tmp_path / "copies", "a-store-visit", transcripts, "s1", "m1")


def test_a_source_that_kept_no_copy_is_refused(tmp_path):
    assert check(_visit("", "moins de 10 cm"), tmp_path / "copies") == ["a-store-visit states no sha256 of the "
                                                                        "message it quotes"]
