"""What a person reported, held to the message they said it in.

A source of authority reported is a person's own account (knowledge.AUTHORITIES), and each of its clauses
quotes them. The quote is checked, not trusted: the message it comes from is kept as a copy (the person's
message as the session's transcript holds it: the transcript's own record, not text an assistant typed
out again), the source states the copy's sha256, and every clause's quote must be found in it. The copy
names the session and the message, so where the transcript is at hand it is compared with it too.

The copies are kept privately, beside the other captures (CAPTURES/reported/<source id>.json). A
package's test calls check() on each of its reported sources and fails on what it returns.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from quern.tree import Node

# A transcript's "user" turns that the person did not type: the harness's summary of a session
# continued, and its notices.
_NOT_TYPED = ("This session is being continued", "<system-reminder>", "<task-notification>")


def _text(content) -> str:
    if isinstance(content, str):
        return content
    return "\n".join(c.get("text", "") for c in content or [] if isinstance(c, dict) and c.get("type") == "text")


def message(transcripts: Path, session: str, uuid: str) -> dict:
    """The person's message `uuid` of the session `session`, as the transcript under `transcripts` holds
    it: {session, message, at, text}. Refused (ValueError) when it is not there or not typed by them."""
    for f in transcripts.glob(f"*/{session}.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            d = json.loads(line)
            if d.get("uuid") != uuid:
                continue
            text = _text((d.get("message") or {}).get("content"))
            if d.get("type") != "user" or not text or text.lstrip().startswith(_NOT_TYPED):
                raise ValueError(f"message {uuid} of session {session} is not one the person typed")
            return {"session": session, "message": uuid, "at": d.get("timestamp", ""), "text": text}
    raise ValueError(f"no message {uuid} in a transcript of session {session} under {transcripts}")


def _bytes(copy: dict) -> bytes:
    return (json.dumps(copy, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode("utf-8")


def keep(copies: Path, source_id: str, transcripts: Path, session: str, uuid: str) -> str:
    """Keep the person's message as the copy of the source `source_id`; its sha256, for the source's
    payload sha256."""
    data = _bytes(message(transcripts, session, uuid))
    path = copies / "reported" / f"{source_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def check(source: Node, copies: Path, transcripts: Path | None = None) -> list[str]:
    """What keeps a reported source from standing on the person's words: no copy stated or kept, a copy
    that is not the one stated, a quote not in it, or (where the transcript is at hand) a copy that is
    not the message it names. Empty: every clause is their words."""
    if (source.payload or {}).get("authority") != "reported":
        return []
    sha = (source.payload or {}).get("sha256", "")
    path = copies / "reported" / f"{source.id}.json"
    if not sha:
        return [f"{source.id} states no sha256 of the message it quotes"]
    if not path.exists():
        return [f"{source.id}: the copy {path} is missing"]
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != sha:
        return [f"{source.id}: the copy {path} is not the one the source states"]
    copy = json.loads(data)
    out = [f"{source.id}/{c.id}: «{c.payload.get('quote', '')}» is not in the person's message"
           for c in source.children if c.kind == "clause" and (not c.payload.get("quote")
                                                               or c.payload["quote"] not in copy["text"])]
    if transcripts is not None and any(transcripts.glob(f"*/{copy['session']}.jsonl")):
        try:
            if message(transcripts, copy["session"], copy["message"])["text"] != copy["text"]:
                out.append(f"{source.id}: the copy is not the message {copy['message']} the transcript holds")
        except ValueError as e:
            out.append(f"{source.id}: {e}")
    return out
