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
#path { font-size:13px; margin:6px 0 0; line-height:1.5; }
#path a { color:inherit; }
li .into { margin-left:auto; color:var(--muted); font-size:18px; }
li .group { width:24px; flex:none; }
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
    <nav id="path" hidden></nav>
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
controls.minDistance = 4;
scene.add(new THREE.HemisphereLight(0xffffff, 0x8a7f70, 0.55));
const sun = new THREE.DirectionalLight(0xffffff, 0.6); sun.position.set(-1.2, 1.6, 1.8); scene.add(sun);

// piece frame (x across, y to the back, z up, mm) -> three (x, z, -y)
const T = (x, y, z) => new THREE.Vector3(x, z, -y);
const lo = DATA.lo, hi = DATA.hi;
const mid = T((lo[0]+hi[0])/2, (lo[1]+hi[1])/2, (lo[2]+hi[2])/2);
const size = Math.max(hi[0]-lo[0], hi[1]-lo[1], hi[2]-lo[2]);
const woodColor = new THREE.Color(0xe6cfa4), newColor = new THREE.Color(0xb07a3c), pick = new THREE.Color(0xf0b45a);

const meshes = [], tip = document.getElementById('tip'), byId = {};
DATA.parts.forEach(p => byId[p.id] = p);
// a piece-frame axis as a three.js direction
const E = [new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 0, -1), new THREE.Vector3(0, 1, 0)];
DATA.parts.forEach((p, i) => {
  // the board's outline in its (u, v) plane, extruded across its thickness t
  const f = p.profile, shape = new THREE.Shape();
  f.outline.forEach(([a, b], k) => k ? shape.lineTo(a, b) : shape.moveTo(a, b));
  const geo = new THREE.ExtrudeGeometry(shape, {depth: f.t1 - f.t0, bevelEnabled: false});
  const m4 = new THREE.Matrix4().makeBasis(E[f.u], E[f.v], E[f.t]);
  m4.setPosition(E[f.t].clone().multiplyScalar(f.t0));
  geo.applyMatrix4(m4);
  const mat = new THREE.MeshStandardMaterial({color: woodColor.clone(), roughness:0.8,
    transparent:true, side: THREE.DoubleSide});
  const m = new THREE.Mesh(geo, mat);
  const centre = T((p.lo[0]+p.hi[0])/2, (p.lo[1]+p.hi[1])/2, (p.lo[2]+p.hi[2])/2);
  m.userData = {part:p, home:new THREE.Vector3(0, 0, 0), centre};
  const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geo),
    new THREE.LineBasicMaterial({color:0x3b3428, transparent:true}));
  m.add(edges);
  scene.add(m); meshes.push(m);
});
const connectors = [];
DATA.joints.forEach(j => j.positions.forEach(q => {
  const s = [8, 8, 8], across = 3 - j.along - j.normal;
  if (j.size) { s[j.along] = j.size[0]; s[across] = j.size[1]; }
  s[j.normal] = 3;
  const geo = new THREE.BoxGeometry(s[0], s[2], s[1]);
  const c = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({color:0xc0392b}));
  c.userData = {joint:j, home:T(q[0], q[1], q[2])};
  c.position.copy(c.userData.home); scene.add(c); connectors.push(c);
}));

function fit() {
  const w = stage.clientWidth, h = stage.clientHeight;
  renderer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix();
}
// the group shown: the ids from the piece down to it, none for the whole piece
let here = [];
const under = p => here.every((id, i) => p.within[i] && p.within[i][0] === id);
// the middle and the largest side of what is shown
function shown() {
  const ps = DATA.parts.filter(under), a = [0, 1, 2].map(i => Math.min(...ps.map(p => p.lo[i]))),
    b = [0, 1, 2].map(i => Math.max(...ps.map(p => p.hi[i])));
  return {mid: T((a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2), size: Math.max(b[0]-a[0], b[1]-a[1], b[2]-a[2]), lo: a, hi: b};
}
let view = shown();
function home() {
  const s = [0, 1, 2].map(i => view.hi[i] - view.lo[i]), long = s.indexOf(Math.max(...s)),
    across = Math.max(...s.filter((_, i) => i !== long));
  if (s[long] > 8 * across) {
    // a bar (a rail, a profile) fitted by its length is a line: it is shown from its end, close
    // enough to read its section, its length running away from the eye
    const end = [0, 1, 2].map(i => (view.lo[i] + view.hi[i]) / 2), off = [0.35, -0.45, 0.35];
    end[long] = long === 2 ? view.hi[2] : view.lo[long];
    off[long] = long === 2 ? 1 : -1;
    const at = T(end[0], end[1], end[2]);
    camera.position.copy(at).add(T(off[0], off[1], off[2]).setLength(across * 5));
    controls.target.copy(at); controls.update();
    return;
  }
  const d = view.size * 2.4;
  camera.position.set(view.mid.x - d*0.55, view.mid.y + d*0.45, view.mid.z + d*0.75);
  controls.target.copy(view.mid); controls.update();
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
    const visible = (!k || at <= k) && under(p);
    m.visible = visible;
    const isNew = k && at === k;
    m.material.color.copy(m.userData.selected ? pick : (isNew ? newColor : woodColor));
    const dir = m.userData.centre.clone().sub(view.mid);
    m.position.copy(dir.multiplyScalar(e * 0.9));
  });
  connectors.forEach(c => {
    const ids = c.userData.joint.parts;
    const on = document.getElementById('showc').checked &&
      ids.every(id => (!k || (placedAt[id] || 0) <= k) && under(byId[id]));
    c.visible = on;
    const dir = c.userData.home.clone().sub(view.mid);
    c.position.copy(c.userData.home).add(dir.multiplyScalar(e * 0.9));
  });
}
['steps', 'explode', 'showc'].forEach(id => document.getElementById(id).addEventListener('input', apply));
document.getElementById('reset').onclick = () => { stepIn.value = 0; document.getElementById('explode').value = 0; go([]); document.querySelector('aside').scrollTop = 0; };

const list = document.getElementById('parts'), trail = document.getElementById('path');
const fmt = n => String(Math.round(n * 10) / 10);
let seen = {};
// the list is the group shown: the groups in it first, then its own parts, one row per letter
function listing() {
  list.innerHTML = ''; seen = {};
  const groups = new Map();
  DATA.parts.filter(under).forEach(p => {
    const g = p.within[here.length];
    if (g) { if (!groups.has(g[0])) groups.set(g[0], {name: g[1], parts: []}); groups.get(g[0]).parts.push(p); return; }
    if (seen[p.mark]) { seen[p.mark].n += p.sheets; seen[p.mark].li.querySelector('.n').textContent = '× ' + seen[p.mark].n; return; }
    const li = document.createElement('li');
    const s = [p.hi[0]-p.lo[0], p.hi[1]-p.lo[1], p.hi[2]-p.lo[2]].sort((a,b)=>b-a);
    li.innerHTML = `<span class="mark">${p.mark}</span><span><b>${p.name}</b> <span class="n">× ${p.sheets}</span><br><span class="dims">${s[0]} × ${s[1]} × ${s[2]/p.sheets} mm</span></span>`;
    li.onclick = () => select(p.mark);
    list.appendChild(li); seen[p.mark] = {li, n:p.sheets};
  });
  [...groups].reverse().forEach(([id, g]) => {
    const li = document.createElement('li');
    const s = [0, 1, 2].map(i => Math.max(...g.parts.map(p => p.hi[i])) - Math.min(...g.parts.map(p => p.lo[i]))).sort((a,b)=>b-a);
    li.innerHTML = `<span class="group"></span><span><b>${g.name}</b><br><span class="dims">${fmt(s[0])} × ${fmt(s[1])} × ${fmt(s[2])} mm</span></span><span class="into" aria-hidden="true">›</span>`;
    li.onclick = () => go([...here, id]);
    list.prepend(li);
  });
  // the way back up: the piece, then each group down to the one shown
  trail.hidden = !here.length;
  trail.innerHTML = '';
  if (!here.length) return;
  const first = DATA.parts.find(under);
  [[null, DATA.title], ...first.within.slice(0, here.length)].forEach(([id, name], i) => {
    if (i) trail.append(' › ');
    if (i === here.length) { const b = document.createElement('b'); b.textContent = name; trail.append(b); return; }
    const a = document.createElement('a'); a.href = '#'; a.textContent = name;
    a.onclick = ev => { ev.preventDefault(); go(here.slice(0, i)); };
    trail.append(a);
  });
}
function go(to) {
  here = to; view = shown(); selected = null;
  meshes.forEach(m => m.userData.selected = false);
  tip.style.display = 'none';
  listing(); home(); apply();
  // the list that was tapped stays where it is seen, under the view
  trail.previousElementSibling.scrollIntoView();
}
document.getElementById('sub').textContent = DATA.subtitle;

let selected = null;
function select(mark) {
  selected = selected === mark ? null : mark;
  meshes.forEach(m => m.userData.selected = selected && m.userData.part.mark === selected);
  Object.entries(seen).forEach(([k, v]) => v.li.classList.toggle('on', k === selected));
  apply();
}
const ray = new THREE.Raycaster(), ptr = new THREE.Vector2();
const strike = ev => {
  const r = renderer.domElement.getBoundingClientRect();
  ptr.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ptr, camera);
  return ray.intersectObjects(meshes.filter(m => m.visible), false)[0];
};
// a second tap at the same place within 0.35 s: on the piece, the view turns around that point and
// comes close to it; beside the piece, it shows the whole of what is shown again
let down = null, last = null;
function closer(hit) {
  if (!hit) { home(); return; }
  const from = camera.position.clone().sub(controls.target), d = Math.max(from.length() * 0.3, 25);
  controls.target.copy(hit.point);
  camera.position.copy(hit.point).add(from.setLength(d));
  controls.update();
}
renderer.domElement.addEventListener('pointerdown', ev => down = [ev.clientX, ev.clientY]);
renderer.domElement.addEventListener('pointerup', ev => {
  const moved = down && Math.hypot(ev.clientX - down[0], ev.clientY - down[1]) > 6;
  const hit = strike(ev);
  if (!moved && last && ev.timeStamp - last.t < 350 && Math.hypot(ev.clientX - last.x, ev.clientY - last.y) < 30) {
    last = null; closer(hit); return;
  }
  last = moved ? null : {t: ev.timeStamp, x: ev.clientX, y: ev.clientY};
  if (!hit) { tip.style.display = 'none'; return; }
  const p = hit.object.userData.part;
  const s = [p.hi[0]-p.lo[0], p.hi[1]-p.lo[1], p.hi[2]-p.lo[2]].sort((a,b)=>b-a);
  tip.innerHTML = `<b>${p.mark} — ${p.name}</b><br>${s[0]} × ${s[1]} × ${s[2]} mm<br>${p.material}`;
  tip.style.display = 'block';
  select(p.mark);
});
listing();
apply();
(function loop() {
  requestAnimationFrame(loop); controls.update();
  // the nearest thing drawn follows the distance, so the view can come right up to a part
  const near = Math.max(0.2, camera.position.distanceTo(controls.target) / 200);
  if (near !== camera.near) { camera.near = near; camera.updateProjectionMatrix(); }
  renderer.render(scene, camera);
})();
</script>
</body>
</html>
"""

WORDS = {
    "fr": {"steps": "Étape de montage", "explode": "Écarter les pièces", "connectors": "Connecteurs",
           "reset": "Réinitialiser", "parts": "Pièces", "finished": "Meuble monté. Glisser pour suivre "
           "le montage étape par étape."},
    "en": {"steps": "Assembly step", "explode": "Pull the parts apart", "connectors": "Connectors",
           "reset": "Reset", "parts": "Parts", "finished": "Finished piece. Slide to follow the "
           "assembly step by step."},
}


def _profile(p) -> dict:
    f = p.profile()
    return {"u": f.u, "v": f.v, "t": f.t, "outline": f.outline, "t0": f.t0, "t1": f.t1}


def viewer_html(sc: Scene, path: Path, lang: str = "fr") -> Path:
    W = WORDS[lang]
    size = [h - l for l, h in zip(sc.lo, sc.hi)]
    data = {
        "lo": sc.lo, "hi": sc.hi, "finished": W["finished"], "title": sc.title,
        "subtitle": f"{sc.info.get('version', '')} · {round(size[0])} × {round(size[1])} × "
                    f"{round(size[2])} mm",
        "parts": [{"id": p.id, "mark": p.mark, "name": p.name, "lo": p.lo, "hi": p.hi,
                   "sheets": p.sheets, "material": p.material_name, "within": p.within,
                   "profile": _profile(p)} for p in sc.parts],
        "joints": [{"id": j.id, "parts": j.parts, "along": j.along_axis, "normal": j.normal_axis,
                    "positions": j.positions, "size": j.size} for j in sc.joints],
        "steps": [{"text": s.text, "add": s.add, "prepare": s.prepare} for s in sc.steps],
    }
    page = (PAGE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
            .replace("__TITLE__", html.escape(sc.title)).replace("__LANG__", lang)
            .replace("__L_STEPS__", W["steps"]).replace("__L_EXPLODE__", W["explode"])
            .replace("__L_CONNECTORS__", W["connectors"]).replace("__L_RESET__", W["reset"])
            .replace("__L_PARTS__", W["parts"]))
    path.write_text(page, encoding="utf-8")
    return path
