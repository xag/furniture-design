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
/* wide: the model, and beside it the tree over the tools; narrow: the tree, the model, the tools */
#app { display:grid; height:100%; grid-template-columns:1fr 300px; grid-template-rows:auto 1fr; }
#stage { grid-column:1; grid-row:1 / span 2; position:relative; min-width:0; min-height:0; overflow:hidden; }
canvas { display:block; width:100%; height:100%; touch-action:none; }
#nav, #tools { grid-column:2; background:var(--panel); border-left:1px solid var(--line); overflow:auto; }
#nav { grid-row:1; padding:16px 16px 0; max-height:60vh; }
#tools { grid-row:2; padding:0 16px 16px; }
#nav.more { -webkit-mask-image:linear-gradient(to bottom, #000 calc(100% - 40px), transparent);
  mask-image:linear-gradient(to bottom, #000 calc(100% - 40px), transparent); }
h1 { font-size:18px; margin:0 0 2px; }
.sub { color:var(--muted); font-size:13px; margin-bottom:14px; }
[hidden] { display:none; }
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
h1 a { color:inherit; }
li .into { margin-left:auto; color:var(--muted); font-size:18px; }
li .group { width:24px; flex:none; }
#tip { position:absolute; left:12px; top:12px; background:var(--panel); border:1px solid var(--line);
  border-radius:8px; padding:8px 10px; font-size:13px; display:none; max-width:70%; }
.row { display:flex; gap:8px; align-items:center; margin-top:10px; font-size:13px; }
button { font:inherit; font-size:13px; padding:6px 10px; border-radius:6px; border:1px solid var(--line);
  background:var(--bg); color:var(--ink); cursor:pointer; }
@media (max-width: 720px) {
  #app { display:flex; flex-direction:column; }
  #nav { max-height:38%; padding:12px 16px 4px; border-left:none; border-bottom:1px solid var(--line); }
  #stage { flex:1; min-height:34%; }
  #tools { max-height:30%; padding:0 16px 12px; border-left:none; border-top:1px solid var(--line); }
}
</style>
</head>
<body>
<div id="app">
  <div id="nav">
    <h1 id="title">__TITLE__</h1>
    <div class="sub" id="sub"></div>
    <label>__L_PARTS__</label>
    <ul id="parts"></ul>
  </div>
  <div id="stage"><div id="tip"></div></div>
  <div id="tools">
    <div id="assembly">
      <label for="steps">__L_STEPS__ <span id="stepn"></span></label>
      <input id="steps" type="range" min="0" value="0">
      <div class="step" id="steptext"></div>
    </div>
    <label for="explode">__L_EXPLODE__</label>
    <input id="explode" type="range" min="0" max="100" value="0">
    <div class="row"><input id="showc" type="checkbox" checked><span>__L_CONNECTORS__</span>
      <span style="flex:1"></span><button id="reset">__L_RESET__</button></div>
  </div>
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
// the way down to what is shown: the ids of the groups from the piece, then, when one part is
// opened, {mark, name}: the parts of that letter in the last group
let here = [];
const groupsOf = () => here.filter(x => typeof x === 'string'), opened = () => here.find(x => typeof x !== 'string');
const under = p => groupsOf().every((id, i) => p.within[i] && p.within[i][0] === id) &&
  (!opened() || p.mark === opened().mark);
// the middle and the largest side of what is shown
function shown() {
  const ps = DATA.parts.filter(under), a = [0, 1, 2].map(i => Math.min(...ps.map(p => p.lo[i]))),
    b = [0, 1, 2].map(i => Math.max(...ps.map(p => p.hi[i])));
  const mid = T((a[0]+b[0])/2, (a[1]+b[1])/2, (a[2]+b[2])/2), s = [b[0]-a[0], b[1]-a[1], b[2]-a[2]].sort((x, y) => y - x);
  // parts whose middles are close (two profiles nested in a rail) are pulled apart by at least
  // most of what is shown's second side, or the pull would not show
  const far = Math.max(1e-6, ...ps.map(p => T((p.lo[0]+p.hi[0])/2, (p.lo[1]+p.hi[1])/2, (p.lo[2]+p.hi[2])/2).distanceTo(mid)));
  return {mid, size: s[0], lo: a, hi: b, pull: Math.max(0.9, 0.6 * s[1] / far)};
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
new ResizeObserver(fit).observe(stage); fit(); home();
// a list longer than its place fades at its foot until it is drawn to its end
const nav = document.getElementById('nav');
const more = () => nav.classList.toggle('more', nav.scrollTop + nav.clientHeight < nav.scrollHeight - 4);
nav.addEventListener('scroll', more);

// steps: 0 shows the finished piece; k shows the state after assembly step k
const steps = DATA.steps.filter(s => !s.prepare);
const stepIn = document.getElementById('steps');
const placedAt = {};
steps.forEach((s, i) => s.add.forEach(id => placedAt[id] = i + 1));
// the steps followed are those that bring a part of what is shown; with fewer than two there is
// nothing to follow, and the slider is not drawn
let mine = [];
function follow() {
  mine = steps.map((s, i) => i + 1).filter(n => steps[n-1].add.some(id => byId[id] && under(byId[id])));
  stepIn.max = mine.length; stepIn.value = 0;
  document.getElementById('assembly').hidden = mine.length < 2;
}

function apply() {
  const n = +stepIn.value, k = n ? mine[n-1] : 0, e = +document.getElementById('explode').value / 100;
  document.getElementById('stepn').textContent = n ? `${n} / ${mine.length}` : '';
  document.getElementById('steptext').textContent = k ? steps[k-1].text : DATA.finished;
  meshes.forEach(m => {
    const p = m.userData.part, at = placedAt[p.id] || 0;
    const visible = (!k || at <= k) && under(p);
    m.visible = visible;
    const isNew = k && at === k;
    m.material.color.copy(m.userData.selected ? pick : (isNew ? newColor : woodColor));
    const host = m.userData.host, from = (host || m).userData.centre.clone().sub(view.mid);
    m.position.copy(from.multiplyScalar(e * view.pull)).add(m.userData.split.clone().multiplyScalar(Math.sqrt(e)));
  });
  connectors.forEach(c => {
    const ids = c.userData.joint.parts;
    const on = document.getElementById('showc').checked &&
      ids.every(id => (!k || (placedAt[id] || 0) <= k) && under(byId[id]));
    c.visible = on;
    const dir = c.userData.home.clone().sub(view.mid);
    c.position.copy(c.userData.home).add(dir.multiplyScalar(e * view.pull));
  });
}
['steps', 'explode', 'showc'].forEach(id => document.getElementById(id).addEventListener('input', apply));
document.getElementById('reset').onclick = () => { stepIn.value = 0; document.getElementById('explode').value = 0; go([]); };

const list = document.getElementById('parts'), title = document.getElementById('title');
const fmt = n => String(Math.round(n * 10) / 10);
let seen = {};
// the list is the group shown: the groups in it first, then its own parts, one row per letter;
// a row opens its group or its part alone. The title is the way back up, the piece then each
// group down to what is shown, and the line under it gives the size of what is shown.
function listing() {
  list.innerHTML = ''; seen = {};
  const groups = new Map();
  const depth = groupsOf().length;
  DATA.parts.filter(under).forEach(p => {
    const g = p.within[depth];
    if (g) { if (!groups.has(g[0])) groups.set(g[0], {name: g[1], parts: []}); groups.get(g[0]).parts.push(p); return; }
    if (seen[p.mark]) { seen[p.mark].n += p.sheets; seen[p.mark].li.querySelector('.n').textContent = '× ' + seen[p.mark].n; return; }
    const li = document.createElement('li');
    const s = [p.hi[0]-p.lo[0], p.hi[1]-p.lo[1], p.hi[2]-p.lo[2]].sort((a,b)=>b-a);
    li.innerHTML = `<span class="mark">${p.mark}</span><span><b>${p.name}</b> <span class="n">× ${p.sheets}</span><br><span class="dims">${s[0]} × ${s[1]} × ${s[2]/p.sheets} mm</span></span>` +
      (opened() ? '' : '<span class="into" aria-hidden="true">›</span>');
    li.onclick = () => opened() ? select(p.mark) : go([...groupsOf(), {mark: p.mark, name: p.name}]);
    list.appendChild(li); seen[p.mark] = {li, n:p.sheets};
  });
  [...groups].reverse().forEach(([id, g]) => {
    const li = document.createElement('li');
    const s = [0, 1, 2].map(i => Math.max(...g.parts.map(p => p.hi[i])) - Math.min(...g.parts.map(p => p.lo[i]))).sort((a,b)=>b-a);
    li.innerHTML = `<span class="group"></span><span><b>${g.name}</b><br><span class="dims">${fmt(s[0])} × ${fmt(s[1])} × ${fmt(s[2])} mm</span></span><span class="into" aria-hidden="true">›</span>`;
    li.onclick = () => go([...here, id]);
    list.prepend(li);
  });
  const [version] = DATA.subtitle.split(' · '), d = [0, 1, 2].map(i => Math.round(view.hi[i] - view.lo[i]));
  document.getElementById('sub').textContent = `${version} · ${d[0]} × ${d[1]} × ${d[2]} mm`;
  title.textContent = DATA.title;
  if (!here.length) return;
  title.innerHTML = '';
  const first = DATA.parts.find(under), part = opened();
  [[null, DATA.title], ...first.within.slice(0, depth), ...(part ? [[part, part.name]] : [])].forEach(([id, name], i) => {
    if (i) title.append(' › ');
    if (i === here.length) { title.append(name); return; }
    const a = document.createElement('a'); a.href = '#'; a.textContent = name;
    a.onclick = ev => { ev.preventDefault(); go(here.slice(0, i)); };
    title.append(a);
  });
}
// A part that sits inside another's box (a channel in the angle that holds it, a frame's bar
// along its panel) is pulled apart from it the way the holder opens: from the middle of the
// holder's material to the middle of its box, which for an angle points out of its corner, away
// from both its faces, and for a channel out of its mouth. A holder that is solid (a panel)
// opens nowhere, and the two part along the line between their middles. They move away from
// each other, half each, fast at first: at a tenth of the slider they are nearly clear, and at
// its end apart by six tenths of what it takes to clear, beyond clearing. A part holding several moves by
// the mean of what they push it, so a panel framed on four sides stays where it is.
function middle(p) {   // the middle of a part's section, in the piece's frame
  const f = p.profile, o = f.outline;
  let a = 0, x = 0, y = 0;
  o.forEach(([x0, y0], i) => { const [x1, y1] = o[(i + 1) % o.length], c = x0 * y1 - x1 * y0;
    a += c; x += (x0 + x1) * c; y += (y0 + y1) * c; });
  const m = [0, 0, 0];
  m[f.u] = x / (3 * a); m[f.v] = y / (3 * a); m[f.t] = (f.t0 + f.t1) / 2;
  return m;
}
function nested() {
  meshes.forEach(m => { m.userData.host = null; m.userData.split = new THREE.Vector3(); m.userData.pushed = []; });
  const ps = meshes.filter(m => under(m.userData.part));
  const vol = p => (p.hi[0]-p.lo[0]) * (p.hi[1]-p.lo[1]) * (p.hi[2]-p.lo[2]);
  ps.forEach(m => {
    const p = m.userData.part;
    const host = ps.filter(o => o !== m && vol(o.userData.part) > vol(p) &&
      [0, 1, 2].every(i => Math.min(p.hi[i], o.userData.part.hi[i]) - Math.max(p.lo[i], o.userData.part.lo[i]) > 0.5))
      .sort((a, b) => vol(a.userData.part) - vol(b.userData.part))[0];
    if (!host) return;
    const q = host.userData.part, h = middle(q), box = [0, 1, 2].map(i => (q.lo[i] + q.hi[i]) / 2);
    let d = [0, 1, 2].map(i => box[i] - h[i]);
    if (Math.hypot(...d) < 0.05 * Math.min(...[0, 1, 2].map(i => q.hi[i] - q.lo[i]))) {
      const g = middle(p); d = [0, 1, 2].map(i => g[i] - h[i]);
    }
    const s = [0, 1, 2].map(i => p.hi[i] - p.lo[i]), long = s.indexOf(Math.max(...s));
    if (s[long] > 4 * Math.max(...s.filter((_, i) => i !== long))) d[long] = 0;   // across a bar's length
    const n = Math.hypot(...d);
    if (n < 1e-6) return;
    const w = d.map(x => x / n);
    // how far along that line the held part goes before the two boxes no longer overlap
    const clear = Math.max(2, Math.min(...[0, 1, 2].filter(i => Math.abs(w[i]) > 1e-6).map(i =>
      w[i] > 0 ? (q.hi[i] - p.lo[i]) / w[i] : (q.lo[i] - p.hi[i]) / w[i])));
    const half = T(w[0], w[1], w[2]).multiplyScalar(1.6 * clear / 2);
    m.userData.host = host;
    m.userData.split.add(half);
    host.userData.pushed.push(half.clone().negate());
  });
  ps.forEach(m => { const v = m.userData.pushed;
    if (v.length) m.userData.split.add(v.reduce((a, b) => a.add(b), new THREE.Vector3()).divideScalar(v.length)); });
}
function go(to) {
  here = to; view = shown(); selected = null; nested(); follow();
  meshes.forEach(m => m.userData.selected = false);
  tip.style.display = 'none';
  listing(); home(); apply();
  nav.scrollTop = 0; more();
}

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
nested(); follow(); listing(); more();
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
