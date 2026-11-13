// Shared three.js viewer for the arcade pit bench models.
// Geometry comes from cad/arcade_pit.py (pit_meshes.json, mm, Z-up CAD frame).
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

export { THREE };

export async function loadData() {
  const r = await fetch('pit_meshes.json');
  if (!r.ok) throw new Error('Could not load model data (' + r.status + ')');
  return r.json();
}

function decode(b64, Type) {
  const bin = atob(b64);
  const buf = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);
  return new Type(buf.buffer);
}

// ---------------------------------------------------------------- textures
function woodTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 512;
  const g = c.getContext('2d');
  g.fillStyle = '#d9bd91';
  g.fillRect(0, 0, 512, 512);
  let seed = 3;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < 140; i++) {
    const y0 = rnd() * 512, amp = 2 + rnd() * 7, f = 0.004 + rnd() * 0.01, ph = rnd() * 6;
    g.strokeStyle = rnd() > 0.5 ? `rgba(150,105,60,${0.05 + rnd() * 0.12})` : `rgba(250,232,200,${0.05 + rnd() * 0.1})`;
    g.lineWidth = 0.6 + rnd() * 2.2;
    g.beginPath();
    for (let x = 0; x <= 512; x += 8) {
      const y = y0 + Math.sin(x * f * 6.28 + ph) * amp;
      x === 0 ? g.moveTo(x, y) : g.lineTo(x, y);
    }
    g.stroke();
  }
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  return t;
}

function screenTexture() {
  const c = document.createElement('canvas');
  c.width = 512; c.height = 390;
  const g = c.getContext('2d');
  const grad = g.createLinearGradient(0, 0, 0, 390);
  grad.addColorStop(0, '#07041a'); grad.addColorStop(0.55, '#1b0838'); grad.addColorStop(1, '#3a0b4a');
  g.fillStyle = grad; g.fillRect(0, 0, 512, 390);
  // sun
  g.fillStyle = '#ff9a3c';
  g.beginPath(); g.arc(256, 205, 70, Math.PI, 0); g.fill();
  g.fillStyle = '#1b0838';
  for (let i = 0; i < 5; i++) g.fillRect(180, 150 + i * 12, 152, 3 + i);
  // perspective grid
  g.strokeStyle = '#ff3fd0'; g.lineWidth = 1.5;
  for (let i = -12; i <= 12; i++) { g.beginPath(); g.moveTo(256 + i * 8, 210); g.lineTo(256 + i * 60, 390); g.stroke(); }
  for (let j = 0; j < 9; j++) { const y = 210 + Math.pow(j / 8, 2) * 180; g.beginPath(); g.moveTo(0, y); g.lineTo(512, y); g.stroke(); }
  // HUD text
  g.fillStyle = '#7df9ff'; g.font = 'bold 22px monospace';
  g.fillText('1UP  004200', 20, 34);
  g.fillStyle = '#ffe66d'; g.fillText('HI 098750', 340, 34);
  g.fillStyle = '#ffffff'; g.font = 'bold 26px monospace';
  g.fillText('INSERT COIN', 172, 110);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

// ---------------------------------------------------------------- materials
export function makeMaterials() {
  const wood = woodTexture();
  return {
    ply: new THREE.MeshStandardMaterial({ color: 0xffffff, map: wood, roughness: 0.72, metalness: 0 }),
    black: new THREE.MeshStandardMaterial({ color: 0x141414, roughness: 0.55, metalness: 0.05 }),
    acrylic: new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0.04, metalness: 0, transparent: true, opacity: 0.12, clearcoat: 1, depthWrite: false }),
    glass: new THREE.MeshPhysicalMaterial({ color: 0x0b0b0e, roughness: 0.04, metalness: 0.1, transparent: true, opacity: 0.45, clearcoat: 1, depthWrite: false }),
    steel: new THREE.MeshStandardMaterial({ color: 0xd4d8dc, roughness: 0.25, metalness: 1 }),
    led: new THREE.MeshBasicMaterial({ color: 0xffd08a }),
    screen: new THREE.MeshBasicMaterial({ map: screenTexture() }),
    pine: new THREE.MeshStandardMaterial({ color: 0xc9a06a, roughness: 0.8 }),
    maple: new THREE.MeshStandardMaterial({ color: 0xe8d2a8, roughness: 0.55 }),
    stay: new THREE.MeshStandardMaterial({ color: 0x3a3a3f, roughness: 0.45, metalness: 0.3 }),
    rope: new THREE.MeshStandardMaterial({ color: 0xe0662a, roughness: 0.8 }),
    diffuser: new THREE.MeshBasicMaterial({ color: 0xfff1d6 }),
    gold: new THREE.MeshStandardMaterial({ color: 0xf4c430, roughness: 0.3, metalness: 0.9 }),
    led_blue: new THREE.MeshBasicMaterial({ color: 0x5a95ff }),
    glow_green: new THREE.MeshBasicMaterial({ color: 0x9bbc0f }),
    glow_warm: new THREE.MeshBasicMaterial({ color: 0xffd166 }),
    glow_blue: new THREE.MeshBasicMaterial({ color: 0x4cc9f0 }),
    pvc: new THREE.MeshStandardMaterial({ color: 0xbfc3c7, roughness: 0.5 }),
    ctrl: new THREE.MeshStandardMaterial({ color: 0x2b2d31, roughness: 0.5, metalness: 0.1 }),
    base_ply: new THREE.MeshStandardMaterial({ color: 0x3b3936, roughness: 0.6, metalness: 0.05 }),
    pp_red: new THREE.MeshStandardMaterial({ color: 0xc62828, roughness: 0.4 }),
    pp_black: new THREE.MeshStandardMaterial({ color: 0x1c1c1c, roughness: 0.4 }),
    floor: new THREE.MeshStandardMaterial({ color: 0x5f5c58, roughness: 0.38, metalness: 0.0 }),
    _items: new Map(),
    item(hex) {
      if (!this._items.has(hex)) this._items.set(hex, new THREE.MeshStandardMaterial({ color: hex, roughness: 0.45 }));
      return this._items.get(hex);
    },
  };
}

// ---------------------------------------------------------------- geometry
const geoCache = new Map();
function partGeometry(p) {
  const key = p.pos + '|' + p.idx;
  if (geoCache.has(key)) return geoCache.get(key);
  let g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(decode(p.pos, Float32Array), 3));
  g.setIndex(new THREE.BufferAttribute(decode(p.idx, Uint32Array), 1));
  g = g.toNonIndexed();
  g.computeVertexNormals();
  if (p.mat === 'ply' || p.mat === 'screen') addUVs(g, p.mat === 'screen');
  geoCache.set(key, g);
  return g;
}

function addUVs(g, planar) {
  const pos = g.attributes.position, nrm = g.attributes.normal;
  const uv = new Float32Array(pos.count * 2);
  g.computeBoundingBox();
  const bb = g.boundingBox;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i);
    if (planar) {
      uv[2 * i] = (x - bb.min.x) / (bb.max.x - bb.min.x);
      uv[2 * i + 1] = (y - bb.min.y) / (bb.max.y - bb.min.y);
      continue;
    }
    const ax = Math.abs(nrm.getX(i)), ay = Math.abs(nrm.getY(i)), az = Math.abs(nrm.getZ(i));
    let u, v;
    if (az >= ax && az >= ay) { u = x; v = y; } else if (ay >= ax) { u = x; v = z; } else { u = y; v = z; }
    uv[2 * i] = u / 700; uv[2 * i + 1] = v / 700;
  }
  g.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
}

function meshFor(p, mats) {
  const mat = p.mat === 'item' ? mats.item(p.color || '#888888') : mats[p.mat];
  const m = new THREE.Mesh(partGeometry(p), mat);
  m.castShadow = !['acrylic', 'glass', 'led', 'screen', 'diffuser'].includes(p.mat);
  m.receiveShadow = true;
  m.userData.partName = p.name;
  m.userData.isItem = p.mat === 'item';
  return m;
}

/** Build a bench on its base as a group in CAD frame (mm, Z-up).
 *  Each lid hangs off its own pivot group on the hinge axis. */
export function buildBench(data, variant, mats, { lights = true, contents = null, base = 'base' } = {}) {
  const v = data.variants[variant];
  const group = new THREE.Group();
  // the low base the bench drops onto (pins, blind-mate 5 V connector, cable slots)
  if (base && data.variants[base]) for (const p of data.variants[base].parts) group.add(meshFor(p, mats));
  const lids = v.pivots.map((pv) => {
    const g = new THREE.Group();
    g.position.set(0, pv.y, pv.z);
    g.userData = { isLid: true, angle: 0, target: 0, dir: pv.dir ?? -1, max: pv.max ?? 100 };
    group.add(g);
    return g;
  });
  const items = [];
  for (const p of v.parts) {
    const m = meshFor(p, mats);
    if (p.lid !== undefined) { const pv = v.pivots[p.lid]; m.position.set(0, -pv.y, -pv.z); lids[p.lid].add(m); }
    else group.add(m);
    if (m.userData.isItem) items.push(m);
  }
  if (contents !== null && data.contents) {
    for (const p of data.contents[contents % data.contents.length].parts) {
      const m = meshFor(p, mats);
      group.add(m);
      items.push(m);
    }
  }
  const glow = [];
  if (lights) {
    for (const L of v.lights) {
      if (L.target) {
        // downlight from the strip in the header, aimed at the display floor
        const sp = new THREE.SpotLight(0xffc27a, 0, 0.8, 1.25, 0.95, 2);
        sp.position.set(L.x, L.y, L.z);
        sp.target.position.set(...L.target);
        sp.userData.gain = 1.6;
        group.add(sp, sp.target);
        glow.push(sp);
        // faint fill so light bouncing off the birch liner reads
        const fill = new THREE.PointLight(0xffb45e, 0, 0.6, 2);
        fill.position.set(L.x, L.target[1], (L.z + L.target[2]) / 2);
        fill.userData.gain = 0.5;
        group.add(fill);
        glow.push(fill);
      } else {
        const pl = new THREE.PointLight(0xffb45e, 0, 0.75, 2);
        pl.position.set(L.x, L.y, L.z);
        group.add(pl);
        glow.push(pl);
      }
    }
  }
  // rope limiters: case eye fixed, lid eye rides on the lid; redrawn as the lid moves
  const ropes = [];
  v.pivots.forEach((pv, k) => {
    if (!pv.rope) return;
    for (const x of pv.rope.x) {
      const mesh = new THREE.Mesh(new THREE.BufferGeometry(), mats.rope);
      mesh.castShadow = true;
      group.add(mesh);
      ropes.push({ mesh, x, pv, lid: lids[k] });
    }
  });
  group.userData = { variant, lids, items, glow, ropes };
  updateRopes(group);
  return group;
}

/** A base section, or the pit-level base joints ('ring_hw'), without a bench. */
export function buildBase(data, name, mats, keep = null) {
  const g = new THREE.Group();
  for (const p of data.variants[name].parts) if (!keep || keep(p.name)) g.add(meshFor(p, mats));
  g.userData = { lids: [], items: [], glow: [], ropes: [] };
  return g;
}

/** Rebuild rope geometry for the current lid angles: slack loop when closed, straight at the stop. */
export function updateRopes(bench) {
  for (const r of bench.userData.ropes || []) {
    const { a, b, c, L, lid_dz } = r.pv.rope;
    const u = r.lid.userData;
    const phi = u.dir * THREE.MathUtils.degToRad(Math.min(u.angle, u.max));
    const p0 = new THREE.Vector3(r.x, r.pv.y + a, r.pv.z - b);
    const p1 = new THREE.Vector3(r.x, r.pv.y + c * Math.cos(phi) - lid_dz * Math.sin(phi),
                                 r.pv.z + c * Math.sin(phi) + lid_dz * Math.cos(phi));
    const d = p0.distanceTo(p1);
    const sag = d < L ? Math.sqrt(L * L - d * d) / 2 : 0;
    const mid = p0.clone().add(p1).multiplyScalar(0.5);
    mid.z -= 2 * sag;
    const curve = new THREE.QuadraticBezierCurve3(p0, mid, p1);
    r.mesh.geometry.dispose();
    r.mesh.geometry = new THREE.TubeGeometry(curve, 20, 1.6, 6, false);
  }
}

/** Set the target angle (degrees) of every lid on a bench. */
export function setLids(bench, deg) { bench.userData.lids.forEach(l => l.userData.target = deg); }

export function buildTable(data, mats) {
  const g = new THREE.Group();
  for (const p of data.variants.table.parts) g.add(meshFor(p, mats));
  const screenGlow = new THREE.PointLight(0x9a6bff, 0, 1.5, 2);
  screenGlow.position.set(0, 0, data.params.table[2] + 250);
  g.add(screenGlow);
  g.userData.glow = [screenGlow];
  return g;
}

/** Bench placements exported by ring_locations() in the CAD script (mm, degrees). */
export function ringPlacements(data) {
  return data.placements.map(p => ({ ...p, rot: p.rot * Math.PI / 180 }));
}

// ---------------------------------------------------------------- stage
export function createStage(container, { floorSize = 12 } = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0d0c0b);
  scene.fog = new THREE.Fog(0x0d0c0b, floorSize * 0.45, floorSize * 0.95);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;

  const camera = new THREE.PerspectiveCamera(38, 1, 0.05, 100);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.maxPolarAngle = Math.PI * 0.495;
  controls.minDistance = 0.4;
  controls.maxDistance = 18;

  // CAD (mm, Z-up) -> three (m, Y-up)
  const root = new THREE.Group();
  root.rotation.x = -Math.PI / 2;
  root.scale.setScalar(0.001);
  scene.add(root);

  const floor = new THREE.Mesh(new THREE.CircleGeometry(floorSize, 64), new THREE.MeshStandardMaterial({ color: 0x5f5c58, roughness: 0.38 }));
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);

  const hemi = new THREE.HemisphereLight(0xfff4e6, 0x2a2622, 0.9);
  scene.add(hemi);
  const key = new THREE.DirectionalLight(0xfff1dd, 2.0);
  key.position.set(4, 7, 5);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.left = key.shadow.camera.bottom = -4;
  key.shadow.camera.right = key.shadow.camera.top = 4;
  key.shadow.bias = -0.0004;
  key.shadow.normalBias = 0.02;
  scene.add(key);

  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), 0.3, 0.4, 0.9);
  composer.addPass(bloom);
  composer.addPass(new OutputPass());

  const stage = { renderer, scene, camera, controls, root, floor, hemi, key, bloom, composer, glow: [], onFrame: [] };

  stage.setNight = (night) => {
    const envI = night ? 0.12 : 0.7;
    scene.traverse(o => { if (o.material && 'envMapIntensity' in o.material) o.material.envMapIntensity = envI; });
    hemi.intensity = night ? 0.06 : 0.9;
    key.intensity = night ? 0.12 : 2.0;
    scene.background.set(night ? 0x060505 : 0x0d0c0b);
    scene.fog.color.copy(scene.background);
    bloom.strength = night ? 0.5 : 0.2;
    for (const pl of stage.glow) pl.intensity = (night ? pl.userData.nightI : pl.userData.dayI) * (pl.userData.gain ?? 1);
  };

  function resize() {
    const w = container.clientWidth, h = container.clientHeight;
    if (!w || !h) return;
    renderer.setSize(w, h, false);
    composer.setSize(w, h);
    bloom.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(container);
  resize();

  // camera tween
  let tween = null;
  stage.flyTo = (pos, target, ms = 900) => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    tween = { p0: camera.position.clone(), t0: controls.target.clone(), p1: new THREE.Vector3(...pos), t1: new THREE.Vector3(...target), start: performance.now(), ms: reduce ? 1 : ms };
  };

  const clock = new THREE.Clock();
  renderer.setAnimationLoop(() => {
    const dt = Math.min(clock.getDelta(), 0.05);
    if (tween) {
      const k = Math.min(1, (performance.now() - tween.start) / tween.ms);
      const e = k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
      camera.position.lerpVectors(tween.p0, tween.p1, e);
      controls.target.lerpVectors(tween.t0, tween.t1, e);
      if (k >= 1) tween = null;
    }
    for (const f of stage.onFrame) f(dt);
    controls.update();
    composer.render();
  });
  return stage;
}

/** Register bench lights with the stage's day/night switch. */
export function registerGlow(stage, lights, dayI, nightI) {
  for (const pl of lights) { pl.userData.dayI = dayI; pl.userData.nightI = nightI; stage.glow.push(pl); }
}

/** Ease every lid toward its target angle (degrees). */
export function lidAnimator(benches) {
  return (dt) => {
    for (const b of benches) {
      let moved = false;
      for (const lid of b.userData.lids) {
        const u = lid.userData;
        if (u.angle === u.target) continue;
        if (Math.abs(u.target - u.angle) < 0.05) u.angle = u.target;
        else u.angle += (u.target - u.angle) * Math.min(1, dt * 6);
        lid.rotation.x = u.dir * THREE.MathUtils.degToRad(Math.min(u.angle, u.max));
        moved = true;
      }
      if (moved) updateRopes(b);
    }
  };
}

export const fmt = {
  mm: (v) => Math.round(v).toLocaleString('en-US') + ' mm',
  ftin(v) {
    const t = Math.round(v / 25.4), ft = Math.floor(t / 12), inch = t % 12;
    return ft ? `${ft}′ ${inch}″` : `${t}″`;
  },
};
