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
#tools { grid-row:2; padding:0 16px 16px; border-top:1px solid var(--line); }
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
.row.end { justify-content:flex-end; }
/* what is drawn: under the tree where there is room, else behind the Display button beside Reset */
#display { padding-top:4px; }
label.opt { display:flex; align-items:center; gap:10px; min-height:44px; margin:0; color:var(--ink); cursor:pointer; }
label.opt input { width:18px; height:18px; margin:0; accent-color:var(--ink); }
.choice > span { display:block; font-size:13px; color:var(--muted); margin:6px 0 6px; }
.seg { display:flex; border:1px solid var(--line); border-radius:8px; overflow:hidden; }
.seg label { flex:1; margin:0; position:relative; color:var(--ink); cursor:pointer; }
.seg label + label { border-left:1px solid var(--line); }
.seg input { position:absolute; width:1px; height:1px; opacity:0; margin:0; pointer-events:none; }
.seg span { display:flex; align-items:center; justify-content:center; min-height:44px; padding:0 4px; text-align:center; }
.seg input:checked + span { background:var(--ink); color:var(--panel); }
.seg input:focus-visible + span { outline:2px solid var(--accent); outline-offset:-2px; }
#marks { position:absolute; inset:0; pointer-events:none; }
#opts { display:none; align-items:center; gap:2px; padding-right:6px; }
#opts svg { transition:transform .15s; }
#opts[aria-expanded="true"] svg { transform:rotate(180deg); }
@media (max-width: 720px) {
  #app { display:flex; flex-direction:column; }
  #nav { max-height:38%; padding:12px 16px 4px; border-left:none; border-bottom:1px solid var(--line); }
  #stage { flex:1; min-height:34%; }
  #tools { max-height:30%; padding:0 16px 12px; border-left:none; border-top:1px solid var(--line); }
  #tools.sheet { max-height:none; flex:none; }   /* open, the settings take what they need; the tree gives it up */
}
/* with a mouse, a row needs no finger's height: the settings fit under the tree on a laptop */
@media (pointer: fine) {
  label.opt, .seg span { min-height:32px; }
}
/* with no room for it under the tree (room(): a phone, or a column too short to hold it and the
   sliders), what is drawn opens in the sliders' place from the Display button at the foot of the tools */
.tight #opts { display:inline-flex; }
.tight #foot { justify-content:space-between; }
.tight #display { display:none; padding-top:8px; }
.tight #display.open { display:block; }
.tight #tools.sheet > :not(#display):not(#foot) { display:none; }
.tight #tools.sheet #foot { position:sticky; bottom:-12px; padding-bottom:12px; margin-bottom:-12px; background:var(--panel); }
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
  <div id="stage"><canvas id="marks"></canvas><div id="tip"></div></div>
  <div id="tools">
    <div id="display">
      <label class="opt"><input id="showc" type="checkbox" checked>__L_CONNECTORS__</label>
      <div class="choice"><span id="dimslab">__L_DIMENSIONS__</span>
        <div class="seg" role="radiogroup" aria-labelledby="dimslab">
          <label><input type="radio" name="dims" value="none" checked><span>__L_NODIMS__</span></label>
          <label><input type="radio" name="dims" value="chain"><span>__L_CHAIN__</span></label>
          <label><input type="radio" name="dims" value="part"><span>__L_SIZES__</span></label>
        </div>
      </div>
      <div id="restrow" class="choice" hidden><span id="restlab">__L_REST__</span>
        <div class="seg" role="radiogroup" aria-labelledby="restlab">
          <label><input type="radio" name="rest" value="hidden" checked><span>__L_HIDDEN__</span></label>
          <label><input type="radio" name="rest" value="see"><span>__L_SEE__</span></label>
          <label><input type="radio" name="rest" value="solid"><span>__L_SOLID__</span></label>
        </div>
      </div>
    </div>
    <div id="assembly">
      <label for="steps">__L_STEPS__ <span id="stepn"></span></label>
      <input id="steps" type="range" min="0" value="0">
      <div class="step" id="steptext"></div>
    </div>
    <label for="explode">__L_EXPLODE__</label>
    <input id="explode" type="range" min="0" max="100" value="0">
    <div class="row end" id="foot"><button id="opts" type="button" aria-expanded="false" aria-controls="display">__L_DISPLAY__<svg
      width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z"/></svg></button><button id="reset">__L_RESET__</button></div>
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
const restColor = new THREE.Color(0x8f8b85);
// how the rest of the piece is drawn while a group is shown: hidden, see, solid
const rest = () => here.length ? document.querySelector('input[name=rest]:checked').value : 'hidden';

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
steps.forEach((s, i) => s.add.forEach(id => { if (!(id in placedAt)) placedAt[id] = i + 1; }));
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
  const mode = rest();
  meshes.forEach(m => {
    const p = m.userData.part, at = placedAt[p.id] || 0;
    if (!under(p)) {
      // the rest of the piece, finished and in its place: transparent, solid in grey without its
      // outlines, or not drawn; never while the parts are pulled apart, since they would pass into it
      m.visible = mode !== 'hidden' && !e;
      look(m, mode === 'see' ? 0.15 : 1, mode === 'see' ? 0.25 : 0);
      m.material.color.copy(restColor);
      m.position.set(0, 0, 0);
      return;
    }
    look(m, 1, 1);
    const visible = (!k || at <= k);
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
document.querySelectorAll('input[name=rest]').forEach(r => r.addEventListener('change', apply));
// a part drawn at an opacity; see-through parts write no depth, so what is shown is seen through them
function look(m, a, edge) {
  const see = a < 1;
  if (m.material.depthWrite === see) { m.material.depthWrite = !see; m.material.needsUpdate = true; }
  m.material.opacity = a; m.children[0].material.opacity = edge; m.children[0].visible = edge > 0;
  m.renderOrder = see ? 1 : 0;
}
// where there is no room under the tree, the Display button at the foot of the tools opens what is
// drawn in the sliders' place and closes it; Escape closes it too. It adds no step to the history:
// the page that holds the view goes back by its own steps
const opts = document.getElementById('opts'), display = document.getElementById('display');
const tools = document.getElementById('tools');
const isOpen = () => display.classList.contains('open');
function sheet(open) {
  if (open === isOpen()) return;
  display.classList.toggle('open', open); tools.classList.toggle('sheet', open);
  opts.setAttribute('aria-expanded', String(open));
  if (!open && display.contains(document.activeElement)) opts.focus();
}
opts.onclick = () => sheet(!isOpen());
document.addEventListener('keydown', ev => { if (ev.key === 'Escape' && isOpen()) sheet(false); });
// room for what is drawn under the tree: never on a narrow screen; else when the tools, with it in
// them, fit their place without scrolling
const narrow = matchMedia('(max-width: 720px)');
function room() {
  const app = document.getElementById('app');
  app.classList.remove('tight');
  if (narrow.matches || tools.scrollHeight > tools.clientHeight + 1) app.classList.add('tight');
}
new ResizeObserver(room).observe(document.getElementById('app'));
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
  document.getElementById('restrow').hidden = !here.length;
  meshes.forEach(m => m.userData.selected = false);
  tip.style.display = 'none';
  listing(); room(); home(); apply();
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
  // a tap passes through a transparent rest, and a solid one catches it
  return ray.intersectObjects(meshes.filter(m => m.visible && (under(m.userData.part) || rest() === 'solid')), false)[0];
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
  if (!hit || !under(hit.object.userData.part)) { tip.style.display = 'none'; return; }
  const p = hit.object.userData.part;
  const s = [p.hi[0]-p.lo[0], p.hi[1]-p.lo[1], p.hi[2]-p.lo[2]].sort((a,b)=>b-a);
  tip.innerHTML = `<b>${p.mark} — ${p.name}</b><br>${s[0]} × ${s[1]} × ${s[2]} mm<br>${p.material}`;
  tip.style.display = 'block';
  select(p.mark);
});
nested(); follow(); listing(); more();
apply();

// Dimensions on what is shown, off the edge of its box that is nearest the bottom of the screen
// (the leftmost for the height), as the plans dimension a view. Positions: along each axis the
// chain of the parts' edges and the whole. Sizes: each part's own length along each axis, in rows
// outward from the box, a row holding sizes that do not overlap. A dimension is drawn only when its
// line is longer than its number, its number meets no number already drawn and none of its lines
// crosses one: the whole first, then the longest; so coming closer brings the short ones in.
// Nothing is measured while the parts are pulled apart, since none is where its dimension would put it.
const dimsMode = () => document.querySelector('input[name=dims]:checked').value;
const markCv = document.getElementById('marks'), mk = markCv.getContext('2d');
const explodeIn = document.getElementById('explode');
let ink = '#1d1d1b', paper = '#fffdf9';
function colours() {
  const s = getComputedStyle(document.documentElement);
  ink = s.getPropertyValue('--ink').trim(); paper = s.getPropertyValue('--panel').trim();
}
colours(); matchMedia('(prefers-color-scheme: dark)').addEventListener('change', colours);
// the parts dimensioned: what is shown, as far as the assembly step has brought it
function measured() {
  const n = +stepIn.value, k = n ? mine[n-1] : 0;
  return DATA.parts.filter(p => under(p) && (!k || (placedAt[p.id] || 0) <= k));
}
const W3 = (q) => T(q[0], q[1], q[2]);
function toScreen(v, w, h) {
  const q = v.clone().project(camera);
  return q.z > 1 || q.z < -1 ? null : [(q.x + 1) / 2 * w, (1 - q.y) / 2 * h];
}
// the edge of a box (lo, hi) along axis a on which its dimensions stand, as its two corners, and
// the side away from the box on screen: the lowest on screen (the leftmost for the height), or with
// far the highest (the rightmost); it stays on the edge it was on until another beats it by 12 px,
// so turning the model a little never moves a number
const kept = new Map();
function edgeFor(lo, hi, a, w, h, name, far) {
  const [b, c] = [0, 1, 2].filter(i => i !== a), eye = camera.position;
  const toPiece = [eye.x, -eye.z, eye.y];          // three -> piece frame
  const facing = (i, s) => s ? toPiece[i] > hi[i] : toPiece[i] < lo[i];
  const key = name || [a, ...lo, ...hi].join(), was = kept.get(key);
  let best = null, held = null;
  for (const sb of [0, 1]) for (const sc of [0, 1]) {
    if (facing(b, sb) === facing(c, sc)) continue;  // on the outline: one face turned to the eye
    const p0 = [0, 0, 0]; p0[a] = lo[a]; p0[b] = sb ? hi[b] : lo[b]; p0[c] = sc ? hi[c] : lo[c];
    const p1 = p0.slice(); p1[a] = hi[a];
    const s0 = toScreen(W3(p0), w, h), s1 = toScreen(W3(p1), w, h);
    if (!s0 || !s1) continue;
    const it = {score: (far ? -1 : 1) * (a === 2 ? -(s0[0] + s1[0]) : (s0[1] + s1[1])) / 2, p0, s0, s1, side: 2 * sb + sc};
    if (it.side === was) held = it;
    if (!best || it.score > best.score) best = it;
  }
  if (held && held.score > best.score - 12) best = held;
  if (!best) return null;
  kept.set(key, best.side);
  const m = toScreen(W3([0, 1, 2].map(i => (lo[i] + hi[i]) / 2)), w, h);
  const dx = best.s1[0] - best.s0[0], dy = best.s1[1] - best.s0[1], len = Math.hypot(dx, dy) || 1;
  let nx = -dy / len, ny = dx / len;
  const ex = (best.s0[0] + best.s1[0]) / 2 - (m ? m[0] : 0), ey = (best.s0[1] + best.s1[1]) / 2 - (m ? m[1] : 0);
  if (nx * ex + ny * ey < 0) { nx = -nx; ny = -ny; }
  return {p0: best.p0, nx, ny};
}
// each dimension: its axis, the edge it stands on, its two ends along the axis, the point of a part
// each end is measured from (where its extension line starts), how far off the box, and its order:
// the whole first, then from the longest down, in mm, so the order never changes as the view turns
function candidates(w, h) {
  const ps = measured(), out = [];
  if (!ps.length) return out;
  const lo = [0, 1, 2].map(i => Math.min(...ps.map(p => p.lo[i]))), hi = [0, 1, 2].map(i => Math.max(...ps.map(p => p.hi[i])));
  [0, 1, 2].forEach(a => {
    const e = edgeFor(lo, hi, a, w, h, 'shown' + a);   // kept across the assembly steps
    if (!e) return;
    const [b, c] = [0, 1, 2].filter(i => i !== a), r1 = v => Math.round(v * 10) / 10;
    // the corner of a part at this position along the axis that is nearest the edge dimensioned
    const corner = (p, x, at = e) => {
      const q = [0, 0, 0]; q[a] = x;
      [b, c].forEach(i => q[i] = Math.abs(p.lo[i] - at.p0[i]) < Math.abs(p.hi[i] - at.p0[i]) ? p.lo[i] : p.hi[i]);
      return {d: Math.hypot(q[b] - at.p0[b], q[c] - at.p0[c]), q};
    };
    const from = v => {
      let best = null;
      ps.forEach(p => [p.lo[a], p.hi[a]].forEach(x => {
        if (r1(x) !== v) return;
        const k = corner(p, x);
        if (!best || k.d < best.d) best = k;
      }));
      return best.q;
    };
    // a part's size stands on the edge of the two opposite ones that is nearer it, as an elevation
    // dimensions a top rail above the view and a bottom rail below; one size per span: two parts
    // as long, side by side, give one
    if (dimsMode() === 'part') {
      const e2 = edgeFor(lo, hi, a, w, h, 'far' + a, true), seen = new Set();
      ps.forEach(p => {
        const key = r1(p.lo[a]) + ':' + r1(p.hi[a]);
        if (seen.has(key)) return;
        seen.add(key);
        const far = e2 && corner(p, p.lo[a], e2).d < corner(p, p.lo[a]).d - 1, at = far ? e2 : e;
        out.push({e: at, a, k: a + (far ? 3 : 0), from: p.lo[a], to: p.hi[a], f: corner(p, p.lo[a], at).q,
                  t: corner(p, p.hi[a], at).q, rows: true, rank: 1, size: p.hi[a] - p.lo[a]});
      });
      return;
    }
    const vs = [...new Set(ps.flatMap(p => [p.lo[a], p.hi[a]]).map(r1))].sort((x, y) => x - y);
    const chained = vs.length > 2, n = vs.length - 1;
    out.push({e, a, from: vs[0], to: vs[n], f: from(vs[0]), t: from(vs[n]), gap: chained ? 40 : 18, rank: 0, size: vs[n] - vs[0]});
    if (chained) vs.slice(1).forEach((v, i) => out.push({e, a, from: vs[i], to: v, f: from(vs[i]), t: from(v), gap: 18, rank: 1, size: v - vs[i]}));
  });
  return out.sort((x, y) => x.rank - y.rank || y.size - x.size);
}
// drawn over the model, never hidden by it: a number is read where it stands
function marks() {
  const w = stage.clientWidth, h = stage.clientHeight, r = Math.min(window.devicePixelRatio, 2);
  if (markCv.width !== Math.round(w * r) || markCv.height !== Math.round(h * r)) {
    markCv.width = Math.round(w * r); markCv.height = Math.round(h * r);
  }
  mk.setTransform(r, 0, 0, r, 0, 0); mk.clearRect(0, 0, w, h);
  if (dimsMode() === 'none' || +explodeIn.value > 0) return;
  mk.font = '12px system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
  mk.lineWidth = 1; mk.strokeStyle = ink; mk.fillStyle = ink;
  const placed = [], lines = [], rows = [[], [], [], [], [], []];
  const meets = (o, b) => b.x < o.x + o.w && o.x < b.x + b.w && b.y < o.y + o.h && o.y < b.y + b.h;
  // whether the segment p-q passes through the box b (clipped against it, Liang-Barsky)
  const through = (p, q, b) => {
    let t0 = 0, t1 = 1;
    const dx = q[0] - p[0], dy = q[1] - p[1];
    for (const [pp, qq] of [[-dx, p[0] - b.x], [dx, b.x + b.w - p[0]], [-dy, p[1] - b.y], [dy, b.y + b.h - p[1]]]) {
      if (pp === 0) { if (qq < 0) return false; continue; }
      const r = qq / pp;
      if (pp < 0) { if (r > t1) return false; if (r > t0) t0 = r; } else { if (r < t0) return false; if (r < t1) t1 = r; }
    }
    return true;
  };
  const ds = candidates(w, h).filter(d => {
    const p0 = d.e.p0.slice(), p1 = d.e.p0.slice();
    p0[d.a] = d.from; p1[d.a] = d.to;
    d.s0 = toScreen(W3(p0), w, h); d.s1 = toScreen(W3(p1), w, h);
    d.f0 = toScreen(W3(d.f), w, h); d.f1 = toScreen(W3(d.t), w, h);
    if (!d.s0 || !d.s1 || !d.f0 || !d.f1) return false;
    d.len = Math.hypot(d.s1[0] - d.s0[0], d.s1[1] - d.s0[1]); d.text = fmt(d.size);
    d.tw = mk.measureText(d.text).width;
    return d.len >= d.tw + 16;
  });
  // the sizes long enough to be read take rows outward from the box, the shortest nearest, each in
  // the first row where it overlaps no other size on that axis, as a drawing stacks its dimensions;
  // the rows stand as far apart as a number is deep across its line, so a row's numbers clear the next
  const sized = ds.filter(d => d.rows), step = [0, 1, 2, 3, 4, 5].map(k => {
    const on = sized.filter(d => d.k === k), e = on.length && on[0].e;
    return on.length ? Math.max(22, Math.abs(e.nx) * (Math.max(...on.map(d => d.tw)) + 8) + Math.abs(e.ny) * 16 + 6) : 0;
  });
  sized.sort((x, y) => x.size - y.size).forEach(d => {
    let row = 0;
    while (rows[d.k][row] && rows[d.k][row].some(o => d.from < o.to - 0.05 && o.from < d.to - 0.05)) row++;
    (rows[d.k][row] = rows[d.k][row] || []).push(d);
    d.gap = 18 + step[d.k] * row;
  });
  ds.forEach(d => {
    const {e, s0, s1, f0, f1, len, text, gap} = d, box = {w: d.tw + 8, h: 16};
    const ox = e.nx * gap, oy = e.ny * gap;
    const a0 = [s0[0] + ox, s0[1] + oy], a1 = [s1[0] + ox, s1[1] + oy];
    const cx = (a0[0] + a1[0]) / 2, cy = (a0[1] + a1[1]) / 2;
    box.x = cx - box.w / 2; box.y = cy - box.h / 2;
    if (box.x < 0 || box.y < 0 || box.x + box.w > w || box.y + box.h > h) return;
    if (placed.some(o => meets(o, box))) return;
    const mine = [[f0, a0], [f1, a1], [a0, a1]];
    if (mine.some(([p, q]) => placed.some(o => through(p, q, o)))) return;
    if (lines.some(([p, q]) => through(p, q, box))) return;
    placed.push(box); lines.push(...mine);
    // the extension lines, from the part's own edge to just past the dimension line
    mk.globalAlpha = 0.55; mk.beginPath();
    [[f0, a0], [f1, a1]].forEach(([s, t]) => {
      const vx = t[0] - s[0], vy = t[1] - s[1], l = Math.hypot(vx, vy) || 1;
      mk.moveTo(s[0] + vx / l * 3, s[1] + vy / l * 3); mk.lineTo(t[0] + vx / l * 4, t[1] + vy / l * 4);
    });
    mk.stroke(); mk.globalAlpha = 1;
    mk.beginPath(); mk.moveTo(a0[0], a0[1]); mk.lineTo(a1[0], a1[1]); mk.stroke();
    const ux = (a1[0] - a0[0]) / len, uy = (a1[1] - a0[1]) / len;
    [[a0, 1], [a1, -1]].forEach(([t, s]) => {           // an arrowhead at each end, pointing out
      mk.beginPath(); mk.moveTo(t[0], t[1]);
      mk.lineTo(t[0] + s * ux * 6 - uy * 2.5, t[1] + s * uy * 6 + ux * 2.5);
      mk.lineTo(t[0] + s * ux * 6 + uy * 2.5, t[1] + s * uy * 6 - ux * 2.5); mk.closePath(); mk.fill();
    });
    mk.fillStyle = paper; mk.fillRect(box.x, box.y, box.w, box.h);
    mk.fillStyle = ink; mk.textAlign = 'center'; mk.textBaseline = 'middle'; mk.fillText(text, cx, cy + 0.5);
  });
}
(function loop() {
  requestAnimationFrame(loop); controls.update();
  // the nearest thing drawn follows the distance, so the view can come right up to a part
  const near = Math.max(0.2, camera.position.distanceTo(controls.target) / 200);
  if (near !== camera.near) { camera.near = near; camera.updateProjectionMatrix(); }
  renderer.render(scene, camera);
  marks();
})();
</script>
</body>
</html>
"""

WORDS = {
    "fr": {"steps": "Étape de montage", "explode": "Écarter les pièces", "connectors": "Connecteurs",
           "reset": "Réinitialiser", "parts": "Pièces", "finished": "Meuble monté. Glisser pour suivre "
           "le montage étape par étape.", "dimensions": "Cotes", "rest": "Reste du meuble",
           "hidden": "Masqué", "see": "Transparent", "solid": "Plein", "display": "Affichage",
           "nodims": "Masquées", "chain": "Positions", "sizes": "Tailles"},
    "en": {"steps": "Assembly step", "explode": "Pull the parts apart", "connectors": "Connectors",
           "reset": "Reset", "parts": "Parts", "finished": "Finished piece. Slide to follow the "
           "assembly step by step.", "dimensions": "Dimensions", "rest": "Rest of the piece",
           "hidden": "Hidden", "see": "Transparent", "solid": "Solid", "display": "Display",
           "nodims": "Hidden", "chain": "Positions", "sizes": "Sizes"},
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
    for key in ("dimensions", "rest", "hidden", "see", "solid", "display", "nodims", "chain", "sizes"):
        page = page.replace(f"__L_{key.upper()}__", html.escape(W[key]))
    path.write_text(page, encoding="utf-8")
    return path
