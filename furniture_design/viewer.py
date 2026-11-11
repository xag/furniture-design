"""An interactive 3D view of a piece, as one HTML file that opens in any browser: turn it
with a finger or the mouse, pull the parts apart, walk through the assembly steps, and
touch a part to see its letter, name and size. Built from the scene (scene.py), so it
shows what the rules checked.

three.js r128 is loaded from cdnjs and its OrbitControls from jsDelivr, by exact version.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from .scene import Scene

PAGE = r"""<!doctype html>
<html lang="__LANG__">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root { --bg:#f6f3ee; --ink:#1d1d1b; --muted:#6b675f; --panel:#fffdf9; --line:#e2dccf; --accent:#c0392b; }
@media (prefers-color-scheme: dark) { :root { --bg:#1b1a18; --ink:#f2efe9; --muted:#a8a296; --panel:#252320; --line:#3a3732; } }
* { box-sizing:border-box; }
html, body { margin:0; height:100%; background:var(--bg); color:var(--ink);
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
#app { display:flex; height:100%; }
#stage { flex:1; position:relative; min-width:0; }
canvas { display:block; width:100%; height:100%; touch-action:none; }
aside { width:300px; background:var(--panel); border-left:1px solid var(--line); padding:16px;
  overflow:auto; }
h1 { font-size:18px; margin:0 0 2px; }
.sub { color:var(--muted); font-size:13px; margin-bottom:14px; }
label { font-size:13px; color:var(--muted); display:block; margin:14px 0 4px; }
input[type=range] { width:100%; }
.step { font-size:14px; line-height:1.35; min-height:3.5em; margin-top:6px; }
ul { list-style:none; padding:0; margin:8px 0 0; }
li { display:flex; gap:10px; align-items:center; padding:6px 4px; border-radius:6px; cursor:pointer;
  font-size:13px; }
li:hover, li.on { background:var(--line); }
.mark { width:24px; height:24px; border-radius:50%; border:1.5px solid var(--ink); display:grid;
  place-items:center; font-weight:700; font-size:12px; flex:none; }
.dims { color:var(--muted); font-size:12px; }
#tip { position:absolute; left:12px; top:12px; background:var(--panel); border:1px solid var(--line);
  border-radius:8px; padding:8px 10px; font-size:13px; display:none; max-width:70%; }
.row { display:flex; gap:8px; align-items:center; margin-top:10px; font-size:13px; }
button { font:inherit; font-size:13px; padding:6px 10px; border-radius:6px; border:1px solid var(--line);
  background:var(--bg); color:var(--ink); cursor:pointer; }
@media (max-width: 720px) { #app { flex-direction:column; } aside { width:auto; height:42%;
  border-left:none; border-top:1px solid var(--line); } }
</style>
</head>
<body>
<div id="app">
  <div id="stage"><div id="tip"></div></div>
  <aside>
    <h1>__TITLE__</h1>
    <div class="sub" id="sub"></div>
    <label for="steps">__L_STEPS__ <span id="stepn"></span></label>
    <input id="steps" type="range" min="0" value="0">
    <div class="step" id="steptext"></div>
    <label for="explode">__L_EXPLODE__</label>
    <input id="explode" type="range" min="0" max="100" value="0">
    <div class="row"><input id="showc" type="checkbox" checked><span>__L_CONNECTORS__</span>
      <span style="flex:1"></span><button id="reset">__L_RESET__</button></div>
    <label>__L_PARTS__</label>
    <ul id="parts"></ul>
  </aside>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
<script>
const DATA = __DATA__;
const stage = document.getElementById('stage');
const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
stage.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 10, 100000);
const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
scene.add(new THREE.HemisphereLight(0xffffff, 0x8a7f70, 0.55));
const sun = new THREE.DirectionalLight(0xffffff, 0.6); sun.position.set(-1.2, 1.6, 1.8); scene.add(sun);

// piece frame (x across, y to the back, z up, mm) -> three (x, z, -y)
const T = (x, y, z) => new THREE.Vector3(x, z, -y);
const lo = DATA.lo, hi = DATA.hi;
const mid = T((lo[0]+hi[0])/2, (lo[1]+hi[1])/2, (lo[2]+hi[2])/2);
const size = Math.max(hi[0]-lo[0], hi[1]-lo[1], hi[2]-lo[2]);
const woodColor = new THREE.Color(0xe6cfa4), newColor = new THREE.Color(0xb07a3c), pick = new THREE.Color(0xf0b45a);

const meshes = [];
DATA.parts.forEach((p, i) => {
  const s = [p.hi[0]-p.lo[0], p.hi[1]-p.lo[1], p.hi[2]-p.lo[2]];
  const geo = new THREE.BoxGeometry(s[0], s[2], s[1]);
  const mat = new THREE.MeshStandardMaterial({color: woodColor.clone(), roughness:0.8, transparent:true});
  const m = new THREE.Mesh(geo, mat);
  m.userData = {part:p, home:T((p.lo[0]+p.hi[0])/2, (p.lo[1]+p.hi[1])/2, (p.lo[2]+p.hi[2])/2)};
  m.position.copy(m.userData.home);
  const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geo),
    new THREE.LineBasicMaterial({color:0x3b3428, transparent:true}));
  m.add(edges);
  scene.add(m); meshes.push(m);
});
const connectors = [];
DATA.joints.forEach(j => j.positions.forEach(q => {
  const s = [10, 10, 10]; s[j.along] = 64; s[j.normal] = 3;
  const geo = new THREE.BoxGeometry(s[0], s[2], s[1]);
  const c = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({color:0xc0392b}));
  c.userData = {joint:j, home:T(q[0], q[1], q[2])};
  c.position.copy(c.userData.home); scene.add(c); connectors.push(c);
}));

function fit() {
  const w = stage.clientWidth, h = stage.clientHeight;
  renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix();
}
function home() {
  const d = size * 2.4;
  camera.position.set(mid.x - d*0.55, mid.y + d*0.45, mid.z + d*0.75);
  controls.target.copy(mid); controls.update();
}
window.addEventListener('resize', fit); fit(); home();

// steps: 0 shows the finished piece; k shows the state after assembly step k
const steps = DATA.steps.filter(s => !s.prepare);
const stepIn = document.getElementById('steps');
stepIn.max = steps.length;
const placedAt = {};
steps.forEach((s, i) => s.add.forEach(id => placedAt[id] = i + 1));

function apply() {
  const k = +stepIn.value, e = +document.getElementById('explode').value / 100;
  document.getElementById('stepn').textContent = k ? `${k} / ${steps.length}` : '';
  document.getElementById('steptext').textContent = k ? steps[k-1].text : DATA.finished;
  meshes.forEach(m => {
    const p = m.userData.part, at = placedAt[p.id] || 0;
    const visible = !k || at <= k;
    m.visible = visible;
    const isNew = k && at === k;
    m.material.color.copy(m.userData.selected ? pick : (isNew ? newColor : woodColor));
    const dir = m.userData.home.clone().sub(mid);
    m.position.copy(m.userData.home).add(dir.multiplyScalar(e * 0.9));
  });
  connectors.forEach(c => {
    const ids = c.userData.joint.parts;
    const shown = document.getElementById('showc').checked &&
      ids.every(id => !k || (placedAt[id] || 0) <= k);
    c.visible = shown;
    const dir = c.userData.home.clone().sub(mid);
    c.position.copy(c.userData.home).add(dir.multiplyScalar(e * 0.9));
  });
}
['steps', 'explode', 'showc'].forEach(id => document.getElementById(id).addEventListener('input', apply));
document.getElementById('reset').onclick = () => { stepIn.value = 0; document.getElementById('explode').value = 0; select(null); home(); apply(); };

const list = document.getElementById('parts');
const seen = {};
DATA.parts.forEach(p => {
  if (seen[p.mark]) { seen[p.mark].n += p.sheets; seen[p.mark].li.querySelector('.n').textContent = '× ' + seen[p.mark].n; return; }
  const li = document.createElement('li');
  const s = [p.hi[0]-p.lo[0], p.hi[1]-p.lo[1], p.hi[2]-p.lo[2]].sort((a,b)=>b-a);
  li.innerHTML = `<span class="mark">${p.mark}</span><span><b>${p.name}</b> <span class="n">× ${p.sheets}</span><br><span class="dims">${s[0]} × ${s[1]} × ${s[2]/p.sheets} mm</span></span>`;
  li.onclick = () => select(p.mark);
  list.appendChild(li); seen[p.mark] = {li, n:p.sheets};
});
document.getElementById('sub').textContent = DATA.subtitle;

let selected = null;
function select(mark) {
  selected = selected === mark ? null : mark;
  meshes.forEach(m => m.userData.selected = selected && m.userData.part.mark === selected);
  Object.entries(seen).forEach(([k, v]) => v.li.classList.toggle('on', k === selected));
  apply();
}
const ray = new THREE.Raycaster(), ptr = new THREE.Vector2(), tip = document.getElementById('tip');
renderer.domElement.addEventListener('pointerup', ev => {
  const r = renderer.domElement.getBoundingClientRect();
  ptr.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ptr, camera);
  const hit = ray.intersectObjects(meshes.filter(m => m.visible), false)[0];
  if (!hit) { tip.style.display = 'none'; return; }
  const p = hit.object.userData.part;
  const s = [p.hi[0]-p.lo[0], p.hi[1]-p.lo[1], p.hi[2]-p.lo[2]].sort((a,b)=>b-a);
  tip.innerHTML = `<b>${p.mark} — ${p.name}</b><br>${s[0]} × ${s[1]} × ${s[2]} mm<br>${p.material}`;
  tip.style.display = 'block';
  select(p.mark);
});
apply();
(function loop() { requestAnimationFrame(loop); controls.update(); renderer.render(scene, camera); })();
</script>
</body>
</html>
"""

WORDS = {
    "fr": {"steps": "Étape de montage", "explode": "Écarter les pièces", "connectors": "Connecteurs",
           "reset": "Revenir", "parts": "Pièces", "finished": "Meuble monté. Glisser pour suivre "
           "le montage étape par étape."},
    "en": {"steps": "Assembly step", "explode": "Pull the parts apart", "connectors": "Connectors",
           "reset": "Reset", "parts": "Parts", "finished": "Finished piece. Slide to follow the "
           "assembly step by step."},
}


def viewer_html(sc: Scene, path: Path, lang: str = "fr") -> Path:
    W = WORDS[lang]
    size = [h - l for l, h in zip(sc.lo, sc.hi)]
    data = {
        "lo": sc.lo, "hi": sc.hi, "finished": W["finished"],
        "subtitle": f"{sc.info.get('version', '')} · {round(size[0])} × {round(size[1])} × "
                    f"{round(size[2])} mm",
        "parts": [{"id": p.id, "mark": p.mark, "name": p.name, "lo": p.lo, "hi": p.hi,
                   "sheets": p.sheets, "material": p.material_name} for p in sc.parts],
        "joints": [{"id": j.id, "parts": j.parts, "along": j.along_axis, "normal": j.normal_axis,
                    "positions": j.positions} for j in sc.joints],
        "steps": [{"text": s.text, "add": s.add, "prepare": s.prepare} for s in sc.steps],
    }
    page = (PAGE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
            .replace("__TITLE__", html.escape(sc.title)).replace("__LANG__", lang)
            .replace("__L_STEPS__", W["steps"]).replace("__L_EXPLODE__", W["explode"])
            .replace("__L_CONNECTORS__", W["connectors"]).replace("__L_RESET__", W["reset"])
            .replace("__L_PARTS__", W["parts"]))
    path.write_text(page, encoding="utf-8")
    return path
