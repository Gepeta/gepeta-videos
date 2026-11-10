// Núcleo da fábrica Gepeta: renderer, ambientes, câmera, partículas e legendas.
import * as THREE from 'three';
export { THREE };
export const W = 1080, H = 1920;

// ---------------------------------------------------------------- utilidades
let _seed = 7;
export const reseed = (s) => { _seed = s; };
export const rnd = () => (_seed = (_seed * 16807) % 2147483647) / 2147483647;
export const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
export const sm = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
export const lerp = (a, b, t) => a + (b - a) * t;
export const V = (x, y, z) => new THREE.Vector3(x, y, z);
export const mat = (c, o = {}) => new THREE.MeshStandardMaterial({ color: c, flatShading: true, roughness: 0.85, metalness: 0, ...o });

// geometria low-poly com cor por face (top/belly/manchas)
export function faceColored(geo, colorFn) {
  const g = geo.index ? geo.toNonIndexed() : geo; const p = g.attributes.position; const cols = [];
  for (let i = 0; i < p.count; i += 3) {
    const cx = (p.getX(i) + p.getX(i + 1) + p.getX(i + 2)) / 3, cy = (p.getY(i) + p.getY(i + 1) + p.getY(i + 2)) / 3, cz = (p.getZ(i) + p.getZ(i + 1) + p.getZ(i + 2)) / 3;
    const c = new THREE.Color(colorFn(cx, cy, cz)); for (let k = 0; k < 3; k++) cols.push(c.r, c.g, c.b);
  }
  g.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3)); g.computeVertexNormals(); return g;
}

// ---------------------------------------------------------------- temas
export const THEMES = {
  mar:      { bg: 0x1f8fb8, fog: 0.045, ground: [0.93, 0.8, 0.55], hemiSky: 0xbff4ff, hemiGround: 0xc8a46a, underwater: true },
  deserto:  { bg: 0x9fd3f0, fog: 0.018, ground: [0.86, 0.55, 0.33], hemiSky: 0xfff4e0, hemiGround: 0xd08a5a, underwater: false },
  floresta: { bg: 0xa8d8ea, fog: 0.03,  ground: [0.42, 0.66, 0.3],  hemiSky: 0xeaffea, hemiGround: 0x5a7a3a, underwater: false },
  noite:    { bg: 0x10183a, fog: 0.035, ground: [0.35, 0.38, 0.45], hemiSky: 0x6070c0, hemiGround: 0x202030, underwater: false },
};

export function createWorld(themeName = 'mar', opts = {}) {
  const T = THEMES[themeName]; reseed(opts.seed ?? 7);
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setSize(W, H, false); renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const scene = new THREE.Scene();
  const BASE = new THREE.Color(T.bg);
  scene.background = BASE.clone(); scene.fog = new THREE.FogExp2(BASE.clone(), T.fog);
  const camera = new THREE.PerspectiveCamera(40, W / H, 0.05, 300);
  const hemi = new THREE.HemisphereLight(T.hemiSky, T.hemiGround, 1.3); scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xfff3d6, 2.2); sun.position.set(6, 14, 4); sun.castShadow = true;
  sun.shadow.mapSize.set(1024, 1024); Object.assign(sun.shadow.camera, { left: -12, right: 12, top: 12, bottom: -12, near: 1, far: 40 });
  scene.add(sun); scene.add(sun.target);

  // chão
  const g = new THREE.PlaneGeometry(90, 90, 64, 64); g.rotateX(-Math.PI / 2);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i); p.setY(i, 0.18 * Math.sin(x * 0.7) * Math.cos(z * 0.6) + 0.12 * Math.sin(x * 1.9 + z * 1.3) + (rnd() - 0.5) * 0.08 + (themeName === 'deserto' ? 1.2 * Math.max(0, Math.sin(x * 0.12 + 1) * Math.cos(z * 0.1)) * sm(10, 25, Math.hypot(x, z)) : 0)); }
  const ground = new THREE.Mesh(faceColored(g, () => { const k = 0.9 + rnd() * 0.12; return new THREE.Color(T.ground[0] * k, T.ground[1] * k, T.ground[2] * k); }), mat(0xffffff, { vertexColors: true }));
  ground.receiveShadow = true; scene.add(ground);

  const decor = new THREE.Group(); scene.add(decor); const swayers = [];
  const keepClear = opts.keepClear ?? ((x, z) => Math.hypot(x, z) < 4);
  const ring = (n, r0, r1, fn) => { for (let i = 0; i < n; i++) { const a = rnd() * 6.28, r = r0 + rnd() * (r1 - r0); const x = Math.cos(a) * r, z = Math.sin(a) * r; if (keepClear(x, z)) continue; fn(x, z); } };
  const rock = (x, z, s, c = 0x8a8178) => { const m = new THREE.Mesh(new THREE.DodecahedronGeometry(s, 0), mat(c)); m.position.set(x, s * 0.35, z); m.rotation.set(rnd() * 3, rnd() * 3, rnd() * 3); m.scale.y = 0.6 + rnd() * 0.4; m.castShadow = m.receiveShadow = true; decor.add(m); };
  const segStalk = (x, z, h, c, w = 0.16) => { const grp = new THREE.Group(); grp.position.set(x, 0, z); decor.add(grp); const segs = []; let parent = grp;
    for (let i = 0; i < 6; i++) { const s = new THREE.Group(); s.position.y = i === 0 ? 0 : h / 6; const b = new THREE.Mesh(new THREE.BoxGeometry(w, h / 6, 0.06), mat(c)); b.position.y = h / 12; b.castShadow = true; s.add(b); parent.add(s); parent = s; segs.push(s); }
    swayers.push({ segs, ph: rnd() * 6, amp: themeName === 'mar' ? 0.12 : 0.03 }); };
  const tree = (x, z, s = 1) => { const grp = new THREE.Group(); grp.position.set(x, 0, z); decor.add(grp);
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.12 * s, 0.2 * s, 3 * s, 5), mat(0x6b4a2b)); trunk.position.y = 1.5 * s; trunk.rotation.z = (rnd() - 0.5) * 0.3; trunk.castShadow = true; grp.add(trunk);
    for (let k = 0; k < 3; k++) { const c = new THREE.Mesh(new THREE.IcosahedronGeometry((0.9 + rnd() * 0.5) * s, 0), mat([0x5aa83a, 0x6cbf45, 0x4c9433][k])); c.position.set((rnd() - 0.5) * 1.2 * s, (3 + rnd() * 0.8) * s, (rnd() - 0.5) * 1.2 * s); c.castShadow = true; grp.add(c); } };
  const cactus = (x, z, s = 1) => { const grp = new THREE.Group(); grp.position.set(x, 0, z); decor.add(grp); const cm = mat(0x2f9e44);
    const b = new THREE.Mesh(new THREE.BoxGeometry(0.35 * s, 3 * s, 0.35 * s), cm); b.position.y = 1.5 * s; b.castShadow = true; grp.add(b);
    for (const side of [-1, 1]) { const arm = new THREE.Mesh(new THREE.BoxGeometry(0.6 * s, 0.25 * s, 0.25 * s), cm); arm.position.set(side * 0.4 * s, (1.4 + rnd()) * s, 0); grp.add(arm); const up = new THREE.Mesh(new THREE.BoxGeometry(0.25 * s, 0.9 * s, 0.25 * s), cm); up.position.set(side * 0.65 * s, arm.position.y + 0.4 * s, 0); up.castShadow = true; grp.add(up); } };
  const coral = (x, z, c) => { const grp = new THREE.Group(); grp.position.set(x, 0, z); decor.add(grp);
    for (let i = 0; i < 5; i++) { const m = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.8 + rnd() * 0.7, 5), mat(c)); m.position.set((rnd() - 0.5) * 0.6, 0.4, (rnd() - 0.5) * 0.6); m.rotation.set((rnd() - 0.5) * 0.8, 0, (rnd() - 0.5) * 0.8); m.castShadow = true; grp.add(m); }
    const ball = new THREE.Mesh(new THREE.IcosahedronGeometry(0.45, 0), mat(c)); ball.position.y = 0.2; grp.add(ball); };
  if (themeName === 'mar') {
    ring(40, 5, 27, (x, z) => rock(x, z, 0.3 + rnd() * 1.2));
    ring(45, 4, 24, (x, z) => segStalk(x, z, 1.6 + rnd() * 2.6, [0x2f9e44, 0x51b84a, 0x2b7a3a][Math.floor(rnd() * 3)]));
    ring(22, 5, 23, (x, z) => coral(x, z, [0xff7a8a, 0xffa94d, 0xb197fc, 0xff6b6b][Math.floor(rnd() * 4)]));
  } else if (themeName === 'deserto') {
    ring(30, 5, 30, (x, z) => rock(x, z, 0.3 + rnd() * 1.4, 0xc98a5a));
    ring(18, 7, 30, (x, z) => cactus(x, z, 0.8 + rnd() * 0.8));
    ring(10, 9, 30, (x, z) => tree(x, z, 0.9 + rnd() * 0.5));
  } else {
    ring(30, 5, 30, (x, z) => rock(x, z, 0.3 + rnd() * 1.0));
    ring(40, 7, 32, (x, z) => tree(x, z, 1 + rnd() * 0.8));
    ring(60, 3, 20, (x, z) => segStalk(x, z, 0.5 + rnd() * 0.5, 0x4c9a2a, 0.08));
  }

  // raios de luz (só no mar)
  const rays = [];
  if (T.underwater) {
    const c = document.createElement('canvas'); c.width = 64; c.height = 256; const x = c.getContext('2d');
    const gr = x.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, 'rgba(255,255,255,0.9)'); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.fillRect(0, 0, 64, 256);
    x.globalCompositeOperation = 'destination-in'; const g2 = x.createLinearGradient(0, 0, 64, 0); g2.addColorStop(0, 'rgba(0,0,0,0)'); g2.addColorStop(0.5, 'rgba(0,0,0,1)'); g2.addColorStop(1, 'rgba(0,0,0,0)'); x.fillStyle = g2; x.fillRect(0, 0, 64, 256);
    const tex = new THREE.CanvasTexture(c);
    for (let i = 0; i < 14; i++) { const m = new THREE.Mesh(new THREE.PlaneGeometry(1.5 + rnd() * 2, 22), new THREE.MeshBasicMaterial({ map: tex, transparent: true, opacity: 0.12, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false }));
      m.position.set((rnd() - 0.5) * 30, 10, (rnd() - 0.5) * 30); m.rotation.set(0, rnd() * 3, 0.35); rays.push({ m, ph: rnd() * 6 }); scene.add(m); }
  }
  // partículas (neve marinha ou poeira)
  const pg = new THREE.BufferGeometry(); const pp = []; for (let i = 0; i < 600; i++) pp.push((rnd() - 0.5) * 30, rnd() * 10, (rnd() - 0.5) * 30);
  pg.setAttribute('position', new THREE.Float32BufferAttribute(pp, 3));
  const motes = new THREE.Points(pg, new THREE.PointsMaterial({ color: T.underwater ? 0xffffff : 0xfff2d0, size: T.underwater ? 0.05 : 0.035, transparent: true, opacity: T.underwater ? 0.7 : 0.4 })); scene.add(motes);
  // bolhas (mar) — burst(t0, pos, small) dispara uma explosão de bolhas
  const bubbles = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 1), new THREE.MeshStandardMaterial({ color: 0xe8fbff, transparent: true, opacity: 0.55, roughness: 0.1, metalness: 0.2 }), 160);
  bubbles.visible = T.underwater; scene.add(bubbles);
  const bd = []; for (let i = 0; i < 160; i++) bd.push({ a: rnd() * 6.28, r: rnd(), s: 0.03 + rnd() * 0.07, ph: rnd(), sp: 0.6 + rnd() * 0.8 });
  let burst = { t0: -99, pos: V(0, 0, 0), small: false };

  const world = {
    THREE, scene, camera, renderer, sun, hemi, ground, decor, theme: T, BASE,
    setFog(color, density) { scene.background.copy(color); scene.fog.color.copy(color); scene.fog.density = density; },
    resetFrame() { world.setFog(BASE, T.fog); sun.position.set(6, 14, 4); sun.target.position.set(0, 0, 0); sun.color.setHex(0xfff3d6); },
    // câmera: aproxima demais? afasta automaticamente pra caber no 9:16
    look(pos, tgt, fov = 40) { const d = pos.distanceTo(tgt); if (d < 6.5) pos = tgt.clone().add(pos.clone().sub(tgt).multiplyScalar(lerp(1.9, 1.15, clamp((d - 2) / 4.5, 0, 1)))); camera.position.copy(pos); camera.lookAt(tgt); camera.fov = fov; camera.updateProjectionMatrix(); },
    burst(t0, pos, small = false) { burst = { t0, pos: pos.clone(), small }; },
    tick(t, u, shake = 0) {
      if (shake) { camera.position.x += Math.sin(t * 90) * shake; camera.position.y += Math.cos(t * 77) * shake; }
      const pu = sm(0, 0.25, u); camera.fov = camera.fov * lerp(1.12, 1, pu); camera.updateProjectionMatrix(); // punch no corte
      swayers.forEach(w => w.segs.forEach((s, i) => { s.rotation.z = w.amp * Math.sin(t * 1.3 + w.ph + i * 0.5); s.rotation.x = w.amp * 0.5 * Math.sin(t * 0.9 + w.ph); }));
      rays.forEach(r => r.m.material.opacity = 0.07 + 0.06 * Math.sin(t * 0.8 + r.ph));
      motes.position.set(camera.position.x + Math.sin(t * 0.2) * 0.3, -((t * 0.15) % 1), camera.position.z);
      if (T.underwater) {
        const M = new THREE.Matrix4(), Q = new THREE.Quaternion();
        bd.forEach((b, i) => { let p, s; const bt = t - burst.t0;
          if (i < 70 && bt >= 0 && bt < 2.5) { const sp = burst.small ? 0.4 : 1.6; p = burst.pos.clone().add(V(Math.cos(b.a) * b.r * sp * (0.3 + bt), bt * b.sp * 2.2, Math.sin(b.a) * b.r * sp * (0.3 + bt))); s = b.s * (burst.small ? 0.8 : 1.6) * (1 - bt / 2.5); }
          else { const c = camera.position, cyc = (t * 0.25 * b.sp + b.ph) % 1; p = V(c.x + Math.cos(b.a) * (3 + b.r * 8), cyc * 9, c.z + Math.sin(b.a) * (3 + b.r * 8)); s = b.s * 0.8; }
          M.compose(p, Q, V(s, s, s)); bubbles.setMatrixAt(i, M); });
        bubbles.instanceMatrix.needsUpdate = true;
      }
    },
  };
  return world;
}

// ---------------------------------------------------------------- linha do tempo
export function buildShots(TL) {
  const shots = []; for (const p of TL.phrases) { if (!shots.length || shots[shots.length - 1].name !== p.shot) shots.push({ name: p.shot, start: p.start, ps: [p] }); else shots[shots.length - 1].ps.push(p); }
  shots[0].start = 0; for (let i = 0; i < shots.length; i++) shots[i].end = i + 1 < shots.length ? shots[i + 1].start : TL.total;
  return shots;
}

// ---------------------------------------------------------------- legenda de uma palavra
export function makeCaptioner(ctx, TL, keywordsRegex) {
  const words = TL.phrases.flatMap(p => p.words.map(w => ({ s: w[0], e: w[1], w: w[2] })));
  return (t) => {
    let cur = null; for (const w of words) { if (w.s <= t) cur = w; else break; }
    if (!cur || t > TL.total - 1.0) return;
    const raw = cur.w.replace(/[.,?!…:;]+$/, ''); const txt = raw.charAt(0).toUpperCase() + raw.slice(1);
    const key = keywordsRegex.test(raw.replace(/[.,?!]/g, ''));
    const pop = 1 + 0.28 * (1 - sm(0, 0.12, t - cur.s));
    ctx.save(); ctx.translate(W / 2, 1330); ctx.scale(pop, pop); ctx.rotate(key ? -0.04 : 0);
    let fs = key ? 118 : 96; ctx.font = `${fs}px Pop`;
    const tw = ctx.measureText(txt).width; if (tw > W - 120) { fs *= (W - 120) / tw; ctx.font = `${fs}px Pop`; }
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
    ctx.shadowColor = 'rgba(0,0,0,0.45)'; ctx.shadowBlur = 18; ctx.shadowOffsetY = 6;
    ctx.lineWidth = 18; ctx.strokeStyle = '#111'; ctx.strokeText(txt, 0, 0);
    ctx.shadowColor = 'transparent'; ctx.fillStyle = key ? '#ffd43b' : '#ffffff'; ctx.fillText(txt, 0, 0); ctx.restore();
  };
}
