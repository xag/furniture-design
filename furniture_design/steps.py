"""The assembly instructions as screens, for an app that shows them one step at a time on a phone.

A whole A4 page on a phone draws a step at about 2 mm to the pixel, which leaves its words 5 to 7 px high.
So each screen takes only its drawing from the instructions, cut from the PDF where
sheets.assembly_instructions drew it (the regions it notes), and the app sets the words beside it as text:
the step's text, its tools and connectors, the boards' letters, counts and sizes, the hardware, a cut card's
sentences and its saw's method, all read from the piece as the PDF reads them.

The screens, in the order of the instructions:
- cover: the piece's name, version, drawing and overall size;
- needed: each kind of board (drawing, letter, count, sizes), the hardware, the tools;
- step: a step's number, tools and connectors, its picture and its text;
- block: a part of a step drawn on its own after its picture: the grooving settings (with the step's head),
  each kind of joint's frames (with how many times), a cut card (its frames, or its drawing and words).

instruction_screens() writes the images (WebP) and screens.json into a folder and returns screens.json's
path. Rasterising needs PyMuPDF, imported only here.
"""
from __future__ import annotations

import json
from pathlib import Path

from .scene import Scene
from .sheets import LABELS, _fmt, cut_sentences

DPI = 200


def _cutter(pdf: Path, out: Path):
    import pymupdf
    from PIL import Image

    doc = pymupdf.open(str(pdf))
    to_pt = 72 / 25.4
    count = [0]

    def cut(region: dict, pad_mm: float = 3, box=None) -> dict | None:
        """The region's drawing, trimmed to what is drawn in it, as a WebP in `out`: {file, mm} (mm: its
        width on the page), or None when nothing is drawn there."""
        x0, y0, x1, y1 = box or region["box"]
        pix = doc[region["page"]].get_pixmap(dpi=DPI, clip=pymupdf.Rect(x0 * to_pt, y0 * to_pt, x1 * to_pt, y1 * to_pt))
        im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        # the page's pictures are kept decoded by MuPDF as they are drawn, some 35 MB for a bench's
        # instructions on a server with 150 MB to spare: what a region needed is let go once it is cut
        del pix
        pymupdf.TOOLS.store_shrink(100)
        px = lambda v: round(v * DPI / 25.4)
        if region.get("blank"):
            bx0, by0, bx1, by1 = region["blank"]
            im.paste("white", (px(bx0 - x0), px(by0 - y0), px(bx1 - x0), px(by1 - y0)))
        drawn = im.point(lambda v: 255 if v < 243 else 0).getbbox()   # what is darker than white by more than 12
        if not drawn:
            return None
        pad = px(pad_mm)
        l, t, r, b = drawn
        im = im.crop((max(0, l - pad), max(0, t - pad), min(im.width, r + pad), min(im.height, b + pad)))
        count[0] += 1
        name = f"{count[0]:02d}.webp"
        im.save(out / name, "WEBP", quality=82, method=4)   # as small as 6 for the bench, in two thirds of the time
        return {"file": name, "mm": round(im.width / DPI * 25.4, 1)}

    return cut


def _head(sc: Scene, number: int) -> dict:
    s = next(s for s in sc.steps if s.number == number)
    joints = [j for j in sc.joints if j.id in s.joints]
    return {"number": number, "tools": list(s.tools), "connectors": 0 if s.prepare else sum(j.count for j in joints)}


def _card_words(sc: Scene, part_id: str, L: dict, lang: str) -> dict:
    p = sc.part(part_id)
    said = [t for t in p.tools if (t.say or {}).get(lang)]
    sources: dict[str, list[str]] = {}
    for t in said:
        for source, locator in t.cites:
            if locator not in sources.setdefault(source, []):
                sources[source].append(locator)
    colon, sep = (" : ", " ; ") if lang == "fr" else (": ", "; ")
    return {"title": f"{L['cutting']} {p.mark}", "mark": p.mark, "sentences": cut_sentences(p, L, lang),
            "methods": [{"name": t.say[lang].get("name", t.name), "method": t.say[lang].get("method", [])} for t in said],
            "sources_title": L["sources"],
            "sources": [f"{src}{colon}{sep.join(locs)}" for src, locs in sources.items()]}


def screens_of(sc: Scene, regions: list[dict], cut, lang: str) -> list[dict]:
    """The screens, from the regions the instructions noted in the order drawn; `cut` turns a region into
    an image."""
    L = LABELS[lang]
    out: list[dict] = []
    block = None
    for r in regions:
        kind = r["kind"]
        if kind == "cover":
            size = [h - l for l, h in zip(sc.lo, sc.hi)]
            out.append({"kind": "cover", "title": sc.title, "version": f"{L['version']} {sc.info.get('version', '')}",
                        "image": cut(r), "size": f"{L['overall']} : {_fmt(size[0])} × {_fmt(size[1])} × {_fmt(size[2])} mm"})
        elif kind == "board":
            if not out or out[-1]["kind"] != "needed":
                tools: list[str] = []
                for s in sc.steps:
                    tools += [t for t in s.tools if t not in tools]
                for j in sc.joints:
                    tools += [t for t in j.tools if t not in tools]
                out.append({"kind": "needed", "title": L["inbox"], "boards_title": L["boards"], "boards": [],
                            "hardware_title": L["hardware"],
                            "hardware": [{"name": n, "count": sum(j.count for j in sc.joints if j.connector == n)}
                                         for n in sorted({j.connector for j in sc.joints})],
                            "tools_title": L["tools"], "tools": tools})
            p = next(p for p in sc.parts if p.mark == r["mark"])
            dims = sorted(p.size, reverse=True)
            out[-1]["boards"].append({"mark": p.mark, "count": sum(q.sheets for q in sc.parts if q.mark == p.mark),
                                      "size": f"{_fmt(dims[0])} × {_fmt(dims[1])} × {_fmt(dims[2] / p.sheets)}",
                                      "image": cut(r, 1)})
            block = None
        elif kind == "step":
            s = next(s for s in sc.steps if s.number == r["step"])
            out.append({"kind": "step", "step": s.number, "head": _head(sc, s.number), "image": cut(r), "text": s.text})
            block = None
        elif kind == "block":
            block = {"kind": "block", "step": r["step"], "images": [], "_region": r}
            if r.get("head"):
                block["head"] = _head(sc, r["step"])
            if r.get("count"):
                block["count"] = r["count"]
            if r.get("part"):
                block["card"] = _card_words(sc, r["part"], LABELS[lang], lang)
            out.append(block)
        elif kind in ("frame", "drawing") and block is not None:
            block.setdefault("_regions", []).append(r)
    for b in (s for s in out if s["kind"] == "block"):
        regions_in = b.pop("_regions", [])
        region = b.pop("_region")
        frames = [r for r in regions_in if r["kind"] == "frame"]
        if b.get("card") and frames:     # a cut card drawn in frames says nothing in words
            b.pop("card")
        chosen = sorted(frames, key=lambda r: r["n"]) if frames else regions_in
        pad = 0 if frames else 3
        b["images"] = [im for im in (cut(r, pad) for r in chosen) if im] or [im for im in [cut(region)] if im]
    return out


def instruction_screens(sc: Scene, pdf: Path, regions: list[dict], out: Path, lang: str = "fr") -> Path:
    """Write the screens of the instructions in `pdf` (drawn with `regions` kept) into the folder `out`: one
    WebP per drawing and screens.json, {steps: how many steps, screens: [...]}, each image named by its file
    in `out`. Returns screens.json's path."""
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.webp"):
        old.unlink()
    screens = screens_of(sc, regions, _cutter(pdf, out), lang)
    path = out / "screens.json"
    path.write_text(json.dumps({"steps": len(sc.steps), "lang": lang, "screens": screens}, ensure_ascii=False, indent=1),
                    encoding="utf-8")
    return path
