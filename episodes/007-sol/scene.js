// ================================================================ ADEREÇOS DO CORREDOR
const HDR = (r, g, b) => new THREE.MeshBasicMaterial({ color: new THREE.Color(r, g, b) });
const props = {};
{
  const G = corridorG;
  const emerM = new THREE.MeshStandardMaterial({ color: 0x300808, emissive: 0xff2010, emissiveIntensity: 0 });
  const em = RB(0.34, 0.14, 0.1, 0.03, emerM); em.position.set(-2.52, 2.5, 1.2); em.castShadow = false; G.add(em);
  const emerL = new THREE.PointLight(0xff2a14, 0, 9, 1.4); emerL.position.set(-2.2, 2.45, 1.2); G.add(emerL);
  const phoneL = new THREE.PointLight(0xcfe0ff, 0, 5, 1.6); phoneL.position.set(0.1, 1.45, 0.75); G.add(phoneL);
  Object.assign(props, { emerM, emerL, phoneL });
  // telégrafo
  const tg = new THREE.Group(); tg.position.set(-0.25, 0, 0.62); G.add(tg); props.tele = tg;
  const wood = std({ color: 0x6a4526, roughness: 0.6 });
  const top = RB(1.0, 0.06, 0.5, 0.02, wood); top.position.y = 1.0; tg.add(top);
  for (const [x, z] of [[-0.44, -0.2], [0.44, -0.2], [-0.44, 0.2], [0.44, 0.2]]) { const l = RB(0.06, 1.0, 0.06, 0.01, wood); l.position.set(x, 0.5, z); tg.add(l); }
  const brass = new THREE.MeshStandardMaterial({ color: 0xc9a45c, metalness: 1, roughness: 0.3 });
  const base = RB(0.26, 0.04, 0.14, 0.01, std({ color: 0x1a1a1a })); base.position.set(-0.05, 1.05, 0); tg.add(base);
  const lev = RB(0.24, 0.025, 0.03, 0.008, brass); lev.position.set(-0.05, 1.1, 0); tg.add(lev); props.lever = lev;
  const kn = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.03, 12), std({ color: 0x111111 })); kn.position.set(-0.16, 1.125, 0); tg.add(kn);
  const coil = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.09, 12), brass); coil.position.set(0.1, 1.09, 0); tg.add(coil);
  const wire = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, 2.6, 6), std({ color: 0x222222 })); wire.rotation.z = 1.15; wire.position.set(1.3, 1.6, 0); tg.add(wire);
  // baldes + torneira
  const bk = new THREE.Group(); bk.position.set(1.15, 0, 0.5); G.add(bk); props.buckets = bk; props.water = [];
  const bM = toy(0x2f6fd0), wM = new THREE.MeshStandardMaterial({ color: 0x7fc8ff, roughness: 0.1, metalness: 0.1, transparent: true, opacity: 0.85 });
  [[0, 0], [0.5, 0.25], [-0.42, 0.3]].forEach(([x, z], i) => {
    const b = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.15, 0.36, 20, 1, true), i === 1 ? toy(0xd04a2f) : bM); b.material.side = THREE.DoubleSide; b.position.set(x, 0.18, z); b.castShadow = true; bk.add(b);
    const bt = new THREE.Mesh(new THREE.CircleGeometry(0.15, 20), b.material); bt.rotation.x = -Math.PI / 2; bt.position.set(x, 0.005, z); bk.add(bt);
    const w = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.17, 0.02, 20), wM); w.position.set(x, 0.05, z); bk.add(w); props.water.push(w);
  });
  const tap = RB(0.08, 0.08, 0.3, 0.02, new THREE.MeshStandardMaterial({ color: 0xb8bcc0, metalness: 0.9, roughness: 0.3 })); tap.position.set(0, 1.0, -0.12); bk.add(tap);
  const pipe = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 2.3, 8), tap.material); pipe.position.set(0, 2.15, -0.26); bk.add(pipe);
  const stream = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.03, 1, 8).translate(0, -0.5, 0), wM); stream.position.set(0, 0.97, 0); bk.add(stream); props.stream = stream;
  // geladeira
  const fr = new THREE.Group(); fr.position.set(-1.25, 0, 0.15); fr.rotation.y = 0.25; G.add(fr); props.fridge = fr;
  const fM = toy(0xe9ecef, { roughness: 0.3 });
  const fb = RB(0.8, 1.9, 0.7, 0.06, fM); fb.position.y = 0.95; fr.add(fb);
  const d1 = RB(0.78, 0.58, 0.05, 0.03, fM); d1.position.set(0, 1.58, 0.37); fr.add(d1); const d2 = RB(0.78, 1.2, 0.05, 0.03, fM); d2.position.set(0, 0.66, 0.37); fr.add(d2);
  for (const y of [1.45, 1.1]) { const h = RB(0.04, 0.3, 0.05, 0.015, new THREE.MeshStandardMaterial({ color: 0x8a8f96, metalness: 0.8, roughness: 0.3 })); h.position.set(0.3, y, 0.42); fr.add(h); }
  // nota de 20, coroa, celular (presos no Gepeta)
  const noteT = canvasTex(256, 128, (x, w, h) => { x.fillStyle = '#e8c23a'; x.fillRect(0, 0, w, h); x.strokeStyle = '#8a6a10'; x.lineWidth = 8; x.strokeRect(8, 8, w - 16, h - 16); x.fillStyle = '#6a4c08'; x.font = 'bold 84px sans-serif'; x.textAlign = 'center'; x.textBaseline = 'middle'; x.fillText('20', w / 2, h / 2 + 4); x.font = 'bold 22px sans-serif'; x.fillText('REAIS', w / 2, h - 24); });
  const note = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.17, 0.004), std({ map: noteT, roughness: 0.6 })); note.position.set(0, -0.22, 0.06); note.rotation.set(0, 0, Math.PI + 0.12); RA.end.add(note); props.note = note;
  const gold = new THREE.MeshStandardMaterial({ color: 0xffc83a, metalness: 1, roughness: 0.25, emissive: 0x5a3a00 });
  const crown = new THREE.Group(); const cb = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.19, 0.1, 24, 1, true), gold); cb.material.side = THREE.DoubleSide; crown.add(cb);
  for (let i = 0; i < 6; i++) { const sp = new THREE.Mesh(new THREE.ConeGeometry(0.045, 0.14, 4), gold); const a = i / 6 * 6.283; sp.position.set(Math.cos(a) * 0.19, 0.11, Math.sin(a) * 0.19); crown.add(sp); const j = new THREE.Mesh(new THREE.SphereGeometry(0.022, 8, 6), HDR(2.5, 0.2, 0.3)); j.position.set(Math.cos(a) * 0.2, 0.0, Math.sin(a) * 0.2); crown.add(j); }
  head.add(crown); props.crown = crown;
  const phone = new THREE.Group(); const pb = RB(0.12, 0.23, 0.016, 0.006, toy(0x0c0c0e, { roughness: 0.3 })); phone.add(pb);
  const scrM = new THREE.MeshBasicMaterial({ color: new THREE.Color(1.6, 1.9, 2.4) }); const sc = new THREE.Mesh(new THREE.PlaneGeometry(0.105, 0.21), scrM); sc.position.z = 0.0095; phone.add(sc);
  phone.position.set(0, -0.2, 0.07); phone.rotation.set(-0.5, 0, 0); RA.end.add(phone); props.phone = phone; props.scrM = scrM;
}
const NSP = 70; const sparkM = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 6, 5), HDR(5, 3.4, 1.2), NSP); sparkM.frustumCulled = false; scene.add(sparkM); let spN = 0; const _sd = new THREE.Object3D();
function sparks(pos, age, n, speed = 2.2, sd = 0, size = 0.02, life = 0.55) { if (age < 0 || age > life) return; for (let i = 0; i < n && spN < NSP; i++) { const a = hash(i + sd) * 6.283, e = hash(i * 3 + sd + 7) * 1.4 - 0.2, v = speed * (0.4 + hash(i * 7 + sd)); _sd.position.set(pos.x + Math.cos(a) * Math.cos(e) * v * age, pos.y + Math.sin(e) * v * age - 3.5 * age * age, pos.z + Math.sin(a) * Math.cos(e) * v * age); _sd.scale.setScalar(size * (1 - age / life)); _sd.updateMatrix(); sparkM.setMatrixAt(spN++, _sd.matrix); } }
function corLight(fn, o = {}) {
  const L = corridorG.userData; let sum = 0;
  L.lamps.forEach((l, i) => { const k = fn(i); sum += i < 3 ? k : 0; l.bulb.material.emissiveIntensity = 2.6 * k; l.cone.material.opacity = 0.15 * k; if (l.light) l.light.intensity = 4.2 * k; });
  const a = Math.min(1, sum / 3); L.spot.intensity = 5.5 * fn(1); L.fill.intensity = 2.4 * a; L.hemi.intensity = 0.4 * a + (o.amb ?? 0.05); L.rim.intensity = 1.3 * a + (o.rim || 0);
  props.emerL.intensity = (o.emer || 0) * 5; props.emerM.emissiveIntensity = (o.emer || 0) * 4; props.phoneL.intensity = (o.phone || 0) * 2.4;
  props.tele.visible = !!o.tele; props.buckets.visible = !!o.buckets; props.fridge.visible = !!o.fridge; props.note.visible = !!o.note; props.crown.visible = o.crown !== undefined; props.phone.visible = !!o.phoneObj;
  if (o.crown !== undefined) { props.crown.position.set(0, 0.26 + (1 - back(o.crown)) * 1.0, 0); props.crown.rotation.z = 0.12; }
}

// ================================================================ ESPAÇO
const spaceG = new THREE.Group(); scene.add(spaceG);
const SUNP = V(0, 6, -40), E0 = V(1.3, -1.9, -7), ER = 1.4;
const sunTex = canvasTex(512, 256, (x, w, h) => { x.fillStyle = '#ff9a1a'; x.fillRect(0, 0, w, h); smudge(x, w, h, 90, 0.5, '255,230,120'); smudge(x, w, h, 70, 0.45, '200,50,0'); noise(x, w, h, 5000, 0.5, '255,240,170'); noise(x, w, h, 3000, 0.5, '160,30,0'); });
const sunM = new THREE.MeshBasicMaterial({ map: sunTex, color: new THREE.Color(1.7, 1.25, 0.8), fog: false }); const sunS = new THREE.Mesh(new THREE.SphereGeometry(6, 40, 24), sunM); sunS.position.copy(SUNP); spaceG.add(sunS);
const glowT = canvasTex(256, 256, (x, w, h) => { const g = x.createRadialGradient(128, 128, 20, 128, 128, 128); g.addColorStop(0, 'rgba(255,200,90,0.9)'); g.addColorStop(0.4, 'rgba(255,120,20,0.35)'); g.addColorStop(1, 'rgba(255,80,0,0)'); x.fillStyle = g; x.fillRect(0, 0, w, h); });
const corona = new THREE.Mesh(new THREE.PlaneGeometry(34, 34), new THREE.MeshBasicMaterial({ map: glowT, transparent: true, opacity: 0.55, blending: THREE.AdditiveBlending, depthWrite: false, fog: false })); corona.position.copy(SUNP).add(V(0, 0, -1)); spaceG.add(corona);
const earthTex = canvasTex(512, 256, (x, w, h) => { x.fillStyle = '#1b4f9c'; x.fillRect(0, 0, w, h); for (let i = 0; i < 46; i++) { x.fillStyle = ['#2f8a3f', '#3f9a4a', '#b89a5a', '#2a7a3a'][i % 4]; x.beginPath(); x.ellipse(rnd() * w, 40 + rnd() * (h - 80), 12 + rnd() * 42, 8 + rnd() * 26, rnd() * 3, 0, 6.3); x.fill(); } x.fillStyle = '#eef4fa'; x.fillRect(0, 0, w, 14); x.fillRect(0, h - 16, w, 16); smudge(x, w, h, 40, 0.5, '255,255,255'); });
const earth = new THREE.Mesh(new THREE.SphereGeometry(ER, 40, 24), std({ map: earthTex, roughness: 0.7 })); earth.position.copy(E0); spaceG.add(earth);
const atmo = new THREE.Mesh(new THREE.SphereGeometry(ER * 1.06, 32, 20), new THREE.MeshBasicMaterial({ color: 0x4aa0ff, transparent: true, opacity: 0.22, blending: THREE.AdditiveBlending, side: THREE.BackSide, depthWrite: false })); atmo.position.copy(E0); spaceG.add(atmo);
const sunL = new THREE.DirectionalLight(0xfff0d8, 1.9); sunL.position.copy(SUNP); sunL.target.position.copy(E0); spaceG.add(sunL, sunL.target); const spAmb = new THREE.AmbientLight(0x6a86b0, 0.9); spaceG.add(spAmb);
{ const g = new THREE.BufferGeometry(); const p = []; for (let i = 0; i < 1400; i++) { const a = rnd() * 6.283, e = (rnd() - 0.5) * 3.1, r = 150; p.push(Math.cos(a) * Math.cos(e) * r, Math.sin(e) * r, Math.sin(a) * Math.cos(e) * r); } g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3)); spaceG.add(new THREE.Points(g, new THREE.PointsMaterial({ color: 0xffffff, size: 0.6, fog: false }))); }
const NPL = 110; const plasma = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 1), HDR(1.7, 0.6, 0.14), NPL); plasma.frustumCulled = false; spaceG.add(plasma);
function plasmaAt(q, t) { const d = SUNP.clone().negate().normalize(), st = SUNP.clone().add(d.clone().multiplyScalar(5.6)); const L = st.length();
  for (let i = 0; i < NPL; i++) { const lag = hash(i) * 0.12, qq = q - lag * Math.min(1, q * 4); const c = st.clone().add(d.clone().multiplyScalar(L * qq)); const sp = (0.6 + 3.4 * Math.max(0, qq)) * (0.25 + hash(i + 5)); const a = hash(i * 3) * 6.283 + t * 0.4 * (hash(i + 2) - 0.5); c.x += Math.cos(a) * sp; c.y += Math.sin(a) * sp * 0.8; _sd.position.copy(c); _sd.scale.setScalar(q <= 0 ? 0 : (0.09 + 0.2 * hash(i + 9)) * Math.min(1, q * 8)); _sd.updateMatrix(); plasma.setMatrixAt(i, _sd.matrix); }
  plasma.instanceMatrix.needsUpdate = true; }
const ringM = new THREE.MeshBasicMaterial({ color: new THREE.Color(0.25, 1.5, 0.7), transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false });
const rings = [1, -1].map(s => { const r = new THREE.Mesh(new THREE.TorusGeometry(1, 0.035, 8, 70), ringM); r.rotation.x = Math.PI / 2; spaceG.add(r); return { r, s }; });
function ringsAt(lat, t) { rings.forEach(({ r, s }) => { r.visible = lat !== null; if (lat === null) return; const la = (lat + 2 * Math.sin(t * 3 + s)) * Math.PI / 180; const rr = ER * 1.03 * Math.cos(la); r.scale.set(rr, rr, 1.6 + 0.6 * Math.sin(t * 5)); r.position.set(E0.x, E0.y + s * ER * 1.03 * Math.sin(la), E0.z); }); }

// ================================================================ CIDADE
const city = new THREE.Group(); scene.add(city);
const cityL = new THREE.Group(); city.add(cityL);
const moon = new THREE.DirectionalLight(0x9fb4ff, 1.0); moon.castShadow = true; moon.shadow.mapSize.set(2048, 2048); Object.assign(moon.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9, near: 1, far: 70 }); moon.shadow.bias = -0.0006; moon.shadow.normalBias = 0.03; cityL.add(moon, moon.target);
const hemiCity = new THREE.HemisphereLight(0x3a4a7a, 0x14141c, 0.7); cityL.add(hemiCity);
const auroraL = new THREE.DirectionalLight(0x5dffb0, 0); auroraL.position.set(0, 30, -40); cityL.add(auroraL);
const skyC = new THREE.Mesh(new THREE.SphereGeometry(320, 24, 16), new THREE.MeshBasicMaterial({ map: canvasTex(8, 512, (x, w, h) => { const g = x.createLinearGradient(0, 0, 0, h); g.addColorStop(0, '#05081a'); g.addColorStop(0.42, '#0e1838'); g.addColorStop(0.5, '#27305a'); g.addColorStop(0.52, '#1a1c2c'); g.addColorStop(1, '#0a0a12'); x.fillStyle = g; x.fillRect(0, 0, w, h); }), side: THREE.BackSide, fog: false, depthWrite: false })); city.add(skyC);
{ const g = new THREE.BufferGeometry(); const p = []; for (let i = 0; i < 900; i++) { const a = rnd() * 6.283, e = 0.08 + rnd() * 1.4, r = 300; p.push(Math.cos(a) * Math.cos(e) * r, Math.sin(e) * r, Math.sin(a) * Math.cos(e) * r); } g.setAttribute('position', new THREE.Float32BufferAttribute(p, 3)); const st = new THREE.Points(g, new THREE.PointsMaterial({ color: 0xffffff, size: 1.3, fog: false, transparent: true })); city.add(st); city.userData.stars = st; }
const blds = [];
{
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(600, 600), std({ color: 0x1c1e24, roughness: 0.9 })); ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; city.add(ground);
  const lane = new THREE.Mesh(new THREE.PlaneGeometry(0.25, 300), new THREE.MeshBasicMaterial({ color: 0x8a8a70 })); lane.rotation.x = -Math.PI / 2; lane.position.set(0, 0.01, -120); city.add(lane);
  const pal = ['#5a5f6e', '#6e6258', '#4f5a66', '#6a6470', '#585e58'];
  const mk = (cols, rows, wall) => { const fac = canvasTex(256, 512, (x, w, h) => { x.fillStyle = wall; x.fillRect(0, 0, w, h); noise(x, w, h, 2500, 0.12); const cw = w / cols, ch = h / rows; for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) { x.fillStyle = '#10141c'; x.fillRect(i * cw + cw * 0.2, j * ch + ch * 0.22, cw * 0.6, ch * 0.56); } });
    const em = canvasTex(256, 512, (x, w, h) => { x.fillStyle = '#000'; x.fillRect(0, 0, w, h); const cw = w / cols, ch = h / rows; for (let i = 0; i < cols; i++) for (let j = 0; j < rows; j++) { if (rnd() < 0.42) continue; x.fillStyle = rnd() < 0.75 ? '#ffd58a' : (rnd() < 0.5 ? '#bfe0ff' : '#ffb060'); x.globalAlpha = 0.55 + rnd() * 0.45; x.fillRect(i * cw + cw * 0.2, j * ch + ch * 0.22, cw * 0.6, ch * 0.56); } x.globalAlpha = 1; }); return [fac, em]; };
  const T4 = [mk(5, 12, pal[0]), mk(4, 9, pal[1]), mk(6, 15, pal[2]), mk(5, 10, pal[3])];
  const roofM = std({ color: 0x24262c });
  const add = (x, z, w, hh, d) => { const [fac, em] = T4[blds.length % 4]; const m = new THREE.MeshStandardMaterial({ map: fac, emissiveMap: em, emissive: 0xffffff, emissiveIntensity: 1.5, roughness: 0.85 });
    const b = new THREE.Mesh(new THREE.BoxGeometry(w, hh, d), [m, m, roofM, roofM, m, m]); b.position.set(x, hh / 2, z); b.castShadow = b.receiveShadow = true; city.add(b); blds.push({ m, x, z, h: hh }); };
  for (let z = -6; z > -190; z -= 12.5) for (const s of [-1, 1]) { add(s * (11 + rnd() * 2), z + rnd() * 2, 9 + rnd() * 2, 14 + rnd() * 22, 10); add(s * (25 + rnd() * 3), z + rnd() * 4, 11 + rnd() * 3, 26 + rnd() * 34, 11); if (z < -40) add(s * (42 + rnd() * 6), z + rnd() * 4, 13, 30 + rnd() * 50, 12); }
  for (let i = 0; i < 9; i++) add(-52 + i * 13 + rnd() * 3, 44 + rnd() * 10, 11, 18 + rnd() * 30, 11);
  for (const s of [-1, 1]) for (let z = 20; z > -4; z -= 12) add(s * (13 + rnd() * 2), z, 10, 16 + rnd() * 10, 10);
  // prédio do Gepeta (cobertura)
  const rb = new THREE.Mesh(new THREE.BoxGeometry(10, 20, 10), [T4[1][0], T4[1][0]].map(() => roofM).concat([])[0]); rb.material = std({ color: 0x3a3d46 }); rb.position.set(0, 10, 13); rb.receiveShadow = true; city.add(rb);
  for (const [x, z, w, d] of [[0, 8.1, 10, 0.3], [-4.85, 13, 0.3, 10], [4.85, 13, 0.3, 10], [0, 17.9, 10, 0.3]]) { const p = RB(w, 0.9, d, 0.05, std({ color: 0x4a4e58 })); p.position.set(x, 20.45, z); city.add(p); }
  const tank = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 1.1, 1.8, 20), std({ color: 0x3f6f9a })); tank.position.set(3.2, 21.5, 16); tank.castShadow = true; city.add(tank);
  // carro
  const car = new THREE.Group(); car.position.set(1.7, 0, 1.2); car.rotation.y = 0.25; city.add(car);
  const cbd = RB(1.7, 0.55, 3.9, 0.2, toy(0xb02a2a, { roughness: 0.3 })); cbd.position.y = 0.6; car.add(cbd); const cab = RB(1.5, 0.52, 2.0, 0.2, toy(0x1a222c, { roughness: 0.15 })); cab.position.set(0, 1.05, -0.2); car.add(cab);
  for (const [x, z] of [[-0.85, 1.25], [0.85, 1.25], [-0.85, -1.25], [0.85, -1.25]]) { const wh = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.24, 18), toy(0x111111, { roughness: 0.8 })); wh.rotation.z = Math.PI / 2; wh.position.set(x, 0.34, z); wh.castShadow = true; car.add(wh); }
  for (const s of [-1, 1]) { const hl = new THREE.Mesh(new THREE.SphereGeometry(0.12, 10, 8), HDR(2.4, 2.2, 1.6)); hl.position.set(s * 0.6, 0.62, 1.93); hl.scale.z = 0.4; car.add(hl); }
  // subestação
  const sub = new THREE.Group(); sub.position.set(80, 0, 0); city.add(sub); city.userData.sub = sub;
  const tm = new THREE.MeshStandardMaterial({ color: 0x5f6f66, roughness: 0.5, metalness: 0.4, emissive: 0xff5a10, emissiveIntensity: 0 }); city.userData.trM = tm;
  const tb = RB(3.0, 3.2, 2.2, 0.12, tm); tb.position.y = 1.9; sub.add(tb); const pad = RB(4.4, 0.3, 3.4, 0.05, std({ color: 0x55585e })); pad.position.y = 0.15; sub.add(pad);
  for (let i = 0; i < 9; i++) for (const s of [-1, 1]) { const f = RB(0.08, 2.4, 0.5, 0.02, tm); f.position.set(-1.3 + i * 0.32, 1.8, s * 1.35); sub.add(f); }
  for (let i = 0; i < 3; i++) { const ins = new THREE.Group(); ins.position.set(-0.9 + i * 0.9, 3.5, 0); sub.add(ins); for (let k = 0; k < 5; k++) { const d = new THREE.Mesh(new THREE.CylinderGeometry(0.2 - k * 0.02, 0.24 - k * 0.02, 0.14, 14), toy(0x8a4a2a)); d.position.y = k * 0.2; d.castShadow = true; ins.add(d); } const wr = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 14, 6), std({ color: 0x111111 })); wr.rotation.x = 1.25; wr.position.set(0, 3.2, -6.5); ins.add(wr); }
  const cons = new THREE.Mesh(new THREE.CylinderGeometry(0.45, 0.45, 2.4, 16), tm); cons.rotation.z = Math.PI / 2; cons.position.set(0, 3.75, -0.85); sub.add(cons);
  for (let i = 0; i < 8; i++) { const fp = RB(0.1, 2.2, 0.1, 0.02, std({ color: 0x777b82 })); fp.position.set(-7 + i * 2, 1.1, 4.2); sub.add(fp); } const fr2 = RB(14, 0.06, 0.06, 0.02, std({ color: 0x777b82 })); fr2.position.set(0, 2.1, 4.2); sub.add(fr2); const fr3 = fr2.clone(); fr3.position.y = 1.2; sub.add(fr3);
  const tw = new THREE.Group(); tw.position.set(0, 0, -13); sub.add(tw); for (const [x, z] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) { const l = RB(0.14, 16, 0.14, 0.02, std({ color: 0x6a6e76 })); l.position.set(x * 0.9, 8, z * 0.9); l.rotation.set(z * 0.05, 0, -x * 0.05); tw.add(l); } for (const y of [9, 12, 15]) { const ar = RB(7, 0.14, 0.14, 0.02, std({ color: 0x6a6e76 })); ar.position.y = y; tw.add(ar); }
  const boom = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), HDR(6, 3.5, 1.2)); boom.position.set(0, 3.2, 0); sub.add(boom); city.userData.boom = boom;
  const smk = []; for (let i = 0; i < 9; i++) { const s = new THREE.Mesh(new THREE.SphereGeometry(0.6, 10, 8), new THREE.MeshStandardMaterial({ color: 0x2a2a2e, transparent: true, opacity: 0.7, roughness: 1 })); sub.add(s); smk.push(s); } city.userData.smk = smk;
  // neve (Quebec)
  const sg = new THREE.BufferGeometry(); const sp = []; for (let i = 0; i < 1500; i++) sp.push((rnd() - 0.5) * 120, rnd() * 60, 30 - rnd() * 150); sg.setAttribute('position', new THREE.Float32BufferAttribute(sp, 3));
  const snow = new THREE.Points(sg, new THREE.PointsMaterial({ color: 0xffffff, size: 0.35, transparent: true, opacity: 0.85 })); city.add(snow); city.userData.snow = snow;
}
const aurT = canvasTex(256, 256, (x, w, h) => { const g = x.createLinearGradient(0, 0, 0, h); g.addColorStop(0, 'rgba(255,60,180,0)'); g.addColorStop(0.25, 'rgba(230,80,200,0.55)'); g.addColorStop(0.55, 'rgba(60,255,150,0.95)'); g.addColorStop(0.9, 'rgba(40,255,140,0.35)'); g.addColorStop(1, 'rgba(40,255,140,0)'); x.fillStyle = g; x.fillRect(0, 0, w, h); x.globalCompositeOperation = 'destination-out'; for (let i = 0; i < 90; i++) { x.fillStyle = `rgba(0,0,0,${0.15 + rnd() * 0.5})`; x.fillRect(rnd() * w, 0, 1 + rnd() * 5, h); } });
const curtains = [];
for (let i = 0; i < 5; i++) { const g = new THREE.PlaneGeometry(260, 46 + i * 6, 60, 1); const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ map: aurT, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, fog: false, color: new THREE.Color(1.5, 1.5, 1.5) })); m.position.set((i - 2) * 14, 62 + i * 9, -80 - i * 26); city.add(m); curtains.push({ m, base: Float32Array.from(g.attributes.position.array), ph: i * 1.7 }); }
function cityState(t, o = {}) { // {aur, dawn, cold, focus, lit:fn(b)->0..1}
  const aur = o.aur || 0, dawn = o.dawn || 0, f = o.focus || V(0, 0, 0);
  curtains.forEach(({ m, base, ph }) => { m.material.opacity = 0.75 * aur; m.visible = aur > 0.01; const p = m.geometry.attributes.position; for (let i = 0; i < p.count; i++) { const x = base[i * 3]; p.setZ(i, 9 * Math.sin(x * 0.045 + t * 0.35 + ph) + 5 * Math.sin(x * 0.11 - t * 0.5 + ph * 2)); p.setY(i, base[i * 3 + 1] + 2.5 * Math.sin(x * 0.07 + t * 0.6 + ph)); } p.needsUpdate = true; });
  blds.forEach((b, i) => { b.m.emissiveIntensity = 1.5 * (o.lit ? o.lit(b, i) : 1); });
  moon.position.copy(f).add(dawn > 0.5 ? V(-14, 9, 10) : V(8, 22, 12)); moon.target.position.copy(f); moon.color.copy(C(0x9fb4ff).lerp(C(0xffc9a0), dawn)); moon.intensity = lerp(1.0, 3.4, dawn) + (o.cold ? 0.4 : 0);
  hemiCity.intensity = lerp(0.7, 1.9, dawn); hemiCity.color.copy(C(0x3a4a7a).lerp(C(0x9fb6e0), dawn)); auroraL.intensity = 1.4 * aur;
  skyC.material.color.copy(C(0xffffff).lerp(C(0xffc8a8), dawn).multiplyScalar(1 + 8 * dawn)); city.userData.stars.material.opacity = 1 - dawn; city.userData.snow.visible = !!o.cold; if (o.cold) city.userData.snow.position.y = -((t * 3) % 20);
  const fc = C(0x0a1024).lerp(C(0x8a8fa8), dawn); scene.fog.color.copy(fc); scene.background.copy(fc); scene.fog.density = lerp(0.0055, 0.004, dawn);
}

// ================================================================ TIMELINE
const phrases = TL.phrases;
const shots = []; for (const p of phrases) { if (!shots.length || shots[shots.length - 1].name !== p.shot) shots.push({ name: p.shot, start: p.start, ps: [p] }); else shots[shots.length - 1].ps.push(p); }
shots[0].start = 0; for (let i = 0; i < shots.length; i++) shots[i].end = i + 1 < shots.length ? shots[i + 1].start : TOTAL;
const SH = Object.fromEntries(shots.map(s => [s.name, s]));
const WALL = phrases.flatMap(p => p.words.map(w => ({ s: w[0], e: w[1], w: w[2], shot: p.shot })));
const wt = (shot, re, fb = 0, nth = 0) => { const l = WALL.filter(w => w.shot === shot && re.test(w.w)); return l[nth] ? l[nth].s : SH[shot].start + fb; };
const p2 = (shot) => SH[shot].ps[1] ? SH[shot].ps[1].start : SH[shot].end;
const T = {
  ejec: wt('sol', /ejeção/i, 1.6), cara: wt('sol', /direção/i, 3),
  nome: wt('calma', /nome/i, 0.8), emc: wt('calma', /ejeção/i, 2), bil: wt('calma', /bilhões/i, 3.6),
  p17: wt('prazo', /^17/, 1.2), dia1: wt('prazo', /bem-vindo/i, 2),
  a1859: wt('c1859', /^1859/, 1.3), mex: wt('c1859', /méxico/i, 3), tel: wt('c1859', /telégrafos/i, 4), fai: wt('c1859', /faísca/i, 5),
  queb: wt('c1989', /quebec/i, 4), s90: wt('c1989', /^90/, 5),
  verde: wt('aurora', /verde/i, 2.5), filmar: wt('aurora', /todo/i, 3), story: wt('aurora', /story/i, 6),
  fritar: wt('frita', /fritar/i, 2.4), meses: wt('frita', /meses/i, 4),
  luz: wt('escuro', /luz/i, 0.5), wifi: wt('escuro', /wi-fi/i, 1.5), pix: wt('escuro', /pix/i, 2.6), fodeu: wt('escuro', /fodeu/i, 3.5),
  bomba: wt('r1', /bomba/i, 1.5), caixa: wt('r1', /caixa/i, 5.5),
  nao: wt('r2', /não/i, 1), h4: wt('r2', /^4/, 4), h48: wt('r2', /^48/, 5.5),
  din: wt('r3', /dinheiro/i, 0.8), cart: wt('r3', /cartão/i, 2.4), rei: wt('r3', /rei/i, 4.2),
  torre: wt('cel', /torre/i, 1), fam: wt('cel', /avisa/i, 2.8),
  tanque: wt('dilema', /tanque/i, 1.6), ir: wt('dilema', /^ir$/i, 4.4),
  fica: wt('cta', /fica/i, 0.5), vai: wt('cta', /vai/i, 1), dia2: wt('cta', /votada/i, 2), segue: wt('cta', /segue/i, 3.6),
};

// ================================================================ PÓS
const composer = new EffectComposer(renderer); composer.setSize(IW, IH);
composer.addPass(new RenderPass(scene, camera));
const ao = new GTAOPass(scene, camera, IW, IH); ao.updateGtaoMaterial({ radius: 0.4, distanceExponent: 1.5, thickness: 1, scale: 1.25, samples: +(Q.get('ao') || 8) }); composer.addPass(ao); { const k = +(Q.get('as') || 0.5); ao.setSize(Math.round(IW * k), Math.round(IH * k)); }
const bloom = new UnrealBloomPass(new THREE.Vector2(IW / 2, IH / 2), 0.5, 0.6, 0.9); composer.addPass(bloom);
composer.addPass(new OutputPass());
const fxaa = new ShaderPass(FXAAShader); fxaa.material.uniforms['resolution'].value.set(1 / IW, 1 / IH); composer.addPass(fxaa);
let mode = '', flashA = 0, shakeA = 0, vig = 0.5, ov = [], T_NOW = 0, sepiaA = 0, darkA = 0;
function setMode(m) {
  mode = m; corridorG.visible = gep.visible = m === 'cor'; spaceG.visible = m === 'space'; city.visible = m === 'city'; headAnt.g.visible = false; spN = 0;
  ao.enabled = m !== 'space' && Q.get('gt') !== '0'; scene.environment = ENVT;
  if (m === 'cor') { scene.background.setHex(0x0d0f0c); scene.fog.color.setHex(0x0d0f0c); scene.fog.density = 0.055; scene.environmentIntensity = 0.2; renderer.toneMappingExposure = 1.08; bloom.strength = 0.5; bloom.threshold = 0.9; vig = 0.6; }
  else if (m === 'space') { scene.background.setHex(0x020308); scene.fog.color.setHex(0x020308); scene.fog.density = 0; scene.environmentIntensity = 0.05; renderer.toneMappingExposure = 1; bloom.strength = 0.55; bloom.threshold = 0.9; vig = 0.55; }
  lensM.envMapIntensity = m === 'city' ? 1.5 : 6;
  if (m === 'cor' || m === 'space') {} else { scene.environmentIntensity = 0.12; renderer.toneMappingExposure = 1.05; bloom.strength = 0.7; bloom.threshold = 0.8; vig = 0.6; }
}
function cam(p, tg, fov, tc) {
  const t = T_NOW; let f = fov; if (tc !== undefined && t >= tc && t - tc < 0.2) f *= 1 - 0.08 * (1 - (t - tc) / 0.2);
  camera.position.set(p.x + 0.006 * Math.sin(t * 2.3) + 0.004 * Math.sin(t * 5.1), p.y + 0.005 * Math.sin(t * 1.7 + 1), p.z);
  if (shakeA > 0) { camera.position.x += (hash(t * 97) - 0.5) * shakeA; camera.position.y += (hash(t * 131 + 3) - 0.5) * shakeA; }
  camera.lookAt(tg); camera.fov = f; camera.updateProjectionMatrix(); camera.updateMatrixWorld(true);
}
const _v = new THREE.Vector3();
const scr = (v) => { _v.copy(v).project(camera); return [(_v.x * 0.5 + 0.5) * W, (-_v.y * 0.5 + 0.5) * H]; };
//@@2D@@
// ---- elementos de tela da série
function hudBar(day, time, status, col = '#ff5548') {
  ctx.save(); ctx.translate(W / 2, 205); ctx.fillStyle = 'rgba(8,10,14,0.88)'; ctx.strokeStyle = 'rgba(255,255,255,0.18)'; ctx.lineWidth = 4; ctx.beginPath(); ctx.roundRect(-440, -52, 880, 104, 30); ctx.fill(); ctx.stroke();
  const bl = Math.sin(T_NOW * 7) > 0 ? 1 : 0.3; ctx.globalAlpha = bl; ctx.fillStyle = col; ctx.beginPath(); ctx.arc(-396, 0, 13, 0, 6.3); ctx.fill(); ctx.globalAlpha = 1;
  ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; ctx.font = '44px Cap'; ctx.fillStyle = '#fff'; ctx.fillText(day, -368, 3);
  ctx.textAlign = 'center'; ctx.font = '66px Cap'; ctx.fillText(time, -40, 4); ctx.textAlign = 'right'; ctx.font = '34px Cap'; ctx.fillStyle = col; ctx.fillText(status, 408, 4); ctx.restore();
}
function bar(label, frac, y, col, t0, right) {
  const t = T_NOW; if (t < t0) return; const s = back((t - t0) / 0.3); ctx.save(); ctx.translate(W / 2, y); ctx.scale(s, s);
  ctx.fillStyle = 'rgba(8,10,14,0.9)'; ctx.beginPath(); ctx.roundRect(-400, -80, 800, 160, 30); ctx.fill();
  ctx.font = '46px Cap'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillStyle = '#fff'; ctx.fillText(label, -360, -36); ctx.textAlign = 'right'; ctx.fillStyle = col; ctx.fillText(right, 360, -36);
  ctx.fillStyle = '#2a2e36'; ctx.beginPath(); ctx.roundRect(-360, 6, 720, 44, 14); ctx.fill(); ctx.fillStyle = col; ctx.beginPath(); ctx.roundRect(-360, 6, Math.max(20, 720 * clamp(frac, 0, 1)), 44, 14); ctx.fill(); ctx.restore();
}
function gone(label, x, y, t0, t1) { // item riscado
  const t = T_NOW; if (t < t0 || (t1 && t > t1)) return; const s = back((t - t0) / 0.25); ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.font = '74px Cap'; const w = ctx.measureText(label).width + 70;
  ctx.fillStyle = 'rgba(8,10,14,0.9)'; ctx.beginPath(); ctx.roundRect(-w / 2, -58, w, 116, 26); ctx.fill(); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = '#8a8f98'; ctx.fillText(label, 0, 4);
  const k = sm(t0 + 0.1, t0 + 0.3, t); ctx.strokeStyle = '#ff3b30'; ctx.lineWidth = 14; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(-w / 2 + 14, 0); ctx.lineTo(-w / 2 + 14 + (w - 28) * k, 0); ctx.stroke(); ctx.restore();
}
function btn(label, x, y, col, t0, w = 470) { const t = T_NOW; if (t < t0) return; const s = back((t - t0) / 0.3) * (1 + 0.03 * Math.sin(t * 6)); ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.fillStyle = 'rgba(8,10,14,0.92)'; ctx.strokeStyle = col; ctx.lineWidth = 9; ctx.shadowColor = col; ctx.shadowBlur = 30; ctx.beginPath(); ctx.roundRect(-w / 2, -70, w, 140, 40); ctx.fill(); ctx.stroke(); ctx.shadowBlur = 0; ctx.font = '58px Cap'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = col; ctx.fillText(label, 0, 4); ctx.restore(); }

// ================================================================ DIREÇÃO
const ALL = () => 1;
function staging(t) {
  T_NOW = t; ov = []; flashA = 0; shakeA = 0; sepiaA = 0; darkA = 0;
  const sh = shots.find(s => t >= s.start && t < s.end) || shots[shots.length - 1];
  const N = sh.name, S = sh.start, E = sh.end, u = t - S, k = sm(S, E, t), pB = p2(N);
  if (u < 0.1 && S > 0) flashA = 0.3 * (1 - u / 0.1);
  const space = (q, lat = null) => { setMode('space'); spAmb.intensity = lat !== null ? 1.7 : 0.9; plasmaAt(q, t); ringsAt(lat, t); sunS.rotation.y = t * 0.05; earth.rotation.y = t * 0.08; corona.scale.setScalar(1 + 0.04 * Math.sin(t * 5)); };

  if (N === 'sol') {
    const a = t - T.ejec, tc = T.cara - 0.25;
    if (t < tc) { space(a > 0 ? 0.3 * sm(0, tc - T.ejec, a) : 0); const pu = a > 0 && a < 0.5 ? 1 - a / 0.5 : 0; sunM.color.setRGB(1.7 + 3 * pu, 1.25 + 1.6 * pu, 0.8 + pu); corona.scale.setScalar(1 + 0.5 * pu); if (pu > 0) { shakeA = 0.5 * pu; flashA = 0.5 * pu; }
      cam(V(0, 0, 0), V(0, lerp(4.5, 5.2, k), -20), lerp(52, 46, sm(S, tc, t)), T.ejec); }
    else { const q = lerp(0.3, 1.12, Math.pow(sm(tc, E - 0.1, t), 1.6)); space(q); sunM.color.setRGB(1.7, 1.25, 0.8); shakeA = 0.25 * q; cam(V(0, 0, 0), V(0, 3.6, -20), 60, tc); if (q > 0.95) flashA = Math.min(1, (q - 0.95) / 0.12); }
    ov.push(() => { pill([{ txt: 'O SOL VAI APAGAR O BRASIL', size: 58 }, { txt: 'DIA 1', size: 120, c: '#ffb23a' }], W / 2, 300, 0.03, { t1: tc });
      stamp('EJEÇÃO', W / 2, 700, T.ejec + 0.05, { t1: tc, size: 170, c: '#ff7a1a' }); if (t > tc) txt('NA SUA DIREÇÃO', W / 2, 330, 96, { c: '#ff5548', s: back((t - tc) / 0.25), rot: -0.04 }); });
  }
  else if (N === 'calma') {
    if (t < T.bil - 0.15) { setMode('cor'); corLight(ALL); const sh2 = t > T.nome - 0.1;
      gepPose(t, { arms: sh2 ? 'shrug' : 'stop', frown: sh2 ? 0 : 1, brow: sh2 ? 0.6 : 0, headZ: sh2 ? 0.07 : 0 }); if (u < 0.25) shakeA = 0.03;
      if (!sh2) cam(V(0.3, 1.9, lerp(3.2, 2.9, sm(S, T.nome, t))), V(0, 1.92, 0), 38, S); else cam(V(-0.4, 1.9, lerp(3.7, 3.4, sm(T.nome, T.bil, t))), V(0, 1.95, 0), 38, T.nome - 0.1);
      ov.push(() => { stamp('CALMA!', W / 2, 330, S + 0.02, { t1: T.nome - 0.1, size: 170 }); pill([{ txt: 'EJEÇÃO DE', size: 64 }, { txt: 'MASSA CORONAL', size: 84, c: '#ffb23a' }, { txt: 'é o nome científico mesmo', size: 40, it: true, c: '#cfcfcf' }], W / 2, 320, T.emc - 0.1); }); }
    else { space(lerp(0.34, 0.5, sm(T.bil, E, t))); cam(V(0, 0, 0), V(0, 3.2, -20), 54, T.bil - 0.15);
      ov.push(() => { const s = back((t - T.bil + 0.1) / 0.3); txt('BILHÕES', W / 2, 300, 170, { c: '#ffb23a', s, rot: -0.03, glow: 'rgba(255,120,20,0.8)' }); txt('DE TONELADAS DE PLASMA', W / 2, 430, 60, { s }); }); }
  }
  else if (N === 'prazo') {
    space(lerp(0.5, 0.66, k)); const d1 = t > T.dia1 - 0.1;
    cam(V(0, 0, 0), V(0.4, lerp(1.6, 1.0, k), -20), lerp(50, 44, k), d1 ? T.dia1 - 0.1 : S);
    if (d1 && t - T.dia1 < 0.3) { flashA = 0.6 * (1 - (t - T.dia1 + 0.1) / 0.4); shakeA = 0.2; }
    ov.push(() => { if (!d1) { const rem = 17 * 3600 - (t - S) * 900; const hh = Math.floor(rem / 3600), mm = Math.floor(rem % 3600 / 60), ss = Math.floor(rem % 60); const s = back((t - T.p17 + 0.5) / 0.3); if (s > 0) { txt('CHEGA EM', W / 2, 270, 60, { s }); txt(`${hh}:${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')}`, W / 2, 400, 170, { c: '#ff5548', s }); } }
      else { stamp('DIA 1', W / 2, 420, T.dia1 - 0.08, { size: 300, c: '#ffb23a', bg: 'rgba(10,10,14,0.92)', rot: -0.06 }); } });
  }
  else if (N === 'c1859') {
    sepiaA = t < T.tel - 0.2 ? 0.45 : 0.8;
    if (t < T.tel - 0.2) { const la = t < T.a1859 ? 70 : lerp(70, 21, sm(T.a1859, T.mex + 0.4, t)); space(-1, la);
      cam(E0.clone().add(V(lerp(0.6, 0, k), 0.9, 7.2)), E0.clone().add(V(0, 0.25, 0)), 40, S);
      ov.push(() => { pill([{ txt: '1859', size: 130, c: '#ffe6b0' }, { txt: 'EVENTO CARRINGTON', size: 50 }], W / 2, 300, S + 0.05, { bg: '#2a1c0c' });
        const la2 = 19 * Math.PI / 180; tag(scr(E0.clone().add(V(ER * Math.cos(la2) * Math.sin(-0.35), ER * Math.sin(la2), ER * Math.cos(la2) * Math.cos(-0.35)))), 'AURORA NO MÉXICO', 120, 330, T.mex - 0.1, { c: '#7dffb0', size: 56 }); }); }
    else { setMode('cor'); const z = t - T.fai, zap = z > 0 && z < 0.9; corLight(ALL, { tele: 1 });
      gepPose(t, { af: (R, L) => { R.sh.rotation.x = -0.75; R.el.rotation.x = -0.95 + (zap ? 0 : 0.18 * Math.max(0, Math.sin(t * 14))); L.sh.rotation.z = 0.1; if (zap) { R.sh.rotation.z = -0.5; L.sh.rotation.z = 1.2; L.el.rotation.x = -0.6; } }, jig: zap ? 1 : 0, brow: zap ? 1 : 0, tongue: 0, headX: zap ? -0.1 : 0.2 });
      if (zap) mouthOpen.visible = true, mouthOpen.scale.set(1.2, 1.3, 1), smile.visible = false;
      props.lever.rotation.z = zap ? 0 : 0.12 * Math.max(0, Math.sin(t * 14));
      const kp = props.tele.localToWorld(V(-0.16, 1.14, 0)); for (let i = 0; i < 4; i++) sparks(kp, z - i * 0.18, 16, 2.6, i * 31, 0.022); if (zap) { shakeA = 0.03; flashA = 0.25 * Math.max(0, Math.sin(t * 40)); }
      cam(V(lerp(1.4, 1.1, sm(T.tel, E, t)), 1.85, 3.7), V(-0.1, 1.8, 0.3), 38, T.tel - 0.2);
      ov.push(() => { pill([{ txt: '1859 · TELÉGRAFO', size: 56, c: '#ffe6b0' }], W / 2, 250, T.tel - 0.15, { bg: '#2a1c0c' }); stamp('BZZZT!', W / 2, 400, T.fai, { size: 170, c: '#ffd21a', bg: 'rgba(20,14,4,0.92)' }); }); }
  }
  else if (N === 'c1989') {
    setMode('city'); const w0 = T.queb - 0.1; cityState(t, { cold: 1, focus: V(0, 0, -20), lit: (b) => (t < w0 ? 1 : (t - w0) * 150 > (-b.z + 10 + hash(b.x) * 20) ? 0 : 1) });
    cam(V(lerp(6, 0, k), lerp(46, 40, k), 34), V(0, 12, -60), 46, S);
    ov.push(() => { pill([{ txt: 'QUEBEC, CANADÁ', size: 58 }, { txt: '1989', size: 120, c: '#9fd0ff' }], W / 2, 300, S + 0.05, { t1: T.s90 - 0.2 });
      if (t > T.s90 - 0.2) { const n = 90 * sm(T.s90 - 0.2, T.s90 + 0.7, t), s = back((t - T.s90 + 0.2) / 0.3); txt(fmt(n) + ' s', W / 2, 300, 200, { c: '#ff5548', s, rot: -0.03 }); txt('E A REDE CAIU INTEIRA', W / 2, 440, 58, { s }); }
      pill([{ txt: '6 MILHÕES NO ESCURO', size: 60 }, { txt: 'por 9 horas', size: 46, c: '#9fd0ff' }], W / 2, 640, T.s90 + 1.0); });
  }
  else if (N === 'aurora') {
    setMode('city'); const au = sm(S + 0.3, T.verde + 0.6, t);
    if (t < T.filmar - 0.15) { cityState(t, { aur: au, focus: V(0, 0, -10) }); cam(V(0, lerp(23, 25, k), 24), V(0, lerp(26, 40, sm(S, T.filmar, t)), -60), 50, S); }
    else if (t < pB) { cityState(t, { aur: 1, focus: V(0, 20, 12) }); corLight(ALL, { phoneObj: 1 }); gep.visible = true;
      gepPose(t, { pos: V(0.2, 20, 11.2), ry: Math.PI, af: (R, L) => { R.sh.rotation.x = -2.5; R.el.rotation.x = -0.35; L.sh.rotation.x = -2.3; L.sh.rotation.z = -0.35; L.el.rotation.x = -0.5; }, headX: -0.3 });
      cam(V(1.0, 21.8, lerp(15.8, 15.2, sm(T.filmar, pB, t))), V(0.1, 23.4, 0), 46, T.filmar - 0.15); }
    else { cityState(t, { aur: 1, focus: V(0, 20, 12) }); corLight(ALL, {}); gep.visible = true;
      gepPose(t, { pos: V(0, 20, 12), ry: 0.25, headX: -0.22, brow: 0.8, arms: 'shrug' }); cam(V(0.5, 21.9, lerp(15.6, 15.0, sm(pB, E, t))), V(0, 22.2, 12), 34, pB); }
    corridorG.visible = false;
    ov.push(() => { hudBar('DIA 1', '03:00', 'TEMPESTADE', '#7dffb0'); if (t > T.story - 0.1) pill([{ txt: 'STORY POSTADO', size: 66, c: '#7dffb0' }, { txt: 'o último', size: 50, c: '#ff8f8f' }], W / 2, 420, T.story - 0.1, { rot: 0.02 }); });
  }
  else if (N === 'frita') {
    setMode('city'); const F = V(80, 2, 0); cityState(t, { aur: 1, focus: F }); const heat = sm(S + 0.2, T.fritar + 0.8, t), bt = T.fritar + 0.9, ba = t - bt;
    city.userData.trM.emissiveIntensity = 1.5 * heat * heat * heat * (ba > 0 ? Math.exp(-ba * 1.2) : 1) * (0.8 + 0.2 * Math.sin(t * 30));
    for (let i = 0; i < 3; i++) sparks(V(79.1 + i * 0.9, 4.5, 0), ((t - T.fritar + 0.3) * 1.2 + i * 0.37) % 0.6, 12, 3.5, i * 17 + Math.floor((t + i * 0.3) * 1.6) * 5, 0.05);
    const bm = city.userData.boom; bm.visible = ba > 0 && ba < 0.5; if (bm.visible) { bm.scale.setScalar(0.5 + ba * 14); bm.material.color.setRGB(6 * (1 - ba * 2), 3.5 * (1 - ba * 2), 1.2 * (1 - ba * 2)); }
    if (ba > 0 && ba < 0.5) { flashA = 0.9 * (1 - ba / 0.5); shakeA = 0.5 * (1 - ba / 0.5); }
    city.userData.smk.forEach((s, i) => { const a = ba - i * 0.12; s.visible = a > 0; if (a > 0) { const q = (a * 0.5) % 1.6; s.position.set(Math.sin(i * 2.1) * 0.8 + q * 0.8, 3.6 + q * 5, Math.cos(i * 1.7) * 0.5); s.scale.setScalar(0.8 + q * 2.2); s.material.opacity = 0.7 * Math.max(0, 1 - q / 1.6); } });
    cam(V(lerp(87.5, 86.5, k), lerp(1.4, 1.9, k), 9.5), V(80, 3.0, 0), 44, S);
    ov.push(() => { hudBar('DIA 1', '03:12', 'SOBRECARGA', '#ff5548'); tag(scr(V(80, 3.4, 1.1)), 'TRANSFORMADOR', 190, -430, S + 0.3, { c: '#ffb23a', size: 60, t1: bt }); stamp('MESES PRA TROCAR', W / 2, 520, T.meses - 0.05, { size: 100 }); });
  }
  else if (N === 'escuro') {
    if (t < T.wifi - 0.15) { setMode('city'); const w0 = T.luz - 0.25; cityState(t, { aur: 1, focus: V(0, 0, -10), lit: (b) => (t < w0 ? 1 : (t - w0) * 210 > (-b.z + 30 + hash(b.x) * 25) ? 0 : (hash(b.z + Math.floor(t * 20)) > 0.2 ? 1 : 0.3)) });
      cam(V(0, lerp(30, 27, k), 30), V(0, 16, -60), 50, S); }
    else { setMode('cor'); const off = (i) => { const to = lerp(T.wifi + 0.1, T.fodeu - 0.05, (5 - i) / 5); return t < to ? 1 : t < to + 0.12 ? (hash(i + Math.floor(t * 40)) > 0.5 ? 0.8 : 0.1) : 0; }; const dead = t > T.fodeu - 0.02; const em = sm(T.fodeu + 0.45, T.fodeu + 0.6, t) * (0.75 + 0.25 * Math.sin(t * 9));
      corLight(dead ? () => 0 : off, { phoneObj: 1, phone: dead ? 0.5 * em : 0.6, emer: em, amb: 0.02 });
      gepPose(t, { af: (R, L) => { R.sh.rotation.x = -0.9; R.el.rotation.x = -1.2; }, headX: dead ? -0.1 : 0.22, headY: dead ? 0.3 * Math.sin((t - T.fodeu) * 5) : 0, brow: dead ? 1 : 0.2 });
      if (dead && t - T.fodeu < 0.3) shakeA = 0.06; if (dead) darkA = 0.75 * (1 - sm(T.fodeu + 0.4, T.fodeu + 0.7, t));
      cam(V(lerp(0.6, 0.3, sm(T.wifi, E, t)), 1.85, lerp(4.4, 3.6, sm(T.wifi, E, t))), V(0, 1.85, 0), 38, T.wifi - 0.15); }
    ov.push(() => { hudBar('DIA 1', '03:14', 'APAGÃO', '#ff5548'); gone('LUZ', W / 2 - 310, 380, T.luz - 0.1); gone('WI-FI', W / 2, 380, T.wifi - 0.1); gone('PIX', W / 2 + 300, 380, T.pix - 0.1); });
  }
  else if (N === 'r1') {
    setMode('cor'); const em = 0.8 + 0.2 * Math.sin(t * 9);
    if (t < pB) { corLight(() => 0, { emer: em, phone: 0.9, phoneObj: 1 }); gepPose(t, { arms: 'point', brow: 0.4 }); cam(V(0.35, 1.9, lerp(3.6, 3.2, sm(S, pB, t))), V(0, 1.98, 0), 38, S); }
    else { const f = sm(pB, E - 0.4, t); corLight(() => 0, { emer: em, phone: 0.9, buckets: 1 }); props.water.forEach((w, i) => { const lv = clamp(f * 1.6 - i * 0.35, 0.02, 1); w.position.y = 0.03 + 0.3 * lv; w.scale.set(0.88 + 0.26 * lv, 1, 0.88 + 0.26 * lv); }); props.stream.scale.set(1 + 0.2 * Math.sin(t * 30), 0.93 - 0.3 * clamp(f * 1.6, 0, 1), 1 + 0.2 * Math.sin(t * 30));
      props.phoneL.position.set(0.9, 1.0, 1.4); gepPose(t, { pos: V(0.15, 0, 0.25), ry: 0.5, af: (R, L) => { L.sh.rotation.x = -0.8; L.el.rotation.x = -0.5; L.sh.rotation.z = 0.5; }, headX: 0.25, headY: 0.2 });
      cam(V(lerp(2.3, 2.0, f), 0.75, 2.6), V(0.95, 0.55, 0.4), 40, pB); }
    if (t < pB) props.phoneL.position.set(0.1, 1.45, 0.75);
    ov.push(() => { hudBar('DIA 1', '03:20', 'APAGÃO', '#ff5548'); stamp('REGRA 1', W / 2, 360, S + 0.03, { size: 130, t1: pB, c: '#1f7ae0' }); pill([{ txt: 'ÁGUA', size: 150, c: '#7fc8ff' }], W / 2, 560, S + 0.35, { t1: T.bomba - 0.1 }); gone('BOMBA DO PRÉDIO', W / 2, 580, T.bomba - 0.05, pB); if (t < pB) return;
      const f = sm(pB, E, t); bar("CAIXA D'ÁGUA", 1 - 0.7 * f, 400, '#7fc8ff', pB + 0.1, Math.round(100 - 70 * f) + '%'); });
  }
  else if (N === 'r2') {
    setMode('cor'); const em = 0.8 + 0.2 * Math.sin(t * 9); corLight(() => 0, { emer: em, phone: 1.0, fridge: 1 }); props.phoneL.position.set(-0.4, 1.5, 1.6);
    const rc = sm(S + 0.5, T.nao, t), sl = Math.exp(-Math.pow((t - T.nao - 0.12) / 0.12, 2));
    gepPose(t, { af: (R, L) => { R.sh.rotation.z = -1.25 * rc * (1 - sl); R.sh.rotation.x = -0.5 * rc; R.el.rotation.x = -0.3; L.sh.rotation.x = -1.0 * sl; L.sh.rotation.z = -0.9 * sl; L.el.rotation.x = -1.2 * sl; }, headY: -0.45, brow: sl, frown: t > T.nao ? 0.6 : 0, jig: sl > 0.3 ? 1 : 0 });
    if (sl > 0.5) shakeA = 0.03;
    if (t < pB) cam(V(lerp(0.3, 0.0, sm(S, pB, t)), 1.85, 4.4), V(-0.6, 1.9, 0), 38, S); else cam(V(-0.1, 1.7, lerp(4.3, 3.9, sm(pB, E, t))), V(-0.6, 1.75, 0.1), 38, pB);
    ov.push(() => { hudBar('DIA 1', '03:25', 'APAGÃO', '#ff5548'); stamp('REGRA 2', W / 2, 360, S + 0.03, { size: 130, t1: pB, c: '#1f7ae0' }); stamp('NÃO ABRE', W / 2, 560, T.nao, { size: 140, t1: pB });
      pill([{ txt: 'GELADEIRA FECHADA', size: 50 }, { txt: '4 HORAS', size: 110, c: '#7fc8ff' }], W / 2, 420, T.h4 - 0.25); pill([{ txt: 'FREEZER CHEIO', size: 50 }, { txt: '48 HORAS', size: 110, c: '#62f26e' }], W / 2, 680, T.h48 - 0.4, { rot: 0.02 }); });
  }
  else if (N === 'r3') {
    setMode('cor'); const em = 0.8 + 0.2 * Math.sin(t * 9); const cr = t > T.rei - 0.1 ? clamp((t - T.rei + 0.1) / 0.35, 0, 1) : undefined; corLight(() => 0, { emer: em, phone: 1.1, note: 1, crown: cr }); props.phoneL.position.set(0.5, 1.7, 1.5);
    gepPose(t, { af: (R, L) => { R.sh.rotation.x = -1.0; R.el.rotation.x = -1.45 + 0.06 * Math.sin(t * 8); R.sh.rotation.z = 0.4; L.sh.rotation.z = 0.5; L.el.rotation.x = -1.3; L.sh.rotation.x = -0.15; }, brow: cr !== undefined ? 0.8 : 0.3, headZ: cr !== undefined ? 0.06 : 0 });
    if (cr !== undefined && cr > 0.6 && cr < 1) { shakeA = 0.025; flashA = 0.25; }
    cam(V(lerp(0.5, 0.2, k), 1.95, lerp(3.5, 3.1, k)), V(-0.05, 2.0, 0), 38, t > T.rei - 0.1 ? T.rei - 0.1 : S);
    ov.push(() => { hudBar('DIA 1', '03:40', 'APAGÃO', '#ff5548'); stamp('REGRA 3', W / 2, 360, S + 0.03, { size: 130, t1: T.cart - 0.1, c: '#1f7ae0' }); pill([{ txt: 'DINHEIRO VIVO', size: 84, c: '#ffe03a' }], W / 2, 540, T.din - 0.05, { t1: T.cart - 0.1 });
      gone('CARTÃO', W / 2 - 200, 400, T.cart - 0.05, T.rei - 0.1); gone('PIX', W / 2 + 230, 400, T.cart + 0.25, T.rei - 0.1); if (t > T.rei - 0.05) txt('REI', W / 2, 420, 200, { c: '#ffc83a', s: back((t - T.rei + 0.05) / 0.25), rot: -0.05, glow: 'rgba(255,190,40,0.9)' }); });
  }
  else if (N === 'cel') {
    setMode('cor'); const em = 0.8 + 0.2 * Math.sin(t * 9);
    if (t < pB) { const d = sm(T.torre, pB - 0.2, t); corLight(() => 0, { emer: em, phone: 0.55, phoneObj: 1 }); props.phoneL.position.set(-0.25, 1.55, 1.0);
      gepPose(t, { af: (R, L) => { R.sh.rotation.x = -1.2; R.el.rotation.x = -1.1; R.sh.rotation.z = 0.25; }, headX: 0.25, headY: 0.15, brow: 0.5 * d });
      cam(V(lerp(-0.6, -0.3, k), 1.9, lerp(3.3, 2.9, k)), V(-0.1, 1.92, 0.1), 36, S);
      ov.push(() => { bar('TORRE DE CELULAR', 1 - 0.93 * d, 400, d > 0.7 ? '#ff5548' : '#62f26e', T.torre - 0.2, Math.round(100 - 93 * d) + '%'); pill([{ txt: 'AVISA A FAMÍLIA', size: 70, c: '#ffe03a' }, { txt: 'enquanto tem sinal', size: 44 }], W / 2, 640, T.fam - 0.1); }); }
    else { const d = sm(pB, pB + 0.5, t); corLight(() => 0, { emer: 0.35 * em * (1 - 0.5 * d), phone: 0.9 * (1 - d), phoneObj: 1 }); props.scrM.color.setRGB(1.6 * (1 - d), 1.9 * (1 - d), 2.4 * (1 - d));
      gepPose(t, { af: (R, L) => { R.sh.rotation.x = -0.4; R.el.rotation.x = -0.5; }, headY: 0.5 * Math.sin((t - pB) * 3), brow: 1 }); cam(V(0, 1.7, lerp(6.2, 7.2, sm(pB, E, t))), V(0, 1.2, 0), 44, pB); darkA = 0.25; }
    if (t < pB) props.scrM.color.setRGB(1.6, 1.9, 2.4);
    ov.push(() => hudBar('DIA 1', '04:10', 'SEM SINAL', '#ff5548'));
  }
  else if (N === 'dilema' || (N === 'cta' && t < pB)) {
    setMode('city'); cityState(t, { dawn: 1, focus: V(0, 0, 3), lit: () => 0 }); corLight(ALL, {}); gep.visible = true; corridorG.visible = false;
    if (N === 'dilema') { const lk = t > pB ? (t < T.ir - 0.1 ? -0.5 : 0.5) : 0.15 * Math.sin(t * 1.5);
      gepPose(t, { pos: V(-0.9, 0, 3), ry: 0.1, arms: t > pB ? 'shrug' : undefined, headY: lk, brow: 0.5 });
      if (t < pB) cam(V(lerp(-2.6, -2.0, k), 1.5, lerp(9.2, 8.2, k)), V(0.2, 1.2, 2), 42, S); else cam(V(-0.6, 1.9, 6.9), V(-0.8, 1.98, 3), 38, pB);
      ov.push(() => { hudBar('DIA 1', '06:00', 'SEM ENERGIA', '#ffb23a');
        if (t > T.tanque - 0.3 && t < pB) { const s = back((t - T.tanque + 0.3) / 0.3); ctx.save(); ctx.translate(W / 2, 520); ctx.scale(s, s); ctx.fillStyle = 'rgba(8,10,14,0.9)'; ctx.beginPath(); ctx.roundRect(-250, -190, 500, 260, 36); ctx.fill(); ctx.strokeStyle = '#444a55'; ctx.lineWidth = 26; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(0, 20, 150, Math.PI, 2 * Math.PI); ctx.stroke(); ctx.strokeStyle = '#ffb23a'; ctx.beginPath(); ctx.arc(0, 20, 150, Math.PI, Math.PI * 1.5); ctx.stroke(); const an = Math.PI * 1.5 + 0.05 * Math.sin(t * 7); ctx.strokeStyle = '#fff'; ctx.lineWidth = 12; ctx.beginPath(); ctx.moveTo(0, 20); ctx.lineTo(Math.cos(an) * 125, 20 + Math.sin(an) * 125); ctx.stroke(); ctx.font = '44px Cap'; ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.fillText('E', -190, 55); ctx.fillText('F', 190, 55); ctx.fillStyle = '#ffb23a'; ctx.fillText('1/2 TANQUE', 0, -165 + 20); ctx.restore(); }
        btn('FICAR NA CIDADE', W / 2, 400, '#4aa8ff', pB, 640); btn('IR PRO INTERIOR', W / 2, 580, '#ff9a3a', T.ir - 0.15, 640); }); }
    else { gepPose(t, { pos: V(-0.9, 0, 3), ry: 0.1, arms: 'point', brow: 0.4 }); cam(V(-0.5, 1.9, lerp(6.6, 6.0, sm(S, pB, t))), V(-0.85, 1.98, 3), 38, S);
      ov.push(() => { hudBar('DIA 1', '06:00', 'VOCÊ DECIDE', '#62f26e'); if (t > T.fica - 0.05) txt('FICA', W / 2 - 250, 400, 190, { c: '#4aa8ff', s: back((t - T.fica + 0.05) / 0.25), rot: -0.06 }); if (t > T.fica + 0.2) txt('ou', W / 2, 410, 70, {}); if (t > T.vai - 0.05) txt('VAI', W / 2 + 250, 400, 190, { c: '#ff9a3a', s: back((t - T.vai + 0.05) / 0.25), rot: 0.06 });
        pill([{ txt: 'A MAIS VOTADA VIRA O', size: 52 }, { txt: 'DIA 2', size: 130, c: '#ffe03a' }], W / 2, 660, T.dia2 - 0.1, { rot: 0.02 }); }); }
  }
  else { // cta, parte 2: sozinho no escuro
    setMode('cor'); const em = 0.8 + 0.2 * Math.sin(t * 9); corLight(() => 0, { emer: em, phone: 0.8 }); props.phoneL.position.set(0.3, 1.5, 1.4);
    gepPose(t, { af: (R, L) => { R.sh.rotation.x = -0.6; R.sh.rotation.z = 0.5; R.el.rotation.x = -1.9; L.sh.rotation.x = -0.6; L.sh.rotation.z = -0.5; L.el.rotation.x = -1.9; }, headY: 0.55 * Math.sin((t - pB) * 4.5), brow: 1, jig: 0.5 });
    cam(V(0.3, 1.9, lerp(3.6, 3.0, sm(pB, E, t))), V(0, 1.95, 0), 38, pB);
    ov.push(() => { pill([{ txt: 'SEGUE PRO', size: 60 }, { txt: 'DIA 2', size: 150, c: '#62f26e' }], W / 2, 330, T.segue - 0.1); });
  }
  sparkM.count = spN; sparkM.instanceMatrix.needsUpdate = true;
}

window.renderAt = (t) => {
  staging(t);
  composer.render();
  ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
  ctx.drawImage(renderer.domElement, 0, 0, W, H);
  if (sepiaA > 0) { ctx.save(); ctx.globalCompositeOperation = 'color'; ctx.globalAlpha = sepiaA; ctx.fillStyle = '#b08850'; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  if (darkA > 0) { ctx.fillStyle = `rgba(0,0,0,${darkA})`; ctx.fillRect(0, 0, W, H); }
  const g = ctx.createRadialGradient(W / 2, H * 0.48, H * 0.26, W / 2, H / 2, H * 0.74); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(8,6,2,${vig})`); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  grain(t);
  if (flashA > 0) { ctx.fillStyle = `rgba(255,246,225,${Math.min(1, flashA)})`; ctx.fillRect(0, 0, W, H); }
  for (const f of ov) f();
  const fade = sm(TOTAL - 0.3, TOTAL, t); if (fade > 0) { ctx.fillStyle = `rgba(0,0,0,${fade})`; ctx.fillRect(0, 0, W, H); }
  caption(t);
  return out.toDataURL('image/jpeg', 0.92);
};
window.TOTAL = TOTAL;
window.SHOTS = shots.map(s => [s.name, +s.start.toFixed(2), +s.end.toFixed(2)]);
window.TT = T;
document.title = 'ready';
