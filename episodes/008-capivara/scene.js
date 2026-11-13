import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
const W = 1080, H = 1920;
const Q = new URLSearchParams(location.search); const SCL = +(Q.get('s') || 1); const IW = Math.round(W * SCL), IH = Math.round(H * SCL);
const TL = await (await fetch('./timeline.json')).json(); const TOTAL = TL.total;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const sm = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
const lerp = (a, b, t) => a + (b - a) * t;
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const hash = (i) => { const s = Math.sin(i * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const back = (x) => { x = clamp(x, 0, 1); const c = 1.9; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const C = (h) => new THREE.Color(h);

// ---------------------------------------------------------------- motor "maquete": câmera isométrica, toon + contorno, sem pós
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setSize(IW, IH, false); renderer.setClearColor(0x000000, 0);
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const scene = new THREE.Scene();
const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 200);
const gm = new THREE.DataTexture(new Uint8Array([120, 120, 120, 255, 190, 190, 190, 255, 255, 255, 255, 255]), 3, 1, THREE.RGBAFormat); gm.minFilter = gm.magFilter = THREE.NearestFilter; gm.needsUpdate = true;
const toon = (c, o = {}) => new THREE.MeshToonMaterial({ color: c, gradientMap: gm, ...o });
const inkM = new THREE.MeshBasicMaterial({ color: 0x2a1c14, side: THREE.BackSide });
function mesh(geo, mat, ink = 1.05) { const m = new THREE.Mesh(geo, mat); m.castShadow = true; m.receiveShadow = true; if (ink) { const o = new THREE.Mesh(geo, inkM); o.scale.setScalar(ink); m.add(o); } return m; }
const RB = (w, h, d, r, mat, ink = 1.05) => mesh(new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2)), mat, ink);
const SP = (r, mat, ink = 1.07) => mesh(new THREE.SphereGeometry(r, 16, 12), mat, ink);
const CY = (r1, r2, h, mat, ink = 1.05) => mesh(new THREE.CylinderGeometry(r1, r2, h, 14), mat, ink);
const sun = new THREE.DirectionalLight(0xffffff, 2.6); sun.position.set(-6, 12, 7); sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9, near: 1, far: 40 }); sun.shadow.bias = -0.0008; sun.shadow.normalBias = 0.04; sun.shadow.radius = 5; scene.add(sun);
const amb = new THREE.HemisphereLight(0xffffff, 0xb0c4d8, 1.5); scene.add(amb);

// ---------------------------------------------------------------- ilha
const isle = new THREE.Group(); scene.add(isle);
const grassM = toon(0x8fd36a), grass2M = toon(0x79c25a), dirtM = toon(0xb9854f), dirt2M = toon(0x8f6238), sandM = toon(0xf1d9a0), snowM = toon(0xf4f8ff);
const waterM = new THREE.MeshToonMaterial({ color: 0x6fd3f2, gradientMap: gm, transparent: true, opacity: 0.78 });
const grassTop = [];
{
  const g1 = RB(9, 0.7, 5, 0.25, grassM); g1.position.set(0, -0.35, -2); isle.add(g1); grassTop.push(g1);
  const g2 = RB(9, 0.7, 0.6, 0.25, grassM); g2.position.set(0, -0.35, 4.2); isle.add(g2); grassTop.push(g2);
  for (const s of [-1, 1]) { const g3 = RB(0.6, 0.7, 4, 0.25, grassM); g3.position.set(s * 4.2, -0.35, 2.2); isle.add(g3); grassTop.push(g3); }
  const bed = RB(8.4, 0.5, 3.9, 0.1, sandM, 0); bed.position.set(0, -1.15, 2.2); isle.add(bed);
  const d1 = RB(8.8, 1.3, 8.8, 0.3, dirtM); d1.position.set(0, -1.3, 0); isle.add(d1);
  const d2 = RB(7.2, 1.0, 7.2, 0.4, dirt2M); d2.position.set(0.2, -2.3, -0.1); isle.add(d2);
  const d3 = RB(4.6, 1.0, 4.8, 0.5, dirt2M); d3.position.set(-0.3, -3.1, 0.2); isle.add(d3);
  const d4 = RB(2.2, 0.9, 2.4, 0.5, dirtM); d4.position.set(0.3, -3.8, 0); isle.add(d4);
  const water = mesh(new RoundedBoxGeometry(7.9, 0.8, 3.7, 2, 0.08), waterM, 0); water.position.set(0, -0.5, 2.2); water.castShadow = false; isle.add(water); isle.userData.water = water;
  // árvore
  const tr = new THREE.Group(); tr.position.set(-3.1, 0, -3.2); isle.add(tr);
  const tk = CY(0.22, 0.3, 1.9, toon(0x8a5a3c)); tk.position.y = 0.95; tr.add(tk);
  for (const [x, y, z, s, c] of [[0, 2.5, 0, 1.5, 0x4fb07a], [0.8, 2.1, 0.3, 1.0, 0x6cc68c], [-0.7, 2.0, -0.2, 1.05, 0x5fbd83], [0.1, 3.3, 0.1, 0.95, 0x6cc68c]]) { const l = RB(s, s * 0.85, s, s * 0.32, toon(c)); l.position.set(x, y, z); l.rotation.y = x; tr.add(l); }
  isle.userData.tree = tr;
  // pedras, juncos, flores, vitórias-régias
  for (const [x, z, s] of [[3.4, -3.6, 0.6], [2.6, -3.9, 0.38], [-4.0, -0.4, 0.45], [3.9, 0.1, 0.35]]) { const r = RB(s * 1.3, s, s * 1.1, s * 0.35, toon(0xb9bec6)); r.position.set(x, s * 0.4, z); r.rotation.y = x; isle.add(r); }
  const reedM = toon(0x5a9a4a), catM = toon(0x7a4a2a);
  for (let i = 0; i < 9; i++) { const x = -3.6 + hash(i) * 1.6 + (i > 5 ? 6.2 : 0), z = 0.5 + hash(i + 3) * 0.5; const h = 0.9 + hash(i + 7) * 0.7; const g = new THREE.Group(); g.position.set(x, -0.1, z); isle.add(g); const st = CY(0.035, 0.045, h, reedM, 1.3); st.position.y = h / 2; g.add(st); const ct = CY(0.07, 0.07, 0.26, catM, 1.15); ct.position.y = h; g.add(ct); (isle.userData.reeds = isle.userData.reeds || []).push({ g, ph: i }); }
  for (let i = 0; i < 14; i++) { const f = SP(0.07, toon([0xff8fb1, 0xffe066, 0xffffff][i % 3]), 1.25); f.position.set(-4 + hash(i * 3) * 8, 0.07, -4.2 + hash(i * 5 + 1) * 3.6); isle.add(f); }
  for (let i = 0; i < 16; i++) { const b = mesh(new THREE.ConeGeometry(0.06, 0.34, 4), grass2M, 0); b.position.set(-4.1 + hash(i * 7) * 8.2, 0.15, -4.2 + hash(i * 9 + 2) * 4); isle.add(b); }
  const pads = []; for (const [x, z, s] of [[-2.6, 3.2, 0.42], [-1.9, 3.5, 0.3], [2.8, 3.3, 0.4], [3.2, 1.2, 0.3]]) { const p = mesh(new THREE.CylinderGeometry(s, s, 0.04, 18), toon(0x4fae6a), 1.06); p.position.set(x, -0.08, z); isle.add(p); pads.push(p); } isle.userData.pads = pads;
}
const ripM = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.7 });
const rips = []; for (let i = 0; i < 4; i++) { const r = new THREE.Mesh(new THREE.TorusGeometry(1, 0.03, 4, 40), ripM.clone()); r.rotation.x = Math.PI / 2; scene.add(r); rips.push(r); }
function ripples(t, p, on = true) { rips.forEach((r, i) => { const u = (t * 0.5 + i / 4) % 1; r.visible = on; r.position.set(p.x, -0.085, p.z); r.scale.setScalar(0.5 + u * 1.5); r.material.opacity = 0.7 * (1 - u); }); }
const bubs = []; for (let i = 0; i < 8; i++) { const b = new THREE.Mesh(new THREE.SphereGeometry(0.07, 8, 6), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 })); scene.add(b); bubs.push(b); }
const steam = []; for (let i = 0; i < 9; i++) { const b = new THREE.Mesh(new THREE.SphereGeometry(0.3, 10, 8), new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.5 })); scene.add(b); steam.push(b); }
const yuzu = []; for (let i = 0; i < 7; i++) { const y = SP(0.17, toon(0xffc42e), 1.1); scene.add(y); yuzu.push(y); }
const lantern = new THREE.Group(); { const p = CY(0.06, 0.06, 1.5, toon(0x5a3a2a)); p.position.y = 0.75; lantern.add(p); const l = RB(0.42, 0.5, 0.42, 0.12, toon(0xe8483a)); l.position.y = 1.65; lantern.add(l); const tp = RB(0.56, 0.1, 0.56, 0.04, toon(0x2a1c14)); tp.position.y = 1.95; lantern.add(tp); lantern.position.set(3.3, 0, -1.0); scene.add(lantern); }

// ---------------------------------------------------------------- capivara
function makeCapi(col = 0xb9814c) {
  const root = new THREE.Group(); const b = new THREE.Group(); root.add(b);
  const furM = toon(col), snM = toon(0x8e5e36), dkM = toon(0x5a3a22);
  const body = RB(1.5, 0.86, 0.84, 0.36, furM); body.position.set(0, 0.68, 0); b.add(body);
  const hd = new THREE.Group(); hd.position.set(0.62, 0.92, 0); b.add(hd);
  const sk = RB(0.66, 0.62, 0.64, 0.24, furM); sk.position.set(0.12, 0.05, 0); hd.add(sk);
  const sn = RB(0.44, 0.44, 0.52, 0.16, snM); sn.position.set(0.5, -0.06, 0); hd.add(sn);
  const ns = RB(0.1, 0.12, 0.26, 0.04, dkM, 0); ns.position.set(0.72, 0.06, 0); hd.add(ns);
  const eyes = [], ears = [];
  for (const s of [-1, 1]) { const e = SP(0.062, new THREE.MeshBasicMaterial({ color: 0x1a1210 }), 0); e.position.set(0.22, 0.26, s * 0.3); hd.add(e); eyes.push(e);
    const er = RB(0.14, 0.14, 0.08, 0.04, dkM, 1.12); er.position.set(-0.1, 0.38, s * 0.22); hd.add(er); ears.push(er);
    const ck = SP(0.07, new THREE.MeshBasicMaterial({ color: 0xff8f9c, transparent: true, opacity: 0 }), 0); ck.position.set(0.36, 0.08, s * 0.33); ck.scale.set(1, 0.6, 0.3); hd.add(ck); (root.userData.ck = root.userData.ck || []).push(ck); }
  const teeth = new THREE.Group(); teeth.position.set(0.66, -0.26, 0); hd.add(teeth);
  for (const s of [-1, 1]) { const tt = RB(0.07, 1, 0.09, 0.02, toon(0xfff6e0), 1.12); tt.geometry.translate(0, -0.5, 0); tt.position.z = s * 0.055; teeth.add(tt); }
  const legs = []; for (const [x, z] of [[0.48, 0.26], [0.48, -0.26], [-0.48, 0.26], [-0.48, -0.26]]) { const p = new THREE.Group(); p.position.set(x, 0.34, z); b.add(p); const l = RB(0.24, 0.42, 0.24, 0.09, dkM); l.position.y = -0.15; p.add(l); legs.push(p); }
  const gl = RB(0.08, 0.2, 0.76, 0.04, new THREE.MeshBasicMaterial({ color: 0x0a0a0c }), 1.08); gl.position.set(0.47, 0.27, 0); hd.add(gl);
  const st = { t: 0, walk: 0, run: 0, teeth: 0.06, sleep: 0, chew: 0, blush: 0, glasses: -1, look: 0, ph: 0 };
  function tick() { const t = st.t + st.ph; const sp = st.run ? 16 : 8; const w = st.walk + st.run;
    legs.forEach((p, i) => p.rotation.z = (st.run ? 0.9 : 0.5) * w * Math.sin(t * sp + (i === 0 || i === 3 ? 0 : Math.PI)));
    b.position.y = 0.03 * w * Math.abs(Math.sin(t * sp)) + (st.run ? 0.08 * Math.abs(Math.sin(t * sp)) : 0) + 0.012 * Math.sin(t * 2.2); b.rotation.z = st.run ? 0.05 * Math.sin(t * sp) : 0;
    body.scale.y = 1 + 0.02 * Math.sin(t * 2.2);
    hd.rotation.z = 0.04 * Math.sin(t * 1.7) + st.look * 0.25 - (st.chew ? 0.05 * Math.abs(Math.sin(t * 11)) : 0); hd.rotation.y = 0.1 * Math.sin(t * 0.9);
    sn.scale.y = 1 + (st.chew ? 0.1 * Math.sin(t * 11) : 0);
    teeth.scale.y = st.teeth; teeth.visible = st.teeth > 0.03;
    const bl = st.sleep ? 0.12 : (Math.sin(t * 0.9 + st.ph) > 0.985 ? 0.12 : 1); eyes.forEach(e => e.scale.set(1, bl, 1));
    ears.forEach((e, i) => e.rotation.x = 0.25 * Math.sin(t * 3 + i) * (Math.sin(t * 0.7) > 0.6 ? 1 : 0));
    root.userData.ck.forEach(c => c.material.opacity = 0.85 * st.blush);
    gl.visible = st.glasses >= 0; gl.position.y = 0.27 + (1 - back(st.glasses)) * 1.6; gl.rotation.z = (1 - st.glasses) * 0.9; }
  return { root, hd, st, tick, back: () => root.localToWorld(V(-0.1, 1.13, 0)), headTop: () => hd.localToWorld(V(0.1, 0.4, 0)) };
}
const capi = makeCapi(); scene.add(capi.root);
const herd = []; for (let i = 0; i < 7; i++) { const c = makeCapi([0xb9814c, 0xa8713f, 0xc79058][i % 3]); c.st.ph = i * 1.3; c.root.scale.setScalar(i > 4 ? 0.5 : 0.8 + hash(i) * 0.2); scene.add(c.root); herd.push(c); }
function capiAt(c, t, x, y, z, ry, o = {}) { c.root.visible = true; c.root.position.set(x, y, z); c.root.rotation.y = ry; Object.assign(c.st, { walk: 0, run: 0, teeth: 0.06, sleep: 0, chew: 0, blush: 0, glasses: -1, look: 0 }, o); c.st.t = t; c.tick(); c.root.updateMatrixWorld(true); }

// passarinhos, carrapatos, cocô
const birds = []; for (let i = 0; i < 3; i++) { const g = new THREE.Group(); const bm = toon([0xffd23f, 0xff9f43, 0x6fd0ff][i]); const bd = RB(0.3, 0.26, 0.24, 0.11, bm, 1.1); bd.position.y = 0.16; g.add(bd); const hd = SP(0.12, bm, 1.12); hd.position.set(0.13, 0.33, 0); g.add(hd); const bk = mesh(new THREE.ConeGeometry(0.045, 0.14, 6).rotateZ(-Math.PI / 2), toon(0xff7a1a), 1.2); bk.position.set(0.28, 0.32, 0); g.add(bk);
  for (const s of [-1, 1]) { const e = SP(0.025, new THREE.MeshBasicMaterial({ color: 0x111111 }), 0); e.position.set(0.19, 0.37, s * 0.085); g.add(e); const w = RB(0.2, 0.05, 0.12, 0.02, bm, 1.15); w.position.set(-0.02, 0.2, s * 0.15); g.add(w); (g.userData.w = g.userData.w || []).push({ w, s }); }
  const tl = RB(0.14, 0.04, 0.1, 0.02, bm, 1.15); tl.position.set(-0.2, 0.2, 0); tl.rotation.z = -0.5; g.add(tl); scene.add(g); birds.push(g); }
function birdAt(i, t, p, ry, fly = 0, peck = 0) { const g = birds[i]; g.visible = true; g.position.copy(p); g.position.y += fly ? 0 : 0.03 * Math.abs(Math.sin(t * 6 + i)); g.rotation.set(0, ry, peck ? -0.7 * Math.max(0, Math.sin(t * 9 + i)) : 0); g.userData.w.forEach(({ w, s }) => w.rotation.x = s * (fly ? 0.9 * Math.sin(t * 30) : 0)); }
const ticks = []; for (let i = 0; i < 6; i++) { const k = SP(0.05, toon(0x7a1f2a), 1.3); scene.add(k); ticks.push(k); }
const poops = []; for (let i = 0; i < 5; i++) { const k = RB(0.16, 0.12, 0.13, 0.05, toon(0x6a4a2a), 1.15); scene.add(k); poops.push(k); }
// mini-Gepeta e onça
const mini = new THREE.Group(); const miniL = [];
{ const bk = toon(0x1c1c20), skn = toon(0xe2a45f); for (const s of [-1, 1]) { const p = new THREE.Group(); p.position.set(0, 0.62, s * 0.13); mini.add(p); const l = RB(0.2, 0.62, 0.2, 0.07, bk); l.position.y = -0.3; p.add(l); const sh = RB(0.3, 0.1, 0.22, 0.04, toon(0xf2f2ee)); sh.position.set(0.04, -0.6, 0); p.add(sh); miniL.push(p);
    const a = new THREE.Group(); a.position.set(0, 1.25, s * 0.34); mini.add(a); const ar = RB(0.17, 0.56, 0.17, 0.06, bk); ar.position.y = -0.25; a.add(ar); const hn = SP(0.09, skn, 1.1); hn.position.y = -0.56; a.add(hn); miniL.push(a); }
  const bd = RB(0.4, 0.72, 0.56, 0.12, bk); bd.position.y = 0.98; mini.add(bd); const hd = RB(0.5, 0.44, 0.5, 0.16, skn); hd.position.y = 1.62; mini.add(hd); const gl = RB(0.1, 0.13, 0.54, 0.04, new THREE.MeshBasicMaterial({ color: 0x0a0a0c }), 1.1); gl.position.set(0.24, 1.66, 0); mini.add(gl); scene.add(mini); }
function miniAt(t, x, z, ry, run = 0, wave = 0) { mini.visible = true; mini.position.set(x, run ? 0.06 * Math.abs(Math.sin(t * 12)) : 0, z); mini.rotation.y = ry; const a = run ? 0.9 * Math.sin(t * 12) : 0; miniL[0].rotation.z = a; miniL[2].rotation.z = -a; miniL[1].rotation.z = -a; miniL[3].rotation.z = wave ? 2.6 + 0.4 * Math.sin(t * 10) : a; mini.rotation.z = run ? -0.12 : 0; }
const onca = new THREE.Group();
{ const om = toon(0xf2a83a); const bd = RB(1.5, 0.6, 0.6, 0.25, om); bd.position.y = 0.72; onca.add(bd); const hd = RB(0.56, 0.5, 0.56, 0.2, om); hd.position.set(0.9, 0.98, 0); onca.add(hd); const mz = RB(0.22, 0.2, 0.34, 0.08, toon(0xfff0d0)); mz.position.set(1.18, 0.9, 0); onca.add(mz);
  for (const s of [-1, 1]) { const e = RB(0.14, 0.16, 0.08, 0.04, om, 1.12); e.position.set(0.78, 1.28, s * 0.2); onca.add(e); const ey = SP(0.045, new THREE.MeshBasicMaterial({ color: 0x1a1210 }), 0); ey.position.set(1.12, 1.06, s * 0.17); onca.add(ey); }
  for (const [x, z] of [[0.5, 0.2], [0.5, -0.2], [-0.5, 0.2], [-0.5, -0.2]]) { const p = new THREE.Group(); p.position.set(x, 0.5, z); onca.add(p); const l = RB(0.2, 0.56, 0.2, 0.08, om); l.position.y = -0.22; p.add(l); (onca.userData.l = onca.userData.l || []).push(p); }
  const tl = RB(0.8, 0.12, 0.12, 0.05, om); tl.position.set(-1.05, 0.95, 0); tl.rotation.z = -0.5; onca.add(tl);
  for (let i = 0; i < 16; i++) { const d = SP(0.06, new THREE.MeshBasicMaterial({ color: 0x3a2412 }), 0); const a = hash(i) * 6.28; d.position.set(-0.65 + hash(i + 4) * 1.3, 0.72 + Math.sin(a) * 0.3, Math.cos(a) * 0.3); d.scale.set(1, 1, 0.5); onca.add(d); } scene.add(onca); }
function oncaAt(t, x, z, ry, walk = 1) { onca.visible = true; onca.position.set(x, 0.01 * Math.sin(t * 8), z); onca.rotation.y = ry; onca.userData.l.forEach((p, i) => p.rotation.z = 0.5 * walk * Math.sin(t * 7 + (i === 0 || i === 3 ? 0 : Math.PI))); }
const mouse = new THREE.Group(); { const mm = toon(0xb9bec6); const b = RB(0.22, 0.14, 0.14, 0.06, mm, 1.15); b.position.y = 0.08; mouse.add(b); for (const s of [-1, 1]) { const e = SP(0.045, toon(0xffb3c0), 1.2); e.position.set(0.07, 0.17, s * 0.06); mouse.add(e); } const tl = RB(0.2, 0.02, 0.02, 0.008, toon(0xffb3c0), 1.4); tl.position.set(-0.2, 0.06, 0); mouse.add(tl); scene.add(mouse); }

// ---------------------------------------------------------------- timeline
const phrases = TL.phrases;
const shots = []; for (const p of phrases) { if (!shots.length || shots[shots.length - 1].name !== p.shot) shots.push({ name: p.shot, start: p.start, ps: [p] }); else shots[shots.length - 1].ps.push(p); }
shots[0].start = 0; for (let i = 0; i < shots.length; i++) shots[i].end = i + 1 < shots.length ? shots[i + 1].start : TOTAL;
const SH = Object.fromEntries(shots.map(s => [s.name, s]));
const WALL = phrases.flatMap(p => p.words.map(w => ({ s: w[0], e: w[1], w: w[2], shot: p.shot })));
const wt = (shot, re, fb = 0, nth = 0) => { const l = WALL.filter(w => w.shot === shot && re.test(w.w)); return l[nth] ? l[nth].s : SH[shot].start + fb; };
const p2 = (shot) => SH[shot].ps[1] ? SH[shot].ps[1].start : SH[shot].end;
const T = { facil: wt('sobe', /fácil/i, 3.4), carr: wt('negocio', /carrapatos/i, 2.4), graca: wt('negocio', /graça/i, 4), k60: wt('maior', /^60/, 2.5), olho: wt('topo', /olho/i, 0.3), orelha: wt('topo', /orelha/i, 0.8), nariz: wt('topo', /nariz/i, 1.2), agua: wt('topo', /escondida/i, 3),
  m5: wt('folego', /^5/, 1.6), dentes: wt('folego', /dentes/i, 3), brasil: wt('fimA', /brasil/i, 1.6), manda: wt('fimA', /manda/i, 2.2), coco: wt('nojo', /cocô/i, 4), duas: wt('digest', /duas/i, 3), nar2: wt('dorme', /nariz/i, 2), onca: wt('dorme', /onça/i, 3.5),
  v35: wt('corre', /^35/, 2), roedor: wt('corre', /roedor/i, 3), voce: wt('corre', /você/i, 4.4), late: wt('bando', /late/i, 2.8), ass: wt('bando', /assobia/i, 3.3), ronr: wt('bando', /ronrona/i, 4), tupi: wt('nome', /tupi/i, 1.6), capim: wt('nome', /comedora/i, 3),
  banho: wt('japao', /banho/i, 1.5), ama: wt('fimB', /ama/i, 2.6), zerou: wt('fimB', /zerou/i, 3.6), porra: wt('fimB', /porra/i, 4.6) };

// ---------------------------------------------------------------- céu 2D + câmera
const MOOD = { day: ['#aee3ff', '#fff4d8', 0xffffff, 2.6, 1.5], morning: ['#ffc8a2', '#fff0d0', 0xffd9b0, 2.7, 1.35], night: ['#101538', '#3b3f86', 0x9fb4ff, 1.5, 0.95], winter: ['#cfe1f2', '#fafdff', 0xffffff, 2.3, 1.7], sunset: ['#ffb37a', '#ffe6b8', 0xffc79a, 2.6, 1.4] };
let mood = 'day', ov = [], T_NOW = 0, flashA = 0;
function setMood(m) { mood = m; const M = MOOD[m]; sun.color.setHex(M[2]); sun.intensity = M[3]; amb.intensity = M[4]; const w = m === 'winter'; grassTop.forEach(g => g.material = w ? snowM : grassM); isle.userData.water.material.color.setHex(w ? 0x8fe0d8 : m === 'night' ? 0x3f6fc0 : 0x6fd3f2); }
function cam(az, el, vh, tg, tc) { const t = T_NOW; let h = vh; if (tc !== undefined && t >= tc && t - tc < 0.22) h *= 1 + 0.1 * (1 - (t - tc) / 0.22);
  const a = az + 0.02 * Math.sin(t * 0.9), e = el; camera.position.set(tg.x + Math.sin(a) * Math.cos(e) * 40, tg.y + Math.sin(e) * 40, tg.z + Math.cos(a) * Math.cos(e) * 40); camera.lookAt(tg);
  camera.top = h / 2; camera.bottom = -h / 2; camera.right = h / 2 * W / H; camera.left = -h / 2 * W / H; camera.updateProjectionMatrix(); camera.updateMatrixWorld(true); }
const _v = new THREE.Vector3(); const scr = (v) => { _v.copy(v).project(camera); return [(_v.x * 0.5 + 0.5) * W, (-_v.y * 0.5 + 0.5) * H]; };
//@@2D@@
function sky(t) { const M = MOOD[mood]; const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, M[0]); g.addColorStop(1, M[1]); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  if (mood === 'night') { for (let i = 0; i < 70; i++) { ctx.globalAlpha = 0.4 + 0.6 * Math.abs(Math.sin(t * 1.5 + i)); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(hash(i) * W, hash(i + 50) * H * 0.75, 2 + hash(i + 9) * 3, 0, 6.3); ctx.fill(); } ctx.globalAlpha = 1; ctx.fillStyle = '#fff6c8'; ctx.shadowColor = '#fff6c8'; ctx.shadowBlur = 60; ctx.beginPath(); ctx.arc(830, 330, 80, 0, 6.3); ctx.fill(); ctx.shadowBlur = 0; }
  else { ctx.fillStyle = mood === 'winter' ? 'rgba(255,255,255,0.9)' : 'rgba(255,255,255,0.75)'; for (let i = 0; i < 5; i++) { const x = ((hash(i) * 1500 + t * (12 + i * 5)) % 1500) - 200, y = 240 + hash(i + 3) * 1300, s = 0.7 + hash(i + 5) * 0.9; ctx.beginPath(); ctx.roundRect(x, y, 230 * s, 64 * s, 32 * s); ctx.fill(); ctx.beginPath(); ctx.roundRect(x + 50 * s, y - 34 * s, 120 * s, 70 * s, 35 * s); ctx.fill(); }
    if (mood === 'winter') { ctx.fillStyle = '#fff'; for (let i = 0; i < 60; i++) { const x = (hash(i) * W + 40 * Math.sin(t + i)) % W, y = (hash(i + 20) * H + t * (90 + hash(i) * 80)) % H; ctx.beginPath(); ctx.arc(x, y, 3 + hash(i + 4) * 4, 0, 6.3); ctx.fill(); } } }
  // sombra macia sob a ilha
  const sg = ctx.createRadialGradient(W / 2, 1500, 20, W / 2, 1500, 520); sg.addColorStop(0, 'rgba(0,0,0,0.16)'); sg.addColorStop(1, 'rgba(0,0,0,0)'); ctx.save(); ctx.scale(1, 0.35); ctx.fillStyle = sg; ctx.fillRect(0, 1500 / 0.35 - 600, W, 1200); ctx.restore(); }
function plus(p, label, t0, col = '#62f26e', size = 70) { const a = T_NOW - t0; if (a < 0 || a > 0.9) return; txt(label, p[0], p[1] - 60 - a * 110, size, { c: col, s: back(a / 0.2), a: 1 - sm(0.6, 0.9, a) }); }
function heart(x, y, s, a) { ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.globalAlpha = a; ctx.fillStyle = '#ff5c7a'; ctx.strokeStyle = '#2a1c14'; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(0, 14); ctx.bezierCurveTo(-40, -14, -20, -44, 0, -20); ctx.bezierCurveTo(20, -44, 40, -14, 0, 14); ctx.closePath(); ctx.stroke(); ctx.fill(); ctx.restore(); }

// ---------------------------------------------------------------- direção
const O = V(0, 0.4, 0);
function hideAll() { [capi.root, mini, onca, mouse, lantern].forEach(o => o.visible = false); herd.forEach(c => c.root.visible = false); birds.forEach(b => b.visible = false); ticks.forEach(k => k.visible = false); poops.forEach(k => k.visible = false); bubs.forEach(b => b.visible = false); steam.forEach(b => b.visible = false); yuzu.forEach(b => b.visible = false); rips.forEach(r => r.visible = false); isle.userData.tree.visible = true; isle.userData.pads.forEach(p => p.visible = true); }
function staging(t) {
  T_NOW = t; ov = []; flashA = 0; hideAll();
  const sh = shots.find(s => t >= s.start && t < s.end) || shots[shots.length - 1];
  const N = sh.name, S = sh.start, E = sh.end, u = t - S, k = sm(S, E, t), pB = p2(N);
  if (u < 0.1 && S > 0) flashA = 0.35 * (1 - u / 0.1);
  isle.rotation.y = 0; isle.userData.reeds.forEach(r => r.g.rotation.z = 0.08 * Math.sin(t * 1.6 + r.ph));
  const stack = (n, peck = -1) => { const bp = capi.back(); for (let i = 0; i < n; i++) birdAt(i, t, V(bp.x + (i === 2 ? 0.55 : 0) - (i === 1 ? 0.0 : 0), bp.y + (i === 1 ? 0.5 : 0) + (i === 2 ? 0.34 : 0), bp.z), i === 1 ? Math.PI : 0, 0, i === peck); };

  if (N === 'sobe') {
    setMood('day'); const bl = sm(T.facil - 0.1, T.facil + 0.3, t); capiAt(capi, t, 0, 0, -1.2, 0.35, { blush: bl, look: -bl * 0.4 });
    const bp = capi.back();
    for (let i = 0; i < 3; i++) { const tL = S + 0.55 + i * 0.55, a = clamp((t - tL + 0.6) / 0.6, 0, 1); if (t < tL - 0.6) continue; const tgt = V(bp.x + (i === 2 ? 0.55 : 0), bp.y + (i === 1 ? 0.5 : 0) + (i === 2 ? 0.34 : 0), bp.z); const st = V(-5 + i * 4, 6, -5); const p = st.clone().lerp(tgt, a * a * (3 - 2 * a)); p.y += Math.sin(a * Math.PI) * 1.2; birdAt(i, t, p, i === 1 ? Math.PI : 0, a < 1); if (a >= 1 && t - tL < 0.25) capi.root.position.y = -0.05 * Math.sin((t - tL) / 0.25 * Math.PI); }
    cam(lerp(0.9, 0.55, k), 0.56, lerp(19, 9.5, sm(S, S + 2.2, t)), V(0, lerp(-0.6, 0.9, sm(S, S + 2.2, t)), lerp(0.4, -0.6, sm(S, S + 2.2, t))), T.facil - 0.1);
    ov.push(() => { pill([{ txt: 'POR QUE TODO MUNDO', size: 60 }, { txt: 'SOBE NA CAPIVARA?', size: 86, c: '#ffe03a' }], W / 2, 290, 0.03); for (let i = 0; i < 3; i++) plus(scr(bp), 'POF!', S + 0.55 + i * 0.55, '#fff', 80); if (bl > 0.3) txt('. . .', W / 2 + 250, 760, 110, { s: back((t - T.facil) / 0.3) }); });
  }
  else if (N === 'negocio') {
    setMood('day'); capiAt(capi, t, 0, 0, -1.2, 0.35, { look: 0.2 }); stack(3, 0); const bp = capi.back();
    ticks.forEach((kk, i) => { const te = T.carr - 0.6 + i * 0.32; kk.visible = t < te; kk.position.set(bp.x - 0.45 + i * 0.16, bp.y - 0.02, bp.z + (i % 2 ? 0.2 : -0.2)); });
    cam(lerp(0.3, 0.6, k), 0.62, lerp(5.2, 4.4, k), V(0.1, 1.25, -1.2), S);
    ov.push(() => { ticks.forEach((kk, i) => plus(scr(kk.position), '+1', T.carr - 0.6 + i * 0.32, '#62f26e', 84)); stamp('LIMPEZA GRÁTIS', W / 2, 330, T.graca - 0.25, { size: 104, c: '#1f9d55' }); pill([{ txt: 'passarinho come carrapato', size: 46 }], W / 2, 300, S + 0.2, { t1: T.graca - 0.3 }); });
  }
  else if (N === 'maior') {
    setMood('day'); capiAt(capi, t, -0.3, 0, -1.4, 0.2, {}); miniAt(t, 1.5, -1.7, -0.5); mouse.visible = true; mouse.position.set(-1.9, 0, -0.6); mouse.rotation.y = 0.3; mouse.scale.setScalar(1 + 0.1 * Math.sin(t * 9));
    cam(lerp(0.45, 0.3, k), 0.5, lerp(8.4, 7.6, k), V(0.5, 1.0, -1.3), S);
    ov.push(() => { pill([{ txt: 'MAIOR ROEDOR DO MUNDO', size: 62, c: '#ffe03a' }], W / 2, 290, S + 0.15); tag(scr(V(-1.9, 0.2, -0.6)), 'rato comum', -40, 230, S + 0.5, { size: 44 });
      if (t > T.k60 - 0.2) { const n = 60 * sm(T.k60 - 0.2, T.k60 + 0.6, t), s = back((t - T.k60 + 0.2) / 0.3); txt('+' + Math.round(n) + ' kg', W / 2, 520, 200, { c: '#62f26e', s, rot: -0.04 }); } });
  }
  else if (N === 'topo') {
    setMood('day'); const dv = sm(T.agua - 0.5, T.agua + 0.2, t); const y = lerp(-0.72, -1.14, dv); capiAt(capi, t, 0, y, 2.2, 0.5, {}); ripples(t, capi.root.position);
    cam(lerp(0.55, 0.8, k), lerp(0.5, 0.42, k), lerp(5.0, 4.2, k), V(0.4, 0.15, 2.2), S);
    ov.push(() => { const h = capi.hd; tag(scr(h.localToWorld(V(0.22, 0.26, 0.3))), 'OLHO', 170, -260, T.olho - 0.1, { size: 60, c: '#ffe03a' }); tag(scr(h.localToWorld(V(-0.1, 0.42, 0.22))), 'ORELHA', -200, -330, T.orelha - 0.1, { size: 60, c: '#ffe03a' }); tag(scr(h.localToWorld(V(0.72, 0.1, 0))), 'NARIZ', 250, -60, T.nariz - 0.1, { size: 60, c: '#ffe03a' });
      pill([{ txt: 'TUDO NO TOPO', size: 78 }], W / 2, 290, S + 0.1); });
  }
  else if (N === 'folego') {
    setMood('day'); const td = T.dentes - 0.2;
    if (t < td) { capiAt(capi, t, 0, -1.55, 2.2, 0.5, {}); isle.userData.pads.forEach(p => p.visible = false); bubs.forEach((b, i) => { const q = (t * 0.7 + i / 8) % 1; b.visible = true; b.position.set(0.75 + 0.2 * Math.sin(i * 2 + t * 3), -0.75 + q * 0.7, 2.45 + 0.15 * Math.cos(i * 3)); b.scale.setScalar(0.5 + q); b.material.opacity = 0.9 * (1 - q); });
      cam(lerp(0.5, 0.35, k), 0.5, 5.6, V(0.2, -0.2, 2.2), S);
      ov.push(() => { const fr = sm(S + 0.3, T.m5 + 0.5, t), sec = Math.round(fr * 300); pill([{ txt: 'SEM RESPIRAR', size: 54 }, { txt: Math.floor(sec / 60) + ':' + String(sec % 60).padStart(2, '0'), size: 170, c: '#62f26e' }], W / 2, 360, S + 0.1); }); }
    else { const g = sm(td, E - 0.3, t); capiAt(capi, t, 0, 0, -1.2, 0.75, { teeth: 0.1 + 0.75 * g, look: 0.35 });
      cam(1.65, 0.22, lerp(3.6, 3.0, g), V(0.8, 0.8, -1.9), td);
      ov.push(() => { stamp('NUNCA PARAM', W / 2, 330, td + 0.3, { size: 110 }); }); }
  }
  else if (N === 'fimA' || N === 'fimB') {
    setMood(N === 'fimA' ? 'day' : 'sunset'); const tg = N === 'fimA' ? T.brasil - 0.3 : T.zerou - 0.2; const gl = t > tg ? clamp((t - tg) / 0.35, 0, 1) : -1;
    const seg = N === 'fimB' && t > pB;
    capiAt(capi, t, 0, 0, -1.2, 0.35, { glasses: gl, chew: N === 'fimB' ? 1 : 0 }); stack(3); if (seg) miniAt(t, 2.1, -0.6, 0.3, 0, 1);
    if (gl > 0.6 && gl < 1) flashA = 0.4 * (1 - (gl - 0.6) / 0.4);
    cam(lerp(0.4, 0.7, k), 0.55, N === 'fimB' ? lerp(9, 17, sm(pB - 0.3, E, t)) : lerp(9.2, 8.2, k), V(0.2, N === 'fimB' ? lerp(0.95, -0.4, sm(pB - 0.3, E, t)) : 0.95, -0.6), gl >= 0 ? tg : S);
    ov.push(() => { const bp = scr(capi.headTop()); for (let i = 0; i < 6; i++) { const q = ((t * 0.5 + i / 6) % 1); heart(bp[0] - 220 + i * 90 + 30 * Math.sin(t * 2 + i), bp[1] - 120 - q * 330, 1.1 + 0.5 * hash(i), (gl >= 0 ? 1 : 0) * (1 - q)); }
      if (N === 'fimA') { pill([{ txt: 'O BICHO MAIS', size: 58 }, { txt: 'DE BOA DO BRASIL', size: 84, c: '#ffe03a' }], W / 2, 290, S + 0.1, { t1: T.manda - 0.1 }); pill([{ txt: 'MANDA PRA AQUELE AMIGO', size: 62, c: '#62f26e' }], W / 2, 290, T.manda - 0.05); }
      else if (!seg) { pill([{ txt: 'come de graça', size: 52 }, { txt: 'dorme na água', size: 52 }, { txt: 'todo mundo ama', size: 52 }], W / 2, 330, S + 0.2, { t1: T.zerou - 0.15 }); if (t > T.zerou - 0.1) { const s = back((t - T.zerou + 0.1) / 0.3); txt('ZEROU', W / 2, 290, 190, { c: '#ffe03a', s, rot: -0.05 }); txt('A VIDA', W / 2, 440, 120, { s, rot: -0.05 }); } }
      else pill([{ txt: 'SEGUE', size: 130, c: '#62f26e' }, { txt: 'pro próximo bicho', size: 54 }], W / 2, 320, pB + 0.05); });
  }
  else if (N === 'nojo') {
    setMood('morning'); const ea = sm(T.coco + 0.2, E - 0.2, t); capiAt(capi, t, -0.4, 0, -1.3, 0.3, { look: 0.45, chew: ea > 0.3 ? 1 : 0 });
    poops.forEach((p, i) => { const gone = ea * 5 > i + 0.6; p.visible = !gone; p.position.set(0.95 + i * 0.22, 0.07, -0.9 + (i % 2) * 0.22 - i * 0.03); p.rotation.y = i; });
    cam(lerp(0.5, 0.7, k), 0.5, lerp(7.2, 5.2, sm(S, T.coco, t)), V(0.5, 0.7, -1.1), T.coco - 0.1);
    ov.push(() => { stamp('PARTE NOJENTA', W / 2, 320, S + 0.2, { size: 104, t1: T.coco - 0.2, c: '#8a5a1f' }); if (t > T.coco - 0.15) { pill([{ txt: 'CAFÉ DA MANHÃ:', size: 54 }, { txt: 'O PRÓPRIO COCÔ', size: 82, c: '#c98a3a' }], W / 2, 310, T.coco - 0.15); } poops.forEach((p, i) => plus(scr(p.position), 'nhac', T.coco + 0.2 + (E - 0.4 - T.coco) * (i + 0.6) / 5, '#fff', 60)); });
  }
  else if (N === 'digest') {
    setMood('morning'); capiAt(capi, t, 0, 0, -1.2, 0.0, { chew: 1 }); cam(0.0, 0.5, lerp(6.6, 6.0, k), V(0, 0.9, -1.2), S);
    ov.push(() => { const c = scr(V(0, 0.75, -1.2)); const n = t > T.duas - 0.1 ? 2 : 1; for (let j = 0; j < n; j++) { const a0 = t * 2.4 + j * Math.PI; ctx.save(); ctx.strokeStyle = j ? '#ffe03a' : '#62f26e'; ctx.lineWidth = 20; ctx.lineCap = 'round'; ctx.setLineDash([46, 34]); ctx.lineDashOffset = -t * 260; ctx.beginPath(); ctx.ellipse(c[0], c[1], 400 + j * 50, 215 + j * 40, 0, 0, 6.283); ctx.stroke(); ctx.restore(); }
      pill([{ txt: 'CAPIM = DIFÍCIL DE DIGERIR', size: 52 }], W / 2, 290, S + 0.15, { t1: T.duas - 0.2 }); if (t > T.duas - 0.15) { txt('2 VOLTAS', W / 2, 330, 170, { c: '#ffe03a', s: back((t - T.duas + 0.15) / 0.3), rot: -0.04 }); } });
  }
  else if (N === 'dorme') {
    setMood('night'); capiAt(capi, t, -0.6, -1.2, 2.3, 0.5, { sleep: 1 }); ripples(t, capi.root.position);
    const ox = lerp(4.0, -2.6, sm(T.onca - 1.4, E + 0.6, t)); if (t > T.onca - 1.4) oncaAt(t, ox, -1.3, Math.PI, 1);
    cam(lerp(0.6, 0.4, k), 0.55, lerp(7.0, 8.2, sm(T.onca - 1.4, T.onca, t)), V(0, 0.5, 0.6), t > T.onca - 1.4 ? T.onca - 1.4 : S);
    ov.push(() => { const hp = scr(capi.headTop()); for (let i = 0; i < 3; i++) { const q = (t * 0.45 + i / 3) % 1; txt('z', hp[0] + 60 + q * 150, hp[1] - 50 - q * 230, 60 + q * 70, { a: 1 - q, c: '#cfd8ff' }); }
      tag(scr(capi.hd.localToWorld(V(0.72, 0.1, 0))), 'só o nariz de fora', 150, 250, T.nar2 - 0.1, { size: 46 }); if (t > T.onca - 0.2) { const op = scr(V(ox + (-0.9), 1.6, -1.3)); txt('?', op[0], op[1] - 30, 190, { c: '#ffe03a', s: back((t - T.onca + 0.2) / 0.25), rot: 0.15 * Math.sin(t * 6) }); } });
  }
  else if (N === 'corre') {
    setMood('day'); isle.userData.tree.visible = true; const a1 = -(t - S) * 2.6 + 2.2, a2 = -(t - S) * 1.5 + 2.9; const R = 3.55;
    const pc = V(Math.cos(a1) * R, 0, Math.sin(a1) * R * 0.0 - 2.6 + Math.sin(a1) * 1.3);
    capiAt(capi, t, Math.cos(a1) * 3.3, 0, -2.1 + Math.sin(a1) * 1.5, -a1 + Math.PI / 2 + Math.PI, { run: 1 }); miniAt(t, Math.cos(a2) * 3.3, -2.1 + Math.sin(a2) * 1.5, -a2 + Math.PI / 2 + Math.PI, 1);
    cam(lerp(0.2, 0.6, k), 0.72, 14.5, V(0, 0.2, -1.2), S);
    ov.push(() => { if (t > T.v35 - 0.2) { const n = 35 * sm(T.v35 - 0.2, T.v35 + 0.5, t), s = back((t - T.v35 + 0.2) / 0.3); txt(Math.round(n) + ' km/h', W / 2, 310, 190, { c: '#62f26e', s, rot: -0.04 }); } if (t > T.roedor - 0.05 && t < T.voce - 0.1) stamp('UM ROEDOR', W / 2, 520, T.roedor - 0.05, { size: 100 }); if (t > T.voce - 0.1) tag(scr(V(mini.position.x, 2.0, mini.position.z)), 'VOCÊ', 0, -170, T.voce - 0.1, { size: 70, c: '#ff5548' }); const cp = scr(capi.root.position); for (let i = 0; i < 3; i++) { ctx.save(); ctx.globalAlpha = 0.5 - i * 0.14; ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(cp[0] - 30 + 70 * Math.sin(t * 9 + i * 2), cp[1] + 10 + i * 6, 26 + i * 9, 0, 6.3); ctx.fill(); ctx.restore(); } });
  }
  else if (N === 'bando') {
    setMood('day'); capiAt(capi, t, 0, 0, -1.4, 0.3, {}); herd.forEach((c, i) => capiAt(c, t, [-2.4, 2.1, -1.2, 1.2, -3.2, 2.9, 0.4][i], 0, [-2.6, -2.9, -0.4, -0.5, -1.0, -1.2, -3.4][i], [0.6, -0.4, 0.2, 2.8, 0.9, 2.4, 0.1][i], { chew: i % 2 }));
    cam(lerp(0.3, 0.6, k), 0.66, lerp(13.5, 12, k), V(0, 0.4, -1.3), S);
    ov.push(() => { pill([{ txt: 'BANDO DE 10 A 20', size: 70, c: '#ffe03a' }], W / 2, 290, S + 0.15); const sp = [[herd[0], 'AU!', T.late], [herd[1], 'fiuuu~', T.ass], [herd[3], 'rrrr', T.ronr]]; sp.forEach(([c, s, t0]) => { if (t > t0 - 0.05) { const p = scr(c.headTop()); pill([{ txt: s, size: 64, c: '#111' }], p[0], p[1] - 110, t0 - 0.05, { bg: '#fff', rot: 0.03 }); } }); });
  }
  else if (N === 'nome') {
    setMood('day'); capiAt(capi, t, 0, 0, -1.2, 0.55, { chew: 1, look: 0.3 }); cam(lerp(0.7, 0.9, k), 0.42, lerp(4.6, 4.0, k), V(0.5, 0.85, -1.1), S);
    ov.push(() => { pill([{ txt: 'CAPIVARA', size: 100, c: '#ffe03a' }, { txt: 'palavra do tupi', size: 46, it: true, c: '#cfcfcf' }], W / 2, 300, S + 0.1, { t1: T.capim - 0.15 }); pill([{ txt: '=', size: 70 }, { txt: 'COMEDORA DE CAPIM', size: 78, c: '#62f26e' }], W / 2, 320, T.capim - 0.1); });
  }
  else { // japao
    setMood('winter'); lantern.visible = true; isle.userData.pads.forEach(p => p.visible = false);
    capiAt(capi, t, -0.2, -0.95, 2.2, 0.45, { sleep: 1, blush: 1 }); capiAt(herd[0], t, 1.6, -0.85, 2.6, -2.2, { sleep: 1, blush: 1 });
    yuzu.forEach((y, i) => { y.visible = true; if (i === 0) { y.position.copy(capi.headTop()).add(V(-0.05, 0.12, 0)); } else { const a = i * 1.1 + t * 0.15; y.position.set(-0.2 + Math.cos(a) * (1.6 + i * 0.25), -0.06 + 0.02 * Math.sin(t * 2 + i), 2.2 + Math.sin(a) * 1.1); } });
    steam.forEach((s, i) => { const q = (t * 0.22 + i / 9) % 1; s.visible = true; s.position.set(-3 + i * 0.8 + 0.3 * Math.sin(t + i), 0.2 + q * 2.6, 1.6 + (i % 3) * 0.7); s.scale.setScalar(0.6 + q * 1.4); s.material.opacity = 0.5 * Math.sin(q * Math.PI); });
    cam(lerp(0.65, 0.45, k), 0.52, lerp(8.4, 6.6, k), V(0.3, 0.5, 1.4), S);
    ov.push(() => { pill([{ txt: 'JAPÃO', size: 110, c: '#e8483a' }, { txt: 'banho quente com yuzu', size: 50, c: '#3a2a22' }], W / 2, 300, S + 0.1, { bg: '#fff8ee', border: '#e8483a' }); });
  }
}

window.renderAt = (t) => {
  staging(t); sky(t);
  renderer.render(scene, camera);
  ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high'; ctx.drawImage(renderer.domElement, 0, 0, W, H);
  if (flashA > 0) { ctx.fillStyle = `rgba(255,255,255,${flashA})`; ctx.fillRect(0, 0, W, H); }
  for (const f of ov) f();
  caption(t);
  return out.toDataURL('image/jpeg', 0.92);
};
window.TOTAL = TOTAL; window.SHOTS = shots.map(s => [s.name, +s.start.toFixed(2), +s.end.toFixed(2)]); document.title = 'ready';
