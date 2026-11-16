"""Writes each state of the prototype as its own HTML page: the real 3D view of the wardrobe
doors (V7), rendered by the worktree's viewer.py, with a script at its end that puts it in the
state. Alternative A draws the plans' chains, B each part's own size.

    <furniture venv python> gen.py
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
FURNITURE = Path("C:/Users/trans/Projects/furniture")
RENDER = HERE / "render.py"
STATES = HERE / "states"


def render(lang: str, out: Path) -> str:
    subprocess.run([str(FURNITURE / ".venv/Scripts/python.exe"), str(RENDER), str(HERE / "piece.json"),
                    str(out), lang], check=True, cwd=FURNITURE)
    return out.read_text(encoding="utf-8")


BRANCH = ["g", "g-porte-avant"]
# name: (what it sets)
STATE = {
    "s01-rest": {},
    "s02-sheet": {"sheet": True},
    "s03-dims": {"dims": True},
    "s04-branch-hidden": {"go": BRANCH},
    "s05-branch-see": {"go": BRANCH, "rest": "see"},
    "s06-branch-solid": {"go": BRANCH, "rest": "solid"},
    "s07-branch-sheet": {"go": BRANCH, "rest": "see", "sheet": True},
    "s08-branch-dims": {"go": BRANCH, "dims": True},
    "s09-branch-dims-close": {"go": BRANCH, "dims": True, "zoom": 0.07},
    "s10-branch-dims-apart": {"go": BRANCH, "dims": True, "explode": 50},
    "s11-step-see": {"go": BRANCH, "rest": "see", "step": 1},
}


def stateful(page: str, s: dict) -> str:
    js = f"""<script>
(function () {{
  const s = {json.dumps(s)};
  if (s.go) go(s.go);
  if (s.rest) document.querySelector('input[name=rest][value=' + s.rest + ']').checked = true;
  if (s.dims) document.getElementById('showd').checked = true;
  if (s.explode) document.getElementById('explode').value = s.explode;
  if (s.step) stepIn.value = s.step;
  if (s.zoom) {{   // as a double tap on the bottom corner nearest the eye does, then closer still
    const at = T(view.lo[0], view.lo[1], view.lo[2]), from = camera.position.clone().sub(controls.target);
    controls.target.copy(at); camera.position.copy(at).add(from.multiplyScalar(s.zoom)); controls.update();
  }}
  apply();
  if (s.sheet) sheet(true);
  document.documentElement.dataset.ready = '1';
}})();
</script>
</body>"""
    return page.replace("</body>", js, 1)


def main():
    STATES.mkdir(exist_ok=True)
    base = {lang: render(lang, HERE / f"after-{lang}.html") for lang in ("fr", "en")}
    alts = {"A": lambda p: p, "B": lambda p: p.replace("const DIMS = 'chain';", "const DIMS = 'part';")}
    for alt, f in alts.items():
        assert alt == "A" or "const DIMS = 'part';" in f(base["fr"])
        for name, s in STATE.items():
            (STATES / f"{alt}-{name}.html").write_text(stateful(f(base["fr"]), s), encoding="utf-8")
        (STATES / f"{alt}-s07-branch-sheet-en.html").write_text(stateful(f(base["en"]), STATE["s07-branch-sheet"]), encoding="utf-8")
        # the page to play: the playable page moves to the next screen on a tap unless the
        # screen holds a form, and a tap on the model must turn it, never reload it
        (HERE / f"play-{alt}.html").write_text(
            stateful(f(base["fr"]), {}).replace("</body>", "<form hidden></form></body>", 1), encoding="utf-8")
    before = (HERE / "before.html").read_text(encoding="utf-8")
    for name in ("s01-rest", "s04-branch-hidden"):
        (STATES / f"before-{name}.html").write_text(stateful(before, STATE[name]), encoding="utf-8")
    print("states:", len(list(STATES.glob("*.html"))))


if __name__ == "__main__":
    sys.exit(main())
